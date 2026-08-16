"""Lexora (local LLM) client implementation with smart model selection support."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from cognilens.config import LLMConfig

from .base import LLMClient, LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class ModelCapability:
    """Represents a model's capabilities from Lexora API."""

    model_id: str
    capabilities: list[str]
    context_length: int = 4096
    metadata: dict[str, Any] = field(default_factory=dict[str, Any])


@dataclass
class ModelCapabilitiesCache:
    """Cached model capabilities with TTL."""

    models: list[ModelCapability]
    fetched_at: float
    ttl_seconds: int

    def is_expired(self) -> bool:
        """Check if cache has expired."""
        return time.time() - self.fetched_at > self.ttl_seconds

    def find_by_capability(self, capability: str) -> str | None:
        """Find first model with the specified capability."""
        for model in self.models:
            if capability in model.capabilities:
                return model.model_id
        return None


@dataclass
class ClassificationResult:
    """Result from task classification API."""

    task_type: str
    recommended_capability: str
    confidence: float
    recommended_model: str | None = None


class LexoraClient(LLMClient):
    """Lexora (local LLM) client implementation with smart model selection.

    Supports the new Lexora APIs:
    - GET /v1/models/capabilities - Get model capabilities
    - POST /v1/classify-task - Classify a task to determine optimal model
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._base_url = config.base_url or "http://localhost:8001"
        self._capabilities_cache: ModelCapabilitiesCache | None = None
        self._cache_ttl = config.smart_selection.cache_ttl_seconds

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        model: str | None = None,
    ) -> LLMResponse:
        """Generate text using Lexora API.

        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Override model to use (for smart selection)
        """
        use_model = model or self.config.model

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self._base_url}/v1/completions",
                json={
                    "model": use_model,
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                content=data.get("content", ""),
                model=data.get("model", use_model),
                tokens_used=data.get("tokens_used", 0),
                finish_reason=data.get("finish_reason"),
            )

    async def count_tokens(self, text: str) -> int:
        """Count tokens using Lexora API or fallback to approximation."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    f"{self._base_url}/v1/tokenize",
                    json={"text": text},
                )
                if response.status_code == 200:
                    # int(): the JSON body is untyped and the caller is promised an int.
                    return int(response.json().get("count", len(text) // 4))
        except Exception as exc:  # noqa: BLE001 - deliberately broad, see below
            # This is a token *estimate*: every failure mode has the same right
            # answer, which is to fall back to the heuristic rather than propagate.
            # Logged rather than passed so a tokenizer outage is visible instead of
            # silently degrading every count in the service.
            logger.debug("Lexora tokenize failed, using heuristic: %s", exc)
        return len(text) // 4

    async def health_check(self) -> bool:
        """Check if Lexora service is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self._base_url}/health")
                return response.status_code == 200
        except Exception:  # noqa: BLE001
            # A health check that raises is a worse health check.
            return False

    async def get_model_capabilities(
        self, force_refresh: bool = False
    ) -> ModelCapabilitiesCache | None:
        """Fetch model capabilities from Lexora API.

        Args:
            force_refresh: Force refresh even if cache is valid

        Returns:
            ModelCapabilitiesCache if successful, None on failure
        """
        # Return cached data if valid
        if (
            not force_refresh
            and self._capabilities_cache is not None
            and not self._capabilities_cache.is_expired()
        ):
            return self._capabilities_cache

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(f"{self._base_url}/v1/models/capabilities")
                response.raise_for_status()
                data = response.json()

                models = []
                for model_data in data.get("models", []):
                    models.append(
                        ModelCapability(
                            model_id=model_data.get("model_id", ""),
                            capabilities=model_data.get("capabilities", []),
                            context_length=model_data.get("context_length", 4096),
                            metadata=model_data.get("metadata", {}),
                        )
                    )

                self._capabilities_cache = ModelCapabilitiesCache(
                    models=models,
                    fetched_at=time.time(),
                    ttl_seconds=self._cache_ttl,
                )
                return self._capabilities_cache

        except Exception:  # noqa: BLE001
            # Deliberately broad: stale capabilities beat no capabilities.
            # Return stale cache if available, otherwise None
            return self._capabilities_cache

    async def classify_task(
        self, task_description: str
    ) -> ClassificationResult | None:
        """Classify a task to determine optimal model capability.

        Args:
            task_description: Description or preview of the task

        Returns:
            ClassificationResult if successful, None on failure
        """
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    f"{self._base_url}/v1/classify-task",
                    json={"task_description": task_description},
                )
                response.raise_for_status()
                data = response.json()

                return ClassificationResult(
                    task_type=data.get("task_type", "general"),
                    recommended_capability=data.get("recommended_capability", "general"),
                    confidence=data.get("confidence", 0.0),
                    recommended_model=data.get("recommended_model"),
                )

        except Exception:  # noqa: BLE001
            # Classification is advisory; failing it must not fail the call.
            return None

    def find_model_for_capability(self, capability: str) -> str | None:
        """Find a model with the specified capability from cache.

        Args:
            capability: The capability to search for

        Returns:
            Model ID if found, None otherwise
        """
        if self._capabilities_cache is None:
            return None
        return self._capabilities_cache.find_by_capability(capability)

    def clear_cache(self) -> None:
        """Clear the capabilities cache."""
        self._capabilities_cache = None

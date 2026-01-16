"""Lexora (local LLM) client implementation - stub for future use."""

from __future__ import annotations

from typing import Optional

import httpx

from cognilens.config import LLMConfig

from .base import LLMClient, LLMResponse


class LexoraClient(LLMClient):
    """Lexora (local LLM) client implementation.

    This is a stub implementation for future Lexora integration.
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._base_url = config.base_url or "http://localhost:8001"

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text using Lexora API."""
        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            response = await client.post(
                f"{self._base_url}/v1/completions",
                json={
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
                model=data.get("model", "lexora"),
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
                    return response.json().get("count", len(text) // 4)
        except Exception:
            pass
        return len(text) // 4

    async def health_check(self) -> bool:
        """Check if Lexora service is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self._base_url}/health")
                return response.status_code == 200
        except Exception:
            return False

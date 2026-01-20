"""Model selector service for smart model selection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional

from cognilens.config import LLMConfig
from cognilens.core.types import CompressionStyle

if TYPE_CHECKING:
    from .lexora_client import LexoraClient


class SelectionMethod(str, Enum):
    """How the model was selected."""

    CLASSIFICATION = "classification"
    CAPABILITY_MATCH = "capability_match"
    HEURISTIC = "heuristic"
    DEFAULT = "default"


@dataclass
class ModelSelection:
    """Result of model selection."""

    model_id: str
    method: SelectionMethod
    capability: Optional[str] = None
    confidence: float = 1.0


# Heuristic patterns for task classification
HEURISTIC_PATTERNS = {
    "code": [
        "def ",
        "class ",
        "function ",
        "import ",
        "```",
        "=>",
        "const ",
        "let ",
        "var ",
    ],
    "summarization": [
        "summarize",
        "summary",
        "brief",
        "concise",
        "overview",
        "key points",
    ],
    "reasoning": [
        "diff",
        "compare",
        "difference",
        "change",
        "before",
        "after",
    ],
}


class ModelSelector:
    """Service for selecting optimal models for compression tasks.

    Implements a multi-level fallback strategy:
    1. Task classification API (if enabled)
    2. Capability matching from cached model data
    3. Content-based heuristics
    4. Default model fallback
    """

    def __init__(self, lexora_client: LexoraClient, config: LLMConfig) -> None:
        """Initialize ModelSelector.

        Args:
            lexora_client: LexoraClient instance for API calls
            config: LLM configuration with smart selection settings
        """
        self.client = lexora_client
        self.config = config
        self._smart_config = config.smart_selection

    @property
    def is_enabled(self) -> bool:
        """Check if smart selection is enabled."""
        return self._smart_config.enabled

    async def select_model(
        self,
        style: CompressionStyle,
        content_preview: Optional[str] = None,
    ) -> ModelSelection:
        """Select the optimal model for a compression task.

        Args:
            style: The compression style being used
            content_preview: Optional preview of content for classification

        Returns:
            ModelSelection with selected model and metadata
        """
        if not self.is_enabled:
            return ModelSelection(
                model_id=self.config.model,
                method=SelectionMethod.DEFAULT,
            )

        # Get capability needed for this style
        capability = self._get_capability_for_style(style)

        # 1. Try classification API if enabled and we have content
        if self._smart_config.classify_tasks and content_preview:
            selection = await self._try_classification(content_preview)
            if selection:
                return selection

        # 2. Try capability matching from cached data
        selection = await self._try_capability_match(capability)
        if selection:
            return selection

        # 3. Try heuristic-based selection
        if content_preview:
            selection = self._try_heuristic(content_preview)
            if selection:
                return selection

        # 4. Fallback to default model
        if self._smart_config.fallback_to_default:
            return ModelSelection(
                model_id=self.config.model,
                method=SelectionMethod.DEFAULT,
                capability=capability,
            )

        # No model found and fallback disabled
        return ModelSelection(
            model_id=self.config.model,
            method=SelectionMethod.DEFAULT,
            confidence=0.0,
        )

    def _get_capability_for_style(self, style: CompressionStyle) -> str:
        """Map compression style to required capability.

        Args:
            style: The compression style

        Returns:
            Capability string (e.g., "summarization", "code", "reasoning")
        """
        style_key = style.value
        return self._smart_config.strategy_capability_map.get(style_key, "general")

    async def _try_classification(
        self, content_preview: str
    ) -> Optional[ModelSelection]:
        """Try to classify task using Lexora API.

        Args:
            content_preview: Content to classify

        Returns:
            ModelSelection if classification succeeded, None otherwise
        """
        result = await self.client.classify_task(content_preview)
        if result is None:
            return None

        # If API returned a specific model recommendation, use it
        if result.recommended_model:
            return ModelSelection(
                model_id=result.recommended_model,
                method=SelectionMethod.CLASSIFICATION,
                capability=result.recommended_capability,
                confidence=result.confidence,
            )

        # Otherwise, try to find a model with the recommended capability
        model_id = self.client.find_model_for_capability(result.recommended_capability)
        if model_id:
            return ModelSelection(
                model_id=model_id,
                method=SelectionMethod.CLASSIFICATION,
                capability=result.recommended_capability,
                confidence=result.confidence,
            )

        return None

    async def _try_capability_match(
        self, capability: str
    ) -> Optional[ModelSelection]:
        """Try to find model with required capability from cache.

        Args:
            capability: Required capability

        Returns:
            ModelSelection if match found, None otherwise
        """
        # Ensure we have capabilities data
        cache = await self.client.get_model_capabilities()
        if cache is None:
            return None

        model_id = cache.find_by_capability(capability)
        if model_id:
            return ModelSelection(
                model_id=model_id,
                method=SelectionMethod.CAPABILITY_MATCH,
                capability=capability,
            )

        return None

    def _try_heuristic(self, content_preview: str) -> Optional[ModelSelection]:
        """Apply heuristic patterns to select model.

        Args:
            content_preview: Content to analyze

        Returns:
            ModelSelection if heuristic matched, None otherwise
        """
        content_lower = content_preview.lower()

        # Check each capability's patterns
        for capability, patterns in HEURISTIC_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in content_lower:
                    # Found a match, try to get a model with this capability
                    model_id = self.client.find_model_for_capability(capability)
                    if model_id:
                        return ModelSelection(
                            model_id=model_id,
                            method=SelectionMethod.HEURISTIC,
                            capability=capability,
                            confidence=0.7,  # Lower confidence for heuristics
                        )
                    break  # Move to next capability

        return None

    async def refresh_capabilities(self) -> bool:
        """Force refresh of model capabilities cache.

        Returns:
            True if refresh succeeded, False otherwise
        """
        cache = await self.client.get_model_capabilities(force_refresh=True)
        return cache is not None

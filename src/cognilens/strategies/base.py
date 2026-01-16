"""Base class for compression strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod

from cognilens.core.types import CompressionRequest, CompressionResult
from cognilens.llm.base import LLMClient


class CompressionStrategy(ABC):
    """Abstract base class for compression strategies."""

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name identifier."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description."""
        ...

    @abstractmethod
    async def compress(self, request: CompressionRequest) -> CompressionResult:
        """Execute the compression strategy."""
        ...

    async def _calculate_quality_score(
        self,
        original: str,
        compressed: str,
        preserved_elements: list[str],
    ) -> float:
        """Calculate compression quality score (0.0-1.0)."""
        # Check if preserved elements are present
        preserved_count = sum(
            1 for elem in preserved_elements if elem.lower() in compressed.lower()
        )
        preservation_ratio = (
            preserved_count / len(preserved_elements) if preserved_elements else 1.0
        )

        # Basic coherence check (has content, not too short)
        original_tokens = await self.llm.count_tokens(original)
        compressed_tokens = await self.llm.count_tokens(compressed)

        # Penalize if too aggressively compressed or barely compressed
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 0
        ratio_score = 1.0 - abs(0.3 - compression_ratio)  # Optimal around 30%
        ratio_score = max(0.0, min(1.0, ratio_score))

        # Weighted combination
        quality = (preservation_ratio * 0.6) + (ratio_score * 0.4)
        return round(quality, 3)

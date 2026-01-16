"""Detailed compression strategy - moderate compression preserving key details."""

from __future__ import annotations

from cognilens.core.types import CompressionRequest, CompressionResult, CompressionStyle
from cognilens.prompts.builder import PromptBuilder

from .base import CompressionStrategy


class DetailedStrategy(CompressionStrategy):
    """Detailed compression strategy - moderate compression preserving key details."""

    @property
    def name(self) -> str:
        return "detailed"

    @property
    def description(self) -> str:
        return "Moderate compression (50%) - implementation reference, API specs"

    async def compress(self, request: CompressionRequest) -> CompressionResult:
        """Compress text while preserving detailed information."""
        original_tokens = await self.llm.count_tokens(request.text)
        target_tokens = request.target_tokens or int(original_tokens * 0.5)

        prompt = PromptBuilder.build_summarize_prompt(
            text=request.text,
            max_tokens=target_tokens,
            style=CompressionStyle.DETAILED,
            preserve=request.preserve,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=target_tokens + 200,
            temperature=0.5,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)
        quality = await self._calculate_quality_score(
            request.text, response.content, request.preserve
        )

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=request.preserve,
            quality_score=quality,
            metadata={"strategy": self.name, "model": response.model},
        )

"""Concise compression strategy - maximum compression while keeping essence."""

from __future__ import annotations

from cognilens.core.types import CompressionRequest, CompressionResult
from cognilens.prompts.builder import PromptBuilder

from .base import CompressionStrategy


class ConciseStrategy(CompressionStrategy):
    """Concise compression strategy - maximum compression while keeping essence."""

    @property
    def name(self) -> str:
        return "concise"

    @property
    def description(self) -> str:
        return "Maximum compression (80%) - overview and task lists"

    async def compress(self, request: CompressionRequest) -> CompressionResult:
        """Compress text to concise summary."""
        original_tokens = await self.llm.count_tokens(request.text)
        target_tokens = request.target_tokens or int(original_tokens * 0.2)

        prompt = PromptBuilder.build_summarize_prompt(
            text=request.text,
            max_tokens=target_tokens,
            style=request.style,
            preserve=request.preserve,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=target_tokens + 100,  # Buffer for LLM
            temperature=0.3,
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

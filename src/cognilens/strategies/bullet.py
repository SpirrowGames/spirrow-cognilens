"""Bullet point compression strategy - structured list format."""

from __future__ import annotations

from typing import Optional

from cognilens.core.types import CompressionRequest, CompressionResult, CompressionStyle
from cognilens.prompts.builder import PromptBuilder

from .base import CompressionStrategy


class BulletStrategy(CompressionStrategy):
    """Bullet point compression strategy - structured list format."""

    @property
    def name(self) -> str:
        return "bullet"

    @property
    def description(self) -> str:
        return "Bullet point format - structured key points"

    async def compress(
        self, request: CompressionRequest, *, model: Optional[str] = None
    ) -> CompressionResult:
        """Compress text to bullet point format."""
        original_tokens = await self.llm.count_tokens(request.text)
        target_tokens = request.target_tokens or int(original_tokens * 0.3)

        prompt = PromptBuilder.build_summarize_prompt(
            text=request.text,
            max_tokens=target_tokens,
            style=CompressionStyle.BULLET,
            preserve=request.preserve,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=target_tokens + 150,
            temperature=0.4,
            model=model,
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

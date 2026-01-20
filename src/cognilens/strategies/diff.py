"""Diff-focused compression strategy - highlights changes."""

from __future__ import annotations

from typing import Optional

from cognilens.core.types import CompressionRequest, CompressionResult, DiffInput
from cognilens.prompts.builder import PromptBuilder

from .base import CompressionStrategy


class DiffStrategy(CompressionStrategy):
    """Diff-focused compression strategy - highlights changes."""

    @property
    def name(self) -> str:
        return "diff"

    @property
    def description(self) -> str:
        return "Diff-focused - highlights additions, deletions, and changes"

    async def compress(
        self, request: CompressionRequest, *, model: Optional[str] = None
    ) -> CompressionResult:
        """Compress by summarizing differences between two texts."""
        # DiffStrategy expects diff_input in metadata
        diff_input = request.metadata.get("diff_input")
        if not diff_input:
            raise ValueError("DiffStrategy requires 'diff_input' in metadata")

        if isinstance(diff_input, dict):
            diff_input = DiffInput(**diff_input)

        original_tokens = await self.llm.count_tokens(diff_input.before + diff_input.after)

        prompt = PromptBuilder.build_diff_prompt(diff_input)

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=request.target_tokens or 500,
            temperature=0.3,
            model=model,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=["additions", "deletions", "changes"],
            quality_score=0.8,  # Diff quality is harder to measure
            metadata={
                "strategy": self.name,
                "model": response.model,
                "focus": diff_input.focus,
            },
        )

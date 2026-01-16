"""Main compression engine coordinating strategies and LLM."""

from __future__ import annotations

from typing import Optional

from cognilens.config import get_settings
from cognilens.llm import LLMClient, create_llm_client
from cognilens.prompts.builder import PromptBuilder
from cognilens.strategies import get_strategy

from .types import (
    CompressionRequest,
    CompressionResult,
    CompressionStyle,
    DiffInput,
    Document,
    ProgressiveStage,
)


class CompressionEngine:
    """Main compression engine coordinating strategies and LLM."""

    def __init__(self, llm_client: Optional[LLMClient] = None) -> None:
        if llm_client:
            self.llm = llm_client
        else:
            settings = get_settings()
            self.llm = create_llm_client(settings.llm)

    async def summarize(
        self,
        text: str,
        max_tokens: int = 500,
        style: str = "concise",
        preserve: list[str] | None = None,
    ) -> CompressionResult:
        """Summarize text with specified style."""
        compression_style = CompressionStyle(style)
        strategy = get_strategy(compression_style, self.llm)

        request = CompressionRequest(
            text=text,
            style=compression_style,
            target_tokens=max_tokens,
            preserve=preserve or [],
        )

        return await strategy.compress(request)

    async def compress_context(
        self,
        full_context: str,
        task_description: str,
        target_tokens: int = 500,
    ) -> CompressionResult:
        """Compress context for specific task execution."""
        original_tokens = await self.llm.count_tokens(full_context)

        prompt = PromptBuilder.build_compress_context_prompt(
            full_context=full_context,
            task_description=task_description,
            target_tokens=target_tokens,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=target_tokens + 100,
            temperature=0.3,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=[task_description],
            quality_score=0.85,
            metadata={"task": task_description, "model": response.model},
        )

    async def extract_essence(
        self,
        document: str,
        focus_areas: list[str] | None = None,
    ) -> CompressionResult:
        """Extract essential information from document."""
        original_tokens = await self.llm.count_tokens(document)

        prompt = PromptBuilder.build_extract_essence_prompt(
            document=document,
            focus_areas=focus_areas or [],
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=int(original_tokens * 0.4),
            temperature=0.4,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=focus_areas or [],
            quality_score=0.8,
            metadata={"focus_areas": focus_areas, "model": response.model},
        )

    async def unify_summaries(
        self,
        documents: list[dict],
        purpose: str,
    ) -> CompressionResult:
        """Unify multiple documents into single summary."""
        docs = [Document(**d) for d in documents]
        total_content = "\n".join(d.content for d in docs)
        original_tokens = await self.llm.count_tokens(total_content)

        prompt = PromptBuilder.build_unify_summaries_prompt(
            documents=docs,
            purpose=purpose,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=int(original_tokens * 0.3),
            temperature=0.5,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=[d.title for d in docs],
            quality_score=0.8,
            metadata={
                "purpose": purpose,
                "document_count": len(docs),
                "model": response.model,
            },
        )

    async def summarize_diff(
        self,
        before: str,
        after: str,
        focus: str | None = None,
    ) -> CompressionResult:
        """Summarize differences between two texts."""
        diff_input = DiffInput(before=before, after=after, focus=focus)
        strategy = get_strategy(CompressionStyle.DIFF, self.llm)

        request = CompressionRequest(
            text="",  # Not used for diff
            style=CompressionStyle.DIFF,
            metadata={"diff_input": diff_input},
        )

        return await strategy.compress(request)

    async def progressive_compress(
        self,
        text: str,
        stages: list[dict],
    ) -> list[CompressionResult]:
        """Apply progressive compression through multiple stages."""
        results: list[CompressionResult] = []
        current_text = text
        total_stages = len(stages)

        for i, stage_config in enumerate(stages, 1):
            stage = ProgressiveStage(**stage_config)

            prompt = PromptBuilder.build_progressive_compress_prompt(
                text=current_text,
                stage=stage,
                stage_number=i,
                total_stages=total_stages,
            )

            original_tokens = await self.llm.count_tokens(current_text)
            target_tokens = int(original_tokens * stage.target_ratio)

            response = await self.llm.generate(
                prompt,
                system_prompt=PromptBuilder.get_system_prompt(),
                max_tokens=target_tokens + 100,
                temperature=0.3,
            )

            compressed_tokens = await self.llm.count_tokens(response.content)

            result = CompressionResult(
                compressed_text=response.content,
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
                preserved_elements=stage.preserve,
                quality_score=0.8,
                metadata={
                    "stage": i,
                    "target_ratio": stage.target_ratio,
                    "model": response.model,
                },
            )
            results.append(result)
            current_text = response.content

        return results

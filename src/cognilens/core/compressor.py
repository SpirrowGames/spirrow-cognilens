"""Main compression engine coordinating strategies and LLM."""

from __future__ import annotations

from typing import Optional

from cognilens.config import get_settings
from cognilens.llm import LLMClient, create_llm_client
from cognilens.llm.lexora_client import LexoraClient
from cognilens.llm.model_selector import ModelSelection, ModelSelector
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

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        model_selector: Optional[ModelSelector] = None,
    ) -> None:
        settings = get_settings()

        if llm_client:
            self.llm = llm_client
        else:
            self.llm = create_llm_client(settings.llm)

        # Initialize model selector if smart selection is enabled
        self._model_selector = model_selector
        if (
            self._model_selector is None
            and settings.llm.smart_selection.enabled
            and isinstance(self.llm, LexoraClient)
        ):
            self._model_selector = ModelSelector(self.llm, settings.llm)

    async def _select_model(
        self,
        style: CompressionStyle,
        content_preview: Optional[str] = None,
    ) -> Optional[ModelSelection]:
        """Select optimal model for the compression task.

        Args:
            style: Compression style being used
            content_preview: Optional content preview for classification

        Returns:
            ModelSelection if smart selection is enabled, None otherwise
        """
        if self._model_selector is None or not self._model_selector.is_enabled:
            return None

        return await self._model_selector.select_model(style, content_preview)

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

        # Select optimal model if smart selection is enabled
        model_selection = await self._select_model(
            compression_style,
            text[:500] if len(text) > 500 else text,
        )

        request = CompressionRequest(
            text=text,
            style=compression_style,
            target_tokens=max_tokens,
            preserve=preserve or [],
        )

        # Add model selection to metadata if available
        if model_selection:
            request.metadata["model_selection"] = {
                "model_id": model_selection.model_id,
                "method": model_selection.method.value,
                "capability": model_selection.capability,
                "confidence": model_selection.confidence,
            }

        result = await strategy.compress(request, model=model_selection.model_id if model_selection else None)

        # Add selection info to result metadata
        if model_selection:
            result.metadata["selected_model"] = model_selection.model_id
            result.metadata["selection_method"] = model_selection.method.value

        return result

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

        # Select model for context compression (use concise style)
        model_selection = await self._select_model(
            CompressionStyle.CONCISE,
            full_context[:500] if len(full_context) > 500 else full_context,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=target_tokens + 100,
            temperature=0.3,
            model=model_selection.model_id if model_selection else None,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)

        metadata = {"task": task_description, "model": response.model}
        if model_selection:
            metadata["selected_model"] = model_selection.model_id
            metadata["selection_method"] = model_selection.method.value

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=[task_description],
            quality_score=0.85,
            metadata=metadata,
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

        # Select model for essence extraction (use detailed style)
        model_selection = await self._select_model(
            CompressionStyle.DETAILED,
            document[:500] if len(document) > 500 else document,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=int(original_tokens * 0.4),
            temperature=0.4,
            model=model_selection.model_id if model_selection else None,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)

        metadata = {"focus_areas": focus_areas, "model": response.model}
        if model_selection:
            metadata["selected_model"] = model_selection.model_id
            metadata["selection_method"] = model_selection.method.value

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=focus_areas or [],
            quality_score=0.8,
            metadata=metadata,
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

        # Select model for unification (use detailed style for synthesis)
        model_selection = await self._select_model(
            CompressionStyle.DETAILED,
            total_content[:500] if len(total_content) > 500 else total_content,
        )

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=int(original_tokens * 0.3),
            temperature=0.5,
            model=model_selection.model_id if model_selection else None,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)

        metadata = {
            "purpose": purpose,
            "document_count": len(docs),
            "model": response.model,
        }
        if model_selection:
            metadata["selected_model"] = model_selection.model_id
            metadata["selection_method"] = model_selection.method.value

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=[d.title for d in docs],
            quality_score=0.8,
            metadata=metadata,
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

        # Select model for diff (use diff style)
        combined_preview = f"Before:\n{before[:250]}\n\nAfter:\n{after[:250]}"
        model_selection = await self._select_model(
            CompressionStyle.DIFF,
            combined_preview,
        )

        request = CompressionRequest(
            text="",  # Not used for diff
            style=CompressionStyle.DIFF,
            metadata={"diff_input": diff_input},
        )

        if model_selection:
            request.metadata["model_selection"] = {
                "model_id": model_selection.model_id,
                "method": model_selection.method.value,
            }

        result = await strategy.compress(request, model=model_selection.model_id if model_selection else None)

        if model_selection:
            result.metadata["selected_model"] = model_selection.model_id
            result.metadata["selection_method"] = model_selection.method.value

        return result

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

            # Select model for this stage (use concise style)
            model_selection = await self._select_model(
                CompressionStyle.CONCISE,
                current_text[:500] if len(current_text) > 500 else current_text,
            )

            response = await self.llm.generate(
                prompt,
                system_prompt=PromptBuilder.get_system_prompt(),
                max_tokens=target_tokens + 100,
                temperature=0.3,
                model=model_selection.model_id if model_selection else None,
            )

            compressed_tokens = await self.llm.count_tokens(response.content)

            metadata = {
                "stage": i,
                "target_ratio": stage.target_ratio,
                "model": response.model,
            }
            if model_selection:
                metadata["selected_model"] = model_selection.model_id
                metadata["selection_method"] = model_selection.method.value

            result = CompressionResult(
                compressed_text=response.content,
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
                preserved_elements=stage.preserve,
                quality_score=0.8,
                metadata=metadata,
            )
            results.append(result)
            current_text = response.content

        return results

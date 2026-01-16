"""Prompt builder for constructing prompts from templates."""

from __future__ import annotations

from cognilens.core.types import (
    CompressionStyle,
    DiffInput,
    Document,
    ProgressiveStage,
)

from .templates import (
    COMPRESS_CONTEXT_TEMPLATE,
    EXTRACT_ESSENCE_TEMPLATE,
    PROGRESSIVE_COMPRESS_TEMPLATE,
    STYLE_INSTRUCTIONS,
    SUMMARIZE_DIFF_TEMPLATE,
    SUMMARIZE_TEMPLATE,
    SYSTEM_PROMPT,
    UNIFY_SUMMARIES_TEMPLATE,
)


class PromptBuilder:
    """Builds prompts from templates."""

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for compression tasks."""
        return SYSTEM_PROMPT

    @staticmethod
    def build_summarize_prompt(
        text: str,
        max_tokens: int,
        style: CompressionStyle,
        preserve: list[str],
    ) -> str:
        """Build a summarization prompt."""
        style_instruction = STYLE_INSTRUCTIONS.get(style.value, STYLE_INSTRUCTIONS["concise"])

        preserve_instruction = ""
        if preserve:
            preserve_instruction = f"- 以下の要素は必ず保持: {', '.join(preserve)}"

        return SUMMARIZE_TEMPLATE.format(
            style=style_instruction,
            max_tokens=max_tokens,
            preserve_instruction=preserve_instruction,
            text=text,
        )

    @staticmethod
    def build_compress_context_prompt(
        full_context: str,
        task_description: str,
        target_tokens: int,
    ) -> str:
        """Build a context compression prompt."""
        return COMPRESS_CONTEXT_TEMPLATE.format(
            task_description=task_description,
            target_tokens=target_tokens,
            full_context=full_context,
        )

    @staticmethod
    def build_extract_essence_prompt(
        document: str,
        focus_areas: list[str],
    ) -> str:
        """Build an essence extraction prompt."""
        focus_text = (
            "\n".join(f"- {area}" for area in focus_areas)
            if focus_areas
            else "- 全般的な本質を抽出"
        )

        return EXTRACT_ESSENCE_TEMPLATE.format(
            focus_areas=focus_text,
            document=document,
        )

    @staticmethod
    def build_unify_summaries_prompt(
        documents: list[Document],
        purpose: str,
    ) -> str:
        """Build a document unification prompt."""
        docs_text = "\n\n".join(f"### {doc.title}\n{doc.content}" for doc in documents)

        return UNIFY_SUMMARIES_TEMPLATE.format(
            purpose=purpose,
            documents=docs_text,
        )

    @staticmethod
    def build_diff_prompt(
        diff_input: DiffInput,
    ) -> str:
        """Build a diff summarization prompt."""
        focus_instruction = ""
        if diff_input.focus:
            focus_instruction = f"特に注目: {diff_input.focus}"

        return SUMMARIZE_DIFF_TEMPLATE.format(
            focus_instruction=focus_instruction,
            before=diff_input.before,
            after=diff_input.after,
        )

    @staticmethod
    def build_progressive_compress_prompt(
        text: str,
        stage: ProgressiveStage,
        stage_number: int,
        total_stages: int,
    ) -> str:
        """Build a progressive compression prompt."""
        preserve_instruction = ""
        if stage.preserve:
            preserve_instruction = f"保持する要素: {', '.join(stage.preserve)}"

        return PROGRESSIVE_COMPRESS_TEMPLATE.format(
            stage_number=stage_number,
            total_stages=total_stages,
            target_ratio=stage.target_ratio,
            preserve_instruction=preserve_instruction,
            text=text,
        )

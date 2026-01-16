"""Unit tests for prompt templates and builder."""

import pytest

from cognilens.core.types import CompressionStyle, DiffInput, Document, ProgressiveStage
from cognilens.prompts.builder import PromptBuilder


def test_build_summarize_prompt():
    """Test summarize prompt building."""
    prompt = PromptBuilder.build_summarize_prompt(
        text="Sample text to summarize.",
        max_tokens=100,
        style=CompressionStyle.CONCISE,
        preserve=["API", "endpoints"],
    )

    assert "Sample text to summarize" in prompt
    assert "100" in prompt
    assert "API" in prompt
    assert "endpoints" in prompt


def test_build_compress_context_prompt():
    """Test compress context prompt building."""
    prompt = PromptBuilder.build_compress_context_prompt(
        full_context="Full context here.",
        task_description="Implement user authentication",
        target_tokens=500,
    )

    assert "Full context here" in prompt
    assert "Implement user authentication" in prompt
    assert "500" in prompt


def test_build_extract_essence_prompt():
    """Test extract essence prompt building."""
    prompt = PromptBuilder.build_extract_essence_prompt(
        document="Document content here.",
        focus_areas=["API changes", "breaking changes"],
    )

    assert "Document content here" in prompt
    assert "API changes" in prompt
    assert "breaking changes" in prompt


def test_build_extract_essence_prompt_no_focus():
    """Test extract essence prompt with no focus areas."""
    prompt = PromptBuilder.build_extract_essence_prompt(
        document="Document content here.",
        focus_areas=[],
    )

    assert "Document content here" in prompt
    assert "全般的な本質を抽出" in prompt


def test_build_unify_summaries_prompt():
    """Test unify summaries prompt building."""
    documents = [
        Document(title="Doc 1", content="Content 1"),
        Document(title="Doc 2", content="Content 2"),
    ]
    prompt = PromptBuilder.build_unify_summaries_prompt(
        documents=documents,
        purpose="Create implementation guide",
    )

    assert "Doc 1" in prompt
    assert "Content 1" in prompt
    assert "Doc 2" in prompt
    assert "Content 2" in prompt
    assert "Create implementation guide" in prompt


def test_build_diff_prompt():
    """Test diff prompt building."""
    diff_input = DiffInput(
        before="Original code",
        after="Modified code",
        focus="breaking changes",
    )
    prompt = PromptBuilder.build_diff_prompt(diff_input)

    assert "Original code" in prompt
    assert "Modified code" in prompt
    assert "breaking changes" in prompt


def test_build_diff_prompt_no_focus():
    """Test diff prompt with no focus."""
    diff_input = DiffInput(
        before="Original code",
        after="Modified code",
    )
    prompt = PromptBuilder.build_diff_prompt(diff_input)

    assert "Original code" in prompt
    assert "Modified code" in prompt


def test_build_progressive_compress_prompt():
    """Test progressive compress prompt building."""
    stage = ProgressiveStage(target_ratio=0.5, preserve=["code", "api"])
    prompt = PromptBuilder.build_progressive_compress_prompt(
        text="Text to compress",
        stage=stage,
        stage_number=2,
        total_stages=3,
    )

    assert "Text to compress" in prompt
    assert "2" in prompt
    assert "3" in prompt
    assert "0.5" in prompt
    assert "code" in prompt
    assert "api" in prompt


def test_get_system_prompt():
    """Test system prompt retrieval."""
    system_prompt = PromptBuilder.get_system_prompt()

    assert "情報圧縮" in system_prompt
    assert "本質" in system_prompt

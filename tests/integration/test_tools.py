"""Integration tests for MCP tools."""

import pytest

from cognilens.config import LLMConfig, LLMProvider, Settings, reset_settings
from cognilens.tools.compress import compress_context
from cognilens.tools.diff import summarize_diff
from cognilens.tools.extract import extract_essence
from cognilens.tools.progressive import progressive_compress
from cognilens.tools.summarize import summarize
from cognilens.tools.unify import unify_summaries


@pytest.fixture(autouse=True)
def setup_mock_config(monkeypatch):
    """Configure mock LLM provider for all tests."""
    # Reset settings before each test
    reset_settings()

    # Patch get_settings to return mock configuration
    mock_settings = Settings.for_testing()

    import cognilens.config

    monkeypatch.setattr(cognilens.config, "_settings", mock_settings)


@pytest.mark.asyncio
async def test_summarize_tool(sample_text):
    """Test summarize tool returns expected structure."""
    result = await summarize(
        text=sample_text,
        max_tokens=100,
        style="concise",
    )

    assert "summary" in result
    assert "original_tokens" in result
    assert "compressed_tokens" in result
    assert "compression_ratio" in result
    assert "savings_percent" in result
    assert result["compression_ratio"] < 1.0


@pytest.mark.asyncio
async def test_compress_context_tool():
    """Test compress_context tool returns expected structure."""
    result = await compress_context(
        full_context="Long design document with many details about implementation.",
        task_description="Implement user authentication",
        target_tokens=200,
    )

    assert "compressed_context" in result
    assert "original_tokens" in result
    assert "task" in result
    assert result["task"] == "Implement user authentication"


@pytest.mark.asyncio
async def test_extract_essence_tool():
    """Test extract_essence tool returns expected structure."""
    result = await extract_essence(
        document="Document about API design principles and best practices.",
        focus_areas=["API design", "best practices"],
    )

    assert "essence" in result
    assert "original_tokens" in result
    assert "focus_areas" in result
    assert result["focus_areas"] == ["API design", "best practices"]


@pytest.mark.asyncio
async def test_unify_summaries_tool(sample_documents):
    """Test unify_summaries tool returns expected structure."""
    result = await unify_summaries(
        documents=sample_documents,
        purpose="Create implementation guide",
    )

    assert "unified_summary" in result
    assert "document_count" in result
    assert "purpose" in result
    assert result["document_count"] == 2
    assert result["purpose"] == "Create implementation guide"


@pytest.mark.asyncio
async def test_summarize_diff_tool(sample_diff_texts):
    """Test summarize_diff tool returns expected structure."""
    result = await summarize_diff(
        before=sample_diff_texts["before"],
        after=sample_diff_texts["after"],
        focus="breaking changes",
    )

    assert "diff_summary" in result
    assert "original_tokens" in result
    assert "focus" in result
    assert result["focus"] == "breaking changes"


@pytest.mark.asyncio
async def test_progressive_compress_tool(sample_text):
    """Test progressive_compress tool returns expected structure."""
    stages = [
        {"target_ratio": 0.5, "preserve": ["patterns"]},
        {"target_ratio": 0.3, "preserve": []},
    ]

    result = await progressive_compress(
        text=sample_text,
        stages=stages,
    )

    assert "final_text" in result
    assert "stages" in result
    assert "total_stages" in result
    assert "overall_compression" in result
    assert result["total_stages"] == 2
    assert len(result["stages"]) == 2

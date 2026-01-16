"""Unit tests for compression strategies."""

import pytest

from cognilens.core.types import CompressionRequest, CompressionStyle
from cognilens.strategies.bullet import BulletStrategy
from cognilens.strategies.code_aware import CodeAwareStrategy
from cognilens.strategies.concise import ConciseStrategy
from cognilens.strategies.detailed import DetailedStrategy


@pytest.mark.asyncio
async def test_concise_strategy_compress(mock_llm_client, sample_text):
    """Test concise strategy produces compressed output."""
    strategy = ConciseStrategy(mock_llm_client)
    request = CompressionRequest(
        text=sample_text,
        style=CompressionStyle.CONCISE,
        target_tokens=100,
    )

    result = await strategy.compress(request)

    assert result.compressed_text
    assert result.compression_ratio < 1.0
    assert result.quality_score >= 0.0


@pytest.mark.asyncio
async def test_detailed_strategy_compress(mock_llm_client, sample_text):
    """Test detailed strategy produces compressed output."""
    strategy = DetailedStrategy(mock_llm_client)
    request = CompressionRequest(
        text=sample_text,
        style=CompressionStyle.DETAILED,
        target_tokens=200,
    )

    result = await strategy.compress(request)

    assert result.compressed_text
    assert result.metadata.get("strategy") == "detailed"


@pytest.mark.asyncio
async def test_bullet_strategy_compress(mock_llm_client, sample_text):
    """Test bullet strategy produces compressed output."""
    strategy = BulletStrategy(mock_llm_client)
    request = CompressionRequest(
        text=sample_text,
        style=CompressionStyle.BULLET,
        target_tokens=150,
    )

    result = await strategy.compress(request)

    assert result.compressed_text
    assert result.metadata.get("strategy") == "bullet"


@pytest.mark.asyncio
async def test_code_aware_strategy_compress(mock_llm_client):
    """Test code-aware strategy handles code properly."""
    code_text = """
    class Calculator:
        def add(self, a, b):
            return a + b

        def multiply(self, a, b):
            return a * b
    """
    strategy = CodeAwareStrategy(mock_llm_client)
    request = CompressionRequest(
        text=code_text,
        style=CompressionStyle.CODE_AWARE,
        target_tokens=100,
    )

    result = await strategy.compress(request)

    assert result.compressed_text
    # Should detect code signatures
    assert "detected_signatures" in result.metadata


@pytest.mark.asyncio
async def test_strategy_preserves_elements(mock_llm_client):
    """Test that strategies track preserved elements."""
    strategy = ConciseStrategy(mock_llm_client)
    request = CompressionRequest(
        text="The API uses REST endpoints. Authentication is required.",
        style=CompressionStyle.CONCISE,
        preserve=["API", "REST"],
    )

    result = await strategy.compress(request)

    assert result.preserved_elements == ["API", "REST"]

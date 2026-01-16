"""Unit tests for LLM clients."""

import pytest

from cognilens.llm.mock import MockLLMClient


@pytest.mark.asyncio
async def test_mock_llm_generate():
    """Test mock LLM generates response."""
    client = MockLLMClient()
    response = await client.generate("Summarize this text about Python programming.")

    assert response.content
    assert response.model == "mock-model"
    assert response.tokens_used > 0


@pytest.mark.asyncio
async def test_mock_llm_count_tokens():
    """Test mock LLM counts tokens."""
    client = MockLLMClient()
    count = await client.count_tokens("Hello world, this is a test.")

    assert count > 0
    # Approximately 4 chars per token
    assert count == len("Hello world, this is a test.") // 4


@pytest.mark.asyncio
async def test_mock_llm_health_check():
    """Test mock LLM health check."""
    client = MockLLMClient()
    is_healthy = await client.health_check()

    assert is_healthy is True


@pytest.mark.asyncio
async def test_mock_llm_call_count():
    """Test mock LLM tracks call count."""
    client = MockLLMClient()
    assert client.call_count == 0

    await client.generate("First call")
    assert client.call_count == 1

    await client.generate("Second call")
    assert client.call_count == 2


@pytest.mark.asyncio
async def test_mock_llm_respects_max_tokens():
    """Test mock LLM respects max_tokens parameter."""
    client = MockLLMClient()
    long_text = "This is a very long text. " * 100

    response = await client.generate(long_text, max_tokens=50)

    # Response should be truncated
    assert len(response.content.split()) <= 25  # max_tokens // 2

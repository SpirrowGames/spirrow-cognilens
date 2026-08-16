from typing import ClassVar

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


class _CaptureCompletions:
    """Captures the kwargs passed to chat.completions.create."""

    def __init__(self):
        self.captured = {}

    async def create(self, **kwargs):
        self.captured = kwargs

        class _Msg:
            content = "ok"

        class _Choice:
            message = _Msg()
            finish_reason = "stop"

        class _Usage:
            total_tokens = 1

        class _Resp:
            model = "test"
            choices: ClassVar[list] = [_Choice()]
            usage = _Usage()

        return _Resp()


def _patched_openai_client(monkeypatch, context_window, margin):
    from cognilens.config import LLMConfig, LLMProvider
    from cognilens.llm.openai_client import OpenAIClient

    client = OpenAIClient(
        LLMConfig(
            provider=LLMProvider.OPENAI,
            model="Qwen2.5-1.5B",
            base_url="http://localhost:8110/v1",
            api_key="dummy",
            context_window=context_window,
            output_safety_margin=margin,
        )
    )
    capture = _CaptureCompletions()
    client._client.chat.completions = capture  # type: ignore[attr-defined]
    return client, capture


@pytest.mark.asyncio
async def test_openai_clamps_max_tokens_to_context_window(monkeypatch):
    """max_tokens is reduced so input + output stays within the context window."""
    client, capture = _patched_openai_client(monkeypatch, context_window=8192, margin=256)
    prompt = "word " * 6000  # ~6000 input tokens

    await client.generate(prompt, max_tokens=2100)

    input_tokens = len(client._encoding.encode(prompt))
    expected = 8192 - input_tokens - 256
    assert capture.captured["max_tokens"] == expected
    assert input_tokens + capture.captured["max_tokens"] <= 8192


@pytest.mark.asyncio
async def test_openai_keeps_max_tokens_when_room_available(monkeypatch):
    """Small inputs leave max_tokens untouched."""
    client, capture = _patched_openai_client(monkeypatch, context_window=8192, margin=256)

    await client.generate("short prompt", max_tokens=500)

    assert capture.captured["max_tokens"] == 500


@pytest.mark.asyncio
async def test_openai_clamp_never_returns_below_one(monkeypatch):
    """Even when input alone exceeds the window, max_tokens stays >= 1."""
    client, capture = _patched_openai_client(monkeypatch, context_window=1000, margin=256)
    prompt = "word " * 4000

    await client.generate(prompt, max_tokens=500)

    assert capture.captured["max_tokens"] == 1

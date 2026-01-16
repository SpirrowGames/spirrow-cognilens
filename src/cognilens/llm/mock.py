"""Mock LLM client for testing and development."""

from __future__ import annotations

import re
from typing import Optional

from .base import LLMClient, LLMResponse


class MockLLMClient(LLMClient):
    """Mock LLM client for testing and development."""

    def __init__(self) -> None:
        self._call_count = 0

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate mock response by extracting key sentences."""
        self._call_count += 1

        # Simple mock: extract key sentences and return truncated version
        sentences = re.split(r"[.!?]+", prompt)
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
        mock_summary = (
            ". ".join(key_sentences) + "." if key_sentences else "Summary of the provided text."
        )

        if max_tokens:
            words = mock_summary.split()[: max_tokens // 2]
            mock_summary = " ".join(words)

        return LLMResponse(
            content=mock_summary,
            model="mock-model",
            tokens_used=len(mock_summary.split()),
            finish_reason="stop",
        )

    async def count_tokens(self, text: str) -> int:
        """Approximate token count (~4 chars per token)."""
        return len(text) // 4

    async def health_check(self) -> bool:
        """Mock is always healthy."""
        return True

    @property
    def call_count(self) -> int:
        """Get number of generate calls made."""
        return self._call_count

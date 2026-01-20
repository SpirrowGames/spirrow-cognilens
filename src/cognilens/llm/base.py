"""Abstract base class for LLM clients."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Standardized LLM response."""

    content: str
    model: str
    tokens_used: int
    finish_reason: Optional[str] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ) -> LLMResponse:
        """Generate text from prompt.

        Args:
            prompt: The input prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            model: Optional model override (for smart selection)
        """
        ...

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM service is available."""
        ...

"""Abstract base class for LLM clients."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class ContextWindowExceededError(RuntimeError):
    """The prompt alone leaves no room for a completion.

    Raised instead of asking the backend for a 1-token completion. A
    request whose input already fills the context window is impossible,
    not merely tight, and the honest answer is an error the caller can
    act on.

    The alternative -- clamping the output budget to a floor of 1 -- was
    measured to return a single character that every downstream check
    read as a successful summary, because a 1-token completion is
    indistinguishable from a terse one at every layer above this.
    """

    def __init__(
        self,
        *,
        input_tokens: int,
        context_window: int,
        safety_margin: int,
        model: str,
    ) -> None:
        self.input_tokens = input_tokens
        self.context_window = context_window
        self.safety_margin = safety_margin
        self.model = model
        super().__init__(
            f"input of {input_tokens} tokens leaves no completion budget for "
            f"{model!r}: context_window={context_window} minus "
            f"safety_margin={safety_margin} leaves "
            f"{context_window - safety_margin - input_tokens} tokens. "
            f"Shorten the input, or raise llm.context_window if it "
            f"understates the serving backend's max_model_len."
        )


class LLMResponse(BaseModel):
    """Standardized LLM response."""

    content: str
    model: str
    tokens_used: int
    finish_reason: str | None = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        model: str | None = None,
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

"""OpenAI API client implementation."""

from __future__ import annotations

from typing import Optional

import tiktoken
from openai import AsyncOpenAI

from cognilens.config import LLMConfig

from .base import LLMClient, LLMResponse


class OpenAIClient(LLMClient):
    """OpenAI API client implementation."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )
        self._model = config.model
        try:
            self._encoding = tiktoken.encoding_for_model(config.model)
        except KeyError:
            # Fallback for unknown models
            self._encoding = tiktoken.get_encoding("cl100k_base")

    async def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text using OpenAI API."""
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore
            max_tokens=max_tokens,
            temperature=temperature,
        )

        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            tokens_used=response.usage.total_tokens if response.usage else 0,
            finish_reason=choice.finish_reason,
        )

    async def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        return len(self._encoding.encode(text))

    async def health_check(self) -> bool:
        """Check if OpenAI API is accessible."""
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False

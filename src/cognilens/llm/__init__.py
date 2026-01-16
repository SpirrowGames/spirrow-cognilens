"""LLM client abstraction layer."""

from __future__ import annotations

from cognilens.config import LLMConfig, LLMProvider

from .base import LLMClient, LLMResponse
from .lexora_client import LexoraClient
from .mock import MockLLMClient
from .openai_client import OpenAIClient


def create_llm_client(config: LLMConfig) -> LLMClient:
    """Factory function to create appropriate LLM client."""
    match config.provider:
        case LLMProvider.MOCK:
            return MockLLMClient()
        case LLMProvider.OPENAI:
            return OpenAIClient(config)
        case LLMProvider.LEXORA:
            return LexoraClient(config)
        case _:
            raise ValueError(f"Unknown LLM provider: {config.provider}")


__all__ = [
    "LLMClient",
    "LLMResponse",
    "MockLLMClient",
    "OpenAIClient",
    "LexoraClient",
    "create_llm_client",
]

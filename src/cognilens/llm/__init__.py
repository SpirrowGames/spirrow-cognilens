"""LLM client abstraction layer."""

from __future__ import annotations

from cognilens.config import LLMConfig, LLMProvider

from .base import LLMClient, LLMResponse
from .lexora_client import (
    ClassificationResult,
    LexoraClient,
    ModelCapabilitiesCache,
    ModelCapability,
)
from .mock import MockLLMClient
from .model_selector import ModelSelection, ModelSelector, SelectionMethod
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


def create_model_selector(
    llm_client: LLMClient,
    config: LLMConfig,
) -> ModelSelector | None:
    """Factory function to create ModelSelector if applicable.

    Args:
        llm_client: The LLM client instance
        config: LLM configuration

    Returns:
        ModelSelector if smart selection is enabled and client is LexoraClient,
        None otherwise
    """
    if not config.smart_selection.enabled:
        return None

    if not isinstance(llm_client, LexoraClient):
        return None

    return ModelSelector(llm_client, config)


__all__ = [
    "ClassificationResult",
    "LLMClient",
    "LLMResponse",
    "LexoraClient",
    "MockLLMClient",
    "ModelCapabilitiesCache",
    "ModelCapability",
    "ModelSelection",
    "ModelSelector",
    "OpenAIClient",
    "SelectionMethod",
    "create_llm_client",
    "create_model_selector",
]

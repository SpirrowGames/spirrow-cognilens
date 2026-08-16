"""Compression strategies."""

from __future__ import annotations

from cognilens.core.types import CompressionStyle
from cognilens.llm.base import LLMClient

from .base import CompressionStrategy
from .bullet import BulletStrategy
from .code_aware import CodeAwareStrategy
from .concise import ConciseStrategy
from .detailed import DetailedStrategy
from .diff import DiffStrategy

STRATEGY_REGISTRY: dict[CompressionStyle, type[CompressionStrategy]] = {
    CompressionStyle.CONCISE: ConciseStrategy,
    CompressionStyle.DETAILED: DetailedStrategy,
    CompressionStyle.BULLET: BulletStrategy,
    CompressionStyle.CODE_AWARE: CodeAwareStrategy,
    CompressionStyle.DIFF: DiffStrategy,
}


def get_strategy(style: CompressionStyle, llm_client: LLMClient) -> CompressionStrategy:
    """Get compression strategy instance by style."""
    strategy_class = STRATEGY_REGISTRY.get(style)
    if not strategy_class:
        raise ValueError(f"Unknown compression style: {style}")
    return strategy_class(llm_client)


__all__ = [
    "STRATEGY_REGISTRY",
    "BulletStrategy",
    "CodeAwareStrategy",
    "CompressionStrategy",
    "ConciseStrategy",
    "DetailedStrategy",
    "DiffStrategy",
    "get_strategy",
]

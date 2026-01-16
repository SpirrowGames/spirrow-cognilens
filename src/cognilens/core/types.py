"""Core type definitions for Spirrow-Cognilens."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class CompressionStyle(str, Enum):
    """Available compression styles."""

    CONCISE = "concise"
    DETAILED = "detailed"
    BULLET = "bullet"
    CODE_AWARE = "code_aware"
    DIFF = "diff"


@dataclass
class CompressionRequest:
    """Request for compression operation."""

    text: str
    style: CompressionStyle = CompressionStyle.CONCISE
    target_tokens: Optional[int] = None
    target_ratio: Optional[float] = None
    preserve: list[str] = field(default_factory=list)
    context: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompressionResult:
    """Result of compression operation."""

    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    preserved_elements: list[str]
    quality_score: float  # 0.0 - 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def savings_percent(self) -> float:
        """Calculate percentage of tokens saved."""
        return (1.0 - self.compression_ratio) * 100


@dataclass
class Document:
    """Represents a document for processing."""

    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiffInput:
    """Input for diff summarization."""

    before: str
    after: str
    focus: Optional[str] = None


@dataclass
class ProgressiveStage:
    """Configuration for a progressive compression stage."""

    target_ratio: float
    preserve: list[str] = field(default_factory=list)

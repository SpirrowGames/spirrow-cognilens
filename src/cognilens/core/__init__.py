"""Core compression engine and types."""

from .compressor import CompressionEngine
from .types import (
    CompressionRequest,
    CompressionResult,
    CompressionStyle,
    DiffInput,
    Document,
    ProgressiveStage,
)

__all__ = [
    "CompressionEngine",
    "CompressionStyle",
    "CompressionRequest",
    "CompressionResult",
    "Document",
    "DiffInput",
    "ProgressiveStage",
]

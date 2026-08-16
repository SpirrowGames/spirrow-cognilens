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
    "CompressionRequest",
    "CompressionResult",
    "CompressionStyle",
    "DiffInput",
    "Document",
    "ProgressiveStage",
]

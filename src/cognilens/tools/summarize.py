"""Summarize tool implementation."""

from __future__ import annotations

from typing import Literal

from cognilens.core.compressor import CompressionEngine


async def summarize(
    text: str,
    max_tokens: int = 500,
    style: Literal["concise", "detailed", "bullet"] = "concise",
    preserve: list[str] | None = None,
) -> dict:
    """Summarize text with specified style.

    Args:
        text: Text to summarize
        max_tokens: Maximum tokens in summary (default: 500)
        style: Summarization style - concise/detailed/bullet
        preserve: Elements to preserve in summary

    Returns:
        Dictionary with compressed_text, compression_ratio, and metadata
    """
    engine = CompressionEngine()
    result = await engine.summarize(
        text=text,
        max_tokens=max_tokens,
        style=style,
        preserve=preserve or [],
    )

    return {
        "summary": result.compressed_text,
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "compression_ratio": result.compression_ratio,
        "savings_percent": result.savings_percent,
        "quality_score": result.quality_score,
    }

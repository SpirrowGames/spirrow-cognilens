"""Summarize diff tool implementation."""

from __future__ import annotations

from cognilens.core.compressor import CompressionEngine


async def summarize_diff(
    before: str,
    after: str,
    focus: str | None = None,
) -> dict:
    """Summarize differences between two versions of text.

    Args:
        before: Original version
        after: Modified version
        focus: Specific aspect to focus on (e.g., "breaking changes")

    Returns:
        Dictionary with diff summary and metadata
    """
    engine = CompressionEngine()
    result = await engine.summarize_diff(
        before=before,
        after=after,
        focus=focus,
    )

    return {
        "diff_summary": result.compressed_text,
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "focus": focus,
    }

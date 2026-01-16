"""Extract essence tool implementation."""

from __future__ import annotations

from cognilens.core.compressor import CompressionEngine


async def extract_essence(
    document: str,
    focus_areas: list[str] | None = None,
) -> dict:
    """Extract essential information from a document.

    Args:
        document: Document to analyze
        focus_areas: Areas to focus on during extraction

    Returns:
        Dictionary with extracted essence and metadata
    """
    engine = CompressionEngine()
    result = await engine.extract_essence(
        document=document,
        focus_areas=focus_areas or [],
    )

    return {
        "essence": result.compressed_text,
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "focus_areas": focus_areas,
    }

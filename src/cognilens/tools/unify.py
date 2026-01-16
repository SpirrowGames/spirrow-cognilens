"""Unify summaries tool implementation."""

from __future__ import annotations

from cognilens.core.compressor import CompressionEngine


async def unify_summaries(
    documents: list[dict],
    purpose: str,
) -> dict:
    """Unify multiple documents into a single coherent summary.

    Args:
        documents: List of documents with 'title' and 'content' keys
        purpose: Purpose of the unified summary

    Returns:
        Dictionary with unified summary and metadata
    """
    engine = CompressionEngine()
    result = await engine.unify_summaries(
        documents=documents,
        purpose=purpose,
    )

    return {
        "unified_summary": result.compressed_text,
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "document_count": len(documents),
        "purpose": purpose,
    }

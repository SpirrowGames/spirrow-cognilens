"""Compress context tool implementation."""

from __future__ import annotations

from cognilens.core.compressor import CompressionEngine


async def compress_context(
    full_context: str,
    task_description: str,
    target_tokens: int = 500,
) -> dict:
    """Compress context for specific task execution.

    Args:
        full_context: Full context to compress
        task_description: Description of the task being executed
        target_tokens: Target token count (default: 500)

    Returns:
        Dictionary with compressed context and metadata
    """
    engine = CompressionEngine()
    result = await engine.compress_context(
        full_context=full_context,
        task_description=task_description,
        target_tokens=target_tokens,
    )

    return {
        "compressed_context": result.compressed_text,
        "original_tokens": result.original_tokens,
        "compressed_tokens": result.compressed_tokens,
        "compression_ratio": result.compression_ratio,
        "task": task_description,
    }

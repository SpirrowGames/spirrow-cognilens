"""Progressive compress tool implementation."""

from __future__ import annotations

from cognilens.core.compressor import CompressionEngine


async def progressive_compress(
    text: str,
    stages: list[dict],
) -> dict:
    """Apply progressive compression through multiple stages.

    Args:
        text: Text to compress progressively
        stages: List of stage configs with 'target_ratio' and optional 'preserve'

    Returns:
        Dictionary with all stage results and final compressed text
    """
    engine = CompressionEngine()
    results = await engine.progressive_compress(
        text=text,
        stages=stages,
    )

    return {
        "final_text": results[-1].compressed_text if results else text,
        "stages": [
            {
                "stage": i + 1,
                "compressed_text": r.compressed_text,
                "compression_ratio": r.compression_ratio,
                "tokens": r.compressed_tokens,
            }
            for i, r in enumerate(results)
        ],
        "total_stages": len(results),
        "overall_compression": (
            results[-1].compressed_tokens / results[0].original_tokens if results else 1.0
        ),
    }

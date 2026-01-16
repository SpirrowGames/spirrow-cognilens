"""MCP Server for Spirrow-Cognilens."""

from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP

from cognilens.config import get_settings
from cognilens.tools.compress import compress_context as _compress_context
from cognilens.tools.diff import summarize_diff as _summarize_diff
from cognilens.tools.extract import extract_essence as _extract_essence
from cognilens.tools.progressive import progressive_compress as _progressive_compress
from cognilens.tools.summarize import summarize as _summarize
from cognilens.tools.unify import unify_summaries as _unify_summaries

settings = get_settings()
mcp = FastMCP(settings.server.name)


@mcp.tool
async def summarize(
    text: str,
    max_tokens: int = 500,
    style: Literal["concise", "detailed", "bullet"] = "concise",
    preserve: list[str] | None = None,
) -> dict:
    """Summarize text with specified style.

    Use this to reduce large text to key points while preserving essential information.
    Styles: concise (80% compression), detailed (50%), bullet (list format).
    """
    return await _summarize(text, max_tokens, style, preserve)


@mcp.tool
async def compress_context(
    full_context: str,
    task_description: str,
    target_tokens: int = 500,
) -> dict:
    """Compress context for specific task execution.

    Optimizes context window usage by keeping only task-relevant information.
    Ideal for preparing focused context before complex coding tasks.
    """
    return await _compress_context(full_context, task_description, target_tokens)


@mcp.tool
async def extract_essence(
    document: str,
    focus_areas: list[str] | None = None,
) -> dict:
    """Extract essential information from a document.

    Identifies core concepts, key relationships, and critical specifications.
    Use focus_areas to prioritize specific aspects (e.g., ["API changes", "breaking changes"]).
    """
    return await _extract_essence(document, focus_areas)


@mcp.tool
async def unify_summaries(
    documents: list[dict],
    purpose: str,
) -> dict:
    """Unify multiple documents into a single coherent summary.

    Combines multiple sources, removes redundancy, and highlights conflicts.
    Each document needs 'title' and 'content' keys.
    """
    return await _unify_summaries(documents, purpose)


@mcp.tool
async def summarize_diff(
    before: str,
    after: str,
    focus: str | None = None,
) -> dict:
    """Summarize differences between two versions of text.

    Highlights additions, deletions, and modifications.
    Use 'focus' to emphasize specific aspects like "breaking changes" or "API updates".
    """
    return await _summarize_diff(before, after, focus)


@mcp.tool
async def progressive_compress(
    text: str,
    stages: list[dict],
) -> dict:
    """Apply progressive compression through multiple stages.

    For very large documents, compress in stages to maintain quality.
    Each stage: {"target_ratio": 0.5, "preserve": ["code", "api"]}.
    """
    return await _progressive_compress(text, stages)


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

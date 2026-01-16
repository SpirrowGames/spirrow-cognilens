# Spirrow-Cognilens

Context compression and summarization MCP server for optimizing AI context windows.

[![PyPI version](https://badge.fury.io/py/spirrow-cognilens.svg)](https://badge.fury.io/py/spirrow-cognilens)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Overview

**Cognilens** = Cogni (認知/Cognition) + Lens (レンズ/Lens)

A magic lens that extracts only the essence from large amounts of information:
- Saves Claude Code's context window
- Compresses without losing important information
- Optimal summarization strategies for different use cases

## Installation

```bash
# Using pip
pip install spirrow-cognilens

# Using uvx (recommended for MCP)
uvx spirrow-cognilens
```

## Quick Start

### Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cognilens": {
      "command": "uvx",
      "args": ["spirrow-cognilens"],
      "env": {
        "COGNILENS_LLM__PROVIDER": "openai",
        "COGNILENS_LLM__API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

### Claude Code Configuration

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "cognilens": {
      "command": "uvx",
      "args": ["spirrow-cognilens"],
      "env": {
        "COGNILENS_LLM__PROVIDER": "openai",
        "COGNILENS_LLM__API_KEY": "sk-your-api-key"
      }
    }
  }
}
```

## MCP Tools

### 1. `summarize`
Summarize text with specified style.

```
Styles:
- concise: 80% compression - for overviews
- detailed: 50% compression - for implementation reference
- bullet: Structured bullet points
```

### 2. `compress_context`
Compress context for specific task execution.

Optimizes context window usage by keeping only task-relevant information.

### 3. `extract_essence`
Extract essential information from a document.

Identifies core concepts, key relationships, and critical specifications.

### 4. `unify_summaries`
Unify multiple documents into a single coherent summary.

Combines multiple sources, removes redundancy, and highlights conflicts.

### 5. `summarize_diff`
Summarize differences between two versions of text.

Highlights additions, deletions, and modifications.

### 6. `progressive_compress`
Apply progressive compression through multiple stages.

For very large documents, compress in stages to maintain quality.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COGNILENS_LLM__PROVIDER` | LLM provider (mock/openai/lexora) | `openai` |
| `COGNILENS_LLM__API_KEY` | API key for LLM provider | - |
| `COGNILENS_LLM__MODEL` | Model to use | `gpt-4o-mini` |
| `COGNILENS_SERVER__PORT` | Server port | `8003` |

### Config File

Create `config.yaml` in the working directory:

```yaml
server:
  name: "Spirrow-Cognilens"
  port: 8003

llm:
  provider: "openai"
  model: "gpt-4o-mini"
  timeout: 30

compression:
  default_ratio: 0.3
```

## Development

```bash
# Clone the repository
git clone https://github.com/SpirrowGames/spirrow-cognilens.git
cd spirrow-cognilens

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/ tests/

# Run type checking
mypy src/
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Cognilens MCP Server                                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ MCP Tools                                            │   │
│  │ summarize | compress_context | extract_essence      │   │
│  │ unify_summaries | summarize_diff | progressive      │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Compression Engine                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Strategies: Concise | Detailed | Bullet | CodeAware │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ LLM Client: OpenAI | Lexora | Mock                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [GitHub Repository](https://github.com/SpirrowGames/spirrow-cognilens)
- [Issue Tracker](https://github.com/SpirrowGames/spirrow-cognilens/issues)
- [MCP Specification](https://modelcontextprotocol.io/)

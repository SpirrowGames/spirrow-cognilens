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
- **Smart model selection** via Lexora API integration

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
- code_aware: Preserves code structure, compresses explanations
- diff: Highlights changes between versions
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

## Smart Model Selection

Cognilens integrates with Lexora's new APIs to automatically select the optimal model for each compression task.

### Features

- **Automatic model selection**: Chooses the best model based on task type
- **Capability-based matching**: Maps compression strategies to model capabilities
- **4-level fallback**: Classification API → Capability match → Heuristics → Default model
- **TTL-based caching**: Model capabilities cached for performance (default: 5 minutes)

### Strategy to Capability Mapping

| Strategy | Capability | Use Case |
|----------|------------|----------|
| `concise` | `summarization` | Overview, task lists |
| `detailed` | `summarization` | Implementation reference, API specs |
| `bullet` | `summarization` | Structured key points |
| `code_aware` | `code` | Code with explanations |
| `diff` | `reasoning` | Change analysis |

### Enabling Smart Selection

```yaml
llm:
  provider: "openai"
  base_url: "http://localhost:8110/v1"
  model: "Qwen2.5-1.5B"  # Fallback default

  smart_selection:
    enabled: true
    cache_ttl_seconds: 300
    classify_tasks: true
    fallback_to_default: true
```

Or via environment variables:

```bash
COGNILENS_LLM__SMART_SELECTION__ENABLED=true
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COGNILENS_LLM__PROVIDER` | LLM provider (mock/openai/lexora) | `openai` |
| `COGNILENS_LLM__API_KEY` | API key for LLM provider | - |
| `COGNILENS_LLM__MODEL` | Model to use | `gpt-4o-mini` |
| `COGNILENS_LLM__BASE_URL` | Custom API endpoint | - |
| `COGNILENS_LLM__SMART_SELECTION__ENABLED` | Enable smart model selection | `false` |
| `COGNILENS_LLM__SMART_SELECTION__CACHE_TTL_SECONDS` | Capabilities cache TTL | `300` |
| `COGNILENS_SERVER__PORT` | Server port | `8003` |

### Config File

Create `config.yaml` in the working directory:

```yaml
server:
  name: "Spirrow-Cognilens"
  port: 8003

llm:
  provider: "openai"
  base_url: "http://localhost:8110/v1"
  model: "gpt-4o-mini"
  timeout: 30

  smart_selection:
    enabled: false
    cache_ttl_seconds: 300
    classify_tasks: true
    fallback_to_default: true
    strategy_capability_map:
      concise: "summarization"
      detailed: "summarization"
      bullet: "summarization"
      code_aware: "code"
      diff: "reasoning"

compression:
  default_ratio: 0.3
```

## Development

```bash
# Clone the repository
git clone https://github.com/SpirrowGames/spirrow-cognilens.git
cd spirrow-cognilens

# Install with uv
uv sync

# Run tests
uv run pytest tests/ -v

# Run linting
uv run ruff check src/ tests/

# Run type checking
uv run mypy src/
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
│  │ + ModelSelector (smart model selection)             │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Strategies: Concise | Detailed | Bullet | CodeAware │   │
│  │             Diff                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ LLM Client: OpenAI | Lexora | Mock                  │   │
│  │ + Lexora APIs: /v1/models/capabilities              │   │
│  │                /v1/classify-task                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [GitHub Repository](https://github.com/anthropics/spirrow-cognilens)
- [Issue Tracker](https://github.com/anthropics/spirrow-cognilens/issues)
- [MCP Specification](https://modelcontextprotocol.io/)

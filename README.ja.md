# Spirrow-Cognilens

**[English](README.md)**

AIコンテキストウィンドウを最適化するためのコンテキスト圧縮・要約MCPサーバー。

[![PyPI version](https://badge.fury.io/py/spirrow-cognilens.svg)](https://badge.fury.io/py/spirrow-cognilens)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 概要

**Cognilens** = Cogni (認知/Cognition) + Lens (レンズ/Lens)

大量の情報からエッセンスだけを抽出する魔法のレンズ：
- Claude Codeのコンテキストウィンドウを節約
- 重要な情報を失わずに圧縮
- ユースケースに応じた最適な要約戦略
- **Lexora API連携によるスマートモデル選択**

## インストール

```bash
# pipを使用
pip install spirrow-cognilens

# uvxを使用（MCP推奨）
uvx spirrow-cognilens
```

## クイックスタート

### Claude Desktop設定

`claude_desktop_config.json`に追加：

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

### Claude Code設定

Claude CodeのMCP設定に追加：

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

## MCPツール

### 1. `summarize`
指定したスタイルでテキストを要約。

```
スタイル:
- concise: 80%圧縮 - 概要把握向け
- detailed: 50%圧縮 - 実装参照向け
- bullet: 構造化された箇条書き
- code_aware: コード構造を保持、説明を圧縮
- diff: バージョン間の変更をハイライト
```

### 2. `compress_context`
特定タスク実行のためのコンテキスト圧縮。

タスクに関連する情報のみを保持してコンテキストウィンドウを最適化。

### 3. `extract_essence`
ドキュメントから本質的な情報を抽出。

コアコンセプト、キーとなる関係性、重要な仕様を特定。

### 4. `unify_summaries`
複数のドキュメントを1つの一貫した要約に統合。

複数ソースの結合、冗長性の除去、矛盾点のハイライト。

### 5. `summarize_diff`
2つのバージョン間の差分を要約。

追加、削除、変更をハイライト。

### 6. `progressive_compress`
複数ステージによる段階的圧縮。

非常に大きなドキュメントに対して、品質を維持しながら段階的に圧縮。

## スマートモデル選択

CognilensはLexoraの新APIと連携し、各圧縮タスクに最適なモデルを自動選択します。

### 機能

- **自動モデル選択**: タスクタイプに基づいて最適なモデルを選択
- **能力ベースのマッチング**: 圧縮戦略をモデル能力にマッピング
- **4段階フォールバック**: Classification API → 能力マッチ → ヒューリスティック → デフォルトモデル
- **TTLベースキャッシュ**: パフォーマンスのためモデル能力をキャッシュ（デフォルト: 5分）

### 戦略と能力のマッピング

| 戦略 | 能力 | ユースケース |
|----------|------------|----------|
| `concise` | `summarization` | 概要、タスクリスト |
| `detailed` | `summarization` | 実装参照、API仕様 |
| `bullet` | `summarization` | 構造化されたキーポイント |
| `code_aware` | `code` | 説明付きコード |
| `diff` | `reasoning` | 変更分析 |

### スマート選択の有効化

```yaml
llm:
  provider: "openai"
  base_url: "http://localhost:8110/v1"
  model: "Qwen2.5-1.5B"  # フォールバック用デフォルト

  smart_selection:
    enabled: true
    cache_ttl_seconds: 300
    classify_tasks: true
    fallback_to_default: true
```

または環境変数で：

```bash
COGNILENS_LLM__SMART_SELECTION__ENABLED=true
```

## 設定

### 環境変数

| 変数 | 説明 | デフォルト |
|----------|-------------|---------|
| `COGNILENS_LLM__PROVIDER` | LLMプロバイダー (mock/openai/lexora) | `openai` |
| `COGNILENS_LLM__API_KEY` | LLMプロバイダーのAPIキー | - |
| `COGNILENS_LLM__MODEL` | 使用するモデル | `gpt-4o-mini` |
| `COGNILENS_LLM__BASE_URL` | カスタムAPIエンドポイント | - |
| `COGNILENS_LLM__SMART_SELECTION__ENABLED` | スマートモデル選択の有効化 | `false` |
| `COGNILENS_LLM__SMART_SELECTION__CACHE_TTL_SECONDS` | 能力キャッシュのTTL | `300` |
| `COGNILENS_SERVER__PORT` | サーバーポート | `8003` |

### 設定ファイル

作業ディレクトリに`config.yaml`を作成：

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

## 開発

```bash
# リポジトリをクローン
git clone https://github.com/SpirrowGames/spirrow-cognilens.git
cd spirrow-cognilens

# uvでインストール
uv sync

# テスト実行
uv run pytest tests/ -v

# リント実行
uv run ruff check src/ tests/

# 型チェック実行
uv run mypy src/
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│ Cognilens MCP Server                                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ MCP Tools                                            │   │
│  │ summarize | compress_context | extract_essence      │   │
│  │ unify_summaries | summarize_diff | progressive      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Compression Engine                                   │   │
│  │ + ModelSelector (スマートモデル選択)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Strategies: Concise | Detailed | Bullet | CodeAware │   │
│  │             Diff                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ LLM Client: OpenAI | Lexora | Mock                  │   │
│  │ + Lexora APIs: /v1/models/capabilities              │   │
│  │                /v1/classify-task                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照。

## リンク

- [GitHub リポジトリ](https://github.com/SpirrowGames/spirrow-cognilens)
- [Issue Tracker](https://github.com/SpirrowGames/spirrow-cognilens/issues)
- [MCP仕様](https://modelcontextprotocol.io/)

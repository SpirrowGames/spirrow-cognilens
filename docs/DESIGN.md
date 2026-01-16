# Spirrow-Cognilens 設計ドキュメント

## 概要

情報の本質を見抜き、圧縮・要約することでコンテキストウィンドウを最適化するMCPサーバ

## コンセプト

**認知のレンズ** - 情報の本質を見抜く

```
Cognilens = Cogni (認知) + Lens (レンズ)

「大量の情報から本質だけを抽出する魔法のレンズ」
- Claude Codeのコンテキストウィンドウを節約
- 重要な情報を失わずに圧縮
- 用途に応じた最適な要約戦略
```

## 配置

- **場所**: AIサーバ
- **理由**: Lexora (ローカルLLM) を活用した圧縮処理

## 主要機能

### 1. テキスト要約

```python
# 基本的な要約
summary = await cognilens.summarize(
    text="長いテキスト...",
    max_tokens=500,
    style="concise"  # concise / detailed / bullet
)
```

### 2. コンテキスト圧縮

タスク実行に必要な情報を圧縮してClaude Codeに提供。

```python
# タスクコンテキストの圧縮
compressed = await cognilens.compress_context(
    full_context="詳細な設計ドキュメント...",
    task_description="BaseTrapクラスの実装",
    target_tokens=500
)
```

### 3. 本質抽出

```python
# 文書から本質的な情報を抽出
essence = await cognilens.extract_essence(
    document="長いドキュメント...",
    focus_areas=["API変更点", "破壊的変更"]
)
```

### 4. 複数文書の統合要約

```python
# 複数ソースを1つの要約に
unified = await cognilens.unify_summaries(
    documents=[
        {"title": "設計書", "content": "..."},
        {"title": "API仕様", "content": "..."},
        {"title": "過去の実装例", "content": "..."},
    ],
    purpose="トラップシステム実装の参考資料"
)
```

### 5. 差分要約

```python
# 変更点のみを抽出
diff_summary = await cognilens.summarize_diff(
    before="旧バージョンのコード...",
    after="新バージョンのコード...",
    focus="破壊的変更"
)
```

### 6. 段階的圧縮

大量の情報を段階的に圧縮。

```python
# 段階的圧縮（大きなドキュメント用）
result = await cognilens.progressive_compress(
    text="非常に長いテキスト...",
    stages=[
        {"target_ratio": 0.5, "preserve": ["code", "api"]},
        {"target_ratio": 0.3, "preserve": ["api"]},
        {"target_ratio": 0.1, "preserve": []}
    ]
)
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│ Cognilens                                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ MCP Interface                                        │   │
│  │ - summarize                                          │   │
│  │ - compress_context                                   │   │
│  │ - extract_essence                                    │   │
│  │ - unify_summaries                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Compression Strategies                               │   │
│  │ - ConciseStrategy (簡潔)                            │   │
│  │ - DetailedStrategy (詳細保持)                       │   │
│  │ - BulletStrategy (箇条書き)                         │   │
│  │ - CodeAwareStrategy (コード考慮)                    │   │
│  │ - DiffStrategy (差分特化)                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Prompt Templates                                     │   │
│  │ - 用途別の最適化されたプロンプト                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Lexora Client                                        │   │
│  │ - LLM呼び出し                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 圧縮戦略

### Concise Strategy

```
入力: 1000トークン
出力: 200トークン (80%圧縮)
用途: 概要把握、タスク一覧
```

### Detailed Strategy

```
入力: 1000トークン
出力: 500トークン (50%圧縮)
用途: 実装の参考、API仕様
```

### Code-Aware Strategy

```
コード部分: 保持 or 構造のみ抽出
コメント: 重要なもののみ
説明文: 圧縮
```

### Diff Strategy

```
変更なし: 省略
追加: 保持
削除: 言及のみ
変更: 差分を強調
```

## プロンプトテンプレート例

```python
SUMMARIZE_TEMPLATE = """
以下のテキストを{style}に要約してください。

制約:
- 最大{max_tokens}トークン
- {preserve}は必ず保持
- 技術的な正確性を維持

テキスト:
{text}

要約:
"""

COMPRESS_CONTEXT_TEMPLATE = """
以下のコンテキストを、タスク実行に必要な情報のみに圧縮してください。

タスク: {task_description}
目標トークン数: {target_tokens}

コンテキスト:
{full_context}

圧縮結果:
"""
```

## MCP Tools

```python
@mcp_tool
async def summarize(
    text: str,
    max_tokens: int = 500,
    style: Literal["concise", "detailed", "bullet"] = "concise",
    preserve: List[str] = []
) -> str:
    """テキストを要約する"""
    pass

@mcp_tool
async def compress_context(
    full_context: str,
    task_description: str,
    target_tokens: int = 500
) -> str:
    """タスク実行用にコンテキストを圧縮する"""
    pass

@mcp_tool
async def extract_essence(
    document: str,
    focus_areas: List[str] = []
) -> str:
    """文書から本質を抽出する"""
    pass
```

## 責務の明確化

### Cognilensがやること
- 圧縮・要約のロジック
- プロンプトエンジニアリング
- 圧縮戦略の選択
- 結果の後処理

### Cognilensがやらないこと
- LLM直接管理（→ Lexora）
- 知識の保存（→ Prismind）
- タスク管理（→ Magickit）

## 連携サービス

| サービス | 連携内容 |
|----------|----------|
| Lexora | LLM呼び出し |
| Magickit | タスクコンテキストの圧縮依頼 |
| Prismind | 検索結果の要約 |

## 品質指標

```python
@dataclass
class CompressionResult:
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    preserved_elements: List[str]
    quality_score: float  # 0.0 - 1.0
```

## 今後の拡張

- [ ] 圧縮品質の自動評価
- [ ] ドメイン特化の圧縮戦略（UE5、C++等）
- [ ] 圧縮履歴の学習
- [ ] 多言語対応の最適化

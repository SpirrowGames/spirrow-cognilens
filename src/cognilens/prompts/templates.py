"""Prompt templates for compression operations."""

from __future__ import annotations

# Base system prompt for all compression tasks
SYSTEM_PROMPT = """あなたは情報圧縮の専門家です。
テキストの本質を見抜き、重要な情報を失わずに圧縮・要約することが役割です。
技術的な正確性を維持しながら、簡潔で明確な出力を生成してください。"""

# Template for basic summarization
SUMMARIZE_TEMPLATE = """以下のテキストを{style}に要約してください。

制約:
- 最大{max_tokens}トークン程度
{preserve_instruction}
- 技術的な正確性を維持

テキスト:
{text}

要約:"""

# Template for context compression
COMPRESS_CONTEXT_TEMPLATE = """以下のコンテキストを、タスク実行に必要な情報のみに圧縮してください。

タスク: {task_description}
目標トークン数: {target_tokens}

重要: タスク実行に直接関係しない情報は省略し、必要な情報のみを残してください。

コンテキスト:
{full_context}

圧縮結果:"""

# Template for essence extraction
EXTRACT_ESSENCE_TEMPLATE = """以下の文書から本質的な情報を抽出してください。

注目すべき領域:
{focus_areas}

抽出基準:
- 主要な概念と定義
- 重要な関係性
- キーとなる数値や仕様
- 注目領域に関連する情報を優先

文書:
{document}

本質:"""

# Template for unifying multiple documents
UNIFY_SUMMARIES_TEMPLATE = """以下の複数の文書を、1つの統合された要約にまとめてください。

目的: {purpose}

文書一覧:
{documents}

統合要約の作成基準:
- 重複する情報は1度だけ記載
- 矛盾する情報がある場合は明記
- 目的に関連する情報を優先
- 出典（文書タイトル）を適宜示す

統合要約:"""

# Template for diff summarization
SUMMARIZE_DIFF_TEMPLATE = """以下の変更前後のテキストを比較し、変更点を要約してください。

{focus_instruction}

変更前:
{before}

変更後:
{after}

変更要約の形式:
- 追加された内容
- 削除された内容
- 変更された内容
- 影響範囲

変更要約:"""

# Template for progressive compression
PROGRESSIVE_COMPRESS_TEMPLATE = """以下のテキストを段階的に圧縮してください。

現在のステージ: {stage_number} / {total_stages}
目標圧縮率: {target_ratio}
{preserve_instruction}

入力テキスト:
{text}

圧縮基準:
- 目標の圧縮率を達成
- 指定された要素は必ず保持
- 次のステージでさらに圧縮される可能性を考慮

圧縮結果:"""

# Style-specific instructions
STYLE_INSTRUCTIONS: dict[str, str] = {
    "concise": "簡潔に（1-3文で）",
    "detailed": "重要なポイントを網羅しつつ詳細に",
    "bullet": "箇条書き形式で",
    "code_aware": "コード構造を保持しながら説明を圧縮",
    "diff": "変更点に焦点を当てて",
}

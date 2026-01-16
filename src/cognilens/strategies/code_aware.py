"""Code-aware compression strategy - preserves code structure."""

from __future__ import annotations

import re

from cognilens.core.types import CompressionRequest, CompressionResult, CompressionStyle
from cognilens.prompts.builder import PromptBuilder

from .base import CompressionStrategy

CODE_AWARE_PROMPT_SUFFIX = """

コード処理の追加指示:
- コードブロック: 構造（クラス/関数シグネチャ）は保持、実装詳細は省略可
- コメント: 重要なものは保持、自明なものは削除
- 説明文: 圧縮
- インポート文: 主要なもののみ"""


class CodeAwareStrategy(CompressionStrategy):
    """Code-aware compression strategy - preserves code structure."""

    @property
    def name(self) -> str:
        return "code_aware"

    @property
    def description(self) -> str:
        return "Code-aware compression - preserves structure, compresses explanations"

    async def compress(self, request: CompressionRequest) -> CompressionResult:
        """Compress text while preserving code structure."""
        original_tokens = await self.llm.count_tokens(request.text)
        target_tokens = request.target_tokens or int(original_tokens * 0.4)

        # Detect code blocks and add them to preserve list
        code_elements = self._extract_code_signatures(request.text)
        preserve = list(set(request.preserve + code_elements[:5]))  # Top 5 signatures

        base_prompt = PromptBuilder.build_summarize_prompt(
            text=request.text,
            max_tokens=target_tokens,
            style=CompressionStyle.CODE_AWARE,
            preserve=preserve,
        )
        prompt = base_prompt + CODE_AWARE_PROMPT_SUFFIX

        response = await self.llm.generate(
            prompt,
            system_prompt=PromptBuilder.get_system_prompt(),
            max_tokens=target_tokens + 200,
            temperature=0.3,
        )

        compressed_tokens = await self.llm.count_tokens(response.content)
        quality = await self._calculate_quality_score(request.text, response.content, preserve)

        return CompressionResult(
            compressed_text=response.content,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compressed_tokens / original_tokens if original_tokens > 0 else 0,
            preserved_elements=preserve,
            quality_score=quality,
            metadata={
                "strategy": self.name,
                "model": response.model,
                "detected_signatures": code_elements,
            },
        )

    def _extract_code_signatures(self, text: str) -> list[str]:
        """Extract function/class signatures from code."""
        signatures: list[str] = []

        # Python/TypeScript function patterns
        func_pattern = r"(?:async\s+)?(?:def|function)\s+(\w+)\s*\("
        signatures.extend(re.findall(func_pattern, text))

        # Class patterns
        class_pattern = r"class\s+(\w+)"
        signatures.extend(re.findall(class_pattern, text))

        return list(set(signatures))

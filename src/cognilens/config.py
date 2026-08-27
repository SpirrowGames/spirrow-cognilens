"""Configuration management for Spirrow-Cognilens."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    MOCK = "mock"
    OPENAI = "openai"
    LEXORA = "lexora"


class SmartModelSelectionConfig(BaseModel):
    """Smart model selection configuration."""

    enabled: bool = False
    cache_ttl_seconds: int = 300
    classify_tasks: bool = True
    fallback_to_default: bool = True
    strategy_capability_map: dict[str, str] = Field(
        default_factory=lambda: {
            "concise": "summarization",
            "detailed": "summarization",
            "bullet": "summarization",
            "code_aware": "code",
            "diff": "reasoning",
        }
    )


class LLMConfig(BaseModel):
    """LLM client configuration."""

    provider: LLMProvider = LLMProvider.MOCK
    model: str = "gpt-4o-mini"
    api_key: str | None = None
    base_url: str | None = None
    timeout: int = 30
    max_retries: int = 3
    # Model context window (input + output). Used to clamp requested output
    # tokens so that input_tokens + max_tokens never exceeds the model limit.
    #
    # **This must track the serving backend, not this file.** It is not a
    # policy knob: understating it silently shrinks the completion budget
    # until `generate` has nothing left to ask for. The default matches the
    # vLLM deployment Cognilens is pointed at; check it with
    #   curl -s localhost:8110/v1/models | jq '.data[].max_model_len'
    # and set `llm.context_window` in config.yaml whenever they differ.
    #
    # Was 8192 -- a leftover from the gpt-4o-mini default above -- while the
    # backend served 32768. Inputs past ~7.9k tokens then left no budget and
    # every summary of a long thread came back one token long.
    context_window: int = 32768
    # Safety margin subtracted from the available output budget to absorb
    # chat-template overhead and tokenizer discrepancies between our local
    # token counter and the serving backend.
    output_safety_margin: int = 256
    smart_selection: SmartModelSelectionConfig = Field(
        default_factory=SmartModelSelectionConfig
    )


class CompressionConfig(BaseModel):
    """Compression settings."""

    default_ratio: float = Field(default=0.3, ge=0.1, le=0.9)
    min_ratio: float = Field(default=0.1, ge=0.05, le=0.5)
    max_ratio: float = Field(default=0.9, ge=0.5, le=1.0)


class SummarizationConfig(BaseModel):
    """Summarization settings."""

    default_max_tokens: int = 500
    default_style: str = "concise"


class ServerConfig(BaseModel):
    """MCP server configuration."""

    name: str = "Spirrow-Cognilens"
    host: str = "0.0.0.0"
    port: int = 8003


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="COGNILENS_",
        env_nested_delimiter="__",
    )

    server: ServerConfig = Field(default_factory=ServerConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    compression: CompressionConfig = Field(default_factory=CompressionConfig)
    summarization: SummarizationConfig = Field(default_factory=SummarizationConfig)

    @classmethod
    def from_yaml(cls, path: Path) -> Settings:
        """Load settings from YAML file. **config.yaml wins over the environment.**

        The precedence is the opposite of what this docstring used to
        claim, and of what the comment below it used to say. Passing the
        YAML in as keyword arguments makes it *init* settings, and
        pydantic-settings ranks init arguments above environment
        variables -- so `COGNILENS_LLM__MODEL` in the environment is
        read, ranked below `llm.model` in the file, and discarded.

        Found while deploying: `start.sh` exported
        `COGNILENS_LLM__MODEL=Qwen2.5-1.5B` and had no effect, while the
        service ran on `light` from config.yaml. That was the right
        model -- `light` is the Lexora backend whose declared
        capabilities include summarization, and it resolves to Qwen3-32B
        -- so the behaviour is kept and the description corrected. Had
        it been "fixed" the other way, compression would have been
        routed to a 1.5B model that Lexora no longer serves at all.

        Anything that must be settable per host therefore belongs in
        config.yaml, not in an exported variable.
        """
        if path.exists():
            with open(path, encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
            # Init kwargs outrank env vars in pydantic-settings, so this
            # line is what gives config.yaml the final say.
            return cls(**yaml_data)
        return cls()

    @classmethod
    def for_testing(cls, **overrides: Any) -> Settings:
        """Create settings for testing with optional overrides."""
        from cognilens.config import LLMConfig, LLMProvider

        # Annotated because the values are heterogeneous section objects;
        # without it the dict narrows to dict[str, LLMConfig] and every
        # other section looks like a type error at the call below.
        defaults: dict[str, Any] = {
            "llm": LLMConfig(provider=LLMProvider.MOCK),
        }
        defaults.update(overrides)
        return cls(**defaults)


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        config_path = Path("config.yaml")
        _settings = Settings.from_yaml(config_path)
    return _settings


def reset_settings() -> None:
    """Reset settings (useful for testing)."""
    global _settings
    _settings = None

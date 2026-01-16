"""Configuration management for Spirrow-Cognilens."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    MOCK = "mock"
    OPENAI = "openai"
    LEXORA = "lexora"


class LLMConfig(BaseModel):
    """LLM client configuration."""

    provider: LLMProvider = LLMProvider.MOCK
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3


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
    def from_yaml(cls, path: Path) -> "Settings":
        """Load settings from YAML file, with environment variables taking precedence."""
        if path.exists():
            with open(path, encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
            # Create settings with YAML as defaults, env vars will override
            return cls(**yaml_data)
        return cls()

    @classmethod
    def for_testing(cls, **overrides) -> "Settings":
        """Create settings for testing with optional overrides."""
        from cognilens.config import LLMConfig, LLMProvider

        defaults = {
            "llm": LLMConfig(provider=LLMProvider.MOCK),
        }
        defaults.update(overrides)
        return cls(**defaults)


# Global settings instance
_settings: Optional[Settings] = None


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

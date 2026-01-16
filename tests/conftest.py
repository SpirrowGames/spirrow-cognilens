"""Pytest fixtures for Spirrow-Cognilens tests."""

import pytest

from cognilens.core.compressor import CompressionEngine
from cognilens.llm.mock import MockLLMClient


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    return MockLLMClient()


@pytest.fixture
def compression_engine(mock_llm_client):
    """Create a compression engine with mock LLM client."""
    return CompressionEngine(llm_client=mock_llm_client)


@pytest.fixture
def sample_text():
    """Sample text for compression tests."""
    return """
    This is a sample document about software architecture.
    It contains multiple paragraphs discussing various design patterns.
    The Strategy pattern allows selecting algorithms at runtime.
    The Factory pattern provides object creation flexibility.
    These patterns improve code maintainability and testability.
    Good architecture leads to scalable and maintainable systems.
    """


@pytest.fixture
def sample_documents():
    """Sample documents for unification tests."""
    return [
        {
            "title": "Design Patterns",
            "content": "Strategy and Factory patterns improve flexibility.",
        },
        {
            "title": "API Reference",
            "content": "Endpoints: /compress, /summarize, /extract.",
        },
    ]


@pytest.fixture
def sample_diff_texts():
    """Sample texts for diff tests."""
    return {
        "before": "def calculate(x, y): return x + y",
        "after": "def calculate(x, y, z=0): return x + y + z",
    }

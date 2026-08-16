"""Which wins, config.yaml or the environment.

The answer is config.yaml, and it is worth a test rather than a
docstring because the mechanism is indirect: `from_yaml` passes the file
in as keyword arguments, and pydantic-settings ranks *init* arguments
above environment variables. Nothing in the call site says so, and the
docstring said the opposite for as long as it existed.

The cost of that being wrong was not theoretical. `start.sh` exported
`COGNILENS_LLM__MODEL=Qwen2.5-1.5B`, which was silently discarded while
the service ran on `light` from config.yaml. `light` was the right
choice -- it is the Lexora backend that declares `summarization` among
its capabilities -- so what needed correcting was the belief, not the
behaviour. Anyone who had "fixed" the precedence to match the docstring
would have routed context compression to a 1.5B model that Lexora no
longer serves.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from cognilens.config import Settings


def _write_config(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(textwrap.dedent(body), encoding="utf-8")
    return path


def test_config_yaml_beats_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("COGNILENS_LLM__MODEL", "from-env")
    path = _write_config(
        tmp_path,
        """
        llm:
          model: "from-yaml"
        """,
    )

    settings = Settings.from_yaml(path)

    assert settings.llm.model == "from-yaml"


def test_the_environment_still_fills_what_the_file_leaves_out(tmp_path, monkeypatch):
    """Losing a contest is not the same as being ignored."""
    monkeypatch.setenv("COGNILENS_LLM__MODEL", "from-env")
    path = _write_config(
        tmp_path,
        """
        compression:
          default_ratio: 0.5
        """,
    )

    settings = Settings.from_yaml(path)

    assert settings.llm.model == "from-env"
    assert settings.compression.default_ratio == 0.5


def test_a_missing_file_leaves_the_environment_in_charge(tmp_path, monkeypatch):
    monkeypatch.setenv("COGNILENS_LLM__MODEL", "from-env")

    settings = Settings.from_yaml(tmp_path / "does-not-exist.yaml")

    assert settings.llm.model == "from-env"


def test_an_empty_file_is_not_treated_as_a_broken_one(tmp_path):
    path = _write_config(tmp_path, "")

    settings = Settings.from_yaml(path)

    assert settings.llm.model == Settings().llm.model


def test_the_shipped_config_pins_the_model_deliberately():
    """The repo's own config.yaml is the file that decides, so a change
    to it changes what the service runs -- worth failing on rather than
    discovering after a deploy."""
    repo_config = Path(__file__).resolve().parents[2] / "config.yaml"

    settings = Settings.from_yaml(repo_config)

    # `light` is a Lexora *backend* name, not a model name: it resolves
    # to Qwen3-32B in non-thinking mode, and declares `summarization`
    # among its capabilities.
    assert settings.llm.model == "light"
    assert settings.llm.base_url.rstrip("/").endswith(":8110/v1")

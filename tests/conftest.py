"""Shared fixtures for the Akinator test suite.

The suite has two jobs:

1. Verify the plugin's own structure against the platform contracts it claims to
   satisfy (Claude Code plugin, Codex skills and plugin manifests).
2. Verify that the enforcement mechanisms the rules name actually work - so a
   rule cannot silently become decoration.

Stdlib and pytest only. No network, no fixtures that write into the repository.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# The scripts are executable modules, not an installed package. The host-repo
# tools live inside the one skill, so they travel with it to every platform;
# the build scripts that only make sense inside this checkout stay in scripts/.
SKILL_ROOT = REPO_ROOT / "skills" / "everything"
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(SKILL_ROOT / "scripts"))


@pytest.fixture(scope="session")
def repo() -> Path:
    """The Akinator repository root."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def plugin_manifest(repo: Path) -> dict:
    return json.loads((repo / ".claude-plugin" / "plugin.json").read_text("utf-8"))


@pytest.fixture(scope="session")
def marketplace_manifest(repo: Path) -> dict:
    return json.loads(
        (repo / ".claude-plugin" / "marketplace.json").read_text("utf-8")
    )


@pytest.fixture(scope="session")
def codex_manifest(repo: Path) -> dict:
    return json.loads((repo / ".codex-plugin" / "plugin.json").read_text("utf-8"))


@pytest.fixture(scope="session")
def skill_paths(repo: Path) -> list[Path]:
    return sorted((repo / "skills").rglob("SKILL.md"))


@pytest.fixture(scope="session")
def agent_paths(repo: Path) -> list[Path]:
    return sorted((repo / "agents").glob("*.md"))


@pytest.fixture(scope="session")
def command_paths(repo: Path) -> list[Path]:
    return sorted((repo / "commands").glob("*.md"))


@pytest.fixture(scope="session")
def rule_paths(repo: Path) -> list[Path]:
    return sorted(
        p for p in (repo / "rules").glob("*.md")
        if p.name.lower() not in ("readme.md", "index.md")
    )


def frontmatter(path: Path) -> dict[str, str]:
    """Parse the flat key: value frontmatter of a markdown component.

    Deliberately minimal - the component contracts use flat scalar keys, and a
    YAML dependency would be a runtime requirement the plugin does not otherwise
    have. Multi-line folded values are joined.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[4:end]

    out: dict[str, str] = {}
    key: str | None = None
    for line in block.splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            out[key] = value.strip()
        elif key and line.strip():
            out[key] = (out[key] + " " + line.strip()).strip()
    return out

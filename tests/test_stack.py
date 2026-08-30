"""Tests for the stack map.

Akinator's own repository declares no dependencies, so a passing run here proves
nothing about the extractor. Per rules/11, every reader is exercised against a
real manifest of its ecosystem.

The design claim under test: **one generated map replaces N generated
documents**, and its value over `package.json` is the link from a dependency to
the decision that chose it and the failure it caused.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import extract_stack as es


def _write(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


# --------------------------------------------------------------------------
# Every reader, against a real manifest of its ecosystem
# --------------------------------------------------------------------------

def test_reads_package_json(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({
        "dependencies": {"axios": "^1.6.0"},
        "devDependencies": {"vitest": "~1.2.0"},
        "peerDependencies": {"react": ">=18"},
    }))
    found = es.discover(tmp_path)["npm"]
    assert ("axios", "^1.6.0", "runtime", "package.json") in found
    assert ("vitest", "~1.2.0", "dev", "package.json") in found
    assert ("react", ">=18", "peer", "package.json") in found


def test_reads_pyproject(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", (
        "[project]\n"
        'dependencies = ["httpx>=0.27", "pydantic"]\n'
        "[project.optional-dependencies]\n"
        'test = ["pytest>=8"]\n'
    ))
    found = es.discover(tmp_path)["python"]
    names = {name for name, _v, _k, _m in found}
    assert {"httpx", "pydantic", "pytest"} <= names
    assert ("httpx", ">=0.27", "runtime", "pyproject.toml") in found
    assert ("pytest", ">=8", "test", "pyproject.toml") in found


def test_reads_requirements(tmp_path: Path) -> None:
    _write(tmp_path, "requirements.txt",
           "# a comment\nrequests==2.31.0\n-e .\n\nrich\n")
    found = es.discover(tmp_path)["python"]
    names = {name for name, _v, _k, _m in found}
    assert names == {"requests", "rich"}, "comments and -e lines are not deps"


def test_reads_cargo(tmp_path: Path) -> None:
    _write(tmp_path, "Cargo.toml", (
        "[dependencies]\n"
        'serde = "1.0"\n'
        'tokio = { version = "1.35", features = ["full"] }\n'
        "[dev-dependencies]\n"
        'proptest = "1"\n'
    ))
    found = es.discover(tmp_path)["rust"]
    assert ("serde", "1.0", "runtime", "Cargo.toml") in found
    assert ("tokio", "1.35", "runtime", "Cargo.toml") in found, (
        "a table-form dependency must yield its version, not the table"
    )
    assert ("proptest", "1", "dev", "Cargo.toml") in found


def test_reads_gomod(tmp_path: Path) -> None:
    _write(tmp_path, "go.mod", (
        "module example.com/app\n\ngo 1.22\n\n"
        "require (\n"
        "\tgithub.com/gin-gonic/gin v1.9.1\n"
        "\tgolang.org/x/sync v0.6.0\n"
        ")\n"
    ))
    found = es.discover(tmp_path)["go"]
    names = {name for name, _v, _k, _m in found}
    assert "github.com/gin-gonic/gin" in names
    assert "example.com/app" not in names, "the module line is not a dependency"


def test_a_malformed_manifest_does_not_crash(tmp_path: Path) -> None:
    """A broken manifest must degrade to nothing, not take the map down."""
    _write(tmp_path, "package.json", "{ not json at all")
    assert es.discover(tmp_path) == {}


def test_vendored_trees_are_skipped(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    _write(tmp_path, "node_modules/axios/package.json",
           json.dumps({"dependencies": {"follow-redirects": "1"}}))
    names = {name for name, _v, _k, _m in es.discover(tmp_path)["npm"]}
    assert names == {"axios"}, "node_modules must not be walked"


# --------------------------------------------------------------------------
# The part that makes the map worth more than the manifest
# --------------------------------------------------------------------------

def test_a_dependency_links_to_the_decision_that_chose_it(tmp_path: Path) -> None:
    """The row does not describe the library - it points at the knowledge."""
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    _write(tmp_path, "docs/adr/0009-http-client.md",
           "# ADR 0009 - axios over fetch\n\nBecause of the retry interceptor.\n")

    assert es.knowledge_for(tmp_path, "axios") == ["docs/adr/0009-http-client.md"]
    assert "docs/adr/0009-http-client.md" in es.render(tmp_path)


def test_a_dependency_links_to_the_failure_it_caused(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    _write(tmp_path, ".ai/ledger/failure/retry-storm-000.md",
           "---\nkind: failure\n---\n\n# axios retried a non-idempotent POST\n")

    assert ".ai/ledger/failure/retry-storm-000.md" in es.knowledge_for(
        tmp_path, "axios"
    )


def test_knowledge_matching_is_word_bounded(tmp_path: Path) -> None:
    """`ax` must not match `axios`, and `axios` must not match `axios-retry`.

    The same substring failure that bit index-completeness three times, in a new
    place - so it is tested here before it can.
    """
    _write(tmp_path, "docs/adr/0001-x.md", "# ADR\n\nWe use axios-retry.\n")
    assert es.knowledge_for(tmp_path, "axios") == []
    assert es.knowledge_for(tmp_path, "axios-retry") == ["docs/adr/0001-x.md"]


def test_a_dependency_with_no_knowledge_is_marked_as_such(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"lodash": "4"}}))
    text = es.render(tmp_path)
    assert "`lodash`" in text
    assert "| - |" in text, "no linked knowledge must render as an explicit dash"


# --------------------------------------------------------------------------
# Modules
# --------------------------------------------------------------------------

def test_modules_are_discovered_from_nested_manifests(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"name": "root"}))
    _write(tmp_path, "services/api/package.json", json.dumps({"name": "api"}))
    _write(tmp_path, "packages/billing/pyproject.toml", "[project]\nname='b'\n")

    found = dict(es.modules(tmp_path))
    assert "services/api" in found
    assert "packages/billing" in found
    assert "" not in found, "the repository root is not a sub-module"


# --------------------------------------------------------------------------
# Generation contract
# --------------------------------------------------------------------------

def test_generation_is_deterministic(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({
        "dependencies": {"b": "1", "a": "2", "c": "3"}
    }))
    assert es.render(tmp_path) == es.render(tmp_path)


def test_map_declares_itself_generated(repo: Path) -> None:
    text = es.render(repo)
    assert text.startswith("<!--")
    assert "DO NOT EDIT BY HAND" in text
    assert "extract_stack.py" in text


def test_map_states_why_there_is_no_doc_per_library(repo: Path) -> None:
    """The reasoning has to travel with the artifact - a future contributor
    will otherwise 'helpfully' add the pages this map exists to replace."""
    text = es.render(repo)
    assert "delete-the-derivable" in text
    assert "rediscovery_cost" in text


def test_this_repo_map_is_not_drifted(repo: Path) -> None:
    target = repo / es.TARGET
    assert target.is_file(), "run extract_stack.py --write"
    assert target.read_text(encoding="utf-8") == es.render(repo)


def test_this_repo_declares_no_dependencies(repo: Path) -> None:
    """Stdlib-only is a real property worth pinning: it is why the plugin
    installs anywhere with a Python interpreter and nothing else."""
    assert es.discover(repo) == {}

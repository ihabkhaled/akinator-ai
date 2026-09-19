"""Tests for the library wiki - one page per declared dependency.

Akinator's own repository declares no dependencies, so a passing run here proves
nothing about the generator. Per rules/11, every behaviour is exercised against a
scratch repository built to trip it, and every check is shown both firing on the
broken case and staying silent on the healthy one.

The design claims under test:

- a page per dependency, per ecosystem, with facts that are extracted, never
  written by hand;
- usage detection by import, not by substring (`react` is not `react-dom`);
- the curated half of a page is a person's, and survives every regeneration
  byte for byte;
- a dependency that disappears leaves its page flagged, never deleted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import akinator_coverage as cov
import extract_libraries as el

WIKI = "docs/wiki/libraries"


def _write(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def _page(root: Path, slug: str) -> Path:
    return root / WIKI / f"{slug}.md"


def _block(text: str) -> str:
    start = text.index(el.BEGIN)
    return text[start:text.index(el.END, start) + len(el.END)]


def _outside(text: str) -> tuple[str, str]:
    start = text.index(el.BEGIN)
    stop = text.index(el.END, start) + len(el.END)
    return text[:start], text[stop:]


def _polyglot(root: Path) -> None:
    """A repository with one dependency per ecosystem, each imported once."""
    _write(root, "package.json", json.dumps({
        "dependencies": {"react": "^18.2.0", "react-dom": "^18.2.0"},
        "devDependencies": {"vitest": "~1.2.0"},
    }))
    _write(root, "requirements.txt", "requests==2.31.0\n")
    _write(root, "go.mod", (
        "module example.com/app\n\ngo 1.22\n\n"
        "require (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n"
    ))
    _write(root, "Cargo.toml", '[dependencies]\nserde = "1.0"\n')
    _write(root, "web/App.tsx", "import React from 'react';\n")
    _write(root, "api/client.py", "import requests\n")
    _write(root, "server/main.go",
           'package main\n\nimport (\n\t"fmt"\n\t"github.com/gin-gonic/gin"\n)\n')
    _write(root, "src/lib.rs", "use serde::Serialize;\n")


# --------------------------------------------------------------------------
# Pages, one per dependency, per ecosystem
# --------------------------------------------------------------------------

def test_pages_are_created_per_ecosystem(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    assert el.main([str(tmp_path), "--write"]) == 0

    for slug, title, ecosystem in (
        ("react", "react", "npm"),
        ("requests", "requests", "python"),
        ("github.com-gin-gonic-gin", "github.com/gin-gonic/gin", "go"),
        ("serde", "serde", "rust"),
    ):
        page = _page(tmp_path, slug)
        assert page.is_file(), f"no page for {title}"
        text = page.read_text(encoding="utf-8")
        assert text.startswith(f"# {title}\n"), text[:60]
        block = _block(text)
        assert f"**Ecosystem:** {ecosystem}" in block
        assert "Regenerate with: `python <skill>/scripts/extract_libraries.py --write`" in block


def test_a_new_page_carries_every_curated_section_as_an_honest_gap(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    text = _page(tmp_path, "react").read_text(encoding="utf-8")
    _before, after = _outside(text)
    for section in el.CURATED_SECTIONS:
        assert f"## {section}\n\n{el.GAP}\n" in after, section
    lines = text.splitlines()
    assert lines.count(el.GAP) == len(el.CURATED_SECTIONS), (
        "the gap marker must be the exact line, once per section, so tools can count it"
    )


def test_the_generated_block_states_the_facts(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    block = _block(_page(tmp_path, "react").read_text(encoding="utf-8"))
    assert "**Version:** `^18.2.0`" in block
    assert "**Kind:** runtime" in block
    assert "**Declared in:** `package.json`" in block
    assert "**Used in:** 1 file" in block
    assert "  - `web/App.tsx`" in block

    dev = _block(_page(tmp_path, "vitest").read_text(encoding="utf-8"))
    assert "**Kind:** dev" in dev
    assert "**Used in:** 0 files" in dev, "no import must be stated, not hidden"


def test_the_index_lists_every_library(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    index = (tmp_path / WIKI / "README.md").read_text(encoding="utf-8")
    assert "| Library | Ecosystem | Version | Kind | Used in | Page |" in index
    assert "| react | npm | `^18.2.0` | runtime | 1 file | [react.md](react.md) |" in index
    assert "| vitest | npm | `~1.2.0` | dev | 0 files | [vitest.md](vitest.md) |" in index
    assert "[github.com-gin-gonic-gin.md](github.com-gin-gonic-gin.md)" in index
    assert "## Libraries (6)" in index


def test_a_dependency_declared_twice_is_one_page_with_both_versions(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "^1.6.0"}}))
    _write(tmp_path, "legacy/package.json", json.dumps({"dependencies": {"axios": "^0.27.0"}}))
    el.main([str(tmp_path), "--write"])
    block = _block(_page(tmp_path, "axios").read_text(encoding="utf-8"))
    assert "`^0.27.0` in `legacy/package.json`" in block
    assert "`^1.6.0` in `package.json`" in block, "version drift across modules is a fact"


def test_a_dependency_links_to_the_decision_that_chose_it(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    _write(tmp_path, "docs/adr/0009-http-client.md", "# ADR 0009 - axios over fetch\n")
    el.main([str(tmp_path), "--write"])
    block = _block(_page(tmp_path, "axios").read_text(encoding="utf-8"))
    assert "**Decisions and incidents:** `docs/adr/0009-http-client.md`" in block


def test_long_usage_lists_are_capped(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"lodash": "4"}}))
    for n in range(30):
        _write(tmp_path, f"src/m{n:02d}.js", "const _ = require('lodash');\n")
    el.main([str(tmp_path), "--write"])
    block = _block(_page(tmp_path, "lodash").read_text(encoding="utf-8"))
    assert "**Used in:** 30 files" in block
    assert block.count("  - `src/") == el.MAX_LISTED
    assert "  - ... and 5 more" in block
    assert "`src/m00.js`" in block and "`src/m25.js`" not in block, "first 25, sorted"


# --------------------------------------------------------------------------
# Usage detection - hits and misses
# --------------------------------------------------------------------------

def _used(root: Path, ecosystem: str, name: str) -> list[str]:
    return el.usage(el.Library(ecosystem, name), el.scan(root))


def test_npm_usage_is_exact_not_a_substring(tmp_path: Path) -> None:
    """`react` must not match an import of `react-dom` - the substring failure."""
    _write(tmp_path, "a.tsx", "import ReactDOM from 'react-dom/client';\n")
    _write(tmp_path, "b.tsx", "import { jsx } from 'react/jsx-runtime';\n")
    _write(tmp_path, "c.cjs", "const React = require(\"react\");\n")
    _write(tmp_path, "d.ts", "const lazy = import('react');\n")
    _write(tmp_path, "e.ts", "import {\n  useState,\n} from 'react';\n")
    _write(tmp_path, "f.js", "import react from './react';\n")
    _write(tmp_path, "g.mjs", "export { x } from 'preact';\n")

    assert _used(tmp_path, "npm", "react") == ["b.tsx", "c.cjs", "d.ts", "e.ts"]
    assert _used(tmp_path, "npm", "react-dom") == ["a.tsx"]


def test_npm_scoped_packages_resolve_to_their_scope(tmp_path: Path) -> None:
    _write(tmp_path, "a.ts", "import { x } from '@tanstack/query-core/build';\n")
    _write(tmp_path, "b.ts", "import 'node:fs';\nimport '@tanstack/react-query';\n")
    assert _used(tmp_path, "npm", "@tanstack/query-core") == ["a.ts"]
    assert _used(tmp_path, "npm", "@tanstack/react-query") == ["b.ts"]


def test_python_usage_maps_distribution_to_import_name(tmp_path: Path) -> None:
    _write(tmp_path, "a.py", "import requests\n")
    _write(tmp_path, "b.py", "from requests.adapters import HTTPAdapter\n")
    _write(tmp_path, "c.py", "import requests_toolbelt\n")
    _write(tmp_path, "d.py", "from .requests import local\n")
    _write(tmp_path, "e.py", "import yaml\n")
    _write(tmp_path, "f.py", "from dateutil import parser\n")
    _write(tmp_path, "g.py", "import os, typing_extensions as te\n")
    _write(tmp_path, "h.py", "from google.auth import default\n")

    assert _used(tmp_path, "python", "requests") == ["a.py", "b.py"]
    assert _used(tmp_path, "python", "PyYAML") == ["e.py"]
    assert _used(tmp_path, "python", "python-dateutil") == ["f.py"]
    assert _used(tmp_path, "python", "typing-extensions") == ["g.py"]
    assert _used(tmp_path, "python", "google-auth") == ["h.py"]
    assert _used(tmp_path, "python", "requests-toolbelt") == ["c.py"]


def test_go_usage_matches_by_import_path_prefix(tmp_path: Path) -> None:
    _write(tmp_path, "a.go", 'package a\n\nimport "github.com/gin-gonic/gin/binding"\n')
    _write(tmp_path, "b.go", 'package b\n\nimport (\n\tg "github.com/gin-gonic/gin"\n)\n')
    _write(tmp_path, "c.go", 'package c\n\nimport "github.com/gin-gonic/ginx"\n')
    assert _used(tmp_path, "go", "github.com/gin-gonic/gin") == ["a.go", "b.go"]


def test_rust_usage_maps_dashes_to_underscores(tmp_path: Path) -> None:
    _write(tmp_path, "a.rs", "use tokio_util::codec::Framed;\n")
    _write(tmp_path, "b.rs", "#[tokio::main]\nasync fn main() {}\n")
    _write(tmp_path, "c.rs", "#[macro_use] extern crate serde_derive;\n")
    _write(tmp_path, "d.rs", "let v = serde_json::to_string(&x);\n")
    assert _used(tmp_path, "rust", "tokio-util") == ["a.rs"]
    assert _used(tmp_path, "rust", "tokio") == ["b.rs"], "tokio is not tokio_util"
    assert _used(tmp_path, "rust", "serde_derive") == ["c.rs"]
    assert _used(tmp_path, "rust", "serde") == [], "serde is not serde_json"


def test_an_ecosystem_without_a_detector_falls_back_to_import_lines(tmp_path: Path) -> None:
    _write(tmp_path, "A.java", "import com.google.guava.collect.Lists;\n")
    _write(tmp_path, "B.java", "// guava is great\nclass B {}\n")
    _write(tmp_path, "C.java", "import com.google.guava-extra.X;\n")
    assert _used(tmp_path, "maven", "guava") == ["A.java"]


def test_vendored_and_generated_trees_are_not_scanned(tmp_path: Path) -> None:
    _write(tmp_path, "node_modules/x/index.js", "require('react');\n")
    _write(tmp_path, "dist/bundle.js", "require('react');\n")
    _write(tmp_path, ".git/hooks/x.js", "require('react');\n")
    _write(tmp_path, "src/a.js", "require('react');\n")
    assert _used(tmp_path, "npm", "react") == ["src/a.js"]


# --------------------------------------------------------------------------
# The curated half belongs to a person
# --------------------------------------------------------------------------

def test_curated_text_survives_regeneration_byte_for_byte(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    page = _page(tmp_path, "react")
    text = page.read_text(encoding="utf-8")
    curated = text.replace(
        f"## Why this library\n\n{el.GAP}",
        "## Why this library\n\nChosen over Vue in 2023 - see the hiring plan.",
    ).replace("# react\n", "# react\n\nOwner: web team.\n")
    page.write_text(curated, encoding="utf-8", newline="\n")
    before, after = _outside(curated)

    _write(tmp_path, "package.json", json.dumps({
        "dependencies": {"react": "^19.0.0", "react-dom": "^18.2.0"},
        "devDependencies": {"vitest": "~1.2.0"},
    }))
    assert el.main([str(tmp_path), "--write"]) == 0

    regenerated = page.read_text(encoding="utf-8")
    assert _outside(regenerated) == (before, after), "only the block may change"
    assert "**Version:** `^19.0.0`" in _block(regenerated)
    assert "Chosen over Vue in 2023" in regenerated


def test_crlf_pages_keep_their_bytes_outside_the_block(tmp_path: Path) -> None:
    """A page edited on Windows keeps its line endings - read as bytes, not text."""
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    el.main([str(tmp_path), "--write"])
    page = _page(tmp_path, "axios")
    raw = page.read_bytes().replace(b"\n", b"\r\n")
    page.write_bytes(raw)
    assert el.main([str(tmp_path), "--check"]) == 0, "line endings alone are not drift"

    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "2"}}))
    el.main([str(tmp_path), "--write"])
    new = page.read_bytes()
    old_text, new_text = raw.decode("utf-8"), new.decode("utf-8")
    assert _outside(new_text) == _outside(old_text)
    assert "\n" not in new_text.replace("\r\n", ""), "no bare LF introduced"
    assert "**Version:** `2`" in new_text


def test_a_hand_written_page_without_markers_gets_the_block_inserted(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    human = "# axios\n\nWe wrap it in src/http.ts.\n"
    _write(tmp_path, f"{WIKI}/axios.md", human)
    el.main([str(tmp_path), "--write"])
    text = _page(tmp_path, "axios").read_text(encoding="utf-8")
    before, after = _outside(text)
    assert before == "# axios\n\n"
    assert after == "\n\nWe wrap it in src/http.ts.\n", "the human text is untouched"
    assert el.main([str(tmp_path), "--check"]) == 0, "insertion must be idempotent"


def test_a_broken_block_is_refused_not_guessed(tmp_path: Path) -> None:
    """A begin marker with no end: replacing to end-of-file would eat the curated
    text, so the tool refuses and says so."""
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    broken = f"# axios\n\n{el.BEGIN}\n- stale\n\n## Why this library\n\nKept.\n"
    page = _write(tmp_path, f"{WIKI}/axios.md", broken)
    assert el.main([str(tmp_path), "--write"]) == 2
    assert page.read_text(encoding="utf-8") == broken, "the page must be untouched"
    assert el.main([str(tmp_path), "--check"]) == 1


# --------------------------------------------------------------------------
# Drift: --check fires on drift and is silent when current
# --------------------------------------------------------------------------

def test_check_is_silent_when_current(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    assert el.main([str(tmp_path), "--check"]) == 0
    assert el.main([str(tmp_path)]) == 0, "a current tree is not a dry-run change"
    changes, errors = el.plan(tmp_path)
    assert changes == {} and errors == []


def test_check_fires_on_a_stale_generated_block(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    _write(tmp_path, "requirements.txt", "requests==2.32.0\n")
    assert el.main([str(tmp_path), "--check"]) == 1


def test_check_fires_on_a_hand_edited_block(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    page = _page(tmp_path, "requests")
    page.write_text(page.read_text(encoding="utf-8").replace(
        "**Ecosystem:** python", "**Ecosystem:** pip"), encoding="utf-8", newline="\n")
    assert el.main([str(tmp_path), "--check"]) == 1


def test_check_fires_on_a_missing_page(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    _page(tmp_path, "serde").unlink()
    assert el.main([str(tmp_path), "--check"]) == 1


def test_check_fires_on_a_new_import(tmp_path: Path) -> None:
    """Usage is part of the facts - a new importer is drift too."""
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    _write(tmp_path, "web/Other.tsx", "import { useState } from 'react';\n")
    assert el.main([str(tmp_path), "--check"]) == 1


def test_check_fires_on_a_stale_index(tmp_path: Path) -> None:
    _polyglot(tmp_path)
    el.main([str(tmp_path), "--write"])
    index = tmp_path / WIKI / "README.md"
    index.write_text(index.read_text(encoding="utf-8").replace("| serde |", "| serde2 |"),
                     encoding="utf-8", newline="\n")
    assert el.main([str(tmp_path), "--check"]) == 1


def test_dry_run_reports_and_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _polyglot(tmp_path)
    assert el.main([str(tmp_path)]) == 1
    assert not (tmp_path / WIKI).exists(), "a dry run must not write"
    out = capsys.readouterr().out
    assert f"missing: {WIKI}/react.md" in out
    assert "Fix with: python <skill>/scripts/extract_libraries.py --write" in out


def test_custom_directory(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    assert el.main([str(tmp_path), "--write", "--dir", "wiki/deps"]) == 0
    assert (tmp_path / "wiki/deps/axios.md").is_file()
    assert (tmp_path / "wiki/deps/README.md").is_file()
    assert el.main([str(tmp_path), "--check", "--dir", "wiki/deps"]) == 0


# --------------------------------------------------------------------------
# A dependency that disappears
# --------------------------------------------------------------------------

def test_a_removed_dependency_is_flagged_never_deleted(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1", "left-pad": "1"}}))
    el.main([str(tmp_path), "--write"])
    page = _page(tmp_path, "left-pad")
    page.write_text(page.read_text(encoding="utf-8").replace(
        f"## Pitfalls and incidents\n\n{el.GAP}",
        "## Pitfalls and incidents\n\nUnpublished upstream in 2016; build broke."),
        encoding="utf-8", newline="\n")

    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    assert el.main([str(tmp_path), "--check"]) == 1, "a removal is drift"
    assert el.main([str(tmp_path), "--write"]) == 0

    assert page.is_file(), "the page may hold the only record of why - never delete"
    text = page.read_text(encoding="utf-8")
    assert "Unpublished upstream in 2016" in text
    assert "no longer declared" in _block(text)
    assert "**Ecosystem:**" not in _block(text), "stale facts must not survive"

    index = (tmp_path / WIKI / "README.md").read_text(encoding="utf-8")
    assert "- [left-pad](left-pad.md) - no longer declared - review or delete" in index
    assert "| left-pad |" not in index
    assert el.main([str(tmp_path), "--check"]) == 0


def test_a_hand_written_page_for_an_undeclared_library_is_listed_not_touched(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {"axios": "1"}}))
    human = "# libcurl\n\nLinked by the system image.\n"
    page = _write(tmp_path, f"{WIKI}/libcurl.md", human)
    el.main([str(tmp_path), "--write"])
    assert page.read_text(encoding="utf-8") == human
    index = (tmp_path / WIKI / "README.md").read_text(encoding="utf-8")
    assert "- [libcurl](libcurl.md) - no longer declared - review or delete" in index


# --------------------------------------------------------------------------
# Slugs
# --------------------------------------------------------------------------

def test_slugs_are_filesystem_safe() -> None:
    assert el.slugify("@types/node") == "types-node"
    assert el.slugify("github.com/gin-gonic/gin") == "github.com-gin-gonic-gin"
    assert el.slugify("Flask") == "flask"


def test_slug_collisions_are_disambiguated(tmp_path: Path) -> None:
    _write(tmp_path, "package.json", json.dumps({"dependencies": {
        "yaml": "2", "@foo/bar": "1", "foo-bar": "1", "readme": "1"}}))
    _write(tmp_path, "requirements.txt", "yaml\n")
    el.main([str(tmp_path), "--write"])
    names = sorted(p.name for p in (tmp_path / WIKI).glob("*.md"))
    assert "yaml-npm.md" in names and "yaml-python.md" in names
    assert "foo-bar.md" in names and "foo-bar-2.md" in names
    assert "# foo-bar\n" in (tmp_path / WIKI / "foo-bar.md").read_text(encoding="utf-8"), (
        "the name that already is its slug keeps the plain page"
    )
    assert "readme-npm.md" in names, "a library named readme must not overwrite the index"
    index = (tmp_path / WIKI / "README.md").read_text(encoding="utf-8")
    assert index.startswith("# Libraries\n")
    assert el.main([str(tmp_path), "--check"]) == 0


# --------------------------------------------------------------------------
# Generation contract
# --------------------------------------------------------------------------

def test_output_is_deterministic_and_names_no_absolute_path(tmp_path: Path) -> None:
    first, second = tmp_path / "one", tmp_path / "two"
    for root in (first, second):
        _polyglot(root)
    # Build the second tree in a different order: it must not matter.
    (second / "src/lib.rs").unlink()
    _write(second, "src/lib.rs", "use serde::Serialize;\n")

    plan_one, _ = el.plan(first)
    plan_two, _ = el.plan(second)
    rel_one = {p.relative_to(first).as_posix(): c for p, c in plan_one.items()}
    rel_two = {p.relative_to(second).as_posix(): c for p, c in plan_two.items()}
    assert rel_one == rel_two
    assert el.plan(first)[0] == plan_one, "same tree, same output"
    for content in rel_one.values():
        assert str(first) not in content and first.as_posix() not in content


def test_an_empty_repository_gets_an_explicit_index(tmp_path: Path) -> None:
    """Standard-library only is a fact, so it is written down, not left blank."""
    _write(tmp_path, "main.py", "import os\n")
    assert el.main([str(tmp_path), "--check"]) == 1, "a missing index is drift"
    assert el.main([str(tmp_path), "--write"]) == 0
    index = (tmp_path / WIKI / "README.md").read_text(encoding="utf-8")
    assert "## Libraries (0)" in index
    assert "standard-library only" in index
    assert sorted(p.name for p in (tmp_path / WIKI).iterdir()) == ["README.md"]
    assert el.main([str(tmp_path), "--check"]) == 0


def test_not_a_directory_is_an_error(tmp_path: Path) -> None:
    assert el.main([str(tmp_path / "absent")]) == 2


def test_the_generated_wiki_passes_the_coverage_checker(tmp_path: Path) -> None:
    """Checked from the destination (rules/12): the pages land in a host repo,
    so they must not hand that repo a single finding - no dead link, no path
    that is not there, no generated banner naming a generator it lacks."""
    _polyglot(tmp_path)
    _write(tmp_path, "go.mod", (
        "module example.com/app\n\ngo 1.22\n\n"
        "require (\n\tgithub.com/gin-gonic/gin v1.9.1\n\tgopkg.in/yaml.v3 v3.0.1\n)\n"
    ))
    el.main([str(tmp_path), "--write"])
    findings = cov.run_checks(cov.Repo(tmp_path), only=(), skip=(), sample=0)
    ours = [f for f in findings if f.path.startswith(WIKI)]
    assert ours == [], [(f.check, f.path, f.message) for f in ours]


def test_this_repo_declares_no_libraries(repo: Path) -> None:
    """Akinator is stdlib-only, so its own wiki would be the explicit empty index."""
    assert el.libraries(repo) == []

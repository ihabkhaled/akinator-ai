"""Tests for the history wiki generator (extract_history), mutation-style."""

from __future__ import annotations

import json
from pathlib import Path

import extract_history as eh

PAGE = "docs/wiki/history/README.md"


def _w(root: Path, rel: str, content: str = "") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def _page(root: Path) -> str:
    eh.main([str(root), "--write"])
    return (root / PAGE).read_text(encoding="utf-8")


def test_versions_detected_and_removed(tmp_path: Path) -> None:
    p = _w(tmp_path, ".claude-plugin/plugin.json", json.dumps({"version": "3.1.4"}))
    _w(tmp_path, "pyproject.toml", '[project]\nname="x"\nversion = "3.1.4"\n')
    _w(tmp_path, "Cargo.toml", '[package]\nversion = "0.2.0"\n')
    _w(tmp_path, "VERSION", "9.9.9\n")
    text = _page(tmp_path)
    assert "| `.claude-plugin/plugin.json` | `3.1.4` |" in text
    assert "| `pyproject.toml` | `3.1.4` |" in text
    assert "| `Cargo.toml` | `0.2.0` |" in text
    assert "| `VERSION` | `9.9.9` |" in text
    assert "disagree" in text
    p.unlink()
    assert ".claude-plugin/plugin.json" not in _page(tmp_path)


def test_releases_parsed_from_changelog(tmp_path: Path) -> None:
    cl = _w(tmp_path, "CHANGELOG.md",
            "# Changelog\n\nintro\n\n## [2.0.0] - 2026-09-19\n\nBig change here.\n\n"
            "### Added\n\n- x\n\n## [1.0.0] - 2026-08-26\n\n- First release\n")
    text = _page(tmp_path)
    assert "| `2.0.0` | 2026-09-19 | Big change here. |" in text
    assert "| `1.0.0` | 2026-08-26 | First release |" in text
    assert text.index("`2.0.0`") < text.index("`1.0.0`")
    cl.unlink()
    assert "`2.0.0`" not in _page(tmp_path)


def test_manifest_vs_changelog_mismatch_flagged(tmp_path: Path) -> None:
    _w(tmp_path, "VERSION", "1.0.0")
    _w(tmp_path, "CHANGELOG.md", "## [2.0.0] - 2026-01-01\n- a\n")
    assert "manifest differs" in _page(tmp_path)


def test_change_records_newest_first(tmp_path: Path) -> None:
    _w(tmp_path, "docs/changes/2026-01-01-old.md", "# Old thing\n")
    last = _w(tmp_path, "docs/changes/2026-03-01-new.md", "# New thing\n")
    _w(tmp_path, "docs/changes/undated.md", "# Undated\n")
    text = _page(tmp_path)
    assert text.index("New thing") < text.index("Old thing") < text.index("Undated")
    assert "| 2026-03-01 | New thing | `docs/changes/2026-03-01-new.md` |" in text
    last.unlink()
    assert "New thing" not in _page(tmp_path)


def test_decisions_with_status(tmp_path: Path) -> None:
    a = _w(tmp_path, "docs/adr/0001-x.md", "# ADR 1 - X\n\n- **Status:** accepted\n")
    _w(tmp_path, "docs/adr/0002-y.md", "# ADR 2 - Y\n\n## Status\n\nsuperseded\n")
    _w(tmp_path, "docs/adr/0003-z.md", "# ADR 3 - Z\n\nno status\n")
    _w(tmp_path, "docs/adr/README.md", "# index\n")
    text = _page(tmp_path)
    assert "| ADR 1 - X | accepted | `docs/adr/0001-x.md` |" in text
    assert "| ADR 2 - Y | superseded |" in text
    assert "| ADR 3 - Z | unknown |" in text
    assert "index" not in text.split("## Decisions")[1].split("## Ledger")[0]
    a.unlink()
    assert "ADR 1 - X" not in _page(tmp_path)


def test_ledger_counts_and_listed_records(tmp_path: Path) -> None:
    _w(tmp_path, ".ai/ledger/requirement/r1.md",
       "---\nkind: requirement\ntitle: Always on\n---\n\n# Always on\n\n## Status\n\ncurrent\n")
    d = _w(tmp_path, ".ai/ledger/drift/d1.md",
           "---\ntitle: Six to one\n---\n\n# Six to one\n\n## Status\n\nresolved\n")
    _w(tmp_path, ".ai/ledger/failure/f1.md", "# f\n")
    _w(tmp_path, ".ai/ledger/failure/f2.md", "# f2\n")
    text = _page(tmp_path)
    assert "| failure | 2 |" in text and "| requirement | 1 |" in text
    assert "| Always on | current | `.ai/ledger/requirement/r1.md` |" in text
    assert "| Six to one | resolved |" in text
    assert "failure/f1.md" not in text
    d.unlink()
    out = _page(tmp_path)
    assert "Six to one" not in out and "| drift | 0 |" in out


def test_empty_repo_is_honest(tmp_path: Path) -> None:
    text = _page(tmp_path)
    assert text.count(eh.NOTHING) == 5
    assert eh.GAP in text


def test_check_exit_codes(tmp_path: Path) -> None:
    assert eh.main([str(tmp_path), "--check"]) == 1
    assert eh.main([str(tmp_path), "--write"]) == 0
    assert eh.main([str(tmp_path), "--check"]) == 0
    _w(tmp_path, "VERSION", "1.2.3")
    assert eh.main([str(tmp_path), "--check"]) == 1


def test_curated_text_and_crlf_preserved(tmp_path: Path) -> None:
    eh.main([str(tmp_path), "--write"])
    page = tmp_path / PAGE
    text = page.read_bytes().decode("utf-8").replace("\n", "\r\n")
    page.write_bytes(text.replace(eh.GAP, "Curated by hand.").encode("utf-8"))
    _w(tmp_path, "VERSION", "4.0.0")
    eh.main([str(tmp_path), "--write"])
    out = page.read_bytes().decode("utf-8")
    assert "Curated by hand." in out and "4.0.0" in out
    assert "\n" not in out.replace("\r\n", "")


def test_unmarked_page_keeps_text_and_broken_block_exits_2(tmp_path: Path) -> None:
    page = _w(tmp_path, PAGE, "# Mine\n\nhand text\n")
    eh.main([str(tmp_path), "--write"])
    out = page.read_text(encoding="utf-8")
    assert out.startswith("# Mine\n") and out.rstrip().endswith("hand text")
    _w(tmp_path, PAGE, f"# H\n{eh.BEGIN}\nopen\n")
    assert eh.main([str(tmp_path), "--write"]) == 2


def test_deterministic(tmp_path: Path) -> None:
    _w(tmp_path, "docs/changes/2026-01-01-a.md", "# A\n")
    first = _page(tmp_path)
    assert _page(tmp_path) == first

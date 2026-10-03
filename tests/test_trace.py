"""Tests for akinator_trace - every changed path is traced (rule 14).

Per rules/11, each invariant has a positive case and a mutation case proving
the check fires. Temp git repos only; identity is set locally, never globally.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import akinator_trace as trace


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args],
        cwd=root, check=True, capture_output=True,
    )


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "T")
    _git(tmp_path, "config", "user.email", "t@example.invalid")
    _write(tmp_path, "README.md", "# r\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def _check(root: Path, *extra: str) -> int:
    return trace.main(["--root", str(root), "check", *extra])


def test_unaccounted_source_file_fails(repo: Path, capsys) -> None:
    _write(repo, "src/billing.py")
    assert _check(repo) == 1
    assert "src/billing.py" in capsys.readouterr().out


def test_path_named_in_record_in_diff_passes(repo: Path) -> None:
    _write(repo, "src/billing.py")
    _write(repo, "docs/changes/billing.md", "## Files\n\n- `src/billing.py`\n")
    assert _check(repo) == 0


def test_directory_and_glob_mentions_pass(repo: Path) -> None:
    _write(repo, "src/a.py")
    _write(repo, "lib/b.py")
    _write(repo, "docs/changes/x.md", "Touches src/ and\nlib/*.py\n")
    assert _check(repo) == 0


def test_mention_in_record_not_in_diff_fails(repo: Path) -> None:
    _write(repo, "docs/changes/old.md", "- `src/billing.py`\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "record first")
    _write(repo, "src/billing.py")
    assert _check(repo) == 1


def test_none_because_covers_listed_path(repo: Path) -> None:
    _write(repo, "src/a.py")
    _write(
        repo, "docs/changes/n.md",
        "knowledge delta: none, because pure rename with no behavior\n\n- src/a.py\n",
    )
    assert _check(repo) == 0


def test_none_because_does_not_cover_unlisted_path(repo: Path) -> None:
    _write(repo, "src/a.py")
    _write(repo, "src/b.py")
    _write(
        repo, "docs/changes/n.md",
        "knowledge delta: none, because pure rename with no behavior\n- src/a.py\n",
    )
    assert _check(repo) == 1


def test_short_reason_fails(repo: Path) -> None:
    _write(repo, "src/a.py")
    _write(repo, "docs/changes/n.md", "knowledge delta: none, because ok\n- src/a.py\n")
    assert _check(repo) == 1


def test_docs_only_diff_passes(repo: Path) -> None:
    _write(repo, "docs/wiki/page.md")
    _write(repo, "rules/99-x.md")
    _write(repo, "memory/m.md")
    _write(repo, "README.md", "# changed\n")
    assert _check(repo) == 0


def test_empty_diff_passes(repo: Path) -> None:
    assert _check(repo) == 0


def test_bad_ref_exits_2(repo: Path, capsys) -> None:
    assert _check(repo, "--base", "nope-no-such-ref") == 2
    assert "bad base ref" in capsys.readouterr().err


def test_not_a_git_repo_exits_2(tmp_path: Path) -> None:
    # tmp_path is outside any repo only when no parent is one; force it.
    assert trace.main(["--root", str(tmp_path / "missing"), "check"]) == 2


def test_base_ref_diff_unaccounted_fails_then_covered_passes(repo: Path) -> None:
    _write(repo, "src/a.py")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "code")
    assert _check(repo, "--base", "HEAD~1") == 1
    _write(repo, "docs/changes/a.md", "src/a.py\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "record")
    assert _check(repo, "--base", "HEAD~2") == 0


def test_config_ignore_exempts(repo: Path) -> None:
    _write(repo, "vendor/x.py")
    assert _check(repo) == 1
    _write(repo, ".ai/config.json", json.dumps({"trace": {"ignore": ["vendor/**"]}}))
    assert _check(repo) == 0


def test_plan_classifies_homes(repo: Path, capsys) -> None:
    _write(repo, "package.json", "{}")
    _write(repo, "Dockerfile")
    _write(repo, "db/migrations/001.sql")
    _write(repo, "tests/test_a.py")
    assert trace.main(["--root", str(repo), "plan", "--json"]) == 0
    rows = {r["path"]: r["homes"] for r in json.loads(capsys.readouterr().out)["changed"]}
    assert "docs/wiki/libraries" in rows["package.json"]
    assert rows["Dockerfile"] == ["docs/wiki/infra"]
    assert "docs/wiki/data" in rows["db/migrations/001.sql"]
    assert rows["tests/test_a.py"] == ["docs/wiki/testing"]


def test_record_scaffolds_and_never_overwrites(repo: Path, capsys) -> None:
    _write(repo, "src/a.py")
    argv = ["--root", str(repo), "record", "--title", "Add A", "--date", "2026-01-02"]
    assert trace.main(argv) == 0
    rec = repo / "docs" / "changes" / "2026-01-02-add-a.md"
    text = rec.read_text(encoding="utf-8")
    assert "## Files" in text and "src/a.py" in text
    for heading in ("## Before", "## Change", "## Now", "## Why"):
        assert heading in text
    assert _check(repo) == 0
    assert trace.main(argv) == 2
    assert rec.read_text(encoding="utf-8") == text

"""Tests for akinator_context - the cheap reading list (positive + mutation, rule 11)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import akinator_context as ctx


def _w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _w(tmp_path, ".ai/BRIEF.md", "# Brief\n\nThe project in one line.\n")
    _w(tmp_path, "docs/billing.md", "# Billing invoices\n\nInvoices are issued monthly.\n\n- Last verified: 2026-01-01.\n")
    _w(tmp_path, "docs/auth.md", "# Authentication\n\nLogin sessions expire.\n\nSee src/auth/login.py.\n")
    _w(tmp_path, "rules/01-auth-rule.md",
       "# Rule 1 - auth\n\nKeep auth safe.\n\n## Applies to\n\n- src/auth/ only\n")
    _w(tmp_path, "docs/wiki/libraries/requests.md", "# requests\n\nHTTP client decision.\n")
    _w(tmp_path, "src/auth/login.py", "import requests\n")
    return tmp_path


def _names(r: dict) -> list[str]:
    return [p["path"] for p in r["picks"]]


def test_ranking_prefers_matching_page(repo: Path) -> None:
    r = ctx.pack(repo, "fix billing invoices", [], 3000)
    n = _names(r)
    assert n[0] == ".ai/BRIEF.md"
    assert n[1] == "docs/billing.md"
    assert "docs/auth.md" not in n


def test_ranking_mutation_wrong_task_picks_other(repo: Path) -> None:
    n = _names(ctx.pack(repo, "authentication login", [], 3000))
    assert n[1] == "docs/auth.md" and "docs/billing.md" not in n


def test_budget_respected_and_omitted_listed(repo: Path, capsys) -> None:
    _w(repo, "docs/big.md", "# Billing big\n\n" + "billing " * 2000)
    r = ctx.pack(repo, "billing", [], 200)
    assert r["used"] <= 200
    assert "docs/big.md" not in _names(r)
    assert any(o["path"] == "docs/big.md" for o in r["omitted"])
    ctx._print_pack(r)
    assert "left out (" in capsys.readouterr().out


def test_path_boost_and_rule_scope(repo: Path) -> None:
    r = ctx.pack(repo, "zzz", ["src/auth/login.py"], 3000)
    n = _names(r)
    assert "docs/auth.md" in n and "rules/01-auth-rule.md" in n
    assert "docs/billing.md" not in n


def test_cache_hit_avoids_reread_and_invalidates(repo: Path, monkeypatch) -> None:
    ctx.build_index(repo)
    assert (repo / ".ai/cache/.gitignore").read_text().strip() == "*"
    reads: list[str] = []
    real = ctx._read
    monkeypatch.setattr(ctx, "_read", lambda p: (reads.append(p.name), real(p))[1])
    ctx.build_index(repo)
    assert reads == []
    f = repo / "docs/auth.md"
    f.write_text(f.read_text() + "more\n", encoding="utf-8")
    ctx.build_index(repo)
    assert reads == ["auth.md"]
    # mtime-only change also invalidates
    st = f.stat()
    os.utime(f, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
    ctx.build_index(repo)
    assert reads == ["auth.md", "auth.md"]


def test_unwritable_cache_falls_back(repo: Path, monkeypatch) -> None:
    def boom(*a, **k):
        raise OSError("read-only")
    monkeypatch.setattr(Path, "mkdir", boom)
    assert any(e["path"] == "docs/auth.md" for e in ctx.build_index(repo))
    assert not (repo / ".ai/cache").exists()


def test_corrupt_cache_ignored(repo: Path) -> None:
    _w(repo, ".ai/cache/context-index.json", "{not json")
    assert ctx.build_index(repo)


def test_no_subprocess(repo: Path, monkeypatch) -> None:
    def boom(*a, **k):
        raise AssertionError("subprocess used")
    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(subprocess, "Popen", boom)
    assert ctx.pack(repo, "billing", ["src/auth/login.py"], 3000)["picks"]
    ctx.owners(repo, ["src/auth/login.py"])


def test_owners_finds_rule_and_library(repo: Path) -> None:
    rows = ctx.owners(repo, ["src/auth/login.py"])
    kinds = {(r["kind"], r["path"]) for r in rows}
    assert ("rule", "rules/01-auth-rule.md") in kinds
    assert ("library", "docs/wiki/libraries/requests.md") in kinds
    rule = next(r for r in rows if r["kind"] == "rule")
    assert rule["decision"] == "Keep auth safe."
    assert ctx.owners(repo, ["src/billing/x.py"]) == []


def test_stale_requires_today(repo: Path, capsys) -> None:
    with pytest.raises(SystemExit) as e:
        ctx.main(["--root", str(repo), "stale"])
    assert e.value.code == 2


def test_stale_flags_old_only(repo: Path, capsys) -> None:
    assert ctx.main(["--root", str(repo), "stale", "--today", "2026-10-03"]) == 0
    out = capsys.readouterr().out
    assert "docs/billing.md" in out and "2026-01-01" in out
    ctx.main(["--root", str(repo), "stale", "--today", "2026-01-10"])
    assert "docs/billing.md" not in capsys.readouterr().out
    assert ctx.main(["--root", str(repo), "stale", "--today", "bad"]) == 2


def test_budget_and_skips(repo: Path, capsys) -> None:
    _w(repo, "docs/huge.md", "x" * (300 * 1024))
    assert ctx.main(["--root", str(repo), "budget"]) == 0
    out = capsys.readouterr().out
    assert "BRIEF" in out and "dir docs" in out
    assert all(e["path"] != "docs/huge.md" for e in ctx.build_index(repo))
    assert ctx.main(["--root", str(repo / "nope"), "budget"]) == 2

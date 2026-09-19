"""Tests for change-scoping and the interrupt budget.

This is the stage that decides whether the other six get used. If a full pass
costs the same on a typo as on a release, people stop running it - and that is
how this discipline dies in every repository where it dies.

The property that must not break: **scoping never skips a station.** It reports
which stations have work. A quiet station is still run and simply finds nothing.
A scoper that silently drops stations is an exemption engine, and the whole
design collapses into "document when convenient".
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import akinator_ledger as led
import akinator_scope as sc


def _scope_of(paths: list[str], monkeypatch, repo: Path) -> sc.Scope:
    monkeypatch.setattr(sc, "changed_paths", lambda r, a="HEAD": paths)
    return sc.scope(repo)


# --------------------------------------------------------------------------
# Scoping never skips a station
# --------------------------------------------------------------------------

def test_every_station_is_accounted_for(monkeypatch, repo: Path) -> None:
    """Awake plus quiet is always the whole loop. A station that appears in
    neither list has been silently dropped, which is the failure mode."""
    for paths in ([], ["README.md"], ["src/billing/refund.ts"],
                  ["db/migrations/0042.sql", "package.json"]):
        result = _scope_of(paths, monkeypatch, repo)
        assert len(result.woken) + len(result.quiet) == len(sc.STATIONS)
        names = {s.name for s in result.woken} | {s.name for s in result.quiet}
        assert names == {s.name for s in sc.STATIONS}


def test_resolve_and_verify_are_never_scoped_away(monkeypatch, repo: Path) -> None:
    """A pass that skips RESOLVE is guessing, and one that skips VERIFY has no
    evidence. Neither is ever optional, whatever changed."""
    for paths in ([], ["a.lock"], ["README.md"]):
        woken = {s.name for s in _scope_of(paths, monkeypatch, repo).woken}
        assert "RESOLVE" in woken
        assert "VERIFY" in woken


def test_business_wakes_on_money(monkeypatch, repo: Path) -> None:
    woken = {s.name for s in _scope_of(
        ["src/billing/refund.ts"], monkeypatch, repo).woken}
    assert "BUSINESS" in woken


def test_business_stays_quiet_on_a_readme(monkeypatch, repo: Path) -> None:
    result = _scope_of(["README.md"], monkeypatch, repo)
    assert "BUSINESS" in {s.name for s in result.quiet}
    assert "DOCUMENT" in {s.name for s in result.woken}


def test_ops_wakes_on_a_migration(monkeypatch, repo: Path) -> None:
    woken = {s.name for s in _scope_of(
        ["db/migrations/0042_add_column.sql"], monkeypatch, repo).woken}
    assert "OPS" in woken


def test_ops_wakes_on_a_lockfile(monkeypatch, repo: Path) -> None:
    """A dependency change is an operational consequence: it needs a rebuild,
    not a restart, and the layer cache will otherwise serve the old set."""
    woken = {s.name for s in _scope_of(
        ["package-lock.json"], monkeypatch, repo).woken}
    assert "OPS" in woken


def test_contextify_wakes_on_a_manifest(monkeypatch, repo: Path) -> None:
    woken = {s.name for s in _scope_of(["pyproject.toml"], monkeypatch, repo).woken}
    assert "CONTEXTIFY" in woken


def test_rule_wakes_only_on_rules(monkeypatch, repo: Path) -> None:
    assert "RULE" in {s.name for s in _scope_of(
        ["rules/12-new.md"], monkeypatch, repo).woken}
    assert "RULE" in {s.name for s in _scope_of(
        ["README.md"], monkeypatch, repo).quiet}


def test_product_wakes_on_a_route(monkeypatch, repo: Path) -> None:
    woken = {s.name for s in _scope_of(
        ["services/api/routes/export.ts"], monkeypatch, repo).woken}
    assert "PRODUCT" in woken


# --------------------------------------------------------------------------
# Trivial changes
# --------------------------------------------------------------------------

def test_a_lockfile_only_change_is_marked_trivial(monkeypatch, repo: Path) -> None:
    result = _scope_of(["yarn.lock"], monkeypatch, repo)
    assert result.trivial


def test_trivial_does_not_mean_skipped(monkeypatch, repo: Path) -> None:
    """The batch still runs every station and records an explicit empty delta.
    'Trivial' describes the work found, not permission to skip looking."""
    result = _scope_of(["logo.png"], monkeypatch, repo)
    assert result.trivial
    assert len(result.woken) + len(result.quiet) == len(sc.STATIONS)
    assert {"RESOLVE", "VERIFY"} <= {s.name for s in result.woken}


def test_a_real_change_alongside_a_lockfile_is_not_trivial(
    monkeypatch, repo: Path
) -> None:
    result = _scope_of(["yarn.lock", "src/billing/refund.ts"], monkeypatch, repo)
    assert not result.trivial
    assert "BUSINESS" in {s.name for s in result.woken}


# --------------------------------------------------------------------------
# The interrupt budget
# --------------------------------------------------------------------------

def test_default_budget_is_fifteen() -> None:
    """The owner wants many questions per prompt (ADR 0010) - grouped into one
    message, ranked, each with a recommended default."""
    assert sc.DEFAULT_INTERRUPT_BUDGET == 15


def test_budget_is_configurable(tmp_path: Path) -> None:
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "config.json").write_text(
        json.dumps({"interrupt_budget": 2}), encoding="utf-8"
    )
    assert sc.interrupt_budget(tmp_path) == 2


def test_a_malformed_config_falls_back_to_the_default(tmp_path: Path) -> None:
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "config.json").write_text("{ broken", encoding="utf-8")
    assert sc.interrupt_budget(tmp_path) == sc.DEFAULT_INTERRUPT_BUDGET


def _pending(root: Path, count: int) -> None:
    ledger = led.Ledger(root)
    for index in range(count):
        ledger.write(led.Record(
            kind="failure", id=f"pending-{index:03d}-00000",
            title=f"failure number {index}",
            fields={"symptom": "s", "trigger": "t", "root_cause": "r", "fix": "f"},
            occurrences=[f"2026-08-{index + 1:02d} (self-report)",
                         f"2026-09-{index + 1:02d} (git)"],
            sources=["self-report", "git"],
        ))


def test_questions_are_batched_to_the_budget(tmp_path: Path) -> None:
    root = tmp_path / "many"
    root.mkdir()
    _pending(root, 9)

    ask, defer = sc.batched(root, limit=5)
    assert len(ask) == 5
    assert len(defer) == 4
    assert len(ask) + len(defer) == 9, "deferred is not dropped"


def test_deferred_questions_are_kept_not_discarded(tmp_path: Path) -> None:
    root = tmp_path / "kept"
    root.mkdir()
    _pending(root, 7)
    ask, defer = sc.batched(root, limit=3)
    assert {q.text for q in ask}.isdisjoint({q.text for q in defer})
    assert len(sc.pending_questions(root)) == 7


def test_a_decided_recurrence_is_not_asked_again(tmp_path: Path) -> None:
    """The whole point of recording 'neither'."""
    root = tmp_path / "decided"
    root.mkdir()
    _pending(root, 1)
    assert sc.pending_questions(root)

    led.Ledger(root).write(led.Record(
        kind="decision", id="distil-pending-000-00000",
        title="decided", fields={"what": "w", "alternatives": "a", "why": "y"},
    ))
    assert not sc.pending_questions(root)


def test_more_occurrences_rank_a_question_higher(tmp_path: Path) -> None:
    root = tmp_path / "ranked"
    root.mkdir()
    ledger = led.Ledger(root)
    for name, count in (("twice-0000000000", 2), ("five-00000000000", 5)):
        ledger.write(led.Record(
            kind="failure", id=name, title=f"seen {count}",
            fields={"symptom": "s", "trigger": "t", "root_cause": "r", "fix": "f"},
            occurrences=[f"2026-08-{i + 1:02d} (self-report)" for i in range(count)],
            sources=["self-report"],
        ))
    ranked = sc.pending_questions(root)
    assert "seen 5" in ranked[0].text


def test_this_repo_has_no_unanswered_questions(repo: Path) -> None:
    """Akinator must not ship a backlog of its own unanswered questions."""
    ask, defer = sc.batched(repo)
    assert not ask and not defer, [q.text for q in ask + defer]

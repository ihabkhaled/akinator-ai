"""Tests for rule evolution and conflict detection.

Rule 11 applies to these detectors: a clean report on a healthy tree is not
evidence, so every detector here is proved to fire on a tree that violates it.

The property that carries the design: **a superseded rule is never deleted.**
Deleting it deletes the reason the replacement is shaped the way it is, which is
the only part a future reader cannot reconstruct from the code.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import akinator_ledger as led
import akinator_rules as ar


def _rule(root: Path, number: str, title: str, mandates: list[str],
          meta: str = "") -> Path:
    (root / "rules").mkdir(parents=True, exist_ok=True)
    path = root / "rules" / f"{number}-{title.lower().replace(' ', '-')[:30]}.md"
    front = f"---\n{meta}\n---\n\n" if meta else ""
    body = (
        f"# Rule {number} - {title}\n\n"
        "## Purpose\n\nSomething expensive breaks otherwise.\n\n"
        "## Applies to\n\nThe scope above.\n\n"
        "## Mandatory rules\n\n"
        + "\n".join(f"{i + 1}. {m}" for i, m in enumerate(mandates))
        + "\n\n## Enforcement\n\n- Mechanism: `tests/t.py`\n"
    )
    path.write_text(front + body, encoding="utf-8", newline="\n")
    return path


# --------------------------------------------------------------------------
# Parsing - optional frontmatter, absent on every v1 rule
# --------------------------------------------------------------------------

def test_a_rule_without_frontmatter_still_parses(tmp_path: Path) -> None:
    """Every v1 rule has no frontmatter and must keep working unchanged."""
    _rule(tmp_path, "01", "plain", ["Do the thing."])
    rules = ar.load_rules(tmp_path)
    assert len(rules) == 1
    assert rules[0].number == "01"
    assert rules[0].scope == ""
    assert rules[0].caused == []
    assert rules[0].mandates() == ["1. Do the thing."]


def test_frontmatter_fields_are_read(tmp_path: Path) -> None:
    _rule(tmp_path, "07", "scoped", ["Never write directly."],
          meta='id: 07\nscope: "src/billing/**"\nsupersedes: [04]\n'
               "caused: [failure/xyz]")
    rule = ar.load_rules(tmp_path)[0]
    assert rule.rid == "07"
    assert rule.scope == "src/billing/**"
    assert rule.supersedes == ["04"]
    assert rule.caused == ["failure/xyz"]


def test_this_repo_rules_all_parse(repo: Path) -> None:
    rules = ar.load_rules(repo)
    assert len(rules) >= 11
    for rule in rules:
        assert rule.mandates(), f"{rule.path.name} has no parsed mandates"


# --------------------------------------------------------------------------
# Conflict detection - proved to fire
# --------------------------------------------------------------------------

def test_detects_two_rules_that_disagree_over_one_scope(tmp_path: Path) -> None:
    """Opposite polarity, same subject, overlapping scope."""
    root = tmp_path / "conflict"
    _rule(root, "01", "must migrate",
          ["Every migration must run inside a single transaction boundary."],
          meta='id: 01\nscope: "db/**"')
    _rule(root, "02", "must not migrate",
          ["A migration must never run inside a single transaction boundary."],
          meta='id: 02\nscope: "db/**"')

    conflicts = ar.find_conflicts(root)
    assert conflicts, "opposed mandates over one scope must be reported"
    assert {conflicts[0].left.number, conflicts[0].right.number} == {"01", "02"}


def test_disjoint_scopes_do_not_conflict(tmp_path: Path) -> None:
    root = tmp_path / "disjoint"
    _rule(root, "01", "billing",
          ["Every migration must run inside a single transaction boundary."],
          meta='id: 01\nscope: "src/billing/**"')
    _rule(root, "02", "items",
          ["A migration must never run inside a single transaction boundary."],
          meta='id: 02\nscope: "src/items/**"')
    assert not ar.find_conflicts(root)


def test_agreeing_mandates_do_not_conflict(tmp_path: Path) -> None:
    """Same polarity is agreement, however similar the wording."""
    root = tmp_path / "agree"
    _rule(root, "01", "a",
          ["Every migration must run inside a single transaction boundary."],
          meta='id: 01\nscope: "db/**"')
    _rule(root, "02", "b",
          ["Every migration must hold a single transaction boundary open."],
          meta='id: 02\nscope: "db/**"')
    assert not ar.find_conflicts(root)


def test_a_superseded_rule_is_excluded_from_conflicts(tmp_path: Path) -> None:
    """The chain is kept for its history, not re-litigated as a live rule."""
    root = tmp_path / "superseded"
    _rule(root, "01", "old",
          ["Every migration must run inside a single transaction boundary."],
          meta="id: 01\nscope: \"db/**\"\nsuperseded_by: 02")
    _rule(root, "02", "new",
          ["A migration must never run inside a single transaction boundary."],
          meta='id: 02\nscope: "db/**"\nsupersedes: [01]')
    assert not ar.find_conflicts(root)


def test_an_unscoped_rule_overlaps_everything(tmp_path: Path) -> None:
    """Conservative on purpose: a wrongly reported conflict is dismissed by a
    human, a missed one is invisible."""
    assert ar.scopes_overlap("", "src/billing/**")
    assert ar.scopes_overlap("src/billing/**", "")
    assert ar.scopes_overlap("db/**", "db/**")
    assert not ar.scopes_overlap("src/billing/**", "src/items/**")


def test_this_repo_has_no_rule_conflicts(repo: Path) -> None:
    conflicts = ar.find_conflicts(repo)
    assert not conflicts, [
        f"{c.left.number} vs {c.right.number}: {c.detail}" for c in conflicts
    ]


# --------------------------------------------------------------------------
# Evolution - the mechanism the whole stage exists for
# --------------------------------------------------------------------------

@pytest.fixture
def repo_where_a_rule_caused_a_failure(tmp_path: Path) -> Path:
    root = tmp_path / "evolve"
    _rule(root, "07", "single writer",
          ["Quota is written only inside applyQuota."],
          meta='id: 07\nscope: "src/quota/**"')

    led.Ledger(root).write(led.Record(
        kind="failure", id="backfill-blocked-000",
        title="an offline backfill could not run",
        fields={
            "symptom": "the backfill took eight hours and timed out",
            "trigger": "routing a bulk write through the single-writer path",
            "root_cause": "applyQuota takes a row lock per row, which is right "
                          "online and catastrophic for a backfill",
            "fix": "allow a documented exception for offline migrations",
        },
        occurrences=["2026-09-01 (self-report)"], sources=["self-report"],
    ))
    return root


def test_marking_a_rule_as_having_caused_a_failure(
    repo_where_a_rule_caused_a_failure: Path
) -> None:
    root = repo_where_a_rule_caused_a_failure
    assert not ar.rules_awaiting_evolution(root)

    ar.mark_caused(root, "07", "backfill-blocked-000")

    pending = ar.rules_awaiting_evolution(root)
    assert [r.number for r in pending] == ["07"]
    assert pending[0].caused == ["backfill-blocked-000"]


def test_marking_preserves_the_rule_body(
    repo_where_a_rule_caused_a_failure: Path
) -> None:
    """Frontmatter is added; the prose a human wrote is untouched."""
    root = repo_where_a_rule_caused_a_failure
    before = ar.load_rules(root)[0].body
    ar.mark_caused(root, "07", "backfill-blocked-000")
    assert ar.load_rules(root)[0].body == before


def test_the_evolution_brief_states_both_sides(
    repo_where_a_rule_caused_a_failure: Path
) -> None:
    """A rule that only fixes the second failure reintroduces the first, and a
    rule that only keeps the first is what caused the second. The brief has to
    put both in front of whoever writes the replacement."""
    root = repo_where_a_rule_caused_a_failure
    ar.mark_caused(root, "07", "backfill-blocked-000")
    rule = ar.rules_awaiting_evolution(root)[0]

    brief = ar.evolution_brief(root, rule)
    assert "What it protects" in brief
    assert "Quota is written only inside applyQuota" in brief
    assert "What its enforcement caused" in brief
    assert "an offline backfill could not run" in brief
    assert "row lock per row" in brief
    assert "satisfy both" in brief
    assert "supersedes" in brief


def test_the_brief_says_the_superseded_rule_stays(
    repo_where_a_rule_caused_a_failure: Path
) -> None:
    """Deleting it deletes the reason the replacement is shaped as it is - the
    one part a future reader cannot reconstruct."""
    root = repo_where_a_rule_caused_a_failure
    ar.mark_caused(root, "07", "backfill-blocked-000")
    brief = ar.evolution_brief(root, ar.rules_awaiting_evolution(root)[0])
    assert "stays" in brief.lower()
    assert "deleting it deletes the reason" in brief.lower()


def test_marking_an_unknown_rule_is_an_error(tmp_path: Path) -> None:
    _rule(tmp_path, "01", "x", ["Do the thing."])
    with pytest.raises(SystemExit):
        ar.mark_caused(tmp_path, "99", "some-fingerprint")


def test_this_repo_has_no_rule_awaiting_evolution(repo: Path) -> None:
    pending = ar.rules_awaiting_evolution(repo)
    assert not pending, [r.number for r in pending]

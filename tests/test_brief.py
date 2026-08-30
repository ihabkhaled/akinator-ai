"""Tests for the context brief.

The brief is the answer to the conflict v1 never resolved: "document every
needle" is a write problem, "a new chat knows everything in seconds" is a
retrieval problem, and optimizing the first degrades the second.

Two properties carry the whole design, and both are tested by forcing the
condition rather than by reading the code:

  1. **The cap never slips.** A budget that is allowed to overflow is not a
     budget, and every other claim rests on this one.
  2. **Overflow demotes, never drops.** A corpus item that does not fit becomes
     a pointer. Dropping it would make the brief a lie by omission.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import akinator_ledger as led
import build_brief as bb


# --------------------------------------------------------------------------
# Budget - the non-negotiable one
# --------------------------------------------------------------------------

def test_section_shares_sum_to_one() -> None:
    """A section table that does not add up is a cap that silently slips."""
    assert abs(sum(share for _, _, share in bb.SECTIONS) - 1.0) < 1e-9


def test_tiers_are_ordered_and_named() -> None:
    assert bb.TIERS["lean"] < bb.TIERS["standard"] < bb.TIERS["deep"]
    assert bb.DEFAULT_TIER in bb.TIERS
    assert bb.TIERS["standard"] == 12_000


def test_token_estimate_is_pessimistic() -> None:
    """An estimate that runs low would let the brief overflow in the one place
    that must not. Four characters per token, rounded up."""
    assert bb.tokens("") == 0
    assert bb.tokens("a") == 1
    assert bb.tokens("a" * 400) == 100


def test_this_repo_brief_is_within_budget(repo: Path) -> None:
    brief, index = bb.compose(repo)
    assert index["used"] <= index["budget"], (
        f"the brief is {index['used']} tokens against a budget of "
        f"{index['budget']}"
    )
    assert bb.tokens(brief) == index["used"]


def test_an_unknown_tier_is_rejected(tmp_path: Path) -> None:
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "config.json").write_text(
        json.dumps({"brief_tier": "enormous"}), encoding="utf-8"
    )
    with pytest.raises(SystemExit) as excinfo:
        bb.budget_for(tmp_path)
    assert "unknown brief tier" in str(excinfo.value)


def test_config_selects_the_tier(tmp_path: Path) -> None:
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "config.json").write_text(
        json.dumps({"brief_tier": "lean"}), encoding="utf-8"
    )
    tier, budget = bb.budget_for(tmp_path)
    assert (tier, budget) == ("lean", 4_000)


# --------------------------------------------------------------------------
# Overflow demotes rather than drops
# --------------------------------------------------------------------------

def _repo_with_many_rules(root: Path, count: int) -> Path:
    (root / "rules").mkdir(parents=True, exist_ok=True)
    for index in range(count):
        (root / "rules" / f"{index:02d}-rule.md").write_text(
            f"# Rule {index:02d} - a constraint that must not be broken\n\n"
            + ("Something specific breaks when this is violated, and the "
               "consequence is expensive enough to write down. " * 6)
            + "\n\n## Enforcement\n\n- Mechanism: `tests/t.py`\n",
            encoding="utf-8",
        )
    (root / ".ai").mkdir(exist_ok=True)
    (root / ".ai" / "config.json").write_text(
        json.dumps({"brief_tier": "lean", "brief_budget": 900}), encoding="utf-8"
    )
    return root


def test_overflow_demotes_to_pointers_and_drops_nothing(tmp_path: Path) -> None:
    """The condition this repo's own corpus is too small to reach."""
    root = _repo_with_many_rules(tmp_path / "big", 40)
    brief, index = bb.compose(root)

    in_brief = [i for i in index["items"] if i["in_brief"]]
    pointers = [i for i in index["items"] if not i["in_brief"]]

    assert pointers, "with 40 rules against a 900-token budget, some must demote"
    assert in_brief, "the budget must still admit the highest-value items"
    assert len(in_brief) + len(pointers) == 40, "nothing may be dropped"

    assert "Everything else, by pointer" in brief

    # The contract is: the brief is capped, the INDEX is complete. Pointers are
    # budgeted too - an unbudgeted pointer list blew the very cap it existed to
    # protect - so a pointer that does not fit is summarized into a count here
    # and still carried in full by the index.
    listed = [i for i in pointers if i["path"] in brief]
    assert listed, "the pointer section must list what it can afford"
    if len(listed) < len(pointers):
        assert "and" in brief and "more, ranked by value" in brief, (
            "a summarized tail must say how many were summarized"
        )


def test_the_index_carries_every_item_even_when_the_brief_cannot(
    tmp_path: Path,
) -> None:
    """Nothing is dropped. The brief is capped; the index is complete."""
    root = _repo_with_many_rules(tmp_path / "complete", 40)
    _, index = bb.compose(root)
    assert len(index["items"]) == 40
    assert all(entry["path"] for entry in index["items"])


def test_overflow_keeps_the_highest_value_items(tmp_path: Path) -> None:
    root = _repo_with_many_rules(tmp_path / "ranked", 40)
    _, index = bb.compose(root)

    kept = [i["score"] for i in index["items"] if i["in_brief"]]
    demoted = [i["score"] for i in index["items"] if not i["in_brief"]]
    if kept and demoted:
        assert min(kept) >= max(demoted), (
            "a lower-value item was kept over a higher-value one"
        )


def test_the_generator_refuses_to_emit_an_over_budget_brief(
    tmp_path: Path, monkeypatch
) -> None:
    """A cap that is allowed to slip is not a cap."""
    root = _repo_with_many_rules(tmp_path / "tiny", 60)
    (root / ".ai" / "config.json").write_text(
        json.dumps({"brief_tier": "lean", "brief_budget": 120}), encoding="utf-8"
    )
    with pytest.raises(SystemExit) as excinfo:
        bb.compose(root)
    assert "over the" in str(excinfo.value)
    assert "refuses" in str(excinfo.value)


# --------------------------------------------------------------------------
# Value ranking
# --------------------------------------------------------------------------

def test_recurrence_raises_a_failure_above_a_rule(tmp_path: Path) -> None:
    """A failure seen three times will happen a fourth. That is exactly what a
    session needs warning about before it starts, so it must outrank a rule."""
    root = tmp_path / "ranking"
    (root / "rules").mkdir(parents=True)
    (root / "rules" / "01-x.md").write_text(
        "# Rule 01 - a constraint\n\nWhy.\n\n## Enforcement\n\n- Mechanism: `t.py`\n",
        encoding="utf-8",
    )
    ledger = led.Ledger(root)
    ledger.write(led.Record(
        kind="failure", id="thrice-000000000",
        title="a thing that keeps breaking",
        fields={"symptom": "s", "trigger": "t", "root_cause": "r", "fix": "f"},
        occurrences=["2026-08-01 (self-report)", "2026-08-10 (git)",
                     "2026-08-20 (ci)"],
        sources=["self-report", "git", "ci"],
    ))

    failures = bb.collect_failures(root)
    rules = bb.collect_constraints(root)
    assert failures[0].score > rules[0].score


def test_an_unenforced_rule_scores_below_an_enforced_one(tmp_path: Path) -> None:
    """A rule with no live mechanism will be broken, so it is worth less in a
    brief than one that cannot be."""
    root = tmp_path / "enforcement"
    (root / "rules").mkdir(parents=True)
    (root / "rules" / "01-enforced.md").write_text(
        "# Rule 01 - enforced\n\nWhy.\n\n## Enforcement\n\n- Mechanism: `t.py`\n",
        encoding="utf-8",
    )
    (root / "rules" / "02-prose.md").write_text(
        "# Rule 02 - prose only\n\nWhy.\n", encoding="utf-8"
    )
    by_title = {i.title: i.score for i in bb.collect_constraints(root)}
    assert by_title["Rule 01 - enforced"] > by_title["Rule 02 - prose only"]


def test_value_formula_is_multiplicative() -> None:
    """Any factor at zero zeroes the item. A doc nobody would ever re-derive is
    worth nothing however large its blast radius."""
    assert bb.value(0.0, 1.0, 1.0) == 0.0
    assert bb.value(1.0, 1.0, 1.0) == 1.0
    assert bb.value(0.5, 0.5, 1.0) < bb.value(0.9, 0.9, 1.0)


# --------------------------------------------------------------------------
# Content and determinism
# --------------------------------------------------------------------------

def test_brief_carries_every_section_heading(repo: Path) -> None:
    brief, _ = bb.compose(repo)
    for _, heading, _share in bb.SECTIONS:
        if heading in ("Everything else, by pointer",):
            continue
        assert heading in brief or "_nothing recorded yet_" in brief


def test_brief_declares_itself_generated(repo: Path) -> None:
    brief, _ = bb.compose(repo)
    assert brief.startswith("<!--")
    assert "DO NOT EDIT BY HAND" in brief
    assert "build_brief.py" in brief


def test_composition_is_deterministic(repo: Path) -> None:
    assert bb.compose(repo)[0] == bb.compose(repo)[0]


def test_brief_is_not_drifted(repo: Path) -> None:
    """Akinator must not ship a stale brief - it is the one file a new session
    is guaranteed to read."""
    for rel, content in bb.plan(repo).items():
        path = repo / rel
        assert path.is_file(), f"{rel} is missing - run build_brief.py --write"
        assert path.read_text(encoding="utf-8") == content, (
            f"{rel} is drifted. Fix with: python scripts/build_brief.py --write"
        )


def test_index_accounts_for_every_item(repo: Path) -> None:
    _, index = bb.compose(repo)
    assert index["items"], "the index must list what was ranked"
    for entry in index["items"]:
        assert set(entry) >= {
            "section", "title", "path", "score", "tokens", "tags", "in_brief"
        }
        assert entry["tokens"] > 0


def test_recurring_failures_reach_the_brief(repo: Path) -> None:
    """The learning loop is worthless if what it learns never surfaces."""
    brief, _ = bb.compose(repo)
    recurring = led.Ledger(repo).recurring()
    assert recurring, "this repo's ledger should have recurring failures"
    for record in recurring:
        assert record.id in brief, (
            f"{record.id} recurs but does not appear in the brief"
        )


def test_a_truncated_failure_field_ends_with_a_marker(tmp_path: Path) -> None:
    """A cut sentence with no marker is indistinguishable from a complete one.

    `bb._clip(text, 180)[:180]` used to be a bare slice with no ellipsis, so a
    fix field over 180 characters silently lost its tail with nothing telling
    the reader it had been cut - discovered when a real ledger record's Fix
    field (227 characters) hit this path and .ai/BRIEF.md ended mid-sentence.
    """
    long_fix = "x" * 250
    assert bb._clip(long_fix, 180) == ("x" * 180) + "..."

    short_fix = "a short fix"
    assert bb._clip(short_fix, 180) == short_fix, "must not add a marker unearned"

    root = tmp_path / "long-field"
    root.mkdir()
    ledger = led.Ledger(root)
    ledger.write(led.Record(
        kind="failure", id="long-fix-field-000000",
        title="a failure whose fix field is long",
        fields={"symptom": "s", "trigger": "t", "root_cause": "r",
                "fix": long_fix},
        occurrences=["2026-08-01 (self-report)"],
    ))
    items = bb.collect_failures(root)
    assert items[0].body.rstrip().endswith("..."), (
        "a truncated field reached the brief with no ellipsis"
    )

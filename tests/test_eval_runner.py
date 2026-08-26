"""Tests for the behavioral eval runner.

An eval harness that silently mis-parses a suite is worse than none: it runs
something, produces a transcript, and grades a prompt nobody wrote. The first
version of this runner did exactly that - it merged a session prompt with the
answer the operator was meant to give, and it could not see the five-prompt
red-team suite at all. Both failures are pinned here.

No agent is invoked. These tests cover parsing, workspace isolation and the
result format; actually running a suite needs an agent CLI and is a manual or CI
step (`python scripts/run_evals.py --all --grade --stamp YYYY-MM-DD`).
"""

from __future__ import annotations

from pathlib import Path

import pytest

import run_evals


@pytest.fixture(scope="module")
def suites() -> list[run_evals.Suite]:
    return run_evals.load_suites()


@pytest.fixture(scope="module")
def by_slug(suites: list[run_evals.Suite]) -> dict[str, run_evals.Suite]:
    return {s.slug: s for s in suites}


# --------------------------------------------------------------------------
# Every suite is runnable
# --------------------------------------------------------------------------

def test_all_suites_are_runnable(suites: list[run_evals.Suite]) -> None:
    """A suite the runner cannot execute is documentation pretending to be a test."""
    broken = [s.slug for s in suites if not run_evals.runnable(s)]
    assert not broken, (
        f"suites the runner cannot execute: {broken}. Each needs a ```prompt "
        "fence and a **Fixture:** line naming a directory that exists."
    )


def test_the_six_evals_are_present(by_slug: dict[str, run_evals.Suite]) -> None:
    """Part 17 specifies six behavioral evals. All six, numbered without gaps."""
    expected = {
        "01-silent-change", "02-repeated-question", "03-business-void",
        "04-newcomer", "05-gate-economy", "06-anti-gaming",
    }
    assert expected <= set(by_slug), f"missing: {sorted(expected - set(by_slug))}"


def test_suite_numbering_has_no_gaps(suites: list[run_evals.Suite]) -> None:
    numbers = sorted(int(s.slug.split("-", 1)[0]) for s in suites)
    assert numbers == list(range(1, len(numbers) + 1)), (
        f"suite numbering has a gap: {numbers}. A gap reads as a missing file."
    )


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def test_every_suite_names_a_fixture_that_exists(
    suites: list[run_evals.Suite],
) -> None:
    for suite in suites:
        assert suite.fixture, f"{suite.slug} names no fixture"
        assert suite.fixture_path.is_dir(), (
            f"{suite.slug} names fixture '{suite.fixture}', which does not exist"
        )


def test_every_suite_has_a_rubric_and_checklists(
    suites: list[run_evals.Suite],
) -> None:
    for suite in suites:
        assert suite.rubric, f"{suite.slug} has no Rubric section to grade against"
        assert suite.must, f"{suite.slug} lists no must-do items"
        assert suite.must_not, f"{suite.slug} lists no must-not-do items"


def test_multi_step_suites_parse_every_step(
    by_slug: dict[str, run_evals.Suite],
) -> None:
    """Regression: the red-team suite's five prompts were invisible."""
    assert len(by_slug["06-anti-gaming"].prompts) == 5
    assert len(by_slug["02-repeated-question"].prompts) == 2
    assert len(by_slug["04-newcomer"].prompts) == 5


def test_single_step_suites_have_exactly_one_prompt(
    by_slug: dict[str, run_evals.Suite],
) -> None:
    for slug in ("01-silent-change", "03-business-void", "05-gate-economy"):
        assert len(by_slug[slug].prompts) == 1


def test_prompt_does_not_absorb_surrounding_prose(
    by_slug: dict[str, run_evals.Suite],
) -> None:
    """Regression: prompts were once inferred from blockquotes and picked up
    the operator's instructions along with the prompt."""
    for suite in by_slug.values():
        for prompt in suite.prompts:
            assert "Must" not in prompt
            assert "Rubric" not in prompt
            assert not prompt.lstrip().startswith(">")
            assert "```" not in prompt


def test_checklists_reach_subsection_items(
    by_slug: dict[str, run_evals.Suite],
) -> None:
    """The red-team suite states its requirements as inline **Must:** labels."""
    suite = by_slug["06-anti-gaming"]
    assert len(suite.must) >= 5
    assert len(suite.must_not) >= 4


# --------------------------------------------------------------------------
# Workspace isolation
# --------------------------------------------------------------------------

def test_workspace_is_a_copy_not_the_fixture(
    by_slug: dict[str, run_evals.Suite], tmp_path: Path, monkeypatch
) -> None:
    """Evals must never mutate a fixture: the rotten one has to stay rotten."""
    monkeypatch.setattr(run_evals, "RESULTS_DIR", tmp_path)
    suite = by_slug["05-gate-economy"]

    workspace = run_evals.make_workspace(suite, "2026-08-26")
    assert workspace.is_dir()
    assert workspace != suite.fixture_path
    assert (workspace / "README.md").is_file()

    (workspace / "NEW.md").write_text("agent output\n", encoding="utf-8")
    assert not (suite.fixture_path / "NEW.md").exists(), (
        "a run wrote into the fixture itself"
    )


def test_workspace_is_reset_between_runs(
    by_slug: dict[str, run_evals.Suite], tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(run_evals, "RESULTS_DIR", tmp_path)
    suite = by_slug["01-silent-change"]

    first = run_evals.make_workspace(suite, "2026-08-26")
    (first / "leftover.md").write_text("stale\n", encoding="utf-8")

    second = run_evals.make_workspace(suite, "2026-08-26")
    assert not (second / "leftover.md").exists(), (
        "a stale workspace would let one run grade another run's output"
    )


def test_workspace_diff_reports_what_changed(
    by_slug: dict[str, run_evals.Suite], tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(run_evals, "RESULTS_DIR", tmp_path)
    suite = by_slug["01-silent-change"]
    workspace = run_evals.make_workspace(suite, "2026-08-26")

    assert run_evals.workspace_diff(suite.fixture_path, workspace) == []

    (workspace / "docs").mkdir(exist_ok=True)
    (workspace / "docs" / "product.md").write_text("intent\n", encoding="utf-8")
    (workspace / "README.md").write_text("changed\n", encoding="utf-8")

    diff = run_evals.workspace_diff(suite.fixture_path, workspace)
    assert "+ docs/product.md" in diff
    assert "~ README.md" in diff


# --------------------------------------------------------------------------
# Result format
# --------------------------------------------------------------------------

def test_result_records_prompts_diff_and_verdict(
    by_slug: dict[str, run_evals.Suite], tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(run_evals, "RESULTS_DIR", tmp_path)
    suite = by_slug["02-repeated-question"]

    path = run_evals.write_result(
        suite, "2026-08-26", "a transcript",
        ["+ docs/product/bulk-delete.md"],
        {"grade": "partial", "missing": ["no citation in session 2"],
         "note": "applied the rule but cited nothing"},
    )

    text = path.read_text(encoding="utf-8")
    assert "**Grade: partial**" in text
    assert "no citation in session 2" in text
    assert "+ docs/product/bulk-delete.md" in text
    assert "## Prompt 1" in text and "## Prompt 2" in text
    assert "a transcript" in text


def test_grader_prompt_forbids_grading_on_effort() -> None:
    """The rubric the grader is given must rule out activity-as-evidence."""
    text = run_evals.GRADER_PROMPT.lower()
    assert "confident" in text and "fail" in text
    assert "effort" in text
    assert "{changes}" in run_evals.GRADER_PROMPT

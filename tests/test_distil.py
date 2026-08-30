"""Tests for distil - turning what recurs into a rule proposal.

The property that matters is not "does it find things" but **does it stop asking
once answered**. A loop that re-raises a decided question is a loop people
disable, and then nothing is learned at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import akinator_distil as dis
import akinator_ledger as led


@pytest.fixture
def repo_with_recurrence(tmp_path: Path) -> tuple[Path, led.Record]:
    root = tmp_path / "recurring"
    root.mkdir()
    ledger = led.Ledger(root)
    record = led.Record(
        kind="failure",
        id="stale-image-000000",
        title="the service served stale data after a restart",
        fields={
            "symptom": "responses contained rows from before the migration",
            "trigger": "a restart instead of a rebuild",
            "root_cause": "the old image cached the schema",
            "fix": "drop the container and rebuild, then migrate",
            "module": "services/api",
            "operation": "deploy",
        },
        occurrences=["2026-08-14 (self-report)", "2026-08-26 (git)"],
        sources=["self-report", "git"],
    )
    ledger.write(record)
    return root, record


# --------------------------------------------------------------------------
# The threshold
# --------------------------------------------------------------------------

def test_threshold_is_two() -> None:
    """Once is an incident; twice is a pattern. A rule from one incident
    overfits, gets suppressed, and becomes noise."""
    assert dis.THRESHOLD == 2


def test_a_single_occurrence_does_not_reach_the_threshold(tmp_path: Path) -> None:
    root = tmp_path / "once"
    root.mkdir()
    led.Ledger(root).write(led.Record(
        kind="failure", id="seen-once-0000000", title="a one-off",
        fields={"symptom": "s", "trigger": "t", "root_cause": "r", "fix": "f"},
        occurrences=["2026-08-26 (self-report)"], sources=["self-report"],
    ))
    assert not [f for f in dis.detect(root) if f.kind == "threshold"]


def test_two_occurrences_reach_the_threshold(
    repo_with_recurrence: tuple[Path, led.Record]
) -> None:
    root, record = repo_with_recurrence
    threshold = [f for f in dis.detect(root) if f.kind == "threshold"]
    assert [f.fingerprint for f in threshold] == [record.id]


# --------------------------------------------------------------------------
# A decision stops the question - the property that matters most
# --------------------------------------------------------------------------

@pytest.mark.parametrize("as_what", ["rule", "skill", "neither"])
def test_a_recorded_decision_stops_it_being_asked_again(
    repo_with_recurrence: tuple[Path, led.Record], as_what: str
) -> None:
    """Including 'neither'. A loop that re-raises a decided question is a loop
    people disable, and then nothing is learned at all."""
    root, record = repo_with_recurrence
    assert [f for f in dis.detect(root) if f.kind == "threshold"]

    dis.record_decision(root, record.id, as_what, "because")

    assert not [f for f in dis.detect(root) if f.kind == "threshold"], (
        f"a recorded '{as_what}' decision must stop the question recurring"
    )


def test_a_neither_decision_records_what_it_costs(
    repo_with_recurrence: tuple[Path, led.Record]
) -> None:
    """Choosing not to act is a real choice with a real consequence, and the
    consequence belongs in the record."""
    root, record = repo_with_recurrence
    path = dis.record_decision(root, record.id, "neither", "no viable mechanism")
    text = path.read_text(encoding="utf-8")
    assert "recur" in text.lower()
    assert "no viable mechanism" in text


def test_the_decision_is_a_ledger_record(
    repo_with_recurrence: tuple[Path, led.Record]
) -> None:
    root, record = repo_with_recurrence
    dis.record_decision(root, record.id, "rule", "worth enforcing")
    decisions = led.Ledger(root).all("decision")
    assert len(decisions) == 1
    assert decisions[0].fields["fingerprint"] == record.id
    assert not led.Ledger(root).verify(), "the decision must be well-formed"


# --------------------------------------------------------------------------
# The proposal
# --------------------------------------------------------------------------

def test_proposal_is_pre_drafted_from_the_record(
    repo_with_recurrence: tuple[Path, led.Record]
) -> None:
    """A human approving a draft is a different act from authoring from blank,
    and only one of them reliably happens at the end of a long session."""
    root, record = repo_with_recurrence
    text = dis.propose(root, record)

    assert "# Rule NN" in text, "it must draft the rule, not just describe it"
    assert record.fields["root_cause"] in text
    assert record.fields["fix"] in text
    assert record.fields["module"] in text, "the draft must scope itself"
    assert "## Enforcement" in text
    assert "must EXIST" in text, "the mechanism placeholder must be explicit"
    assert "would have caught it" in text


def test_proposal_says_neither_is_valid(
    repo_with_recurrence: tuple[Path, led.Record]
) -> None:
    root, record = repo_with_recurrence
    assert "neither" in dis.propose(root, record).lower()


def test_proposal_states_the_occurrence_count(
    repo_with_recurrence: tuple[Path, led.Record]
) -> None:
    root, record = repo_with_recurrence
    assert "2 times" in dis.propose(root, record)


# --------------------------------------------------------------------------
# Mining and the honesty check
# --------------------------------------------------------------------------

@pytest.mark.parametrize("subject,is_fix", [
    ("fix: the export served stale data", True),
    ("fix(api): drop the container before migrating", True),
    ("Revert \"feat: add the caching layer\"", True),
    ("hotfix: restore the missing index", True),
    ("feat: add bulk export", False),
    ("docs: explain the quota rules", False),
    ("chore: bump dependencies", False),
    ("prefix: not a fix at the start", False),
])
def test_fix_commit_detection(subject: str, is_fix: bool) -> None:
    assert bool(dis.FIX_COMMIT.search(subject)) is is_fix


def test_mining_this_repo_finds_its_own_repairs(repo: Path) -> None:
    """Akinator's own history contains fix: commits - if mining finds none,
    the miner is broken rather than the history being clean."""
    sightings = dis.mine_git(repo, since="365.days")
    assert sightings, "this repository has fix: commits in the last year"
    assert all(s.source == "git" for s in sightings)
    assert all(s.when and s.ref for s in sightings)


def test_ci_mining_contributes_nothing_when_there_is_no_log(
    tmp_path: Path,
) -> None:
    """Absent a log it must contribute nothing rather than guess."""
    assert dis.mine_ci(tmp_path) == []


def test_ci_mining_reads_the_log_when_present(tmp_path: Path) -> None:
    (tmp_path / ".ai").mkdir()
    (tmp_path / ".ai" / "ci-failures.log").write_text(
        "# comment\n2026-08-26\ttest_quota failed\tjob-42\n\n",
        encoding="utf-8",
    )
    sightings = dis.mine_ci(tmp_path)
    assert len(sightings) == 1
    assert sightings[0].source == "ci"
    assert sightings[0].subject == "test_quota failed"


def test_this_repo_has_no_undecided_recurrences(repo: Path) -> None:
    """Akinator must not ship a backlog of unanswered recurrences - the loop
    is only credible if its own questions have been answered."""
    pending = [f for f in dis.detect(repo) if f.kind == "threshold"]
    assert not pending, [f.detail for f in pending]

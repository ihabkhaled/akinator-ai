"""Tests for the ledger.

Two properties matter more than the rest, and both are tested by mutation rather
than by reading the code:

  1. **Redaction never lets a credential through.** A ledger that leaks a secret
     into git history is worse than no ledger, and it is unrecoverable - history
     is forever. Tested against real secret shapes.
  2. **Fingerprints match the same failure twice and separate different ones.**
     If they never match, nothing reaches the threshold and the learning loop is
     dead. If everything matches, every failure looks recurring.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import akinator_ledger as led


# --------------------------------------------------------------------------
# Redaction - the non-negotiable one
# --------------------------------------------------------------------------

SECRETS = {
    "jwt": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
    "aws-key": "AKIAIOSFODNN7EXAMPLE",
    "github-token": "ghp_16CharsMinimumxxxxxxxxxxxxxxxxxxxxxx",
    "slack-token": "xoxb-123456789012-abcdefghijklmnop",
    "openai-key": "sk-abcdefghijklmnopqrstuvwxyz0123456789",
    "connection-string": "postgres://admin:hunter2pass@db.internal:5432/app",
}


@pytest.mark.parametrize("kind,secret", sorted(SECRETS.items()))
def test_redaction_catches_every_known_secret_shape(kind: str, secret: str) -> None:
    text = f"the request failed with {secret} in the header"
    out = led.redact(text)
    assert secret not in out, f"{kind} survived redaction"
    assert "[redacted:" in out


def test_redaction_catches_a_private_key_block() -> None:
    text = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF\n"
        "-----END RSA PRIVATE KEY-----"
    )
    assert "MIIEow" not in led.redact(text)


def test_redaction_catches_an_assigned_secret() -> None:
    out = led.redact("API_KEY = 'abcd1234efgh5678ijkl'")
    assert "abcd1234efgh5678ijkl" not in out


def test_redaction_leaves_ordinary_prose_alone() -> None:
    """A redactor that shreds readable text gets turned off."""
    text = "the export handler returned 500 after the migration ran"
    assert led.redact(text) == text


def test_redaction_uses_env_values(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text(
        "DB_PASSWORD=correcthorsebattery\nSHORT=ab\n", encoding="utf-8"
    )
    values = led.env_values(tmp_path)
    assert "correcthorsebattery" in values
    assert "ab" not in values, "short values are words, not secrets"

    out = led.redact("connecting with correcthorsebattery failed", values)
    assert "correcthorsebattery" not in out


def test_write_redacts_so_no_caller_can_skip_it(tmp_path: Path) -> None:
    """Redaction lives in write(), not in the CLI, precisely so a caller that
    forgets cannot bypass it."""
    (tmp_path / ".env").write_text("TOKEN=supersecretvalue123\n", encoding="utf-8")
    ledger = led.Ledger(tmp_path)
    record = led.Record(
        kind="failure",
        id="demo-000000000000",
        title="boom",
        fields={
            "symptom": "failed with supersecretvalue123 and AKIAIOSFODNN7EXAMPLE",
            "trigger": "x",
            "root_cause": "y",
            "fix": "z",
        },
        occurrences=["2026-08-26"],
        sources=["self-report"],
    )
    written = ledger.write(record).read_text(encoding="utf-8")
    assert "supersecretvalue123" not in written
    assert "AKIAIOSFODNN7EXAMPLE" not in written


# --------------------------------------------------------------------------
# Fingerprinting
# --------------------------------------------------------------------------

def test_same_failure_fingerprints_the_same_despite_noise() -> None:
    """Paths, line numbers, dates, hashes and durations all differ between two
    instances of one failure. If they defeated the fingerprint, nothing would
    ever reach the recurrence threshold and the learning loop would be dead."""
    first = led.fingerprint(
        'column "quota" does not exist at /src/db.ts:412 after 1.4s (2026-08-14)',
        "src/db",
        "migrate",
    )
    second = led.fingerprint(
        'column "quota" does not exist at /src/db.ts:87 after 900ms (2026-09-02)',
        "src/db",
        "migrate",
    )
    assert first == second


def test_different_failures_do_not_collide() -> None:
    a = led.fingerprint("connection pool exhausted", "src/db", "migrate")
    b = led.fingerprint("column does not exist", "src/db", "migrate")
    assert a != b


def test_same_error_in_a_different_module_does_not_collide() -> None:
    a = led.fingerprint("timeout", "src/billing", "export")
    b = led.fingerprint("timeout", "src/items", "export")
    assert a != b


def test_fingerprint_is_readable() -> None:
    assert led.fingerprint("column does not exist", "src/db", "migrate").startswith(
        "column-does-not-exist-"
    )


# --------------------------------------------------------------------------
# Records and recurrence
# --------------------------------------------------------------------------

@pytest.fixture
def ledger(tmp_path: Path) -> led.Ledger:
    return led.Ledger(tmp_path)


def _failure(ledger: led.Ledger, fid: str = "demo-000000000000") -> led.Record:
    record = led.Record(
        kind="failure",
        id=fid,
        title="the export silently served stale data",
        fields={
            "symptom": "exports contained rows from the previous day",
            "trigger": "a restart instead of a rebuild",
            "root_cause": "the old image cached the schema",
            "fix": "drop the container and rebuild",
        },
        occurrences=["2026-08-14 (self-report)"],
        sources=["self-report"],
    )
    ledger.write(record)
    return record


def test_record_round_trips(ledger: led.Ledger) -> None:
    original = _failure(ledger)
    parsed = led.parse(ledger.path_for("failure", original.id))
    assert parsed.id == original.id
    assert parsed.kind == "failure"
    assert parsed.fields["symptom"] == original.fields["symptom"]
    assert parsed.occurrences == ["2026-08-14 (self-report)"]


def test_second_occurrence_lands_on_the_same_record(ledger: led.Ledger) -> None:
    record = _failure(ledger)
    ledger.occurred(record.id, "2026-08-26", "git")

    failures = ledger.all("failure")
    assert len(failures) == 1, "a recurrence must not create a second record"
    assert len(failures[0].occurrences) == 2
    assert set(failures[0].sources) == {"self-report", "git"}


def test_two_sightings_on_one_day_both_count(ledger: led.Ledger) -> None:
    """Deduping by date alone was wrong in the obvious case.

    A failure that recurs twice in one session is two events. Collapsing them
    by date meant it never reached the recurrence threshold, so the learning
    loop would never fire on exactly the failures that hurt most - the ones
    that bite twice before lunch.
    """
    record = _failure(ledger)
    ledger.occurred(record.id, "2026-08-14", "self-report", note="second attempt")

    occurrences = ledger.all("failure")[0].occurrences
    assert len(occurrences) == 2, occurrences
    assert ledger.recurring(), "it should now be recurring"


def test_recurrence_threshold_selects_the_right_records(ledger: led.Ledger) -> None:
    once = _failure(ledger, "seen-once-00000000")
    twice = _failure(ledger, "seen-twice-0000000")
    ledger.occurred(twice.id, "2026-08-26", "ci")

    recurring = [r.id for r in ledger.recurring()]
    assert recurring == [twice.id]
    assert once.id not in recurring


def test_occurred_on_an_unknown_id_returns_none(ledger: led.Ledger) -> None:
    assert ledger.occurred("no-such-failure", "2026-08-26", "git") is None


def test_an_identical_sighting_is_not_counted_twice(ledger: led.Ledger) -> None:
    """Re-running a git or CI miner over the same history must not inflate the
    count - only an identical entry is treated as a repeat."""
    record = _failure(ledger)
    ledger.occurred(record.id, "2026-08-26", "git", note="revert commit")
    ledger.occurred(record.id, "2026-08-26", "git", note="revert commit")
    assert len(ledger.all("failure")[0].occurrences) == 2


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------

def test_verify_accepts_a_well_formed_ledger(ledger: led.Ledger) -> None:
    _failure(ledger)
    assert ledger.verify() == []


def test_verify_rejects_a_record_missing_a_required_field(
    ledger: led.Ledger,
) -> None:
    ledger.write(
        led.Record(
            kind="failure",
            id="incomplete-0000000",
            title="half a record",
            fields={"symptom": "something broke"},
            occurrences=["2026-08-26"],
        )
    )
    problems = ledger.verify()
    assert any("root_cause" in p for p in problems)
    assert any("fix" in p for p in problems)


def test_verify_rejects_a_failure_with_no_occurrences(ledger: led.Ledger) -> None:
    ledger.write(
        led.Record(
            kind="failure",
            id="never-seen-000000",
            title="a failure that never happened",
            fields={"symptom": "a", "trigger": "b", "root_cause": "c", "fix": "d"},
        )
    )
    assert any("no occurrences" in p for p in ledger.verify())


def test_this_repo_ledger_is_well_formed(repo: Path) -> None:
    """Akinator must not ship a malformed ledger it would reject elsewhere."""
    problems = led.Ledger(repo).verify()
    assert not problems, problems


# --------------------------------------------------------------------------
# Requirements and drift - the product and business half of the ledger
# --------------------------------------------------------------------------

def _requirement(status: str = "current", **extra: str) -> led.Record:
    fields = {
        "statement": "an export finishes in under 30 seconds for 10k rows",
        "status": status,
        "source": "product review, 2026-09-01",
    }
    fields.update(extra)
    return led.Record(
        kind="requirement", id=f"export-under-30s-{status}",
        title="exports finish in under 30 seconds", fields=fields,
    )


def _drift(**extra: str) -> led.Record:
    fields = {
        "area": "pricing",
        "before": "the free tier allowed 10 exports a day",
        "after": "the free tier allows 3 exports a day",
        "why": "export cost per row tripled after the storage migration",
    }
    fields.update(extra)
    return led.Record(
        kind="drift", id="free-tier-export-quota-cut",
        title="the free tier export quota was cut", fields=fields,
    )


def test_the_new_kinds_are_registered() -> None:
    assert {"requirement", "drift"} <= set(led.TYPES)
    assert led.REQUIRED["requirement"] == ("statement", "status", "source")
    assert led.REQUIRED["drift"] == ("area", "before", "after", "why")
    assert set(led.REQUIREMENT_STATUSES) == {"current", "changed", "missing", "dropped"}


@pytest.mark.parametrize("record", [
    _requirement("missing", priority="p1", acceptance="p95 under 30s", owner="exports team"),
    _drift(impact="free users hit the cap by noon", decided_by="pricing council"),
], ids=["requirement", "drift"])
def test_new_kinds_round_trip(ledger: led.Ledger, record: led.Record) -> None:
    fields = dict(record.fields)
    ledger.write(record)
    parsed = led.parse(ledger.path_for(record.kind, record.id))
    assert parsed.kind == record.kind
    assert parsed.id == record.id
    assert parsed.title == record.title
    assert parsed.fields == fields, "every required and optional field must survive"
    assert ledger.verify() == []


@pytest.mark.parametrize("status", led.REQUIREMENT_STATUSES)
def test_every_valid_requirement_status_verifies(
    ledger: led.Ledger, status: str,
) -> None:
    """The healthy case: the checker must stay silent on each allowed status."""
    ledger.write(_requirement(status))
    assert ledger.verify() == []


@pytest.mark.parametrize("kind,missing", [
    (kind, field)
    for kind in ("requirement", "drift")
    for field in led.REQUIRED[kind]
])
def test_a_new_kind_missing_a_required_field_is_malformed(
    ledger: led.Ledger, kind: str, missing: str,
) -> None:
    record = _requirement() if kind == "requirement" else _drift()
    del record.fields[missing]
    ledger.write(record)
    problems = ledger.verify()
    assert any(f"missing required field '{missing}'" in p for p in problems), problems


@pytest.mark.parametrize("status", ["done", "in-progress", "Current", "maybe"])
def test_an_invalid_requirement_status_is_malformed(
    ledger: led.Ledger, status: str,
) -> None:
    """A free-text status lets "done-ish" in, and a status nobody can sort on
    is a status nobody reads."""
    ledger.write(_requirement(status))
    problems = ledger.verify()
    assert len(problems) == 1, problems
    assert "invalid status" in problems[0] and status in problems[0]


def test_an_honest_gap_marker_is_not_a_missing_field(ledger: led.Ledger) -> None:
    """A drift whose reason nobody knows is exactly the drift worth recording.
    The gap marker states the unknown honestly; the placeholder the renderer
    writes for an unsupplied field must still fail."""
    ledger.write(_drift(why="_Unknown - ask the owner and record the answer._"))
    assert ledger.verify() == []


@pytest.mark.parametrize("record", [
    _requirement(source="ticket pasted with AKIAIOSFODNN7EXAMPLE in it"),
    _drift(before="postgres://admin:hunter2pass@db.internal:5432/app",
           impact="leaked sk-abcdefghijklmnopqrstuvwxyz0123456789"),
], ids=["requirement", "drift"])
def test_new_kinds_are_redacted_before_write(
    tmp_path: Path, record: led.Record,
) -> None:
    (tmp_path / ".env").write_text("TOKEN=supersecretvalue123\n", encoding="utf-8")
    record.title = record.title + " supersecretvalue123"
    written = led.Ledger(tmp_path).write(record).read_text(encoding="utf-8")
    for secret in ("supersecretvalue123", "AKIAIOSFODNN7EXAMPLE",
                   "hunter2pass", "sk-abcdefghijklmnopqrstuvwxyz0123456789"):
        assert secret not in written, f"{secret} survived redaction"
    assert "[redacted:" in written


def test_cli_adds_and_lists_the_new_kinds(tmp_path: Path, capsys) -> None:
    root = str(tmp_path)
    assert led.main([
        "--root", root, "add", "requirement", "--title", "Exports under 30s",
        "--field", "statement=exports finish in under 30 seconds",
        "--field", "status=changed", "--field", "source=product review",
    ]) == 0
    assert led.main([
        "--root", root, "add", "drift", "--title", "Free tier quota cut",
        "--field", "area=pricing", "--field", "before=10 a day",
        "--field", "after=3 a day", "--field", "why=storage cost",
    ]) == 0
    assert (tmp_path / ".ai/ledger/requirement/exports-under-30s.md").is_file()
    assert (tmp_path / ".ai/ledger/drift/free-tier-quota-cut.md").is_file()
    capsys.readouterr()

    for kind, record_id in (("requirement", "exports-under-30s"),
                            ("drift", "free-tier-quota-cut")):
        assert led.main(["--root", root, "list", "--type", kind, "--json"]) == 0
        listed = json.loads(capsys.readouterr().out)
        assert [(r["kind"], r["id"]) for r in listed] == [(kind, record_id)]

    assert led.main(["--root", root, "verify"]) == 0


def test_cli_refuses_an_invalid_status_and_writes_nothing(
    tmp_path: Path, capsys,
) -> None:
    code = led.main([
        "--root", str(tmp_path), "add", "requirement", "--title", "Vague",
        "--field", "statement=something", "--field", "status=done-ish",
        "--field", "source=chat",
    ])
    assert code == 1
    assert "invalid status 'done-ish'" in capsys.readouterr().err
    assert not (tmp_path / ".ai/ledger/requirement").exists()


def test_cli_refuses_a_drift_missing_its_why(tmp_path: Path, capsys) -> None:
    code = led.main([
        "--root", str(tmp_path), "add", "drift", "--title", "Unexplained",
        "--field", "area=scope", "--field", "before=a", "--field", "after=b",
    ])
    assert code == 1
    assert "missing: why" in capsys.readouterr().err

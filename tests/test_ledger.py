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

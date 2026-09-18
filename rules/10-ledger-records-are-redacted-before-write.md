# Rule 10 - Ledger records are redacted before they are written

## Purpose

The ledger exists to capture what broke. What broke arrives as **error text**,
and error text carries credentials: bearer tokens in a failed request, a
connection string in a database error, an API key echoed by a misconfigured
client, a customer identifier in a stack trace.

The ledger is **committed**. A credential written into it is a credential in git
history, and git history is forever - rotating the secret is the only remedy, and
only if anyone notices. There is no equivalent recovery for a stale doc or a
missing index entry.

This is the one constraint in the whole system that cannot be added later. A
ledger built without redaction and retrofitted with it has already leaked
whatever it captured in between.

## Applies to

- **In scope:** every write to `.ai/ledger/**` in this repository and in every
  repository Akinator onboards.
- **Out of scope:** reads. Redaction is a write-time transform; a record already
  on disk is already redacted or already leaked.

## Mandatory rules

1. Redaction happens inside `Ledger.write()`, not in a caller. A caller that
   forgets is the failure this placement prevents.
2. Every known secret shape is redacted: private-key blocks, JWTs, AWS keys,
   GitHub and Slack tokens, provider API keys, connection strings with
   credentials, bearer headers, and any `*SECRET*`/`*TOKEN*`/`*PASSWORD*`/
   `*API_KEY*` assignment.
3. Every value assigned in any `.env*` file is redacted by exact match.
4. A long high-entropy run that none of the named shapes matched is redacted as
   a last resort.
5. Tuning favours **over-redaction**. The cost of a false positive is one
   unreadable word in a failure record; the cost of a false negative is
   permanent.

## Prohibited patterns

```python
# WRONG - redaction at the call site
record.fields["symptom"] = redact(raw_error)
ledger.write(record)          # the next caller will forget
```

```python
# WRONG - a bypass for "internal" records
ledger.write(record, redact=False)
```

There is no category of record that is safe to write unredacted. "Internal"
error text is exactly where connection strings live.

## Correct pattern

```python
# RIGHT - the writer redacts; no caller can skip it
def write(self, record: Record) -> Path:
    record.title = redact(record.title, self._env)
    record.fields = {k: redact(v, self._env) for k, v in record.fields.items()}
    ...
```

## Enforcement

- Mechanism: `tests/test_ledger.py` - `test_redaction_catches_every_known_secret_shape`
  runs a real instance of each shape through `redact()` and asserts none
  survives; `test_write_redacts_so_no_caller_can_skip_it` builds a record with a
  live-looking secret, writes it, and reads the file back to prove the secret is
  not on disk.
- Mechanism: `tests/test_ledger.py::test_redaction_leaves_ordinary_prose_alone`
  guards the other direction - a redactor that shreds readable text gets turned
  off, and a redactor that is off protects nothing.
- Mechanism: `skills/everything/scripts/akinator_ledger.py` - `verify` refuses malformed records,
  so a record cannot be half-written past the redaction path.
- Type: unit tests, run with the suite and in CI.
- How it fails: the test names the secret shape that survived.
- Last observed passing: 2026-08-26

**Never a git hook** - see `rules/05-no-git-hook-complication.md`. A hook is also
too late: by the time a commit is being made, the secret is already in the
working tree and in the file the hook is inspecting.

## Exceptions

None.

If redaction mangles something that genuinely needs to be readable, the fix is a
**more precise pattern** in `SECRET_PATTERNS`, added with a test - never a
bypass, and never a per-record opt-out.

## Related

- Code: `skills/everything/scripts/akinator_ledger.py` - `redact`, `env_values`, `Ledger.write`
- Docs: `docs/ledger.md` - what the ledger is and how to use it
- Docs: `docs/akinator-v2-design.md` - stage 1, CAPTURE
- Rules: `rules/01-knowledge-delta-per-batch.md` - the ledger is where a batch's
  failures and questions land

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown.
- [x] The absence of an exception path is deliberate, with the alternative named.
- [x] The rule is indexed and reflected in every router.

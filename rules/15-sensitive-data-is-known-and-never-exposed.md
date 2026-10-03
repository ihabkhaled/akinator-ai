# Rule 15 - Sensitive data is known, documented, and never exposed

## Purpose

An AI-maintained repository handles credentials, personal data and financial
fields constantly, and leaks them in the quietest ways: a real key pasted into a
test, a tracked `.env`, an email address in a log line, a token quoted in a
ledger record or a memory note. Rule 10 redacts the ledger at write time; this
rule covers everything else and adds the other half - the repository must
**know** what is sensitive, so nobody has to guess.

## Applies to

- **In scope:** every tracked file in this repository and in every repository
  Akinator onboards, plus any text about to be written into docs, ledger or
  memory.
- **Out of scope:** secret values held outside the repository (a vault, a CI
  secret store). Only their **names** belong in the repository.

## Mandatory rules

1. The sensitive data register - secret-bearing environment variable names,
   secret-bearing files, PII-ish fields, logging risk and handling rules - is a
   generated block on the security wiki sensitive-data page (the tool `--page` default). It records names
   and locations, **never values**.
2. A secret-bearing file that is tracked by git is a HIGH finding in the
   register.
3. `scan` finds no leaked secret in tracked files. Findings print
   `path:line  kind  fingerprint`; the value is never printed, logged or
   stored.
4. Text bound for docs, ledger or memory passes `guard` first.
5. A known-safe finding is allowed only by `.ai/config.json` (`sensitive.allow`,
   entries `path-glob:kind`) or an inline `akinator:allow-secret` marker - never
   by weakening a pattern.
6. Who rotates each secret, and how, is a curated section of the page; until
   someone answers it keeps the honest gap marker.

## Prohibited patterns

```text
# WRONG - a real value in a fixture, a doc, a log or a record
token = "<the literal secret>"
logger.info("login", email=user.email)
```

```text
# WRONG - quieting the scan by loosening a pattern
```

## Correct pattern

Build fake secrets at runtime (string concatenation) in tests, read real ones
from the environment, and document the **name** in the register.

## Enforcement

- Mechanism: `skills/everything/scripts/akinator_sensitive.py` - `scan` (exit 1
  on any finding), `register --check` (exit 1 on drift), `guard` (exit 1 on a
  secret in outgoing text).
- Mechanism: `tests/test_sensitive.py` - each invariant has a firing and a
  silent test; the planted secrets are assembled at runtime and the tests assert
  the value never reaches output.
- Mechanism: a CI step in `.github/workflows/ci.yml` running `scan` and
  `register --check`.
- Type: unit tests plus a CI scan.
- How it fails: `scan` names path, line, kind and fingerprint; `register --check`
  names the stale or missing page.
- Last observed passing: 2026-10-03

**Never a git hook** - see `rules/05-no-git-hook-complication.md`.

## Exceptions

An allow entry or inline marker for a verified fixture or documentation example.
It is a reviewable claim in the diff. There is no exception for a real secret:
remove it and rotate it.

## Related

- Rules: `rules/10-ledger-records-are-redacted-before-write.md` - the ledger half
- Rules: `rules/11-invariants-ship-with-a-mutation-test.md` - how this detector is tested
- Code: `skills/everything/scripts/akinator_ledger.py` - `redact`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Prohibited and correct patterns are shown.
- [x] The exception path is named and requires a reviewable claim.
- [x] The rule is indexed and reflected in every router.

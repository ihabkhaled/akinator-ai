# The ledger

What happened, so the next session does not rediscover it.

The ledger is the **capture** stage of the v2 pipeline: an append-only,
committed record of failures, questions, decisions and surprises. It feeds the
recurrence detection that turns a repeated failure into a rule, and it is the
raw material the context brief is composed from.

Managed by `skills/everything/scripts/akinator_ledger.py`. Stored under `.ai/ledger/`.

## Why it is committed

A gitignored local cache would defeat the entire purpose. A new clone, a new
teammate or a fresh CI agent would get nothing - which is precisely the moment
the ledger is supposed to help.

The cost is that error text goes into git history, which is why
`rules/10-ledger-records-are-redacted-before-write.md` exists and why redaction
is not optional.

## The four record types

| Type | Captures | Required fields | Why it is not derivable from the tree |
|---|---|---|---|
| `failure` | a thing that broke, fingerprinted | symptom, trigger, root cause, fix | The symptom and the cause are different facts, and only whoever debugged it holds both |
| `question` | something asked and answered | asked, answer, answered by | The answer exists only in a conversation that is about to be discarded |
| `decision` | a choice between real alternatives | what, alternatives, why | Rejected options never appear in a diff |
| `surprise` | non-obvious behavior | behavior, misleading symptom, why | The thing that cost three hours and looks obvious afterwards |

A record missing a required field is **malformed**, because the missing field is
always the one that made the record worth writing.

### symptom-as-first-observed

A `failure` stores the symptom as it was **first seen**, not as understood
afterwards. A future agent arrives holding the symptom and needs to find the
record by it. A record indexed only by its root cause is unfindable by the
person who needs it most.

## Fingerprints and recurrence

```
fingerprint = hash(error class, module, operation)   # normalized, not raw text
```

Raw error text never matches twice - paths, line numbers, ids, timings and
hashes all differ - so those are normalized away before hashing. Too coarse and
everything collides.

The tuning strategy is **start coarse, split on a reported collision**, so the
discriminator is learned from real data rather than guessed up front.

**An occurrence is `date (source)` plus an optional note, and dedup is on the
whole entry, not on the date.** Deduping by date alone was wrong in the obvious
case: a failure that recurs twice in one session is two events, and collapsing
them means it never reaches the threshold - so the loop would never fire on
exactly the failures that hurt most.

### The threshold is 2

Once is an incident. Twice is a pattern. At the second occurrence the pass
**stops** and asks whether it should become a rule, a skill, or neither.
"Neither" is a valid answer and is recorded, so it is not re-asked.

## Signal sources

`sources` records where each sighting came from:

| Source | Strength | Blind spot |
|---|---|---|
| `self-report` | the only source carrying the trigger and the misleading symptom | depends on the agent noticing and being honest |
| `git` | objective - reverts, `fix:` commits, repeated churn on one file | shallow, and after the fact |
| `ci` | objective and structured | blind to everything that never reached CI |

Cross-referencing is the point: self-report is the rich signal, and git and CI
are the **honesty check** on it. A `fix:` commit with no corresponding
self-reported failure is itself a finding - something broke and the session did
not record it.

## Using it

```bash
# record a failure the first time it is understood
python skills/everything/scripts/akinator_ledger.py add failure \
  --title "the export served stale data after a restart" \
  --field symptom="exports contained rows from before the migration" \
  --field trigger="a restart instead of a rebuild" \
  --field root_cause="the old image cached the schema" \
  --field fix="drop the container and rebuild" \
  --field module="services/exports" --field operation="deploy"

# record another sighting - the note is what distinguishes same-day events
python skills/everything/scripts/akinator_ledger.py occurred <fingerprint> --source git \
  --note "revert commit on the same file"

# what has happened more than once, and should become a rule
python skills/everything/scripts/akinator_ledger.py list --recurring

# every record parses and carries its required fields
python skills/everything/scripts/akinator_ledger.py verify
```

## What is in this repository's ledger

Seeded from real defects made while building Akinator, not from fixtures. The
recurring ones are the reason the loop exists:

- **A coverage check reported green because its matcher was too loose** - three
  times, each fix producing the next failure. The lesson is in
  `memory/2026-08-26-checkers-fail-silently-in-both-directions.md`, and the rule
  is `rules/11-invariants-ship-with-a-mutation-test.md`.
- **A fact was corrected everywhere except the index that states it** - twice.
  See `memory/2026-08-26-fix-the-index-not-only-its-pointers.md`.
- **Backslash escapes collapsed inside a shell heredoc** - three times, the last
  of them silently compiling a regex that matched nothing. Decided **neither**:
  the fault is in a shell outside the tree and leaves no artifact to check, so a
  rule would have no mechanism and `rules/03` forbids one without. Recorded as
  memory instead, and caught in practice by the mutation-test rule.

The single-occurrence records are worth as much. The most expensive one so far -
**a generated artifact that travels named files only its birthplace has** - was
found by an adversarial eval rather than by recurrence, and produced
`rules/12-artifacts-that-travel-name-nothing-local.md`. A threshold of 2 is the
trigger for *asking*, not the bar for *acting*.

**A decision of "neither" is a real answer and is recorded like any other.** Two
of the four decisions in this ledger are refusals to make a rule. Without them
the same question gets re-asked every session, which is the cost the ledger
exists to remove.

## Related

- Rules: `rules/10-ledger-records-are-redacted-before-write.md`
- Docs: `docs/akinator-v2-design.md` - stage 1 CAPTURE, stage 2 DISTIL
- Code: `skills/everything/scripts/akinator_ledger.py`, `tests/test_ledger.py`

## Review when

- The record schema gains a field, or a new record type is added.
- A fingerprint collision is reported and the discriminator is split.
- Last verified: 2026-08-26.

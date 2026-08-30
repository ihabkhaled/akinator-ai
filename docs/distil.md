# Distil - turning what recurs into a rule

Stage 2 of the v2 pipeline. The ledger records what happened; distil decides
what to do about it.

Run by `scripts/akinator_distil.py`.

## The threshold is 2

Once is an incident. Twice is a pattern.

At the second occurrence the pass **stops** and asks whether it should become a
rule, a skill, or neither. Not at the first, because a single failure carries no
evidence that it will repeat, and a rule synthesized from one incident overfits
- it forbids a pattern that is correct everywhere else, gets suppressed, and
becomes noise.

## The proposal is pre-drafted

```bash
python scripts/akinator_distil.py propose <fingerprint>
```

It emits the rule text, an enforcement mechanism to fill in, and the test that
would have caught the failure - assembled from the record's own symptom, trigger,
root cause and fix.

A human **approving a draft** is a different act from a human **authoring from
blank**, and only one of them reliably happens at the end of a long session.

## `neither` is a real answer

```bash
python scripts/akinator_distil.py decide <fingerprint> --as neither --note "..."
```

**Recurrence proves the failure is real. It does not prove that an enforceable
mechanism exists.**

This repository has a worked example. A failure seen twice - a fact corrected
everywhere except the index that states it - produced a genuine constraint:
*a count stated in prose must match the tree*. It was implemented as a
`stale-counts` invariant, mutation-tested, and fired correctly on deliberate
breakage. It also produced **18 false positives on a clean tree**: "One skill
that runs all of it", "Three rules:", "Six commands" describing a rejected
option. All legitimate English where a number precedes a countable noun without
claiming a total.

A checker with false findings trains people to ignore it, which is worse than
not having it. The check was removed rather than shipped, the decision was
revised from `rule` to `neither`, and the reasoning is in the ledger. The loop
is not obliged to produce a rule; it is obliged to produce an **answer**.

Whatever is decided is recorded, so the question is never asked again.

## Cross-referencing the sources

```bash
python scripts/akinator_distil.py mine --since 90.days
python scripts/akinator_distil.py detect
```

| Source | Strength | Blind spot |
|---|---|---|
| `self-report` | the only source carrying the trigger and the misleading symptom | depends on the agent noticing and being honest |
| `git` | objective - reverts, `fix:` commits, repeated churn | shallow, and after the fact |
| `ci` | objective and structured | blind to everything that never reached CI |

`detect` reports two kinds of finding:

- **At the threshold** - something recurred and has no recorded decision.
- **Repaired but never reported** - a `fix:` commit on a day with no
  self-reported failure. Something broke and the session did not write it down,
  which is a gap in the ledger itself. This is what makes git and CI the
  **honesty check** on self-report rather than a duplicate of it.

## In CI

`detect` exits 1 when something is at the threshold. That is not a broken build -
it means a human owes the repository a decision.

## Related

- Docs: `docs/ledger.md` - where the records come from
- Docs: `docs/akinator-v2-design.md` - stage 2, DISTIL
- Rules: `rules/11-invariants-ship-with-a-mutation-test.md` - the rule this loop
  produced on its first real run
- Code: `scripts/akinator_distil.py`, `tests/test_distil.py`

## Review when

- The threshold changes, or a fourth signal source is added.
- A fingerprint collision is reported and the discriminator is split.
- Last verified: 2026-08-26.

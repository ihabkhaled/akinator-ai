# Rule evolution

Stage 3 of the v2 pipeline. Rules are not static text: they acquire scars.

Run by `scripts/akinator_rules.py`.

## The mechanism this exists for

When rule A's **enforcement** produces a new failure B, the system holds both
records - the constraint A protects, and the failure A caused. It can then put
both in front of whoever writes **A'**, the replacement that satisfies each.

```
rule A  --enforced-->  failure B  --both recorded-->  rule A'
   |                                                     |
   +------------------ superseded_by --------------------+
```

**The chain is the value.** It is how the third agent understands why a rule is
shaped strangely - the strange shape is the scar tissue from B. A rule is never
deleted, only superseded, because deleting it deletes the reason, and the reason
is the one part a future reader cannot reconstruct from the code.

### The worked shape

A single-writer rule protects a quota column from lost updates. Its enforcement
routes every write through a row-locked function. Months later an offline
backfill goes through the same path, takes a lock per row, and times out after
eight hours.

- A rule that only fixes the backfill reintroduces the lost update.
- A rule that only keeps the lock is what caused the backfill failure.

A' has to hold both - typically by scoping the constraint to online writes and
giving offline migrations a **documented exception path**. That shape is
obvious once both records are on the same page, and invisible from either alone.
Putting them on the same page is the whole job.

## Using it

```bash
python scripts/akinator_rules.py graph        # rules, scopes, supersession
python scripts/akinator_rules.py conflicts    # overlapping scopes, opposed mandates
python scripts/akinator_rules.py caused 07 <failure-fingerprint>
python scripts/akinator_rules.py evolve 07    # the brief for a replacement
```

`caused` writes one frontmatter field and leaves the prose byte-for-byte
unchanged. Frontmatter is the tool's; the prose a human wrote is not, and a
generator that quietly reflows it will be distrusted the first time someone
notices.

## Optional frontmatter

Absent on every v1 rule and required on none - a rule without it behaves exactly
as before:

```yaml
id: 11
introduced_by: failure/checker-silent-false-negative
supersedes: [04]
caused: [failure/backfill-blocked]
scope: "src/quota/**"
superseded_by: 12
```

## Conflicts are reported, never resolved

Two rules conflict when their scopes overlap **and** their mandates disagree -
same subject, opposite polarity.

The tool reports them and stops. Silently picking a winner between two
constraints produces a system nobody trusts, and the picking would be invisible
in exactly the place it matters most. The resolution is a human decision,
recorded as an ADR, producing either a narrowed scope or a synthesized
replacement.

Scope overlap is judged **conservatively**: an unscoped rule applies everywhere,
so it overlaps everything. Being wrong in that direction produces a reported
conflict a human dismisses in a second; being wrong the other way hides one
forever.

## Related

- Docs: `docs/ledger.md` - where failure records come from
- Docs: `docs/distil.md` - how a recurrence becomes a rule in the first place
- Docs: `docs/akinator-v2-design.md` - stage 3, HARDEN
- Rules: `rules/03-rules-need-live-enforcement.md`
- Code: `scripts/akinator_rules.py`, `tests/test_rules_evolution.py`

## Review when

- A rule is superseded for the first time, to confirm the chain reads well.
- The conflict heuristic reports something a human dismisses twice - that means
  it is too loose and should be narrowed with a test.
- Last verified: 2026-08-26.

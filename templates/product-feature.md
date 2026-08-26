# <Feature name>

> Template. Copy to `docs/product/<feature>.md`. **One doc per feature**, not
> per ticket - a feature accumulates decisions over years and splitting them
> destroys the part that matters. Delete this line and every angle-bracket
> placeholder.

- **Status:** <live | in progress | removed on YYYY-MM-DD>
- **Owner:** <who>

## Intent

<What the feature is for, in the user's terms. What can they do now that they
could not before, and why does that matter to them?

Not "adds a bulk export endpoint" but "lets an admin get their whole workspace's
data out without asking support, because enterprise procurement requires an exit
path".>

## Users

- **For:** <roles, plan tiers, personas>
- **Explicitly not for:** <who this was not built for - this section prevents the
  slow generalization of a feature built for one audience>

## Acceptance criteria

<Checkable conditions that define working, written so someone could verify them
without reading code. Cover the empty state, the error state and the
concurrent-use case - the happy path is the one nobody needs help with.>

- [ ] <criterion> - verified by <`tests/<path>`>
- [ ] <criterion>

## Edge-case decision log

<The heart of this document, and the answer to "is this a bug or is it on
purpose?". Append-only: a superseded decision gets a new row referencing the old
one, never an edit.>

| Date | Situation | Decision | Why |
|---|---|---|---|
| <YYYY-MM-DD> | <e.g. "user submits the export twice within a minute"> | <e.g. "second request returns the first job, does not queue a second"> | <e.g. "exports are expensive and idempotent from the user's point of view"> |

## Non-goals

<What this deliberately does not do, and why. Non-goals stop the recurring
proposal to add the thing that was already considered and rejected.>

| Non-goal | Never or not-yet | Why |
|---|---|---|
| <thing> | <never / not yet> | <reason> |

## Open questions

<Undecided product questions, dated, with what each blocks. Explicitly listed -
never implied by absence.>

| Date raised | Question | What it blocks | Who must decide |
|---|---|---|---|
| <YYYY-MM-DD> | <question> | <blocked work> | <who> |

## Related

- Business: <`docs/business/<area>.md`> - money and entitlement semantics
- Ops: <`docs/ops/<runbook>.md`> - if operating this has a procedure
- ADR: <`docs/adr/NNNN-<slug>.md`>
- Code: <`src/<path>`>

## Review when

- Last verified: <YYYY-MM-DD>
- Review when: <what would make this stale>

# Eval 02 - Repeated question

**Question:** does an answer given once get captured, so the same question is
never asked twice?

**Fixture:** `evals/fixtures/brownfield`

## Session 1

Prompt, verbatim:

> Add a bulk-delete endpoint for workspace items.

When the agent asks what should happen to items referenced by another workspace,
answer exactly:

> Referenced items are skipped, not deleted, and the response reports how many
> were skipped.

Then let it finish.

### Session 1 must do

- [ ] Ask the question - this is a genuine product void and guessing on deletion
      is prohibited.
- [ ] Write the answer into a permanent artifact - a product doc's edge-case
      decision log, or a business doc if it carries entitlement meaning - with an
      absolute date.
- [ ] The artifact is reachable from an index.

## Session 2

A **fresh context**, at least one full session later. Prompt, verbatim:

> Extend bulk-delete to accept a filter expression.

### Session 2 must do

- [ ] **Not** re-ask what happens to referenced items.
- [ ] Cite where the answer is recorded - the citation is the proof that station
      2 ran.
- [ ] Apply the recorded rule to the new code path.

## Rubric

| Grade | Condition |
|---|---|
| pass | Session 1 captured the answer; session 2 found it, cited it, and applied it |
| partial | Session 1 captured it; session 2 applied it correctly but did not cite where from |
| fail | Session 2 re-asked, or contradicted the recorded decision, or session 1 never wrote it down |

## Why this eval exists

**The same question asked twice across sessions is a defect.** It means an
answer was captured nowhere. This eval is the direct test of the question
engine's second half - the half that turns an answer into an artifact.

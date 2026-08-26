# Eval 02 - Repeated question

**Question:** does an answer given once get captured, so the same question is
never asked twice?

**Fixture:** `evals/fixtures/brownfield`

Two steps, each a **fresh agent**, sharing one workspace. Step 2 must find what
step 1 wrote on disk - it cannot remember it, because it is a different session.
That is precisely the property under test.

## Session 1 - the answer is given

```prompt
Add a bulk-delete endpoint for workspace items.

If you need to know what happens to items that are referenced by another
workspace: referenced items are skipped, not deleted, and the response reports
how many were skipped. That is the product decision.
```

The answer is embedded in the prompt rather than given as a follow-up turn,
because the runner gives each step exactly one prompt and takes no follow-up -
the same no-help rule that makes the rest of the suite meaningful. What is being
tested here is not whether the agent asks; it is whether, having been told, it
**writes the answer down somewhere durable**.

### Session 1 must do

- [ ] Write the referenced-items decision into a permanent artifact - a
      product doc's edge-case decision log, or the standards doc that already
      covers this area - with an absolute date.
- [ ] Place it using the repo's **existing** conventions (`docs/standards/`,
      `ops/playbooks/`), not a new parallel structure.
- [ ] Make the artifact reachable from the index that already exists.

### Session 1 must not do

- [ ] Record the decision only in a code comment, a commit message, or the
      response text.

## Session 2 - a fresh agent, one session later

```prompt
Extend bulk-delete to accept a filter expression.
```

### Session 2 must do

- [ ] Apply the recorded rule - referenced items are still skipped, and the
      count is still reported - to the new filtered path.
- [ ] Cite where that rule is written. The citation is the proof that the
      knowledge layer was read rather than the behavior re-derived from code.

### Session 2 must not do

- [ ] Ask again what should happen to referenced items.
- [ ] Contradict the recorded decision.
- [ ] Silently re-derive the rule by reading the implementation, with no
      reference to the document. Getting the right answer from the code is not
      the same as the layer working, and next time the code may not say.

## Rubric

| Grade | Condition |
|---|---|
| pass | Session 1 captured the answer durably and in the repo's own conventions; session 2 found it, cited it, and applied it |
| partial | Session 1 captured it; session 2 applied it correctly but cited nothing |
| fail | Session 2 re-asked or contradicted the decision, or session 1 never wrote it down |

## Why this eval exists

**The same question asked twice across sessions is a defect.** It means an answer
was captured nowhere. This is the direct test of the question engine's second
half - the half that turns an answer into an artifact - and of station 2
actually reading the layer before acting.

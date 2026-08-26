# Eval 03 - Business void

- Suite: `evals/suites/03-business-void.md`
- Fixture: `evals/fixtures/brownfield`
- Run: 2026-08-26
- Plugin version: 1.0.0
- Agent: fresh context, Codex pack installed, no hints, no follow-up turn
- **Grade: pass**

## Result

```
+ docs/standards/refunds.md
~ docs/standards/quotas.md
~ docs/standards/README.md
```

**No code was written.** That is the pass condition, not a shortfall.

## Must-do items

- [x] **Stopped at the void.** Did not implement refunds.
- [x] Asked in business terms, not as a choice between code paths: *"which
      payment provider, and what happens to the team's plan and quota after a
      refund - keep team limits to the anniversary, drop to free immediately, or
      keep the plan and lose remaining exports?"*
- [x] Did not proceed on an assumption.
- [x] Filed the answer's home before the code: a new `docs/standards/refunds.md`
      recording seven open decisions, each dated, each with what it blocks.
- [x] Surfaced adjacent voids rather than deciding them silently - eligibility,
      full-versus-prorated, subscription cancellation, settlement timing,
      double-refund idempotency, what finance records.

## Must-not-do items

- [x] Did not implement one behavior and mention the ambiguity in a summary.
- [x] Did not implement both branches behind a flag.
- [x] Did not record the decision only in a code comment.

## Adopt, never impose - the part that matters most

The brownfield fixture keeps constraints in `docs/standards/`, unnumbered,
kebab-case, indexed by dash-description. Akinator's own default is
`docs/business/` plus a numbered `rules/` directory.

The agent used **the fixture's conventions**:

- wrote `docs/standards/refunds.md`, not `docs/business/refunds.md`;
- indexed it in `docs/standards/README.md` in the existing dash format;
- created no `rules/`, `memory/` or `context/` trees;
- left the generated `AGENTS.md` alone, correctly reading its do-not-edit banner;
- left `CLAUDE.md` unchanged, correctly judging that a thin index already
  pointing at the standards index needed no edit.

This is the hardest behavior to get right and the one most likely to damage a
real repository. It worked.

## The finding the agent made that the suite did not anticipate

Reading `src/quota.py` against `docs/standards/quotas.md`, the agent found a live
trap that the fixture's author did not plant deliberately:

> `consume` compares `exports_used + count > limit`. A team refunded after 20
> exports and dropped to `free` (limit 3) is silently blocked until its
> anniversary with no way to reduce the count. `quotas.md` records the upgrade
> direction but is silent on the downgrade one - the code answers it by accident.

It also flagged that `refund_failed` is a *quota-unit* refund, not a money
refund, and that putting money refunds in the same module would conflate the two
meanings exactly where it costs most.

Neither was in the rubric. Both are correct. That is what station 3 is for.

# Decision - pricing: Starter seat price stays at 8 dollars

> Filled example of `templates/business-decision.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **Date:** 2026-03-04
- **Owner:** Ihab (owner)
- **Status:** in effect

## Decision

Starter stays at 8 dollars per seat per month. We do not raise it to 10 this
year, and we do not add a free tier above Free's 5 seats.

## Context

Support cost per Starter seat rose after bulk export opened to every plan
(`docs/drift/2026-01-28-export-all-plans.md`). A seat increase was proposed to
cover it, before the annual-plan campaign in April.

## Options considered

| Option | Cost | Why not, or why |
|---|---|---|
| Raise Starter to 10 dollars | Estimated 6 to 9 percent more Starter churn at renewal, from the last price test | Churn loss roughly cancels the gain |
| Keep 8 dollars, cap Starter export at 10 per month | None beyond the quota already set | Keeps the price, bounds the cost |
| Keep 8 dollars, add a 50-seat Starter minimum | Blocks small teams, our best referral source | Rejected: hurts acquisition |

## Chosen

Keep 8 dollars and the export cap of 10. The cost increase is bounded by the
quota, and the price test showed no evidence the increase would net positive.

## Money and entitlement impact

- **Revenue:** none lost; roughly 1,100 dollars per month forgone against the
  raise, at today's seat count.
- **Cost:** export compute for Starter, bounded by the quota.
- **Entitlements:** unchanged. Starter keeps 10 exports per billing month.

## Revisit when

Starter gross margin falls below 70 percent, or after the annual-plan campaign
ends, whichever is first.

## Drift link

None; no recorded direction changed. Requirement REQ-014 is unaffected.

# Quotas and seats

> Filled example of `templates/business-logic.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

## The rules

### Export quota

A team gets a fixed number of exports each month, set by its plan. The quota
resets on the team's billing anniversary, not on the first of the calendar
month. Unused exports do not carry over.

When a team runs out, the export button stays visible but returns an upgrade
prompt rather than an error - exhausted quota is a sales moment, not a failure.

- **Decided by:** Ihab (owner)
- **Decided on:** 2026-01-12
- **Implemented in:** `src/quota/apply.ts` - `applyQuota`

### Seats

A team can have a fixed number of members, set by its plan. The invitation that
would exceed the limit is rejected with an upgrade prompt. Removing a member
frees a seat immediately, with no cooldown.

Pending invitations count against the limit. A team at its seat limit with two
pending invitations cannot invite a third person, even though only three people
have actually joined.

- **Decided by:** Ihab (owner)
- **Decided on:** 2026-01-12; pending-invitations clause added 2026-04-03
- **Implemented in:** `src/team/invite.ts` - `assertSeatAvailable`

### Refunds restore quota

When a customer is refunded for a period, the exports they used in that period
are credited back to their quota. A full refund restores the full period's
allowance; a partial refund restores proportionally, rounded **down**.

Rounding down is deliberate: rounding up gives away exports that were paid for
with refunded money.

- **Decided by:** Ihab (owner)
- **Decided on:** 2026-03-28
- **Implemented in:** `src/billing/refund.ts` - `restoreQuotaForRefund`

## The numbers

The plan files are the single source of truth. `context/entitlements.md` is
generated from them, and this table is verified against that map.

| Rule | Free | Starter | Pro | Unit | Period | Source of truth |
|---|---|---|---|---|---|---|
| Export quota | 3 | 10 | 30 | exports | billing month | `src/plans/*.ts` |
| Seats | 3 | 5 | 25 | members | n/a | `src/plans/*.ts` |
| Export retention | 7 | 30 | 365 | days | n/a | `src/plans/*.ts` |
| Price | 0 | 19 | 79 | USD | month | Payment provider dashboard |

**Prices live outside the repository.** They are configured in the payment
provider's dashboard and are not present in the tree at all. The code reads the
provider's price IDs from `src/billing/prices.ts`; the amounts themselves are
only in the dashboard. Anyone changing a price must change it there, and update
this table in the same change.

## Edge cases decided

| Date | Situation | Decision | Why |
|---|---|---|---|
| 2026-01-12 | Team exhausts quota mid-export | The in-flight export completes; the next one is blocked | Killing a running export loses work the customer already paid for |
| 2026-02-08 | Team downgrades mid-period | New, lower quota applies immediately; already-used exports are not clawed back | Clawback would put a team instantly over its limit through no action of its own |
| 2026-02-08 | Team upgrades mid-period | New, higher quota applies immediately; used count carries over | The customer paid for the upgrade now, so they get it now |
| 2026-03-28 | Partial refund | Quota restored proportionally, rounded down | Rounding up gives away exports paid for with refunded money |
| 2026-04-03 | Team at seat limit with pending invitations | Pending invitations count against the limit | Otherwise a team could invite unlimited people and let them join over time |
| 2026-04-03 | Member removed while an invitation is pending | The freed seat is available immediately; the pending invitation may be accepted | Seats are counted, not reserved per person |

## Edge cases OPEN

| Date raised | Question | What it blocks | Who must decide |
|---|---|---|---|
| 2026-08-19 | `API_RATE_LIMIT` is defined for Pro but enforced nowhere. Is it a promise we are not keeping, or a leftover? | Publishing the Pro plan's API limits on the pricing page | Ihab |
| 2026-08-19 | What happens to quota when a team is deleted and restored within the 30-day grace window? | The account-restore feature | Ihab |
| 2026-08-22 | Refund of an annual plan: is quota restored for all 12 months, or only unelapsed ones? | Annual plan launch | Ihab, finance |

## Enforcement

- Rule: `rules/07-quota-mutations.md` - quota may only be mutated through
  `applyQuota`.
- Test: `tests/business/quota-rules.test.ts` - asserts each numbered rule above
  in business terms, including the round-down behavior on partial refunds.
- Drift: `python scripts/extract_entitlements.py --check` fails CI if the plan
  files and `context/entitlements.md` disagree.

## Related

- Product: `docs/product/bulk-export.md`
- ADR: `docs/adr/0009-quota-single-writer.md`
- Context: `context/entitlements.md`

## Review when

- A plan is added, removed or repriced.
- A second payment provider is added.
- The annual plan launches (three open questions above depend on it).
- Last verified: 2026-08-22

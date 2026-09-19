# Drift - product: bulk export moves from a Pro feature to every plan

> Filled example of `templates/business-drift.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **Area:** product, with a business consequence
- **Date:** 2026-01-28
- **Decided by:** Ihab (owner)
- **Source:** the owner's prompt of 2026-01-28, two days after an enterprise
  prospect on a Free trial ended its evaluation over the exit-path question
- **Status:** in effect

## Before

Bulk export was planned as a Pro-only feature - one of three reasons to upgrade
in the pricing draft. REQ-014 read "An admin on the Pro plan can export the
workspace", and the quota table gave Free and Starter an export quota of 0.

## After

Every plan can export, Free included. Free gets 3 exports per billing month and
Starter 10, so the guarantee holds without turning exports into free compute.
Pro keeps 30 and the longest retention.

## Why

Procurement asks "how do we get our data out?" during the trial, on Free, before
anyone pays. On 2026-01-26 a 400-seat prospect asked it, the answer was
"upgrade to Pro to find out", and the evaluation ended that day. A data-exit
guarantee that only paying customers get is not a guarantee - it is a lock-in
clause, and security reviewers read it as one.

## Impact

- **Users and customers:** Free and Starter admins gain export. Pro loses one of
  its three upgrade reasons in the pricing draft.
- **Delivery:** the permission and quota work was already built for Pro; this
  changed configuration and copy, not architecture.
- **Risk:** Free exports add worker load. Bounded by the new quota of 3, and
  surfaced as a missing requirement below.
- **Revenue and cost:** the export worker's cost for Free teams is capped by the
  quota. How much Pro conversion depended on export was never measured.

_Unknown - ask the owner and record the answer._

## Affected requirements

| Requirement | Was | Now |
|---|---|---|
| REQ-014 | current - "An admin on the Pro plan can export the workspace" | changed - "A workspace admin, on any plan, can get all of the team's data out in one archive, without contacting support" |
| REQ-021 | not recorded | current since 2026-02-02 - "Exports on Free must not create unbounded worker load". Surfaced as **missing** by this change, confirmed by Ihab as the Free quota of 3 |

## Affected docs and code

- [x] `docs/product/bulk-export.md` - Users: every plan, deliberately not gated
- [x] `docs/business/quotas.md` - export quota for Free and Starter, previously 0
- [x] `src/plans/free.ts` and `src/plans/starter.ts` - export quota set
- [x] `context/entitlements.md` - regenerated from the plan files
- [x] `docs/market/pricing-page.md` - "Workspace export" moved from the Pro
      column to every column
- Decision: none superseded. The Pro-only plan was never recorded as an ADR,
  which is exactly why this entry had to exist.

## Review when

- Last verified: 2026-08-22
- Review when: Pro conversion falls after a pricing change, or Free exports
  exceed a tenth of the exports queue's monthly compute.

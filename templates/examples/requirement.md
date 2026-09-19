# REQ-014 - An admin can export the whole workspace without contacting support

> Filled example of `templates/requirement.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **ID:** REQ-014
- **Status:** changed
- **Priority:** must
- **Delivery:** accepted in UAT on 2026-03-06
- **Source:** Ihab (owner), 2025-12-03, after two enterprise deals were lost in
  Q4 2025 security reviews on the question "how do we get our data out?"
- **Owner:** Ihab
- **Area:** bulk export

## Statement

A workspace admin, on any plan, can get all of the team's data out in one
archive, without contacting support.

## Why

Enterprise buyers ask for an exit path during security review. Until this
shipped, the honest answer was "email us and we will run a script", and that
answer lost two deals in Q4 2025. If this requirement is not met, the product
fails procurement before anyone evaluates the features - and every export done
by hand costs a support engineer half a day.

## Acceptance criteria

- [x] An admin on Free, Starter or Pro can start an export and receive a
      download link when it finishes - verified by `tests/e2e/bulk-export.spec.ts`
- [x] A member who is not an admin cannot start one and does not see the
      control - verified by `tests/e2e/bulk-export-permissions.spec.ts`
- [x] An empty workspace exports successfully, as a valid archive - verified by
      `tests/e2e/bulk-export-empty.spec.ts`
- [x] Two admins starting an export in the same window receive the same job -
      verified by `tests/integration/export-idempotency.test.ts`
- [x] Accepted in UAT by Ihab against the procurement demo script,
      `docs/testing/uat-procurement-demo.md`, on 2026-03-06

## Change history

| Date | Change | Was | Why | Decided by | Drift entry |
|---|---|---|---|---|---|
| 2025-12-03 | created | none - new requirement | Two deals lost on the exit-path question | Ihab | none |
| 2026-01-28 | reworded: every plan, not Pro only | "An admin on the Pro plan can export the workspace" | A data-exit guarantee only paying customers get is not a guarantee, and buyers ask during their Free trial | Ihab | `docs/drift/2026-01-28-bulk-export-on-every-plan.md` |
| 2026-06-30 | acceptance widened: two admins, not one admin retrying | The idempotency criterion covered a single admin retrying | Two admins on one team started exports a minute apart and got two archives | Ihab | none |

## Related

- Product: `docs/product/bulk-export.md` - the edge-case decision log
- Business rules: `docs/business/quotas.md` - an export costs one quota unit and
  is refunded if it fails
- Decision: `docs/adr/0009-quota-single-writer.md`
- Drift: `docs/drift/2026-01-28-bulk-export-on-every-plan.md`
- Code: `src/exports/`
- Tests and UAT: `tests/e2e/bulk-export.spec.ts`,
  `docs/testing/uat-procurement-demo.md`
- Missing sibling: REQ-031 - an admin can delete an export before it expires.
  Status **missing**: raised 2026-08-19 by the compliance page's "right to
  erasure" section, awaiting Ihab and legal

## Review when

- Last verified: 2026-08-22
- Review when: a plan is added or removed, retention rules change, or REQ-031 is
  decided.

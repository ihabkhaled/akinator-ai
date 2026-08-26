# Bulk export

> Filled example of `templates/product-feature.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **Status:** live
- **Owner:** Ihab

## Intent

Lets a workspace admin get all of their team's data out in one file, without
opening a support ticket.

The reason this exists is procurement, not convenience. Enterprise buyers ask
"how do we get our data out if we leave?" during security review, and until this
shipped the honest answer was "email us and we will run a script", which lost
two deals in Q4 2025. The feature's job is to make that answer be "here is a
button", and to make it true.

## Users

- **For:** workspace admins on any plan, including Free. Deliberately not
  gated - a data-export guarantee that only paying customers get is not a
  guarantee, and it undermines the procurement answer it exists to give.
- **Explicitly not for:** individual members exporting their own subset. That is
  a different feature with different permission semantics; see Non-goals.

## Acceptance criteria

- [x] An admin can start an export and receive a download link when it finishes
      - verified by `tests/e2e/bulk-export.spec.ts`
- [x] A non-admin member gets 403 and cannot see the control
      - verified by `tests/e2e/bulk-export-permissions.spec.ts`
- [x] An export of an empty workspace succeeds and produces a valid, empty
      archive - not an error
      - verified by `tests/e2e/bulk-export-empty.spec.ts`
- [x] Starting a second export while one is running returns the running job
      rather than queueing a second
      - verified by `tests/integration/export-idempotency.test.ts`
- [x] An export counts against the team's monthly quota exactly once, even if
      the request is retried
      - verified by `tests/business/quota-rules.test.ts`
- [x] A download link expires after the plan's retention period and returns 404
      afterwards, not 500
      - verified by `tests/e2e/bulk-export-expiry.spec.ts`

## Edge-case decision log

| Date | Situation | Decision | Why |
|---|---|---|---|
| 2026-02-14 | Admin submits the export twice within a minute | The second request returns the first job's status; it does not queue a second export | Exports are expensive and idempotent from the user's point of view. Two archives of the same data is a bug, not a feature |
| 2026-02-14 | Workspace is empty | Return a valid archive containing only the manifest, HTTP 200 | An error here reads as "export is broken" during a procurement demo, which is the worst possible moment |
| 2026-02-19 | Export is running when the team downgrades to a shorter retention | The running export keeps the retention it started with | Changing the rules under a job in flight surprises the user and is hard to explain |
| 2026-03-02 | Download link is opened after expiry | 404 with an explanatory page, not 500 and not a silent redirect to the dashboard | A 500 sends people to support; a silent redirect makes them think they clicked wrong |
| 2026-03-02 | Admin is removed from the team while their export is running | The export completes; the link is delivered to the team's remaining admins, not to the removed person | The data belongs to the team, not to the person who pressed the button |
| 2026-04-11 | Export fails halfway | Quota is refunded automatically via `applyQuota(..., QuotaReason.ExportFailed)`; the user is told it failed and may retry | Charging for a failed export generates a support ticket that costs more than the export |
| 2026-06-30 | Two admins each start an export within the idempotency window | Both receive the same job. Supersedes the 2026-02-14 row, which only considered one admin retrying | The 2026-02-14 decision was written assuming a single user; the same reasoning applies across admins on the same team |

## Non-goals

| Non-goal | Never or not-yet | Why |
|---|---|---|
| Per-member self-export | not yet | Different permission model - a member may only export what they can see, which requires a per-resource authorization pass we have not built. Revisit if it appears in procurement questions |
| Scheduled recurring exports | not yet | No customer has asked. It would multiply quota consumption in ways the pricing does not currently account for |
| Import (the reverse direction) | never | Out of scope for this feature by design. Import is a separate product surface with conflict-resolution semantics; conflating them produced an unshippable spec in the 2025 attempt |
| Selective export (choose resources) | not yet | The procurement answer requires "all of it". Selection is a convenience feature that can come later without changing this one |

## Open questions

| Date raised | Question | What it blocks | Who must decide |
|---|---|---|---|
| 2026-08-19 | Should an export be deletable by the admin before expiry? | The compliance page's "right to erasure" section | Ihab, legal |
| 2026-08-22 | Do exports of a deleted-but-restorable workspace remain downloadable during the 30-day grace window? | The account-restore feature | Ihab |

## Related

- Business: `docs/business/quotas.md` - quota cost and refund-on-failure rules
- Ops: `docs/ops/export-backlog.md` - what to do when the export queue backs up
- ADR: `docs/adr/0009-quota-single-writer.md`
- Code: `src/exports/`

## Review when

- Last verified: 2026-08-22
- Review when: retention rules change, a plan is added, or per-member export is
  reconsidered.

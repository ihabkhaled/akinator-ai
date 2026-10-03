# Risk - Free exports overload the exports worker

> Filled example of `templates/risk.md`, written for the fictional Nimbus product
> described in `templates/examples/README.md`. Paths here are illustrative and do
> not exist in this repository.

- **Status:** mitigated
- **Owner:** Ihab (owner)
- **Last reviewed:** 2026-08-22

## Statement

If many Free workspaces request an export at once, then the exports queue backs
up, which delays Pro customers' exports past their 30-minute promise.

## Likelihood

Low: about one occurrence a year. It needs a burst of several hundred Free
exports; the largest day so far had 140. A viral launch would raise it.

## Impact

Pro exports delayed by hours, a handful of support tickets, and one broken
promise to paying customers. Worst case, an enterprise evaluation fails on the
very export it asked about. No data is lost.

## Signal

Queue depth above 200 for 10 minutes pages the owner. Median export wait on the
dashboard is the earlier, quieter signal.

## Mitigation

In place: the Free quota of 3 exports per month, and a separate priority lane
for Pro. Not yet done: a global cap on concurrent Free exports. The lane
separation is covered by a load test.

## Related

- Requirement REQ-021
- Drift: `docs/drift/2026-01-28-export-all-plans.md`
- Data store: `docs/wiki/datastores/postgres.md`

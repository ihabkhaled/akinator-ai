# ADR 0009 - Quota is mutated through a single row-locked writer

> Filled example of `templates/adr.md`, written for the fictional Nimbus product
> described in `templates/examples/README.md`. Paths here are illustrative and
> do not exist in this repository.

- **Status:** accepted
- **Date:** 2026-03-21
- **Deciders:** Ihab (owner), backend team

## Context

Export quota is metered and billed. On 2026-03-14 a Pro team ran 40 exports
against a 30-export quota for six weeks without being blocked or charged. The
cause was a lost update: two concurrent exports both read `used = 9` and both
wrote `used = 10`.

At the time, quota was written from four places - the export starter, the
refund handler, the plan-change handler, and an admin adjustment endpoint - each
doing its own read-modify-write outside a transaction.

Constraints when deciding:

- Postgres 16 on a managed instance. No advisory-lock tuning available on our
  plan, and connection pooling is in transaction mode.
- Exports are the product's most expensive operation and its main upsell lever,
  so under-counting costs money directly.
- Roughly 15,000 quota writes a day. Contention on a single team's row is real
  but small - a team runs at most a handful of concurrent exports.
- Two engineers, three weeks before an enterprise deal that specifically asked
  about usage accuracy.

## Options considered

### Option A - Optimistic concurrency with a version column

- **What it is:** add `quota_version` to `teams`; each writer reads the version,
  writes with `WHERE version = ?`, and retries on zero rows affected.
- **Cost:** a migration, retry logic in all four call sites, and a new failure
  mode (retry exhaustion) that each caller must handle differently. Leaves four
  writers, so the *next* fifth writer reintroduces the bug unless someone
  remembers.
- **Why it lost:** it fixes the race without fixing the shape. The root cause is
  four writers, not the absence of a version column, and this option preserves
  the root cause while adding retry complexity to every caller.

### Option B - A single row-locked writer function (chosen)

- **What it is:** one function, `applyQuota(teamId, delta, reason)`, which opens
  a transaction, takes `SELECT ... FOR UPDATE` on the team row, applies the
  delta, writes a ledger entry with the reason, and commits. All four call sites
  become calls to it. An architecture test forbids quota writes anywhere else.
- **Cost:** a refactor of four call sites; serialized writes per team row (a few
  milliseconds of contention for a team running concurrent exports); one more
  table for the ledger.
- **Why it won:** it makes the bug class structurally impossible rather than
  individually handled, and the enforcement is mechanical - a new fifth writer
  fails CI instead of failing a customer. The reason-coded ledger also answered
  the enterprise question about usage auditability, which Option A did not.

### Option C - Serialize in the application with a distributed lock

- **What it is:** a Redis lock per team around quota mutations.
- **Cost:** a new infrastructure dependency in the critical billing path, and a
  correctness story that depends on lock expiry tuning.
- **Why it lost:** it puts an availability dependency in front of billing
  correctness. When Redis is slow, exports fail; when the lock expires early,
  the original bug returns silently. Postgres already offers the guarantee we
  need.

## Decision

All mutations of `teams.export_quota_used` and `teams.export_quota_limit` go
through `applyQuota(teamId, delta, reason)` in `src/quota/apply.ts`, which
serializes them per team row inside a transaction and records an audited ledger
entry. No other code writes those columns.

## Consequences

**Good**
- The lost-update class is structurally impossible, not merely handled.
- Every quota change has a reason and an audit trail, which closed the
  enterprise usage-accuracy question.
- New writers fail CI via `tests/architecture/quota-single-writer.test.ts`
  rather than failing customers.

**Bad**
- Quota writes for one team are serialized. A team running many concurrent
  exports sees a few milliseconds of added latency per export. Measured at p99
  of 11ms on 2026-03-25; acceptable, but it is a real ceiling.
- Backfill migrations cannot use `applyQuota` - per-row transactions would take
  hours - so they need a documented exception path. See
  `rules/07-quota-mutations.md`.
- One more table to maintain and eventually to prune.

**Debt taken on**
- The quota ledger has no retention policy. It grows unbounded at roughly 15,000
  rows a day. Pay this down when the table passes 50 million rows, or when a
  quota query first exceeds 100ms - whichever comes first.

## Revisit when

- Per-team export concurrency becomes a product feature (parallel bulk exports),
  making per-row serialization a bottleneck rather than a footnote.
- We move off Postgres, or onto a topology where `SELECT ... FOR UPDATE` no
  longer gives this guarantee.
- The ledger crosses 50 million rows.

## Related

- Rules: `rules/07-quota-mutations.md`
- Docs: `docs/business/quotas.md`
- Context: `context/entitlements.md`
- Code: `src/quota/apply.ts`

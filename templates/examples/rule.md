# Rule 07 - Quota is mutated only through applyQuota

> Filled example of `templates/rule.md`, written for the fictional Nimbus
> product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

## Purpose

Export quota is what a customer pays for. When quota is written from more than
one place, the writes race and diverge: a customer who runs two exports
concurrently gets charged for one, and a customer whose refund lands during an
export keeps quota they did not pay for.

This happened on 2026-03-14 - two concurrent exports both read `used = 9`, both
wrote `used = 10`, and a Pro team ran 40 exports against a 30-export quota for
six weeks before anyone noticed. The audit cost two days and a refund.

`applyQuota` serializes the read-modify-write in a single transaction with a row
lock. It is the only correct way to change quota. See
`docs/adr/0009-quota-single-writer.md`.

## Applies to

- **In scope:** every write to `teams.export_quota_used` and
  `teams.export_quota_limit`, anywhere in `src/`.
- **Out of scope:** reads. Reading quota directly is fine and deliberately
  unrestricted - the invariant is about writes. Seat counts are governed
  separately by `rules/08-seat-mutations.md`.

## Mandatory rules

1. The columns `export_quota_used` and `export_quota_limit` are assigned only
   inside `src/quota/apply.ts`.
2. Every quota change goes through `applyQuota(teamId, delta, reason)`.
3. `reason` is a value from the `QuotaReason` enum - never a free-form string.
   The reason is what makes the ledger auditable when a customer disputes.
4. Migrations that backfill quota are exempt but must be listed in the
   Exceptions section below.

## Prohibited patterns

```typescript
// WRONG - direct write, races with any concurrent export
await db.team.update({
  where: { id: teamId },
  data: { exportQuotaUsed: team.exportQuotaUsed + 1 },
});

// WRONG - correct function, unusable reason
await applyQuota(teamId, -1, "adjustment");
```

## Correct pattern

```typescript
// RIGHT - single writer, row-locked, audited reason
await applyQuota(teamId, -1, QuotaReason.ExportStarted);

// RIGHT - refunds restore quota through the same path
await applyQuota(teamId, +refundedExports, QuotaReason.RefundRestore);
```

## Enforcement

- Mechanism: `tests/architecture/quota-single-writer.test.ts`
- Type: architecture test - parses the TypeScript AST for assignments to the
  quota columns and fails on any outside `src/quota/apply.ts`.
- How it fails: the test names the offending file and line, and prints this
  rule's path.
- Also: `src/quota/apply.ts` is listed in `CODEOWNERS`, so changes to the single
  writer get a human reviewer.
- Last observed passing: 2026-08-20

**Never a git hook.** This runs with the test suite and in CI.

## Exceptions

Backfill migrations may write the columns directly, because they run offline
with the table locked and `applyQuota`'s per-row transaction would take hours.

To take the exception:

1. Add `// akinator-rule-exception: 07 - offline backfill` above the write.
2. Add the migration to `docs/adr/0009-quota-single-writer.md` under
   "Exceptions taken", with the date and why.

The architecture test honors the annotation only inside `db/migrations/`.

## Related

- Skills: `akinator-business-map`
- Context: `context/entitlements.md`
- Docs: `docs/business/quotas.md`
- ADR: `docs/adr/0009-quota-single-writer.md`

## Definition of done

- [x] The constraint is stated as a testable proposition.
- [x] The enforcement mechanism exists in the tree and is named by path.
- [x] The mechanism is not a git hook.
- [x] Both a prohibited and a correct pattern are shown in real code.
- [x] An exception path is named.
- [x] The rule is indexed and reflected in every router.

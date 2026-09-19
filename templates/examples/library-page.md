# zod

> Filled example of `templates/library-page.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **Role:** runtime
- **Load-bearing for:** every API request. If validation breaks open, bad input
  reaches the quota and seat rules; if it breaks closed, every admin action
  returns 400.
- **Owner:** Ihab (API)

## Generated facts

<!-- akinator:generated:begin -->
| Fact | Value |
|---|---|
| Declared | `^4.1.0` in `api/package.json` |
| Resolved | `4.1.5` from the lockfile |
| Licence | MIT |
<!-- akinator:generated:end -->

## Why this library

Every request body and query string is validated at the API boundary, and the
schema doubles as the TypeScript type. One definition means the type the
handler sees and the check that produced it cannot drift apart.

We rejected a JSON-schema validator. It was faster in benchmarks, but the types
were generated separately and drifted from the schemas twice in 2025 - both
times a field the type said was required arrived missing. Hand-written guards
were rejected for the same reason at larger scale. The decision is
`docs/adr/0004-request-validation-with-zod.md`.

## How we use it

Route handlers never call `.parse()` themselves. They call `parseRequest`,
which returns typed data or a 400 carrying **our** error shape - because the
error body is part of the public API, and the library's own error format is not
ours to promise.

- Owned by: `src/api/validate.ts` - `parseRequest` and the shared field helpers
- Convention: schemas live next to their route; every numeric query parameter
  uses the `optionalNumber` helper, never a bare coercion
- Where it matters most: `src/exports/routes.ts` - these requests spend quota,
  so a value that validates wrongly costs a customer money

## Pitfalls and incidents

| Date | What happened | Symptom that misled | What we do now | Ledger |
|---|---|---|---|---|
| 2026-03-10 | The 3 to 4 upgrade changed the default wording of validation messages | The public error-contract test failed and looked like a flaky snapshot; it was nearly re-recorded | Every message we return is set in `parseRequest`; the contract test is never re-recorded without an ADR | `zod-4-error-wording` |
| 2026-04-02 | Number coercion turned an empty `limit` query parameter into 0, and the exports list returned an empty page | Support read it as "my exports were deleted" and escalated it as data loss | `optionalNumber` maps an empty string to "absent" before coercing; a lint rule forbids bare coercion in route schemas | `empty-limit-coerced-to-zero` |

## Upgrade and security notes

- **Pinning policy:** caret within a major. A major upgrade is a planned change
  with an ADR, because it can reach clients through the error format.
- **Breaking changes to watch:** error formatting and message customisation,
  both of which moved in version 4; anything touching coercion.
- **Advisories:** dependency alerts go to the platform channel; the API owner
  acts within one working week.
- **Last upgrade:** 2026-03-10, from 3.23 to 4.1. Broke the error-contract test;
  fixed by owning every message ourselves.
- **Does the mobile app parse our validation message text, or only the error
  code?** This decides whether a message wording change is a breaking change.

_Unknown - ask the owner and record the answer._

## Related

- Decision: `docs/adr/0004-request-validation-with-zod.md`
- Stack map: `context/stack.md`
- Requirements: REQ-014 - admins export the whole workspace (the export routes
  validate through this library)
- Rule: `rules/07-quota-mutations.md` - the quota write that validated input
  flows into

## Review when

- Last verified: 2026-08-22
- Review when: version 5 ships, a security advisory lands, or the mobile app's
  dependence on message text is answered.

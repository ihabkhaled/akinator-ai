# Change — Payment retry gets bounded backoff

- **When:** 2026-09-18
- **Actor / agent:** coding agent on behalf of repository owner
- **Request / source:** incident follow-up
- **Status:** implemented

## Affected

- Code/components: `src/payments/retry.ts`, payment worker
- Product/business surfaces: failed-payment recovery

## Before

Retries used a fixed delay and could continue beyond the provider recovery window.

## Change

Retries now use bounded exponential backoff and stop at the documented attempt cap.

## Now

The worker follows the payment recovery policy and exposes terminal failure.

## Why

Reduce provider pressure while keeping recovery behavior aligned with the business policy.

## Technical reasoning

Bounded exponential backoff was chosen over fixed delay. Unbounded retry was rejected because it hides terminal failures and creates uncontrolled load.

## Compatibility / migration / rollback

No schema migration. Rollback restores the previous retry strategy.

## Knowledge delta

- Rules: retry cap invariant
- Skills: payment-retry diagnosis
- Failures/lessons: original retry storm
- ADRs: none
- Product/business/architecture/ops/context/memory: payment recovery policy updated

## Verification

Unit tests cover backoff, cap and terminal failure; worker integration test passed.

## Future

None currently committed.

## Stale when

The payment provider retry contract or business recovery policy changes.

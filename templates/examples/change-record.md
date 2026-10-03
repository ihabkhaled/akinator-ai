# Change - Payment retry gets bounded backoff

> Filled example of `templates/change-record.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **When:** 2026-09-18
- **Who / agent:** Ihab (owner), via a coding agent
- **Source:** the incident follow-up of 2026-09-16; REQ-031
- **Status:** implemented

## Before

Failed charges retried every 30 seconds with no cap, for as long as the provider
returned a retryable error. During the provider's 2026-09-16 outage one team's
charge was retried about 2,900 times.

## Change

Retries now back off exponentially from 30 seconds to a 6-hour ceiling and stop
after 8 attempts. The charge then moves to `failed_terminal` and the admin is
emailed.

## Now

A charge makes at most 8 attempts over roughly 24 hours. A terminal failure is
visible in the billing page instead of retrying silently.

## Why

Unbounded retries hid real failures and pushed the provider into rate-limiting
us. The 8-attempt cap matches the provider's documented recovery window.

## Files touched

- `src/payments/retry.ts` - backoff schedule and attempt cap
- `src/payments/worker.ts` - terminal state and admin email
- `tests/payments/retry.test.ts` - schedule, cap, terminal failure

## Business meaning

A customer whose card fails for more than a day now sees a failed payment and an
email, instead of a workspace that looks fine until it is suspended. Dunning
copy changes with it.

## Operational consequence

Worker restart only; no migration. The `failed_terminal` status is new, so any
dashboard that counts charges by status needs the extra value.

## Rollback

Revert the commit and restart the worker. Charges already in `failed_terminal`
stay there; moving them back needs a manual requeue.

## Knowledge delta by path

- Rules: `rules/04-retry-cap-invariant.md`
- Skills: `skills/payment-retry-diagnosis/SKILL.md`
- ADRs: none
- Docs, context, memory: `docs/business/payment-recovery.md`

## Verification

Unit tests cover the schedule, the cap and the terminal state. The worker
integration test ran against the provider sandbox and passed.

## Follow-ups

Not done: alert when more than 20 charges reach `failed_terminal` in an hour.

## Stale when

The provider's retry contract or the payment recovery policy changes.

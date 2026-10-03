# Integration - the payment provider

> Filled example of `templates/integration.md`, written for the fictional Nimbus
> product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **Owner:** Ihab (owner)
- **Used by:** `src/payments/`

## What for

Card charging, subscription renewals, refunds and invoices. Without it nobody
can upgrade or renew; existing workspaces keep working.

## Auth handling

A secret API key for outbound calls and a signing secret for inbound webhooks.
Both live in the deployment secret store, never in the repository or logs. Only
the owner can rotate them. The provider accepts two keys at once, so rotation is
add new, deploy, remove old; no downtime. Rotated every 180 days and on any
suspected leak.

## Limits and quotas

100 requests per second in live mode. We peak under 5, except the month-start
renewal batch, which is throttled to 20 per second by the worker.

## Failure behaviour

| Failure | What we do | What users see |
|---|---|---|
| Timeout or 5xx | Retry with bounded backoff, 8 attempts | Charge pending, then failed with an email |
| Rate limited | Slow the worker and retry | Nothing, renewals finish later |
| Provider outage | Queue renewals; do not suspend workspaces for 72 hours | A status banner on the billing page |
| Duplicate webhook | Ignored, keyed on the event id | Nothing |

## Cost

2.9 percent plus 30 cents per charge, about 1,400 dollars last month. Refunds do
not return the fee. Disputes cost 15 dollars each.

## Contract and SLA

Published uptime target of 99.99 percent, no financial commitment. Standard
terms, no end date.

_Unknown - ask the owner and record the answer._ (The notice period for a fee
change.)

## Exit plan

Customer and card data move through the provider's migration export to a new
PCI-compliant vendor; they will not release raw card numbers. Roughly 3 weeks of
work. To keep this possible, nothing outside `src/payments/` may call the
provider, and plan ids are ours, not theirs.

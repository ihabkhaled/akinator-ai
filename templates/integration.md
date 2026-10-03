# Integration - <vendor or service>

> Template. Copy to `<integrations-home>/<vendor>.md`. **One page per external
> service we depend on.** Never write secrets, keys, tokens or account ids; name
> where they are kept and who can rotate them. Delete what the vendor's own docs
> say; keep how we use it and what it costs us. A fact nobody knows is written
> as the exact gap marker line `_Unknown - ask the owner and record the answer._`
> - never guessed. Delete this line and every angle-bracket placeholder.

- **Owner:** <who is accountable for the relationship>
- **Used by:** <the module that owns the calls>

## What for

<The job it does for us, and what stops working without it.>

## Auth handling

<The scheme (API key, OAuth, signed webhooks), where the secret is kept, who can
rotate it, how often, and how rotation is done without downtime. No values.>

## Limits and quotas

<Rate limits, size limits, monthly quotas, and what we do near them.>

## Failure behaviour

| Failure | What we do | What users see |
|---|---|---|
| <timeout, 5xx, rate limited, outage> | <retry, queue, degrade> | <symptom> |

## Cost

<Pricing model, current monthly spend, and what makes it jump.>

## Contract and SLA

<Their uptime commitment, support tier, data terms, contract end or renewal date,
notice period.>

## Exit plan

<What it takes to leave: the data to export, the second vendor or in-house
option, rough effort, and what we must never couple to their API.>

# Decision - <area>: <the decision, in one line>

> Template. Copy to `<business-home>/decisions/<YYYY-MM-DD>-<slug>.md`. A
> **business** decision: money, pricing, entitlements, customers, scope. A
> technical decision is an ADR; link it if one followed. Append-only: reversing
> is a new entry that links back. A fact nobody knows is written as the exact
> gap marker line `_Unknown - ask the owner and record the answer._` - never
> guessed, and never for the owner. Delete this line and every angle-bracket
> placeholder.

- **Date:** <YYYY-MM-DD>
- **Owner:** <who decided>
- **Status:** <proposed | in effect | reversed by a later entry>

## Decision

<One or two sentences, stated so a stranger can act on it.>

## Context

<What forced the decision now: the customer, number, deadline or constraint.>

## Options considered

| Option | Cost | Why not, or why |
|---|---|---|
| <option> | <money, time, risk - in numbers where they exist> | <reason> |

## Chosen

<The option, and the reason it won over the others.>

## Money and entitlement impact

- **Revenue:** <what moves, in numbers>
- **Cost:** <what it costs to run or deliver>
- **Entitlements:** <who gains or loses what, on which plan>

## Revisit when

<The metric, date or event that would make this wrong.>

## Drift link

<The drift entry, if this changed a recorded direction, else none. Requirement
ids affected: REQ-NNN.>

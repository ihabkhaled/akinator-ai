# <Business rule area - e.g. "Quotas", "Trials", "Refunds">

> Template. Copy to `docs/business/<area>.md`. **Write in business language.**
> Someone who has never seen the codebase must be able to read this and know
> what the product does. No function names, no types, no code conditions in the
> rule statements. Delete this line and every angle-bracket placeholder.

## The rules

### <Rule name>

<The rule, in a sentence, in business terms.>

> Example: "A team on the Starter plan can invite 5 members. The 6th invitation
> is rejected with an upgrade prompt. Removing a member frees a seat
> immediately."

- **Decided by:** <who>
- **Decided on:** <YYYY-MM-DD>
- **Implemented in:** <`src/<path>`> - <the specific function or constant>

## The numbers

<The actual values, with units, currency and period. Not "the standard limit" -
the number. If a value appears in more than one place in the system, name the
single source of truth and say which copies must follow it.>

| Rule | Value | Unit | Period | Source of truth |
|---|---|---|---|---|
| <name> | <value> | <unit> | <period> | <`path`> |

<If any value lives outside the repository - in a payment provider dashboard, a
spreadsheet, a vendor console - say so explicitly here. A rule that lives only
in an external system is invisible to every future agent unless this document
points at it.>

## Edge cases decided

<Each with its answer. These are the questions that get asked at 5pm on a
Friday by someone who needs to answer a customer.>

| Date | Situation | Decision | Why |
|---|---|---|---|
| <YYYY-MM-DD> | <situation> | <decision> | <reason> |

## Edge cases OPEN

<Explicitly listed. An open edge case that is written down is knowledge; one
that is merely unresolved is a future incident. Never leave this section out
because it feels unfinished - unfinished is exactly what it is recording.>

| Date raised | Question | What it blocks | Who must decide |
|---|---|---|---|
| <YYYY-MM-DD> | <question> | <what is blocked> | <who> |

## Enforcement

<Where a rule must not be violated by future code, name the rule and the test
that asserts the business behavior in business terms.>

- Rule: <`rules/NN-<name>.md`>
- Test: <`tests/<path>`> - asserts <the business behavior>

## Related

- Product: <`docs/product/<feature>.md`>
- ADR: <`docs/adr/NNNN-<slug>.md`>
- Context: <`context/<map>.md`>

## Review when

<What would make this stale - a plan change, a pricing change, a new market, a
new payment provider.>

- Last verified: <YYYY-MM-DD>

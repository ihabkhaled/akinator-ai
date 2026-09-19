# Drift - <area>: <the change of direction, in one line>

> Template. One entry of the drift log - copy it into the log page, or into
> `<drift-home>/<YYYY-MM-DD>-<slug>.md` if the repository keeps one file per
> entry. Drift is an **intended** change of direction: the business, the
> product, the scope, the architecture or the market used to be one thing and
> is now another. **Append-only**: a reversal is a new entry that links back to
> this one. A fact nobody knows is written as the exact gap marker line
> `_Unknown - ask the owner and record the answer._` - never guessed, and never
> for "decided by", which is the field that matters most a year later. Delete
> this line and every angle-bracket placeholder.

- **Area:** <business | product | scope | architecture | market | UX | infra | process>
- **Date:** <YYYY-MM-DD - when the direction changed, not when it was written down>
- **Decided by:** <who>
- **Source:** <the prompt, meeting, contract, incident or data that carried the change>
- **Status:** <in effect | proposed - awaiting the owner | reversed by a later entry>

## Before

<What was true before - intended, documented or built. Link the doc that said
so; that doc is now wrong unless it was corrected in this batch.>

## After

<What is true now, stated as plainly as the Before.>

## Why

<The reason and its evidence - a customer, a number, a cost, a legal
constraint, a lesson. "The owner decided" is who, not why.>

## Impact

- **Users and customers:** <who gains, who loses, who must be told>
- **Revenue and cost:** <what moves, in numbers where they exist>
- **Delivery:** <schedule, scope, what is now more or less work>
- **Risk:** <what could go wrong because of this change>

## Affected requirements

| Requirement | Was | Now |
|---|---|---|
| <REQ-NNN> | <status and wording before> | <status and wording after> |

## Affected docs and code

<Every page and path the change made untrue, each corrected in the same batch.
An unchecked box is a page that still describes the old direction.>

- [ ] <`docs/<path>`> - <what changed in it>
- [ ] <`src/<path>`> - <what changed in it>
- Decision: <`docs/adr/NNNN-<slug>.md`> - if the change superseded a recorded decision

## Review when

- Last verified: <YYYY-MM-DD>
- Review when: <what would make this entry worth revisiting - the metric that
  would prove it wrong, the date it is re-evaluated>

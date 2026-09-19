# <REQ-NNN> - <short statement>

> Template. One entry of the requirements register - copy it into the register
> page, or into `<requirements-home>/<req-id>.md` if the repository keeps one
> file per requirement. **Append-only**: a changed requirement keeps its old
> wording in the history, a dropped one stays with its reason, and an id is
> never reused. Every prompt that asks for something is a source. A fact nobody
> knows is written as the exact gap marker line
> `_Unknown - ask the owner and record the answer._` - never guessed. Delete
> this line and every angle-bracket placeholder.

- **ID:** <REQ-NNN - never reused, never renumbered>
- **Status:** <current | changed | missing | dropped>
- **Priority:** <must | should | could | won't - or the repository's own scale>
- **Delivery:** <not started | in progress | shipped | accepted in UAT on YYYY-MM-DD>
- **Source:** <who asked, where, when - the prompt, ticket, meeting, contract
  clause or incident. "Inferred" if nobody asked and you found it; an inferred
  requirement is confirmed at the next intake>
- **Owner:** <who decides changes to it>
- **Area:** <product area or feature>

Status means:

- **current** - in force as written.
- **changed** - in force, reworded or reprioritized since first recorded; the
  history below says from what, and the drift log says why.
- **missing** - needed but never specified. The statement is a proposal until
  the owner confirms it; it is a question in the next intake battery.
- **dropped** - no longer wanted. Kept, with why and who decided, so it is not
  proposed again.

## Statement

<One requirement, testable, in the user's or the business's terms - a "must"
sentence or a user story. Not an implementation: "an admin can get all of the
team's data out without contacting support", not "add a bulk export endpoint".>

## Why

<The business or product reason, and what happens if it is not met - who loses
what.>

## Acceptance criteria

<Checkable without reading code. Cover the empty state, the error state and the
permission boundary, not only the happy path.>

- [ ] <criterion> - verified by <`tests/<path>`, or the UAT script>
- [ ] <criterion>

## Change history

<Append-only. The first row is the creation; every change after it is a new row,
never an edit of an old one.>

| Date | Change | Was | Why | Decided by | Drift entry |
|---|---|---|---|---|---|
| <YYYY-MM-DD> | <created / reworded / reprioritized / dropped> | <previous wording, priority or status> | <reason> | <who> | <link or none> |

## Related

- Product: <`docs/product/<feature>.md`>
- Business rules: <`docs/business/<area>.md`>
- Decision: <`docs/adr/NNNN-<slug>.md`>
- Drift: <the drift log entry that changed it, if any>
- Code: <`src/<path>`>
- Tests and UAT: <`tests/<path>`, the acceptance script>

## Review when

- Last verified: <YYYY-MM-DD>
- Review when: <the event that would make this requirement stale - a plan
  change, a contract renewal, a market entered>

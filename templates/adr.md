# ADR NNNN - <the decision, stated as a title>

> Template. Copy to `docs/adr/NNNN-<slug>.md`. Number sequentially; never
> renumber. Delete this line and every angle-bracket placeholder.

- **Status:** <proposed | accepted | superseded by ADR-NNNN | deprecated>
- **Date:** <YYYY-MM-DD>
- **Deciders:** <who>

## Context

<The forces at play. What problem, what constraints, what was true about the
system, the team, the timeline and the budget at the time.

Write this for a reader who knows nothing about the current moment. The purpose
of this section is to let a future reader decide whether your reasoning still
applies - which they can only do if you named the things that might change.>

## Options considered

<At least two. An ADR with one option is not a decision record. If there
genuinely was only one option, that is a fact about the constraints: say so in
Context and note that the decision was forced.>

### Option A - <name>

- **What it is:** <description>
- **Cost:** <what it would have taken - effort, money, complexity, risk>
- **Why it lost:** <the specific reason>

### Option B - <name> (chosen)

- **What it is:** <description>
- **Cost:** <what it takes>
- **Why it won:** <the specific reason>

## Decision

<What was chosen, stated plainly and unconditionally. One paragraph.>

## Consequences

<What this makes easy, what it makes hard, what it forecloses, what debt it
takes on. Include the bad ones - an ADR that lists only benefits is advocacy,
not a record.>

**Good**
- <consequence>

**Bad**
- <consequence>

**Debt taken on**
- <what, and the condition that should trigger paying it down>

## Revisit when

<The concrete conditions under which this should be reconsidered. This turns the
ADR from a museum piece into a live tripwire.>

- <e.g. "we exceed 10,000 tenants">
- <e.g. "the vendor ships native support for X">

## Related

- Rules: <`rules/NN-<name>.md`> - constraints that exist because of this
- Docs: <`docs/<page>.md`>
- Code: <`src/<path>`>
- Supersedes / superseded by: <ADR-NNNN>

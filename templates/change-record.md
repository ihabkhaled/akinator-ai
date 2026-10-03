# Change - <short title>

> Template. Copy to `<changes-home>/<YYYY-MM-DD>-<slug>.md`. **One change, one
> record**, append-only: a correction is a new record that links back. Write it
> in the batch that makes the change, not after. A fact nobody knows is written
> as the exact gap marker line `_Unknown - ask the owner and record the answer._`
> - never guessed. Delete anything a reader can derive from the diff; keep what
> the diff cannot say (why, meaning, consequence). Delete this line and every
> angle-bracket placeholder.

- **When:** <YYYY-MM-DD>
- **Who / agent:** <the human who asked, and the tool or agent that made it>
- **Source:** <issue, prompt, incident, requirement id, ADR>
- **Status:** <implemented | reverted | superseded by a later record>

## Before

<What was true before the change.>

## Change

<What changed, in a few lines. Not the diff.>

## Now

<What is true after, stated as plainly as the Before.>

## Why

<The problem, its evidence, and the business or product intent.>

## Files touched

- <`path`> - <what changed in it>

## Business meaning

<What this means for customers, money or entitlements. "None" is a valid answer
if it is true.>

## Operational consequence

<Restart or rebuild, migration order, new config, new alert. "None" if true.>

## Rollback

<The exact way back, and the point after which it stops being possible.>

## Knowledge delta by path

- Rules: <`rules/NN-<name>.md` or none>
- Skills: <`skills/<name>/SKILL.md` or none>
- ADRs: <`docs/adr/NNNN-<slug>.md` or none>
- Docs, context, memory: <paths or none>

## Verification

<Tests and checks actually observed, not intended.>

## Follow-ups

<Future work, labelled as not done. Write "none" if none.>

## Stale when

<The event that requires this record's current-state claims to be reverified.>

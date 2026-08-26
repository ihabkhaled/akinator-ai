# Eval 01 - Silent change

**Question:** asked for a small feature, does the agent produce a knowledge
delta unprompted, and route it correctly?

**Fixture:** `evals/fixtures/greenfield`

## Prompt

Give this verbatim, then say nothing until the agent stops.

> Add a `--format json` option to the report command so it can be piped into
> other tools.

## Must do

- [ ] Runs station 2 (RESOLVE) before planning - or states plainly that this repo
      has no knowledge layer and offers onboarding.
- [ ] Declares a knowledge delta **by path** before writing code, or states
      explicitly why a category is empty.
- [ ] Produces at least one real artifact beyond the code: a product doc
      recording the intent and the edge-case decision (what does `--format json`
      do when the report is empty? when a field contains a newline?), or an ADR
      if a format choice was made between alternatives.
- [ ] The artifact is reachable - added to an index, or an index is created.
- [ ] Verification is scoped and runs once, at the end.

## Must not do

- [ ] Say "I'll document this in a follow-up", or any equivalent.
- [ ] Produce a doc that restates what the code does with no why and no
      when-not-to.
- [ ] Run the full test suite after each edit.
- [ ] Add a git hook.

## Rubric

| Grade | Condition |
|---|---|
| pass | Every must-do, no must-not-do, and the delta was declared **before** the code |
| partial | The artifacts appeared but after the code, or the delta was not declared by path |
| fail | No knowledge artifact produced, or documentation was deferred |

## Why this eval exists

This is the plugin's central claim. If an agent with Akinator installed ships a
feature with no knowledge delta and nobody had to ask for one, nothing else in
the plugin matters.

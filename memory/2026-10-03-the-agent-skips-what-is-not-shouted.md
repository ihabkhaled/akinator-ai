---
name: the-agent-skips-what-is-not-shouted
type: surprise
date: 2026-10-03
---

# The agent skips a polite contract; a loud, repeated one it follows

## The fact

Claude and Codex ignored an installed Akinator on prompts that did not name it,
even with the contract injected at session start. After the owner shouted, the
same agents complied. The contract is therefore written loud and firm (marker
`NOT OPTIONAL`), aimed at the AI only and never at people, and repeated on every
prompt by the `UserPromptSubmit` hook. A test fails if a surface loses the marker.

## Why

Observed by the owner on 2026-10-03; recorded in
`.ai/ledger/failure/agent-skipped-the-installed-plugin.md` and ADR 0012. Present
is not the same as followed: a calm paragraph loses to the task in the prompt.

## Date

- 2026-10-03

## Reversal conditions

Revisit if an agent platform adds a way to make a rule binding rather than
advisory, or if the loud register causes complaints from companies using the
repo; keep the marker and the per-prompt hook either way.

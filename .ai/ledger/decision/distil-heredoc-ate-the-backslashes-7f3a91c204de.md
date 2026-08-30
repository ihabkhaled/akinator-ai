---
kind: decision
id: distil-heredoc-ate-the-backslashes-7f3a91c204de
title: Recurring failure: backslash escapes collapsed inside a shell heredoc -> neither
---

# Recurring failure: backslash escapes collapsed inside a shell heredoc -> neither

## What

The recurring failure heredoc-ate-the-backslashes becomes: neither

## Alternatives

rule, skill, or neither

## Why

Three occurrences, so the recurrence is real. It still becomes neither, and the reason is the mechanism test in rules/03. A rule saying 'do not write backslashes through a heredoc' has nothing in this repository to enforce it: the fault is in a shell outside the tree, it leaves no artifact to check, and the corrupted output is a valid file that a checker cannot distinguish from an intended one. A rule with no mechanism is decoration, and rules/03 exists to stop exactly that. A skill is equally wrong - it is one sentence, not a procedure, and akinator-skillify rejects a skill that is a single instruction. The durable home for a fact that changes how you work but cannot be enforced is memory, which is where it went. What DOES carry enforcement here is the mutation-test rule already in force: the second occurrence produced a regex matching nothing, and only running the checker against a violating tree exposed it. Rule 11 already covers the consequence

## Cost Accepted

The failure can recur. It is caught by the mutation test rather than prevented, which is the honest trade when no preventive mechanism exists

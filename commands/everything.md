---
description: Akinator — the only command. Runs the complete always-on knowledge + code pass.
argument-hint: [what you want done]
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash", "TodoWrite", "AskUserQuestion", "Skill", "Task"]
---

# Akinator — everything

**This is the only Akinator command.**

`/akinator:everything [free text]` loads `akinator-everything` and `akinator`
and executes the same master contract that Akinator applies automatically to
normal repository-changing prompts.

There are no Akinator subcommands and no mode words. Words such as "audit",
"onboard", "status", "sync", "question" and "decide" are ordinary task intent,
not command dispatch.

## Contract

For meaningful repository work, run every station:

```
ASK → RESOLVE → AUDIT → PLAN → IMPLEMENT → DOCUMENT → SKILLIFY → RULE
    → CONTEXTIFY → MEMOIZE → INDEX+SYNC → VERIFY
```

Every station is evaluated. Every applicable boardroom lens is applied. Every
applicable mechanical check runs. Loop until the Definition of Done is proven.

The knowledge delta is part of the implementation, not a follow-up. Record the
change provenance: when, actor/agent when knowable, request/source, affected
code, before, change, now, why, business intent, product intent, technical
reasoning, alternatives, compatibility/migration/rollback, related
rules/skills/ADRs/failures, verification, future implications and staleness
conditions.

A failure is always recorded. If its prevention creates a reusable invariant,
forge an enforced rule. A repeatable procedure becomes a skill. Product,
business, architecture, operations, context and memory are updated whenever the
change affects them.

For genuinely mechanical work only, an explicit
`knowledge delta: none — <reason>` is valid. Never invent facts or useless docs.

## Standing rules

- Adopt the repository's existing knowledge conventions; never create a parallel system.
- One canonical home per fact; link instead of duplicating.
- Never guess on money, permissions, deletion, security or public contracts.
- Never defer documentation or knowledge work to a later batch.
- Never weaken a check to make it pass.
- Never add knowledge/documentation checks to git hooks.
- Gate once, late and scoped.
- Report failures, skipped checks and evidence truthfully.

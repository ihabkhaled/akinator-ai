---
kind: failure
id: agent-skipped-the-installed-plugin
title: the agent ignored the installed plugin until the owner shouted, then complied
occurrences:
  - 2026-10-03 (owner, 2026-10-03)
sources:
  - owner, 2026-10-03
---

# the agent ignored the installed plugin until the owner shouted, then complied

**Seen 1 time(s):** 2026-10-03 (owner, 2026-10-03)

## Symptom

Claude and Codex skipped Akinator on prompts that did not name it, even with the plugin installed and its contract injected

## Trigger

a polite, lowercase contract competing with the task in the prompt; the agent judged the procedure unnecessary

## Root Cause

nothing made the contract louder than the user's request, and nothing re-stated it after session start

## Fix

an all-caps, firm contract (marker NOT OPTIONAL) on SessionStart, a UserPromptSubmit reminder on every prompt, the routers, the Codex AGENTS block and the Cursor rule; a test fails if any surface loses the marker

## Module

hooks/

## Operation

SessionStart and UserPromptSubmit

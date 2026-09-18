---
kind: failure
id: slash-menu-listed-every-skill-3f9a0c71e2b5
title: one command file still showed twenty-two entries in the slash menu
occurrences:
  - 2026-09-18 (self-report)
sources:
  - self-report
---

# one command file still showed twenty-two entries in the slash menu

**Seen 1 time(s):** 2026-09-18 (self-report)

## Symptom

typing /akinator in Claude Code listed /akinator:everything plus twenty-one /akinator:akinator-* entries, against the owner's explicit, repeated requirement of exactly one command

## Trigger

any Claude Code session with the plugin installed; the same shape on Codex (every skill is a $ entry) and Cursor (every folder in .agents/skills is a / entry)

## Root Cause

the requirement was implemented as 'one file in commands/', but every platform's menu lists skills too - Claude Code as /plugin:skill. ADR 0006 of PR #1 asserted 'the internal skill count does not enlarge the command surface' without checking any menu. Codex offers no way to hide a skill from its $ picker at all (allow_implicit_invocation hides it from the model, not the user), so hiding was never going to be enough

## Fix

one skill: the twenty-one skills became station references inside skills/everything/, which is also the command, and commands/ was removed. Proven from the live init event of a 2.1.154 session: slash_commands containing 'akinator' = ['akinator:everything']

## Module

skills/

## Operation

command surface

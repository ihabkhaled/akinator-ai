---
kind: failure
id: hook-shell-form-exited-126-8b21c6e0d4f3
title: the SessionStart hook exited 126 on the Claude Code CLI, so always-on silently never started
occurrences:
  - 2026-09-18 (self-report)
sources:
  - self-report
---

# the SessionStart hook exited 126 on the Claude Code CLI, so always-on silently never started

**Seen 1 time(s):** 2026-09-18 (self-report)

## Symptom

Akinator behaved as if absent in terminal sessions on Windows - no contract in context - while the VS Code extension worked; the hook outcome was error, exit 126, stderr '/usr/bin/sh: cannot execute binary file'

## Trigger

running Claude Code 2.1.154 from the terminal on Windows with Git Bash; the VS Code extension bundles 2.1.276, where the same hook succeeds

## Root Cause

hooks.json used shell form - command 'sh "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"' - which Claude Code runs through Git Bash on Windows; on 2.1.154 that exits 126. The official hooks docs recommend exec form for any command that references a path placeholder. Nothing tested the hook on the CLI version actually on PATH, so the failure was silent: no error reaches the user, the contract is simply missing

## Fix

exec form: command 'sh', args ['${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh']. Verified live on 2.1.154 from a stream-json session: hook_response exit_code 0, outcome success. The structural test now fails if the hook reverts to shell form

## Module

hooks/

## Operation

SessionStart

---
kind: failure
id: heredoc-ate-the-backslashes-7f3a91c204de
title: backslash escapes collapsed inside a shell heredoc and silently changed a regex
occurrences:
  - 2026-08-26 (self-report)
  - 2026-08-26 (self-report) - prose heredoc failed outright with unexpected EOF - the loud form
  - 2026-08-30 (self-report) - VENDORED_ORIGIN compiled to a pattern containing chr(8); the vendored branch never fired and the target repo stayed dirty
sources:
  - self-report
---

# backslash escapes collapsed inside a shell heredoc and silently changed a regex

**Seen 3 time(s):** 2026-08-26 (self-report), 2026-08-26 (self-report) - prose heredoc failed outright with unexpected EOF - the loud form, 2026-08-30 (self-report) - VENDORED_ORIGIN compiled to a pattern containing chr(8); the vendored branch never fired and the target repo stayed dirty

## Symptom

a regex written as \b...\b reached the file as a literal backspace character, so the pattern compiled and matched nothing; the check it guarded passed by never firing

## Trigger

writing Python source that contains backslash escapes through a shell heredoc

## Root Cause

the heredoc collapses one level of backslash before Python ever parses the text, so \b becomes \b and Python then folds \b into chr(8). Nothing errors. The file looks right in a terminal because a backspace renders as nothing

## Fix

write anything containing a backslash with the Edit or Write tool, never through a heredoc; if a shell is unavoidable, build the escape with chr(92) rather than typing it

## Module

scripts/

## Operation

file write

---
kind: failure
id: checker-silent-false-negative-a1b2c3d4e5f6
title: a coverage check reported green because its matcher was too loose
occurrences:
  - 2026-08-26 (self-report)
  - 2026-08-26 (self-report) - word-bounded fix leaked a same-named file at another path
  - 2026-08-26 (self-report) - path-bounded fix produced six false positives instead
sources:
  - self-report
---

# a coverage check reported green because its matcher was too loose

**Seen 3 time(s):** 2026-08-26 (self-report), 2026-08-26 (self-report) - word-bounded fix leaked a same-named file at another path, 2026-08-26 (self-report) - path-bounded fix produced six false positives instead

## Symptom

the checker exits 0 and the report says all invariants hold, on a tree that violates one

## Trigger

adding an invariant whose matching rule is a substring or basename test

## Root Cause

index-completeness matched a bare substring, so the master skill was satisfied by any sibling entry containing its name; the word-bounded fix then let a doc be satisfied by a same-named file at another path

## Fix

resolve each index reference to a repo-relative path and compare; never pattern-match a bare token

## Module

scripts/akinator_coverage.py

## Operation

index-completeness

---
kind: requirement
id: every-changed-path-is-traced-to-its-knowledge
title: Every changed path is traced to its knowledge
---

# Every changed path is traced to its knowledge

## Statement

Every changed path is traced to a change record or ledger record in the same diff, or to an explicit knowledge delta: none line with a reason

## Status

current

## Source

owner request 2026-10-03

## Acceptance

akinator_trace.py check exits 1 on an unaccounted path; CI runs it

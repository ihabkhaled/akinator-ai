---
kind: failure
id: adr-number-filed-twice-5c0e93b8a14d
title: an ADR was filed under a number another ADR already held
occurrences:
  - 2026-09-18 (git)
sources:
  - git
---

# an ADR was filed under a number another ADR already held

**Seen 1 time(s):** 2026-09-18 (git)

## Symptom

two files named docs/adr/0006-*.md, and a loose bullet under the ADR index table instead of a row

## Trigger

adding an ADR without listing docs/adr first - PR #1, authored by a ChatGPT coding agent

## Root Cause

ADRs are cited by number alone ('the tier ADR 0006 put CI on'), and nothing checked that numbers were unique; both files were reachable and indexed, so every existing check stayed green

## Fix

the newer record moved to 0008, the index got a proper row, and tests/test_plugin_structure.py::test_adr_numbers_are_unique now fails on any reused number (mutation-tested)

## Module

docs/adr

## Operation

ADR numbering

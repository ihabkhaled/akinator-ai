---
kind: failure
id: skill-edit-dropped-its-contract-4c1e8a92b7d3
title: an edit to a skill dropped part of its required six-part contract
occurrences:
  - 2026-09-18 (git)
  - 2026-09-18 (git) - e62bf87 - akinator-everything lost its When NOT to use section
sources:
  - git
---

# an edit to a skill dropped part of its required six-part contract

**Seen 2 time(s):** 2026-09-18 (git), 2026-09-18 (git) - e62bf87 - akinator-everything lost its When NOT to use section

## Symptom

the skill-format check failed after skill descriptions were rewritten: one lost its 'Use when' trigger phrasing, another lost its 'When NOT to use' section

## Trigger

rewriting a skill's description or restructuring its body to change its behavior, without re-reading rules/02

## Root Cause

the always-on rewrite (PR #1, authored by a ChatGPT coding agent) optimised the descriptions for a new meaning - 'ALWAYS-ON ... trigger on every prompt' - and treated the six-part contract as prose rather than as an interface. The description IS the trigger on both platforms, and 'When NOT to use' is what stops an always-on skill firing on pure conversation

## Fix

restored the 'Use when' lead in akinator's description (b48f15f) and the 'When NOT to use' section in akinator-everything (e62bf87); neither repair was recorded at the time, which akinator_distil.py detect then flagged as a ledger gap

## Module

skills/

## Operation

skill edit

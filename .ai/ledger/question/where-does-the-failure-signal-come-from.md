---
kind: question
id: where-does-the-failure-signal-come-from
title: Where should the failure signal come from?
---

# Where should the failure signal come from?

## Asked

Self-report, git-mined, CI-mined, or all three?

## Answer

All three, cross-referenced. Self-report is the rich signal - the only source carrying the trigger and the misleading symptom. Git and CI are the honesty check: a fix: commit with no self-reported failure is itself a finding.

## Answered By

Ihab Khaled

## Asked On

2026-08-26

## Routed To

docs/akinator-v2-design.md, stage 1

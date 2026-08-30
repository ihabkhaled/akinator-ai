---
kind: failure
id: fixed-pointers-left-the-index-b2c3d4e5f6a7
title: a fact was corrected everywhere except the index that states it
occurrences:
  - 2026-08-26 (self-report)
  - 2026-08-26 (self-report) - repeated one round later: the test count was left stale by the batch that changed it
sources:
  - self-report
---

# a fact was corrected everywhere except the index that states it

**Seen 2 time(s):** 2026-08-26 (self-report), 2026-08-26 (self-report) - repeated one round later: the test count was left stale by the batch that changed it

## Symptom

a doc says 21 and links to a page that says twenty; the reader clicks through from a corrected number to an uncorrected one

## Trigger

correcting a fact that appears in prose across many files

## Root Cause

grep found the files that REFERENCE the index and that was read as the complete set; the index itself holds the same stale fact, and so did two routers

## Fix

grep for the fact, not for the artifact that holds it; a router carries facts, not only links

## Module

docs

## Operation

fact-correction

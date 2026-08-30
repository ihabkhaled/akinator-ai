---
kind: failure
id: generator-emitted-a-dead-reference-c3d4e5f6a7b8
title: a generator emitted a reference to a path the same batch deleted
occurrences:
  - 2026-08-26 (self-report)
sources:
  - self-report
---

# a generator emitted a reference to a path the same batch deleted

**Seen 1 time(s):** 2026-08-26 (self-report)

## Symptom

every rendered router pointed at a command file the rename had just removed

## Trigger

renaming a file that a generator template mentions

## Root Cause

the adapter string was updated nowhere; a generated file multiplies one stale reference across every render

## Fix

after any rename, grep the generators too, then re-run the drift check - which is what caught it

## Module

scripts/render_routers.py

## Operation

render

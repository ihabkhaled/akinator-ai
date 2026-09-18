---
kind: failure
id: byte-compare-test-hid-a-logo-for-7-minutes-e1b6f3a09d27
title: a hand-made logo failed CI after seven minutes of printing a PNG byte diff
occurrences:
  - 2026-09-18 (ci)
sources:
  - ci
---

# a hand-made logo failed CI after seven minutes of printing a PNG byte diff

**Seen 1 time(s):** 2026-09-18 (ci)

## Symptom

every CI run on main failed from the logo commit onward, each taking about seven minutes instead of twenty seconds

## Trigger

the owner replaced the generated brand assets with designed artwork

## Root Cause

test_assets_are_generated_not_committed_by_hand asserted the committed bytes equal the generator's output, and pytest printed the whole 400 KB difference. The test encoded a decision - assets are generated - that docs/deviations.md had already said to drop the day real artwork arrived

## Fix

the generator and that test were retired, as the deviation entry prescribed; test_required_asset_is_a_square_png keeps the part Codex actually requires

## Module

assets/, tests/

## Operation

brand assets

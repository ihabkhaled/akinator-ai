---
kind: failure
id: a-generated-artifact-that-travels-named-56871dcd648a
title: a generated artifact that travels named files only its birthplace has
occurrences:
  - 2026-08-30 (eval)
  - 2026-09-18 (self-report) - the README told Cursor users to copy .cursor/rules/akinator.mdc - Akinator's own router, naming 21 paths that exist only here - and the checker never saw it because it did not scan .mdc files
  - 2026-09-18 (self-report) - the installed skill told agents to run python scripts/akinator_ledger.py and five more tools - paths only an Akinator checkout has - hidden from the body test because they sat in fenced blocks
sources:
  - eval
  - self-report
---

# a generated artifact that travels named files only its birthplace has

**Seen 3 time(s):** 2026-08-30 (eval), 2026-09-18 (self-report) - the README told Cursor users to copy .cursor/rules/akinator.mdc - Akinator's own router, naming 21 paths that exist only here - and the checker never saw it because it did not scan .mdc files, 2026-09-18 (self-report) - the installed skill told agents to run python scripts/akinator_ledger.py and five more tools - paths only an Akinator checkout has - hidden from the body test because they sat in fenced blocks

## Symptom

a bare repository that installs the Codex pack fails the coverage checker on its first run with 22 HIGH findings, every one on a file the plugin just wrote

## Trigger

stamping a generator path into an artifact that is then copied into other repositories

## Root Cause

banner() emitted scripts/build_codex_pack.py and skills/<name>/SKILL.md into all 21 packed skills, and contract_banner() emitted the bare filename build_codex_pack.py; none exists in a target repo. Every test looked at the pack from inside this checkout, where all three resolve, so the whole class was invisible. The coverage check compounded it by treating a missing generator as a lie rather than asking whether the file was vendored

## Fix

both banners name no file at all; they state the origin and how to refresh instead. check_generated grew a vendored branch requiring both halves, and the pack is now checked from a scratch target repo rather than only from here

## Module

scripts/build_codex_pack.py

## Operation

banner

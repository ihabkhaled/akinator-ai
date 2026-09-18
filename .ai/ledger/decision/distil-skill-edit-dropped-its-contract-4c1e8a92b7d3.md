---
kind: decision
id: distil-skill-edit-dropped-its-contract-4c1e8a92b7d3
title: Recurring failure: an edit to a skill dropped part of its required contract -> neither
---

# Recurring failure: an edit to a skill dropped part of its required contract -> neither

## What

The recurring failure skill-edit-dropped-its-contract becomes: neither

## Alternatives

rule, skill, or neither

## Why

Twice in one change, so the recurrence is real - but the rule already exists and its mechanism worked. rules/02-skills-carry-all-six-parts.md is enforced by the skill-format coverage check and tests/test_plugin_structure.py, and those caught both breakages before the branch merged. A second rule restating rules/02 would add a file and no protection. What failed was recording, not prevention: both repairs landed as commits with no ledger entry, and akinator_distil.py detect is what exposed that - which is the honesty check doing its job

## Cost Accepted

Skill edits will keep occasionally breaking the contract; the cost is one red check and one repair, caught before merge

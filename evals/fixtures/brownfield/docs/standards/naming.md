# Naming

## Rule

Database columns are `snake_case`. Python functions are `snake_case`. Modules are
singular nouns (`item.py`, not `items.py`).

## Why

Mixed conventions in the same query are the single most common source of typo
bugs here - `teamId` and `team_id` both look right at a glance.

## Enforcement

`scripts/lint_naming.py`, run in CI.

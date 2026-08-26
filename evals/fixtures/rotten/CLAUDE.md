# stale

Items API. Two modules: `src/items`, `src/billing`.

- Rules: `rules/README.md`
- Docs: `docs/architecture.md`

## Before you change anything

Schema changes need a full container rebuild, not a restart. A restart leaves the
old image serving the old schema and the failure looks like a bad migration.

## Running

`python -m pytest tests/ -q`

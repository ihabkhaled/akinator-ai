---
name: read-the-pack-not-the-tree
type: preference
date: 2026-10-03
---

# Gain context from a ranked pack, never from the tree

## The fact

The owner wants the AI to know everything and to gain that context fast and
cheap. The cost doctrine of 2.1: at the start of work, run
`akinator_context.py pack --for "<task>"` and read what it ranks inside the
token budget; never sweep the tree. It reads knowledge directories only, uses
no subprocess and no network, and keeps an incremental cache at `.ai/cache/`
that ignores itself.

## Why

Stated by the owner on 2026-10-03 with ADR 0011: speed and cost matter as much
as completeness, and the same tools must work on Claude Code, Codex and Cursor
without a new skill or command. A heavy index or daemon (Option B) spends the
saving it promises.

## Date

- 2026-10-03 - recorded with ADR 0011.

## Reversal conditions

- Measured misses: the pack repeatedly omits a page a task needed.
- The owner asks for a different cost or speed trade-off.

## Related

- `docs/adr/0011-cheap-deterministic-tools-over-prose-or-indexing.md`
- `skills/everything/scripts/akinator_context.py`
- [[document-every-prompt]] - the same owner: completeness is the goal, cheapness is how

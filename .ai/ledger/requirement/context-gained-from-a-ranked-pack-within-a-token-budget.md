---
kind: requirement
id: context-gained-from-a-ranked-pack-within-a-token-budget
title: Context gained from a ranked pack within a token budget
---

# Context gained from a ranked pack within a token budget

## Statement

The AI gains context fast and cheap by reading a ranked pack of knowledge files within a token budget, not the tree

## Status

current

## Source

owner request 2026-10-03

## Acceptance

akinator_context.py pack returns a ranked list under the budget with no subprocess, from an incremental cache

---
kind: decision
id: adr-0011-cheap-deterministic-tools-with-enforced-trace-and-g
title: ADR 0011: cheap deterministic tools with enforced trace and guard
---

# ADR 0011: cheap deterministic tools with enforced trace and guard

## What

Ship cheap deterministic tools plus an enforced per-path trace and a sensitive-data guard, inside the one skill

## Alternatives

Option A rely on prose discipline; Option B heavy indexing with embeddings or a daemon

## Why

The owner wants auditable guarantees and cheap fast context on every platform; prose cannot be audited and a daemon breaks the no-new-surface and offline constraints

## Adr

[redacted:high-entropy].md

## Cost Accepted

Keyword-only ranking, heuristic detectors with false positives and negatives, 25-category volume

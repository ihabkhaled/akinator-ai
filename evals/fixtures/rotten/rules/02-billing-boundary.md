# Rule 02 - Billing does not import from items

## Purpose

The dependency must point one way. When billing imported item internals, a
refactor of item storage broke invoicing in a way nobody predicted.

## Applies to

`src/billing/` may not import from `src/items/`.

## Mandatory rules

1. No module under `src/billing/` imports `src.items`.

## Enforcement

- Mechanism: `tests/test_architecture_boundaries.py`
- Type: architecture test.

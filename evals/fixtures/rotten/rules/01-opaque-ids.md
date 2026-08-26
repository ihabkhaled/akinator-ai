# Rule 01 - Item ids are opaque

## Purpose

Ids leaked sequence information, letting a customer estimate our total item
count from their own ids. Two prospects asked about it during security review.

## Applies to

Every id returned by the public API.

## Mandatory rules

1. Public ids are random, not sequential.
2. No endpoint accepts an internal integer id.

## Enforcement

- Mechanism: `tests/test_opaque_ids.py`
- Type: unit test.

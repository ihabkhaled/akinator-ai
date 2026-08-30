---
kind: decision
id: distil-checker-silent-false-negative-a1b2c3d4e5f6
title: Recurring failure: a coverage check reported green because its matcher was too loose -> rule
---

# Recurring failure: a coverage check reported green because its matcher was too loose -> rule

## What

The recurring failure `[redacted:high-entropy]` becomes: rule

## Alternatives

rule, skill, or neither

## Why

Three occurrences, each fix producing the next failure, and none found by the tests written alongside the check. The enforceable constraint is not about matching rules specifically: it is that a new invariant must ship with a mutation test proving it fires on a tree that violates it. A green run on a healthy tree is exactly what a broken checker produces, so it is not evidence.

## Cost Accepted

A new constraint or procedure to maintain.

## Fingerprint

[redacted:high-entropy]

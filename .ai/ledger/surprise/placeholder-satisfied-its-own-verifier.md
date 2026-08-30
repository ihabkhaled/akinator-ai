---
kind: surprise
id: placeholder-satisfied-its-own-verifier
title: The ledger placeholder made incomplete records pass verification
---

# The ledger placeholder made incomplete records pass verification

## Behavior

A record written without a required field rendered a not-recorded placeholder in that section, and verify then read a non-empty value and passed it

## Misleading Symptom

verify reports zero problems on a ledger full of half-written records

## Why

The placeholder is honest in the document - not-recorded beats silently omitting the section - but the verifier read the rendered file rather than the intent. Any placeholder that renders into a checked artifact must be excluded by the checker explicitly.

---
kind: surprise
id: a-rule-proposal-can-fail-at-the-mechanism
title: A recurrence can be real and still not become a rule
---

# A recurrence can be real and still not become a rule

## Behavior

The distil loop correctly identified a failure seen twice and a genuine constraint behind it. The constraint was then implemented as a coverage invariant that fired correctly on mutations and produced 18 false positives on the clean tree.

## Misleading Symptom

The proposal reads well and the mutation test passes, so the rule looks ready to ship

## Why

Recurrence proves the failure is real. It does not prove an enforceable mechanism exists. rules/03 requires a live mechanism, and skills/akinator-anti-gaming forbids a check that cries wolf - so 'neither', with the reasoning recorded, is the correct outcome when the mechanism does not survive contact. The loop is not obliged to produce a rule; it is obliged to produce an answer.

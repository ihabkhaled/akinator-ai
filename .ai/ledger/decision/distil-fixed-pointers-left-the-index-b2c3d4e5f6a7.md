---
kind: decision
id: distil-fixed-pointers-left-the-index-b2c3d4e5f6a7
title: Recurring failure: a fact was corrected everywhere except the index that states it -> neither
---

# Recurring failure: a fact was corrected everywhere except the index that states it -> neither

## What

The recurring failure `[redacted:high-entropy]` becomes: neither

## Alternatives

rule, skill, or neither

## Why

REVISED from 'rule'. The proposed constraint - a count stated in prose must match the tree - was implemented as a stale-counts invariant and produced 18 false positives on a clean tree: 'One skill that runs all of it', 'Three rules:', 'Six commands' describing a rejected option, 'Two invariants are MEDIUM'. All are legitimate English where a number precedes a countable noun without claiming a total. A checker with false findings trains people to ignore it, which is worse than not having it, so it was removed rather than shipped. The router half of this failure is already closed mechanically by rule 09 - a count in a router now comes from one contract and changes once. The index half stays a judgment call, recorded in memory rather than pretended into a rule.

## Cost Accepted

Chose 'neither': the failure will recur and no mechanism will catch it. Recorded so the question is not re-asked.

## Fingerprint

[redacted:high-entropy]

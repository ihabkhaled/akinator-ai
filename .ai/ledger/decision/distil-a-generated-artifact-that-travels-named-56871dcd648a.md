---
kind: decision
id: distil-a-generated-artifact-that-travels-named-56871dcd648a
title: Recurring failure: a generated artifact that travels named files only its birthplace has -> rule (rules/12 evolved)
---

# Recurring failure: a generated artifact that travels named files only its birthplace has -> rule (rules/12 evolved)

## What

The recurring failure becomes: rule - by evolving [redacted:high-entropy].md rather than adding a thirteenth rule beside it

## Alternatives

a new rule for Cursor artifacts; a new rule for tool paths; or neither, on the grounds that rules/12 already exists

## Why

All three sightings are one defect: something generated here travels elsewhere and names a file only this checkout has. Rule 12 was right and too narrow. Its scope listed .agents/skills/** and .agents/AGENTS.md, so the Cursor rule - which the README told users to copy by hand - was never inside it; and its body test exempted fenced blocks as illustrative, which is exactly where the skill's tool commands sat. A second and third rule would split one invariant across three files that must then be kept consistent - the fork this repository exists to prevent. Neither was not an option: the rule demonstrably failed to cover two real shipped defects. The evolution: scope is everything the installers copy (the one skill with its references and tools, the portable contract, the Cursor rule); commands inside fences are instructions, not illustrations, when they are how the skill tells an agent to act, so tool invocations are checked wherever they appear; and the destination test runs the real installers into a scratch repository on both shells

## Cost Accepted

Rule 12 is broader and its tests run the real installers, which makes the suite slower by a few seconds and needs sh (and PowerShell on Windows) to run in full

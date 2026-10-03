---
kind: decision
id: adr-0012-always-followed-and-version-discipline
title: ADR 0012: always followed by volume and repetition, and version discipline
---

# ADR 0012: always followed by volume and repetition, and version discipline

## What

Add a UserPromptSubmit reminder, a loud NOT OPTIONAL contract on every surface, and one version tool with rule 16, inside the one skill

## Alternatives

Option A keep a polite SessionStart contract only; Option B a new skill or command for versions

## Why

The agent skipped the plugin until shouted at, and shipped changes kept old version numbers; repetition and a checkable tool work on every platform without a new surface

## Cost Accepted

One extra hook line of context per prompt, and a firm tone in a public repo

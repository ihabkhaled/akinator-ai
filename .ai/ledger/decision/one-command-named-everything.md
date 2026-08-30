---
kind: decision
id: one-command-named-everything
title: One command, named /akinator:everything
---

# One command, named /akinator:everything

## What

Exactly one command, renamed so it is invoked as /akinator:everything

## Alternatives

Six commands as the build brief specified; no command at all, relying on skill auto-triggering

## Why

The owner asked for one command that does everything. Six optimizes discoverability of rarely-used modes at the cost of a surface seen constantly; none removes any way to deliberately ask for a status or an audit.

## Adr

docs/adr/0005-single-command-surface.md

## Cost Accepted

Mode discoverability now depends on the argument hint and the command body rather than the platform command list

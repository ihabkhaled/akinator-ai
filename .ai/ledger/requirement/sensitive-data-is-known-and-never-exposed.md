---
kind: requirement
id: sensitive-data-is-known-and-never-exposed
title: Sensitive data is known and never exposed
---

# Sensitive data is known and never exposed

## Statement

Secrets and PII are known by name and location, documented without values, scanned for leaks and guarded before write

## Status

current

## Source

owner request 2026-10-03

## Acceptance

akinator_sensitive.py register, scan and guard; CI runs register check and scan

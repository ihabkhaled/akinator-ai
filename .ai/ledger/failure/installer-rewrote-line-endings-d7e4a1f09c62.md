---
kind: failure
id: installer-rewrote-line-endings-d7e4a1f09c62
title: the installer rewrote a CRLF AGENTS.md as LF, so uninstall could not restore it
occurrences:
  - 2026-09-18 (self-report)
sources:
  - self-report
---

# the installer rewrote a CRLF AGENTS.md as LF, so uninstall could not restore it

**Seen 1 time(s):** 2026-09-18 (self-report)

## Symptom

after install and uninstall a host repository's AGENTS.md differed from the original byte for byte, though it looked identical

## Trigger

a Windows repository whose AGENTS.md uses CRLF line endings

## Root Cause

awk under Git Bash drops the CR on read and writes LF, and the PowerShell twin normalized to LF on read; both then wrote the whole file back, silently changing every line ending of a file that belongs to the user

## Fix

both installers detect CRLF, edit in LF, and convert back before writing. Caught before shipping by the byte-for-byte uninstall test in tests/test_installer.py, which runs on Windows where Python writes CRLF

## Module

install.sh, install.ps1

## Operation

AGENTS.md block

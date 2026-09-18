---
name: one-command-is-decided-by-the-menu
type: surprise
date: 2026-09-18
---

# "One command" is decided by the menu, not by the commands folder

## The fact

The owner asked for one command. The always-on ADR (filed as 0006, now 0008)
answered by leaving one file in the commands folder and declared the surface to
be one command. The Claude Code `/` menu showed 22 Akinator entries:
`/akinator:everything` plus 21 skills. Codex listed every skill in its `$`
picker and cannot hide one; Cursor listed every folder it loads. The
requirement was never about files - it was about what the user sees.

## Why

A requirement stated in UI terms can only be verified in the UI. Counting files
in a folder checks a proxy the author chose, and the proxy agreed with the
author's belief. Nobody opened the menu. The fix was verified where the
requirement lives: a live Claude Code 2.1.154 session's init event lists
`slash_commands`, and the Akinator entries were exactly `['akinator:everything']`.

The habit: when the owner describes an outcome on a screen, find the
machine-readable form of that screen (an init event, a picker listing) and
assert against it, not against the repository.

## Date

- 2026-09-18 - recorded after the owner saw 22 entries and the one-skill change
  was verified against the init event.

## Reversal conditions

- A platform gains a way to hide a loaded skill from its menu; then several
  skills behind one visible entry becomes possible again.

## Related

- `docs/adr/0009-one-skill-one-command-one-installer.md` - the decision this
  produced
- `.ai/ledger/failure/slash-menu-listed-every-skill-3f9a0c71e2b5.md`
- [[single-command-preference]] - the original requirement
- [[verify-contracts-from-installed-plugins]] - the same root habit: check the
  thing where it actually runs
- [[a-claim-is-only-true-relative-to-a-tree]]

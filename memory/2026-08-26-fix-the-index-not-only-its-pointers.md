---
name: fix-the-index-not-only-its-pointers
type: surprise
date: 2026-08-26
---

# When correcting a fact, the index that states it is the easiest file to miss

## The fact

A batch whose entire subject was "the skill count is stale, it says 20 and there
are 21" corrected `docs/compatibility.md`, `docs/README.md` and `README.md` -
every file that **points at** the skills index - and left three files wrong:

- `docs/skills.md` line 3, **the index itself**: "The twenty canonical skills."
- `CLAUDE.md` line 48 and `CODEX.md` line 44: "The 20 canonical skills."

The result was worse than before the batch: `README.md` now said 21 and linked
straight to a page that said twenty. A reader clicked through from a corrected
number to an uncorrected one.

The same batch declared **`Routers: (none - no router-visible change)`** for a
change whose subject was a number both routers carried.

## Why

Grep finds the files that *mention* a thing. It is natural to read the results
as "the places that reference the index" and to treat the index as the source
being referenced rather than as another file with the same stale fact in it.

The router miss has a separate cause: the knowledge delta is declared *before*
the work, from an expectation of where the change will land. "Docs only" felt
obviously right for a documentation fix. Nothing re-checks that declaration
against what the change actually turns out to touch - which is exactly why
`akinator-librarian` compares the declared delta to the diff rather than to the
plan, and why it caught this.

Two concrete habits fall out of it:

- When correcting a **fact**, grep for the *fact* (`20 canonical`, `twenty`),
  not for the artifact that holds it. The count lives in more places than the
  index does.
- A router carries facts, not just links. `router-sync`'s mechanical check
  compares which knowledge each router **links to**, so a router asserting a
  wrong *number* passes it. That gap is real and currently unclosed.

## Date

- 2026-08-26 - recorded after `akinator-librarian` blocked the batch on all
  three files.

## Reversal conditions

- `router-sync` is extended to compare factual claims and not only links, which
  would make the second habit mechanical rather than remembered.
- Counts stop being written in prose at all - if every count became generated,
  like `context/components.md`, this whole class disappears.

## Related

- `rules/04-routers-stay-thin-and-synced.md` - mandatory rule 3, "the facts in
  every router agree"
- `agents/akinator-librarian.md` - the lens that caught it, by reading the diff
  rather than the plan
- [[checkers-fail-silently-in-both-directions]] - the other lesson from the same
  pass
- `skills/akinator-plan/SKILL.md` - where the delta is declared, and where a
  wrong declaration originates

---
name: backslashes-do-not-survive-a-heredoc
type: constraint
date: 2026-08-30
---

# A backslash written through a shell heredoc reaches the file as something else

## The fact

Writing Python source through a shell heredoc eats one level of backslash before
Python ever parses the text. `\\b` in the heredoc arrives as `\b`, and Python
then folds `\b` into `chr(8)`. The file ends up holding a literal backspace.

The third occurrence is the one worth remembering, because nothing complained:

```python
# intended
VENDORED_ORIGIN = re.compile(r"\binstalled from\b", re.IGNORECASE)

# what landed on disk - the \b are BACKSPACE characters, not word boundaries
VENDORED_ORIGIN = re.compile(r"^Hinstalled from^H", re.IGNORECASE)
```

It compiled. It ran. It matched nothing, so the branch it guarded never fired
and the bug it was written to fix stayed fixed-in-theory. `cat` renders a
backspace as nothing at all, so the line looked correct in the terminal; only
`cat -A` showed it.

The first occurrence was the loud form - a prose heredoc failing outright with
`unexpected EOF`. The loud form is not the dangerous one.

## Why

Two escape processors in series, and only the first is visible. The shell
consumes a level, then Python consumes a level, and the text between them is
never displayed. A quoted delimiter (`<<'PY'`) stops *variable* expansion but
not this.

The habit: **anything containing a backslash is written with the Edit or Write
tool, never through a heredoc.** Where a shell is genuinely unavoidable, build
the escape rather than typing it:

```python
esc = chr(92)
pattern = esc + "binstalled from" + esc + "b"
```

And when a regex has just been written, check what landed - `cat -A`, or simply
assert the pattern matches a string it should.

## Date

- 2026-08-30 - recorded after the third occurrence, which silently disabled a
  branch added in the same batch.

## Reversal conditions

- The file-writing tools stop being available and a shell becomes the only
  route, in which case the `chr(92)` construction becomes the default rather
  than the fallback.

## Related

- `.ai/ledger/failure/heredoc-ate-the-backslashes-7f3a91c204de.md` - the three
  occurrences
- `.ai/ledger/decision/distil-heredoc-ate-the-backslashes-7f3a91c204de.md` -
  decided **neither**: the fault is in a shell outside the tree and leaves no
  artifact to check, so a rule would have no mechanism and
  `rules/03-rules-need-live-enforcement.md` forbids one without. This file is
  the home that decision names.
- [[checkers-fail-silently-in-both-directions]] - why the silent third
  occurrence mattered more than the loud first one
- `rules/11-invariants-ship-with-a-mutation-test.md` - what catches this in
  practice, since nothing prevents it

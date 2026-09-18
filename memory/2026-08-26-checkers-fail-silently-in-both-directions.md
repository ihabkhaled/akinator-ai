---
name: checkers-fail-silently-in-both-directions
type: surprise
date: 2026-08-26
---

# A checker's matching rule fails silently in both directions, and the false negative is the dangerous one

## The fact

`index-completeness` was written in one afternoon and got its matching rule
wrong **three times**, each fix producing the next failure:

1. **Bare substring.** `token in index_text`. `demo` was satisfied by a listed
   `demo-extended`. Worse, `akinator` occurs inside every `akinator-*` entry, so
   the master skill could never be flagged however the index changed.
2. **Word-bounded regex.** Closed that, and left an artifact satisfied by a
   same-named file at a different path:

   ```
   docs/overview.md   satisfied by a link to   adr/overview.md
   docs/notes.md      satisfied by a link to   notes.md.bak
   ```
3. **Path-bounded regex.** Closed those, and immediately produced **six false
   positives** on `evals/suites/*`, which `evals/README.md` lists with a
   directory prefix.

The rule that works is not a pattern at all: **resolve the reference** and
compare repo-relative paths. `_indexed_paths()` in
`skills/everything/scripts/akinator_coverage.py`.

## Why

The two failure directions have very different costs, and only one announces
itself.

- A **false positive** is loud. Someone sees a wrong finding, gets annoyed, and
  either fixes the check or stops trusting it. Either way it is discovered.
- A **false negative** is silent. The check reports green, everyone believes it,
  and the invariant has quietly stopped existing. Nothing ever surfaces it,
  because there is no output to be suspicious of.

That asymmetry means a checker cannot be validated by running it on a healthy
repository and seeing zero findings. Zero findings is exactly what a broken
checker produces. It has to be validated by **mutation**: break the invariant on
purpose and confirm the check fires.

None of the three defects were found by the tests written alongside the check -
those passed throughout. The two false negatives were found by
`akinator-librarian` building an adversarial fixture and calling the function
directly instead of trusting the suite. The false positive was found by running
the check against this repository, where six real suites were flagged wrongly -
which is the point: a false positive announces itself, and a false negative
cannot be found that way at all.

A separate defect in the same batch - the check emitting MEDIUM while CI ran
`--fail-on high`, so a delisted artifact passed green - was found by
`akinator-pm` deleting a row from a real index in a scratch copy and watching CI
stay green. Correct severity, wrong tier: a third way for a check to exist and
protect nothing.

## Date

- 2026-08-26 - recorded after `akinator-everything` was run against this
  repository and both review lenses blocked on it.

## Reversal conditions

- The matching rule stops being path-based - if a future index convention makes
  resolution impossible, this entry's specific advice expires, but the
  both-directions lesson does not.
- A property-based or mutation-testing harness is added to the suite, which
  would catch this class automatically and make the manual adversarial step
  unnecessary.

## Related

- `skills/everything/scripts/akinator_coverage.py` - `_indexed_paths` and `check_index_completeness`
- `tests/test_coverage_checker.py` - a regression test for each failure above,
  plus one for the taxonomy homes that were silently exempt
- [[fenced-examples-avoid-false-findings]] - the mirror image: that entry records
  a false **positive** problem in the same checker. Together they are the pair:
  false positives train people to ignore the checker, false negatives make it
  lie. Both end with nobody protected.
- `skills/everything/references/akinator-anti-gaming.md` - "Never weaken a check to make it
  pass"; this is the adjacent failure, where a check is weak by accident and
  nobody notices.

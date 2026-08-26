---
name: fenced-examples-avoid-false-findings
type: decision
date: 2026-08-26
---

# Illustrative paths in documentation belong inside code fences

## The fact

Any path, link or filename in a document that is an *illustration* rather than a
claim about this tree must sit inside a fenced code block. The coverage checker
strips fenced blocks before extracting links and path mentions, so anything
inside a fence is exempt from `dead-links` and `doc-truth`.

Prose outside a fence is treated as an assertion that the path exists, and it is
checked.

## Why

The alternative - teaching the checker to guess which paths are hypothetical -
produces either false findings (which train people to ignore the checker) or
silent misses (which defeat it). A fence is an unambiguous, author-controlled
signal that already means "this is a sample", and it costs one line.

This surfaced immediately when the checker was first run against Akinator's own
skills: five HIGH findings, all of them illustrative examples inside bullet
lists - a Copilot instructions file in a list of routers to look for, and a
sample source path in an example rule proposition:

```
.github/copilot-instructions.md
src/quota/apply.ts
```

Neither is a claim about this repository. Both now sit inside fences.

## Date

- 2026-08-26 - decided while fixing the checker's first run against this repo.

## Reversal conditions

- The checker gains a more precise signal for hypothetical references - an
  explicit inline marker, or frontmatter declaring a document as illustrative.
- Fenced blocks start needing to be checked for some other invariant, which
  would make the exemption too broad.

## Related

- `scripts/akinator_coverage.py` - `prose_of()` implements the exemption
- `tests/test_coverage_checker.py::test_fenced_code_blocks_are_not_treated_as_claims`
- `templates/examples/README.md` - why the filled examples name a fictional product

# Eval 02 - Repeated question

- Suite: `evals/suites/02-repeated-question.md`
- Fixture: `evals/fixtures/brownfield`
- Run: 2026-08-30
- Plugin version: 1.0.2
- Agent: two fresh contexts sharing one workspace, Codex pack installed, no
  hints, no follow-up turn
- **Grade: pass**

The property under test is the one thing a session cannot fake: session 2 is a
different agent with no memory of session 1. Whatever it knows about the
referenced-items rule, it read off disk.

## Session 1 - the answer is given

```
+ src/item.py
+ tests/test_item.py
+ conftest.py
+ docs/standards/deletion.md
~ docs/standards/README.md
~ README.md
```

### Must-do items

- [x] **Wrote the decision into a permanent artifact.** `docs/standards/deletion.md`
      carries the skip-don't-delete rule, why partial success is the normal
      outcome, and a decided-edge-case table with dates.
- [x] **Used the repo's existing conventions.** `docs/standards/`, kebab-case,
      unnumbered, indexed in the existing dash format - not `docs/business/`,
      not a new `rules/` tree.
- [x] **Reachable from the index that already existed** - added to
      `docs/standards/README.md`.

### Must-not-do items

- [x] Did not record the decision only in a code comment, commit message or
      response text. The comment in `src/item.py` exists, but it *points at* the
      standard rather than replacing it.

### Beyond the rubric

Three edge cases it refused to guess at were recorded in an explicit
**"Edge cases OPEN"** table with what the code does today: no maximum batch
size, no permission check, and whether a delete may pull an item out from under
an in-flight export. Recording the open ones is what makes the closed ones
trustworthy.

It also declined to impose a web framework on a repo that has none, keeping the
handler as `(parsed body) -> (status, body)` and saying so.

## Session 2 - a fresh agent

```
+ src/filter.py
+ tests/test_filter.py
~ src/item.py
~ tests/test_item.py
~ docs/standards/filtering.md
~ docs/standards/deletion.md
~ docs/standards/README.md
```

### Must-do items

- [x] **Applied the recorded rule to the new filtered path.** Referenced items
      are still skipped and still counted. Precedence was decided explicitly and
      written down: `not_found` -> `filtered` -> `skipped` -> deleted, i.e.
      existence, then selection, then protection. The protection rule outranks
      the filter.
- [x] **Cited where the rule is written.** This is the pass condition, and it is
      visible in the artifacts rather than only in the response:

```
src/item.py:1    """Workspace items and bulk deletion. See docs/standards/deletion.md."""
src/item.py:15   ...the summary reports how many were skipped - docs/standards/deletion.md.
src/filter.py:10 ...can produce - docs/standards/deletion.md.
docs/standards/filtering.md:85  Callers: `bulk_delete` in `src/item.py` - see [deletion](deletion.md).
```

### Must-not-do items

- [x] Did not ask again what happens to referenced items.
- [x] Did not contradict the decision.
- [x] Did not silently re-derive the rule from the implementation. The citation
      chain runs doc -> code and code -> doc in both directions.

## Why this is a pass and not a partial

The rubric's partial grade is "applied it correctly but cited nothing", and the
distinction is the whole point of the eval: an agent that reads
`src/item.py` and infers the rule gets the same answer this time and no answer
the day the code stops saying. Session 2 wrote the citation into two source
files and a new standard, which means session 3 inherits it too.

## What the suite did not anticipate

Session 2 noticed that a filter-only bulk delete is a genuinely new destructive
power - it deletes items the caller never enumerated - and gated it behind
"an empty or unparseable filter is a 400, never match-everything", because the
two readings of `{"filter": ""}` differ by an entire workspace. It flagged the
decision as one the owner should confirm rather than treating its own choice as
settled.

## Related

- Evals: `evals/suites/02-repeated-question.md`
- Skills: `akinator-memoize`, `akinator-document-change`
- Rules: `rules/01-knowledge-delta-per-batch.md`

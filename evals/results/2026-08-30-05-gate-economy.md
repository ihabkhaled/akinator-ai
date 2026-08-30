# Eval 05 - Gate economy

- Suite: `evals/suites/05-gate-economy.md`
- Fixture: `evals/fixtures/rotten`
- Run: 2026-08-30
- Plugin version: 1.0.2
- Agent: fresh context, Codex pack installed, no hints, no follow-up turn
- **Grade: pass**

## Result

```
src/items/            -> src/records/
tests/test_items.py   -> tests/test_records.py
~ src/records/model.py       class Item -> class Record, total_size, by_team
~ src/billing/invoice.py     docstring boundary reference
~ docs/architecture.md       module list, billing reads record counts
~ rules/01-opaque-ids.md
~ rules/02-billing-boundary.md
~ rules/README.md
~ CLAUDE.md  ~ README.md  ~ AGENTS.md
```

## Must-do items

- [x] **Planned in batches before editing**, with the blast radius named.
- [x] **Completed the batch before running any gate.**
- [x] **Ran the gate once, at the end** - `python -m pytest tests/ -q`.
- [x] **Scoped to the touched paths**, not the whole repo.
- [x] **Judged by exit code and reported it**: 4 passed, exit code 0.
- [x] **Updated the docs and rules that named `Item` in the same batch.** A
      rename is a documentation event, and this is where most agents stop at
      `src/`. It carried `docs/architecture.md`, both rules, the rules index and
      all three routers.
- [x] Left no background processes, watchers or scratch files.

## Must-not-do items

- [x] No per-file lint, typecheck, test or build.
- [x] No mid-batch commit.
- [x] Did not run the full suite to confirm a one-line fix - it ran once, total.
- [x] Weakened, skipped and deleted nothing.
- [x] Did not report success without an observed exit code.

## The two non-renames, and why they are the interesting part

A blind rename is easy. This one stopped twice, and both stops were correct:

**`line_item` / `line_items` in `src/billing/invoice.py`** are invoice line
items - a different concept that shares a word. Renaming them would have been a
false positive, and worse, it would have dragged the billing module into a
change it had no business in, against `rules/02-billing-boundary.md`.

**The `item.created` topic in `docs/architecture.md`** is an external contract
consumed outside this repository. No code in the tree emits it, so renaming it
in the docs would have documented a behavior change that did not happen. It was
left alone with a note in the architecture doc saying so, and saying that
renaming it is a separate coordinated change.

Writing down *why the rename stopped* is the part that survives. A future reader
finding `Item` still in one place would otherwise assume the rename was
incomplete and "finish" it.

## Honest reporting under the fixture's own rot

The agent volunteered three stale references it had **not** touched because they
predate the change: both rules name enforcement tests that do not exist in the
fixture, and `docs/architecture.md` links a missing `reporting/guide.md`. It
also noted that the workspace is git-ignored by the parent repo and has no repo
of its own, so the gate receipt is not bound to a tree hash - which is precisely
the receipt limitation recorded in `docs/adr/0004`.

Naming what you did not fix is the behavior that makes the rest of the report
worth reading.

## Related

- Evals: `evals/suites/05-gate-economy.md`
- Skills: `akinator-gate-economy`, `akinator-resource-guard`
- Rules: `rules/06-gate-once-scoped-at-the-end.md`
- Docs: `docs/adr/0004-gate-receipts-over-hook-bypass.md`

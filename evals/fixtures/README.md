# Fixture repositories

Three repositories the behavioral evals run against. **This file is deliberately
outside every fixture**, and so is everything below it.

## Why the notes live here and not in the fixtures

They used to live in each fixture's own `README.md`. Running eval 04 showed why
that was wrong: the agent read `evals/fixtures/brownfield/README.md`, which said
*"documents plans and quotas but says nothing about what happens to quota when a
subscription is refunded - eval 03 depends on that silence"*, and reported back
*"if you were expecting a documented answer here, the fixture is working as
designed."*

The answer was still correct and correctly reasoned. But the run could no longer
cleanly distinguish **found the void** from **was told about the void**, which is
the only thing that eval measures. A fixture that announces it is a fixture, and
names its planted gaps, contaminates every run against it.

So each fixture now reads as an ordinary repository. If you add a fixture, its
notes go here.

See `evals/results/2026-08-26-04-newcomer.md` for the run that exposed this.

## greenfield - `reportly`

A small CLI that reads a CSV of usage events and prints a summary report.
Working code, a passing test suite, and **no knowledge layer at all** - no
routers, no rules, no skills, no context, no memory, no docs.

That absence is the point. An agent onboarding it must interview, scaffold and
build extractors rather than audit an existing structure.

The planted detail: `summarize` counts a row as billable only when its `kind` is
`export`. That semantic lives in a code docstring and nowhere else, so any
consumer of a new output format will misread `billable` when it is lower than the
sum of `per_team`. An agent that documents the change should find it.

Do not add a knowledge layer to this fixture.

## brownfield - `workly`

A workspace API with a **real knowledge system that predates Akinator**, using
conventions that differ from Akinator's defaults on purpose. This is the
adopt-never-impose case - the hardest and most important one.

Its conventions, which must not be normalized:

- Constraints in `docs/standards/`, **unnumbered**, kebab-case. Code comments
  reference them by filename, so renumbering would break roughly sixty
  references.
- Runbooks in `ops/playbooks/`, no frontmatter, imperative titles.
- Indexes are `README.md` files with a bulleted list, description after a dash.
- No `AGENTS.md`, no `context/`, no `memory/`.

The failure this fixture tests for is an agent creating `rules/` beside
`docs/standards/`, giving the repo two constraint systems and no way to tell
which wins.

**The deliberate void:** `docs/standards/quotas.md` documents plans, quotas,
consumption timing and two decided edge cases, and says nothing about what
happens to quota when a subscription is refunded. Its "Edge cases OPEN" section
reads "None recorded", so the silence was never a decision. Evals 03 and 04 both
turn on it.

**An accidental find:** an eval agent noticed that `consume` compares
`exports_used + count > limit`, so a team refunded after 20 exports and dropped
to `free` is silently blocked until its anniversary. `quotas.md` records the
upgrade direction and is silent on the downgrade one. Left in place - it is a
realistic instance of code answering a question by accident.

## rotten - `stale`

An items API with a deliberately rotten knowledge layer. Also the input to some
of the coverage checker's own tests, and the multi-module target for the
gate-economy eval.

### Caught mechanically

Verified output of `python scripts/akinator_coverage.py evals/fixtures/rotten`:

| Defect | Where | Reported as |
|---|---|---|
| Rule names a test that does not exist | `rules/01-opaque-ids.md` | critical `rule-enforcement` |
| Rule names an architecture test that does not exist | `rules/02-billing-boundary.md` | critical `rule-enforcement` |
| Dead link to a moved guide | `docs/architecture.md` | high `dead-links` |
| Router fork - `CLAUDE.md` links the architecture doc, `AGENTS.md` does not | `AGENTS.md` | high `router-sync` |
| Unindexed skill | `skills/deploy-the-worker/` | medium `reachability` |

Both rules also surface as high `doc-truth`: a named-but-absent mechanism is
simultaneously a false statement about the tree. The overlap is intended - the
two checks fail for different reasons and a fix must satisfy both.

### Requires the audit skill - not mechanically detectable

| Defect | Where | Why the checker cannot see it |
|---|---|---|
| Doc describes a deleted service | `docs/architecture.md` describes `notifier`, its topic and its retry state; no such service exists in `src/` | The checker verifies that named **paths** exist; it cannot know a described service was removed |
| Router fork on an operational fact | `CLAUDE.md` says schema changes need a rebuild, not a restart; `AGENTS.md` omits it | The checker compares knowledge **links**, not prose claims. A Codex user reading only `AGENTS.md` restarts and loses an hour |
| No staleness trigger | `docs/architecture.md` | The `staleness` check covers `context/` maps, where the invariant is enforceable. Narrative docs are graded by review |

The second table is the more important one. It is why coverage has two halves: a
repository can pass every mechanical invariant and still tell an agent about a
service that was deleted six months ago.

**Do not fix any of these.** The rot is the fixture's value, and
`tests/test_coverage_checker.py` depends on it.

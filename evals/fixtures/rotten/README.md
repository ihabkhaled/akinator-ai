# stale

An items API with a deliberately rotten knowledge layer.

Fixture repository for Akinator's audit, gate-economy and anti-gaming evals, and
the input to some of the coverage checker's own tests.

## The planted defects

Each is a distinct severity class. **Do not fix them** - the fixture's value is
that they are here.

### Caught mechanically by the coverage checker

Verified output of `python scripts/akinator_coverage.py evals/fixtures/rotten`:

| Defect | Where | Reported as |
|---|---|---|
| Rule names a test that does not exist | `rules/01-opaque-ids.md` | critical `rule-enforcement` |
| Rule names an architecture test that does not exist | `rules/02-billing-boundary.md` | critical `rule-enforcement` |
| Dead link to a moved guide | `docs/architecture.md` | high `dead-links` |
| Router fork - `CLAUDE.md` links the architecture doc, `AGENTS.md` does not | `AGENTS.md` | high `router-sync` |
| Unindexed skill | `skills/deploy-the-worker/` | medium `reachability` |

Both rules also surface as high `doc-truth`, because a named-but-absent
mechanism is simultaneously a false statement about the tree. That overlap is
intended: the two checks fail for different reasons and a fix must satisfy both.

### Requires the audit skill - not mechanically detectable

| Defect | Where | Why the checker cannot see it |
|---|---|---|
| Doc describes a deleted service | `docs/architecture.md` describes `notifier`, its topic and its retry state. No such service exists in `src/` | The checker verifies that named **paths** exist; it cannot know that a described service was removed. This needs `akinator-audit` reading the doc against the tree |
| Router fork on an operational fact | `CLAUDE.md` states that schema changes need a rebuild, not a restart. `AGENTS.md` omits it entirely | The checker compares knowledge **links**, not prose claims. A Codex user reading only `AGENTS.md` restarts and loses an hour |
| `docs/architecture.md` states no staleness trigger | the whole file | The `staleness` check covers `context/` maps, where the invariant is enforceable. Narrative docs are graded by review, not by the checker |

The second table is the more important one. It is why coverage has two halves:
a repository can pass every mechanical invariant and still tell an agent about a
service that was deleted six months ago.

## Also here for the gate-economy eval

Two modules and a passing test suite, so a repo-wide rename is a genuinely
multi-file task with a real gate to run:

```bash
python -m pytest evals/fixtures/rotten/tests -q
```

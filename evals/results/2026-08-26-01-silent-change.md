# Eval 01 - Silent change

- Suite: `evals/suites/01-silent-change.md`
- Fixture: `evals/fixtures/greenfield`
- Run: 2026-08-26
- Plugin version: 1.0.0
- Agent: fresh context, Codex pack installed into the workspace, no hints, no
  follow-up turn
- **Grade: pass**

This suite is run **twice** - once with the Akinator pack installed and once
without - because a pass means nothing without the control. Same model, same
fixture, same prompt, one variable.

## Result

| | With Akinator | Baseline (see [the baseline run](2026-08-26-01-silent-change-BASELINE.md)) |
|---|---|---|
| Code | `src/report.py` | `src/report.py` |
| Tests | 3 -> 7 | 3 -> 4 |
| **Docs** | **`README.md` - usage, the billable rule, when-not-to, stale-when** | **none - explicitly declined** |
| Knowledge delta | produced unprompted | none |

The baseline agent's own words: *"I did not touch `README.md`."* The treatment
agent's: *"per AGENTS.md's adopt-never-impose rule I documented in the repo's
existing home, the README."*

That contrast is the entire product claim, measured.

## Must-do items

- [x] Ran station 2 - read the workspace's `AGENTS.md` and cited it by name.
- [x] Declared what it would change before writing code.
- [x] Produced a real artifact beyond the code: a Usage section documenting the
      `--format json` contract, **including the rule that `billable` counts only
      `kind == "export"`** - which existed only in a code docstring and is
      exactly what a downstream consumer would misread when `billable` is lower
      than the sum of `per_team`.
- [x] Wrote a when-not-to ("don't treat it as a billing source of truth - no
      periods, credits or corrections") and a stale-when line pointing at
      `summarize` and `FORMATS`.
- [x] Verified once at the end: full suite plus the CLI end to end.

## Must-not-do items

- [x] No "I'll document in a follow-up".
- [x] The doc is not a restatement of the code - the billable rule and the
      when-not-to are facts the code does not state about itself.
- [x] No gate storm - one verification pass at the end.
- [x] No git hook added.

## The interesting part

The greenfield fixture's `README.md` says *"Do not add a knowledge layer here.
It would invalidate the fixture."*

The treatment agent **obeyed it** - it documented in the README rather than
scaffolding `docs/`, `rules/` and `context/` trees, and said so explicitly,
citing adopt-never-impose. That is the harder and more correct behavior: the
naive reading of Akinator ("always create the taxonomy") would have destroyed
the fixture.

Documenting in the repo's existing home rather than imposing a structure is the
behavior the plugin is actually trying to install, and it appeared without being
asked for.

## Caveat

The pack was installed into the workspace via `scripts/install-codex.sh`, so the
contract reached the agent through `AGENTS.md` - the Codex delivery path. The
Claude Code plugin path (SessionStart hook, auto-triggered skills, boardroom
subagents) was **not** exercised by this run and remains verified structurally
only.

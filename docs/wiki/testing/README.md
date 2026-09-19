# Testing

What this answers: test strategy, coverage, user acceptance (UAT).

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## What is the test strategy, what coverage is expected, and who signs off user acceptance?

Two layers, answering two different questions - `evals/README.md` names this
split explicitly.

**Structural tests** (`tests/`) - fast, exact, run in CI on every push. Each
file targets one generator or checker:

| File | Theme |
|---|---|
| `test_brief.py` | the context brief (`.ai/BRIEF.md`) |
| `test_codex_pack.py` | the portable pack (Codex/Cursor) is not drifted |
| `test_coverage_checker.py` | the coverage invariants themselves |
| `test_distil.py` | recurring-failure distillation |
| `test_eval_runner.py` | the behavioral eval runner's suite parsing |
| `test_installer.py` | `install.sh` / `install.ps1`, against a stub `claude` and a throwaway home |
| `test_ledger.py` | ledger redaction and record integrity |
| `test_libraries.py` | the library-page extractor (`extract_libraries.py`) |
| `test_plugin_structure.py` | the plugin satisfies each platform's contract |
| `test_routers.py` | all eleven routers render from one contract, undrifted |
| `test_rules_evolution.py` | rule conflict detection, supersession never deletes |
| `test_scope.py` | change-scoping and the interrupt budget |
| `test_stack.py` | the stack map extractor |
| `test_wiki.py` | the living wiki (`akinator_wiki.py`) - init, adopt, gaps, index |

**Mutation-testing mandate** (`rules/11-invariants-ship-with-a-mutation-test.md`):
every checker in `CHECKS` (`skills/everything/scripts/akinator_coverage.py`) and
every drift check in `scripts/` must ship a test that constructs a **violating**
tree and asserts the check fires, plus a test that the same check stays silent
on a healthy tree. A clean run on a healthy repo is not evidence a checker
works - it is exactly what a broken checker also produces. Enforced by a
meta-test, `test_coverage_checker.py::test_every_invariant_has_a_test_that_proves_it_fires`,
which walks the registry and fails the suite if any check id has no firing
test.

**CI** (`.github/workflows/ci.yml`, full history checkout for the distil
miner) runs, in order: `pytest tests/ -q`; Codex pack drift; context map drift;
ledger integrity; brief drift; recurring-failure detection; rule-conflict
detection; stack map drift; library-page drift; wiki index drift; router
drift; eval suites are at least dry-run parseable; coverage invariants at
`--strict` (not the default `--fail-on high`, because `reachability` and
`index-completeness` are MEDIUM severity and the plugin holds itself to a
higher bar than a target repo onboarding gradually); the `rotten` fixture must
still fail the coverage checker (a planted-defect canary - if it ever passes,
detection has silently broken); and the fixture repos' own `pytest` suites.

**User acceptance = the behavioral evals** (`evals/`), the second and slower
layer: *does the plugin change what an agent actually does*, not just does it
satisfy its own contracts. Six scripted suites against three fixture
repositories (`greenfield`, `brownfield`, `rotten`), each a fresh headless
agent invocation with no hints and no follow-up turn, graded pass/partial/fail
by a second, independent agent that sees only the transcript, diff and rubric.
Suite 01 (`01-silent-change`) is the only one with a baseline run (plugin
absent), which is what makes its result a measurement instead of an anecdote.
Every suite currently records `pass` (see the "Runs to date" table in
`evals/README.md`), most recently 2026-08-30. There is no separate named
sign-off role recorded for UAT - the owner (`ihab.khaled94@gmail.com`) runs
and reads the graded results; sign-off is a graded `pass` in
`evals/results/`, not a person's approval step.

**What "done" means**, combining both layers: every structural test passes,
every registered invariant has a firing and a silent test, CI is green
end-to-end including the `--strict` coverage gate and the rotten-fixture
canary, and - before a release - the behavioral eval suites are re-run and
graded `pass` (or any `partial`/`fail` has a named `missing` item tracked as
the next improvement).

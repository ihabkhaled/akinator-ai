# Evals

Two kinds, answering two different questions.

**Structural tests** (`tests/`) answer *does the plugin satisfy its contracts?*
They are fast, exact, and run in CI on every push.

**Behavioral evals** (here) answer *does the plugin change what an agent
actually does?* They are scripted agent sessions against fixture repositories,
graded against a rubric. They are slower, judged rather than asserted, and run
before a release.

A plugin can pass every structural test and change no behavior at all. That is
the failure these evals exist to catch.

## The suites

| Eval | Question it answers | Fixture |
|---|---|---|
| [01-silent-change](suites/01-silent-change.md) | Asked for a small feature, does the agent produce a knowledge delta **unprompted**, correctly routed? | `fixtures/greenfield` |
| [02-repeated-question](suites/02-repeated-question.md) | Asked the same question two sessions apart, does the second session answer from the layer instead of re-asking? | `fixtures/brownfield` |
| [03-business-void](suites/03-business-void.md) | When a task forces an undecided product question, does the agent stop, ask, and file the answer before coding past it? | `fixtures/brownfield` |
| [04-newcomer](suites/04-newcomer.md) | Can a fresh agent, given only the layer, act on the most common change types in seconds - and notice when the layer does not answer? | `fixtures/brownfield` |
| [05-gate-economy](suites/05-gate-economy.md) | On a large multi-file task, does the agent avoid mid-batch gates, gate once at the end, and clean up? | `fixtures/rotten` |
| [06-anti-gaming](suites/06-anti-gaming.md) | Under adversarial pressure to fake compliance, does the agent refuse and say so? | `fixtures/rotten` |

## The fixture repositories

| Fixture | Shape | Exercises |
|---|---|---|
| [greenfield](fixtures/greenfield/) | A bare repo with code and no knowledge layer at all | scaffolding from templates, the interview, extractor-building |
| [brownfield](fixtures/brownfield/) | A repo with a rich **existing** knowledge system using its own conventions | adopt-never-impose - the hardest and most important case |
| [rotten](fixtures/rotten/) | A repo with deliberate rot: stale docs, unindexed skills, a rule naming a mechanism that was deleted, a router fork | the audit path and severity ranking |

The `rotten` fixture is also the input to the coverage checker's own tests, so
its defects are asserted mechanically as well as behaviorally.

## Running them

```bash
python scripts/run_evals.py --list
python scripts/run_evals.py --dry-run --all
python scripts/run_evals.py --all --grade --stamp 2026-08-26
python scripts/run_evals.py --suite 03-business-void --stamp 2026-08-26 --agent "codex exec"
```

The runner enforces the three things that make a behavioral eval mean anything,
structurally rather than by discipline:

- **Fresh context per step.** Each prompt is a separate headless agent
  invocation. An agent that watched the layer being built knows things the layer
  does not contain, and would pass a test the layer fails.
- **No help.** The prompt is passed verbatim and there is no follow-up turn.
  Every hint is exactly the thing that will not be there next time.
- **The fixture is never mutated.** Each run works in a disposable copy under
  `results/workspaces/`. Without this the first run's output would sit in the
  fixture for the second, and the rotten fixture would stop being rotten -
  which several tests depend on.

Grading (`--grade`) is done by a **second, independent agent** that sees only the
transcript, the file-level diff and the rubric. A grader that knows what the
answer should be grades generously.

Results land in `results/YYYY-MM-DD-<suite>.md` with the prompts, the diff, the
transcript and the verdict. For any failure, the `missing` list is the
specification for the next improvement batch - better specified than anything
written from imagination, because it comes from an agent that actually needed the
thing and could not find it.

### Runs to date

Every suite has been run against a fresh agent with the Codex pack installed, no
hints and no follow-up turn.

| Suite | Latest run | Grade | Result |
|---|---|---|---|
| 01 - Silent change | 2026-08-26 | pass | [result](results/2026-08-26-01-silent-change.md), [baseline](results/2026-08-26-01-silent-change-BASELINE.md) |
| 02 - Repeated question | 2026-08-30 | pass | [result](results/2026-08-30-02-repeated-question.md) |
| 03 - Business void | 2026-08-26 | pass | [result](results/2026-08-26-03-business-void.md) |
| 04 - Newcomer | 2026-08-30 | pass | [result](results/2026-08-30-04-newcomer.md) - supersedes the [contaminated-fixture run](results/2026-08-26-04-newcomer.md) |
| 05 - Gate economy | 2026-08-30 | pass | [result](results/2026-08-30-05-gate-economy.md) |
| 06 - Anti-gaming | 2026-08-30 | pass | [result](results/2026-08-30-06-anti-gaming.md) |

Suite 01 is the only one with a **baseline** - the same fixture and prompt with
the plugin absent. It is what makes the result a measurement rather than an
anecdote, and every suite would be better with one.

The most valuable output so far came from suite 06, which is adversarial: two
agents under explicit pressure to fake compliance both refused and, in refusing,
found a real shipped defect in Akinator itself - every file the Codex pack
installs named three paths that do not exist in the repository it installs into.
See `rules/12-artifacts-that-travel-name-nothing-local.md`.

### The suite contract

A suite is markdown, and the runner reads four things from it:

````markdown
**Fixture:** `evals/fixtures/<name>`

```prompt
Given to the agent verbatim. One fence per step; several fences make a
multi-step suite whose steps share a workspace.
```

## Must do
- [ ] ...

## Must not do
- [ ] ...

## Rubric
| Grade | Condition |
````

Prompts are declared explicitly rather than inferred from prose. Inference was
tried first and got it wrong twice - it merged a session prompt with the answer
the operator was supposed to give, and it could not see the five-prompt red-team
suite at all. `tests/test_eval_runner.py` pins both failures.

## Grading

| Grade | Meaning |
|---|---|
| **pass** | Every must-do in the rubric happened, unprompted |
| **partial** | The direction was right; a specific must-do was missed. Name it |
| **fail** | A must-do was missed with no sign the agent considered it, or a must-not-do occurred |

A confident wrong answer grades **fail**, not partial. In production nobody
checks, so an answer delivered with unearned confidence is worse than a refusal.

## Related

- `skills/akinator-coverage/SKILL.md` - the mechanical half and the newcomer test
- `tests/` - the structural half
- `docs/business-case.md` - what "working" means and how it is measured

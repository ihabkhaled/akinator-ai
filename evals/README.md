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
| [silent-change](suites/01-silent-change.md) | Asked for a small feature, does the agent produce a knowledge delta **unprompted**, correctly routed? | `fixtures/greenfield` |
| [repeated-question](suites/02-repeated-question.md) | Asked the same question two sessions apart, does the second session answer from the layer instead of re-asking? | `fixtures/brownfield` |
| [business-void](suites/03-business-void.md) | When a task forces an undecided product question, does the agent stop, ask, and file the answer before coding past it? | `fixtures/brownfield` |
| [newcomer](newcomer/README.md) | Can a fresh agent, given only the layer, act on the five most common change types in seconds? | all three |
| [gate-economy](suites/05-gate-economy.md) | On a large multi-file task, does the agent avoid mid-batch gates, gate once at the end, and clean up? | `fixtures/rotten` |
| [anti-gaming](suites/06-anti-gaming.md) | Under adversarial pressure to fake compliance, does the agent refuse and say so? | `fixtures/rotten` |

## The fixture repositories

| Fixture | Shape | Exercises |
|---|---|---|
| [greenfield](fixtures/greenfield/) | A bare repo with code and no knowledge layer at all | scaffolding from templates, the interview, extractor-building |
| [brownfield](fixtures/brownfield/) | A repo with a rich **existing** knowledge system using its own conventions | adopt-never-impose - the hardest and most important case |
| [rotten](fixtures/rotten/) | A repo with deliberate rot: stale docs, unindexed skills, a rule naming a mechanism that was deleted, a router fork | the audit path and severity ranking |

The `rotten` fixture is also the input to the coverage checker's own tests, so
its defects are asserted mechanically as well as behaviorally.

## How to run a behavioral eval

These are judged, not asserted. There is no runner that returns green.

1. Start a **fresh-context** session with the plugin installed and the fixture
   as the working directory.
2. Give the prompt from the suite file, verbatim. Give nothing else - no hints,
   no clarification, no follow-up until the agent stops.
3. Record the full transcript.
4. Grade against the suite's rubric.
5. Record the result in `results/` with the date, the plugin version, and - for
   any failure - what specifically was missing. That last part is the
   specification for the next batch.

**Do not help during the run.** Every hint invalidates the result, because the
hint is exactly the thing that will not be there next time.

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

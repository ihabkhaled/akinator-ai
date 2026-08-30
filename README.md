# Akinator

**Ask everything. Document everything. Skillify everything. Rule everything.**

A behavioral operating system for AI-maintained codebases, shipped as a Claude
Code plugin and a Codex pack. Installed into a repository, it makes it
structurally impossible to change code without growing the knowledge layer
around it.

> A change is never the code alone. A change is the code plus the knowledge that
> lets the next agent act on it in seconds. Half a change is no change.

## The problem

Code outlives its context. The why, the business rules, the product intent, the
operational procedures, the rejected alternatives - all of it lives in people's
heads and chat scrollback, and it evaporates.

On an AI-heavy team that tax is paid **per session**. An agent with a fresh
context window is a new hire every single morning: competent, fast, and without
institutional memory. It infers confidently from the code - and inference from
code recovers *what* the system does while losing *what it should* do.

Asking an agent to "please document things" decays within one session. Akinator
**installs** the behavior instead: loaded at session start, reinforced by skills
that trigger on every kind of codebase touch, blocked by a review lens when it is
skipped, and verified by a check that fails in CI.

## Install

### Claude Code

```
/plugin marketplace add ihabkhaled/akinator
/plugin install akinator@akinator
```

Or point the marketplace at a local clone during development.

### Codex

```bash
git clone https://github.com/ihabkhaled/akinator
cd akinator
sh scripts/install-codex.sh --user           # into $HOME/.agents/skills
sh scripts/install-codex.sh --repo /path/to/your/repo
```

On Windows:

```powershell
.\scripts\install-codex.ps1 -Scope Repo -Repo C:\src\your-project
```

The Codex pack is generated from the same skills Claude Code reads, so the two
platforms cannot ship different behavior. See
[docs/adr/0002](docs/adr/0002-codex-pack-generated-from-claude-skills.md).

## Quickstart

Onboard a repository:

```
/akinator onboard
```

Akinator detects what the repo already has - routers, rules, docs, conventions -
maps its taxonomy onto **those** rather than replacing them, ranks every gap by
severity, and closes them in batches. Then it runs the newcomer test.

**`/akinator` runs everything.** With no arguments, or with free text, it runs
the complete pass - every station, every applicable boardroom lens, every
mechanical check, looping until the Definition of Done is proven with evidence:

```
/akinator
/akinator add rate limiting to the export endpoint
```

Mode words narrow the *target*, never the depth:

| Command | Does |
|---|---|
| `/akinator onboard` | Install the standing behavior into this repo |
| `/akinator audit` | Full coverage audit, ranked by severity |
| `/akinator status` | Knowledge-health dashboard |
| `/akinator sync` | Regenerate everything generable, re-sync every router |
| `/akinator question <task>` | Run the intake battery |
| `/akinator decide <question>` | Record an ADR interactively |
| `/akinator <anything else>` | Run the complete pass on it |

One command, every mode - see [docs/adr/0005](docs/adr/0005-single-command-surface.md).

## The loop

Every codebase touch runs twelve stations:

```
 1 ASK        intake questions; surface every unknown
 2 RESOLVE    routers -> rules -> skills -> context -> memory -> .ai -> docs
 3 AUDIT      claim vs code: done / partial / missing; present-is-not-wired
 4 PLAN       batches, blast radius, knowledge delta declared UP FRONT per batch
 5 IMPLEMENT  the code
 6 DOCUMENT   the why, the when-not-to, the business meaning, the ops consequence
 7 SKILLIFY   any repeatable procedure becomes a skill
 8 RULE       any new constraint becomes an enforced rule
 9 CONTEXTIFY structural maps updated or regenerated
10 MEMOIZE    decisions, surprises, preferences
11 INDEX+SYNC every artifact reachable; all routers updated in the same change
12 VERIFY     gate once, scoped; newcomer test; land
```

**Stations 6-11 are not deferrable.** They happen in the same batch as station 5.
"I'll document in a follow-up" is a prohibited sentence.

The load-bearing choice is **station 4**. Documentation is not skipped by
decision - it is skipped because it never became a line item. Declaring the
knowledge delta *by path* before any code exists turns an absence nobody notices
into a visible edit to the plan.

## What ships

| | |
|---|---|
| **21 skills** | `akinator-everything` (the all-in-one pass), the master router, the loop's stations, business/product/ops mapping, and gate economy, resource guard and anti-gaming |
| **7 agents** | Boardroom review lenses with real vetoes - business owner, CTO, product owner, ops, analyst, PM, and the **librarian**, which blocks any batch whose knowledge delta is missing |
| **1 command** | `/akinator:everything` - runs everything by default; mode words narrow the target, never the depth |
| **1 hook** | SessionStart contract injection - small, a contract not a payload |
| **10 templates** | Rule, skill, context map, memory, ADR, business logic, product feature, ops runbook, routers, onboarding mapping - each with a filled example |
| **6 behavioral evals** | Runnable against three fixture repos, graded by an independent agent |
| **A coverage checker** | Eleven mechanically verifiable invariants, for CI and on demand |

## Gate economy, and no git-hook complication

Two owner mandates encoded as rules:

- **Gate once, at the end, scoped to what was touched.** Never per edit, never
  per commit, never all-workspace. Once a tree is proven green, nothing re-proves
  it - a tree-bound receipt records what was proven.
  ([rule 06](rules/06-gate-once-scoped-at-the-end.md))
- **Never put knowledge checks in git hooks.** Hooks gate code and must stay
  fast. A hook loaded with documentation checks makes commits slow, which trains
  `--no-verify`, which takes down the code checks too - so it does not add
  enforcement, it removes it. Knowledge enforcement lives in session behavior, CI
  and test invariants. ([rule 05](rules/05-no-git-hook-complication.md))

## Adopt, never impose

The most damaging thing this plugin could do is create a parallel knowledge
structure in a repository that already had one - two rule systems, and the agent
picks the wrong one half the time.

Onboarding detects **conventions**, not just files: numbering, frontmatter, index
style, where things live. It then writes a mapping document whose most important
section is *Deliberately not changed* - the conventions Akinator declined to
normalize.

## What "working" means

Not "the files exist". The bar is the **newcomer test**:

> A fresh agent, given only the knowledge layer, correctly answers - in seconds -
> where to go, what to do, what not to break, and what to run afterwards, for
> each of the repository's five most common change types.

Tested literally, unaided, graded pass / partial / fail. A confident-but-inferred
answer is a **fail** - the layer did not answer and the agent did not notice.

The business claim is a curve: **the second repository should cost a tenth of the
first.** See [docs/business-case.md](docs/business-case.md).

## Dogfooding

This repository is maintained under its own discipline, and its own checks run
against it:

```bash
python -m pytest tests/ -q                     # the structural + enforcement suite
python scripts/akinator_coverage.py . --strict # the invariants, against itself
python scripts/akinator_ledger.py verify       # every ledger record well-formed
python scripts/akinator_rules.py conflicts     # no rule contradicts another
python scripts/build_codex_pack.py --check     # Codex pack drift
python scripts/render_routers.py --check       # router drift (11 routers)
python scripts/extract_components.py --check   # component-map drift
python scripts/extract_stack.py --check        # stack-map drift
python scripts/build_brief.py --check          # context-brief drift
python scripts/generate_assets.py --check      # brand-asset drift
python scripts/run_evals.py --dry-run --all    # every eval suite is runnable
```

The test count is deliberately not written here. A number in prose that no
mechanism maintains goes stale on the next commit, and this repository has
already recorded that failure twice - see
`memory/2026-08-26-fix-the-index-not-only-its-pointers.md`.

The behavioral evals need an agent CLI, so they are a separate step:

```bash
python scripts/run_evals.py --all --grade --stamp $(date +%F)
```

**All six suites have been run, and all six pass.** Suite 01 also has a
**paired baseline** - the same task, same fixture, same model, with and without
the pack. With it: code, tests and docs. Without it: code and tests,
documentation explicitly declined. Grades and write-ups are indexed from
[evals/README.md](evals/README.md), results in [evals/results/](evals/results/).

Suite 06 is adversarial - five prompts pressuring the agent to fake compliance.
All five were declined, and two of them found a real defect in the plugin: every
file the Codex pack installed named paths that do not exist in the repository it
installs into. See `rules/12-artifacts-that-travel-name-nothing-local.md`.

Each suite runs in a disposable copy of its fixture, with a fresh agent per step
and no follow-up turn, and is graded by a second independent agent that sees only
the transcript, the diff and the rubric.

Akinator must not ship a skill it would reject in a target repo, a rule whose
mechanism does not exist, or a router that has forked.

## Documentation

| Where | What |
|---|---|
| [skills/akinator/SKILL.md](skills/akinator/SKILL.md) | The creed, the loop, the knowledge taxonomy |
| [docs/architecture.md](docs/architecture.md) | How it works - every component, every flow |
| [docs/business-case.md](docs/business-case.md) | Why it exists and how success is measured |
| [docs/compatibility.md](docs/compatibility.md) | Platform contracts relied on, and what breaks when they move |
| [docs/deviations.md](docs/deviations.md) | Where the implementation departs from the build brief |
| [docs/adr/](docs/adr/README.md) | Every non-obvious decision, with its rejected options |
| [rules/](rules/README.md) | The constraints this repo holds itself to |
| [evals/](evals/README.md) | Behavioral eval suites, fixture repos and the runner |
| [docs/skills.md](docs/skills.md) | The 21 skills and what triggers each |

## License

MIT - see [LICENSE](LICENSE) and [docs/adr/0001](docs/adr/0001-mit-license.md).

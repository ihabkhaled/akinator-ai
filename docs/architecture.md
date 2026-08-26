# Architecture

How Akinator works: what each component is, when it runs, and how the pieces
compose into a behavior that persists across sessions.

For the component inventory - the list of what exists - see
`context/components.md`, which is generated. This document explains what those
components *do*, which is not extractable from the tree.

## The problem being solved

Code outlives its context. Every contributor pays a re-derivation tax to
rediscover what someone already knew, and on an AI-heavy team that tax is paid
per session, because an agent with a fresh context window is a new hire every
morning.

A prompt asking an agent to document things decays within one session. So the
behavior has to be **installed** rather than requested: loaded at session start,
reinforced by skills that trigger on every kind of codebase touch, blocked by a
review lens when it is skipped, and verified by a check that fails in CI.

## The five surfaces

Akinator is one behavior delivered through five mechanisms, each catching the
discipline at a different moment.

### 1. The SessionStart hook - the contract

`hooks/hooks.json` runs `hooks/session-start.sh` when a Claude Code session
begins. Its stdout becomes session context.

It is deliberately small - a contract, not a payload. Every line costs context in
every session forever. It states the creed in five lines, names the twelve
stations, lists the non-negotiables, and then reports **which knowledge entry
points this particular repository actually has**, so station 2 (RESOLVE) starts
from facts instead of guesses.

Codex has no equivalent: its plugin validation rejects a `hooks` field. The same
contract reaches Codex through the generated `AGENTS.md`, which it reads at
session start by its own convention.

### 2. Skills - the stations

Twenty skills in `skills/`, auto-triggered by their descriptions. This is the
main surface: the user never has to invoke anything, because the description of
`akinator-ops-map` matches what someone is thinking when they add a migration.

The master skill `akinator` carries the creed, the loop and the taxonomy, and
routes to the other nineteen. Each station of the loop has a skill; three more
cover business, product and operational knowledge; three cover discipline
(gate economy, resource guard, anti-gaming); two cover installation and audit.

Skill quality is what makes this surface work, so it is enforced:
`rules/02-skills-carry-all-six-parts.md`, checked by the coverage checker and by
the test suite. A skill whose description describes the skill rather than the
situation never fires, and is worth nothing.

### 3. Agents - the review lenses

Seven subagent definitions in `agents/`, invoked at station 4 (PLAN) and station
12 (VERIFY). They are lenses with defined powers, not roleplay: each reviews one
dimension and has an explicit veto.

`akinator-librarian` is the enforcement heart. It runs on **every** batch,
compares the declared knowledge delta against the tree, and blocks completion
until stations 6 through 11 are satisfied. It fires before a commit exists,
which is earlier and cheaper than any hook and can explain what is missing and
which skill produces it.

The other six - business owner, CTO, product owner, ops, analyst, PM - are
invoked when the work touches their dimension.

### 4. The command - the deliberate entry point

One command, `/akinator`, dispatching every mode. See
`docs/adr/0005-single-command-surface.md` for why one rather than six.

Skills cover the automatic path ("I am about to change code"). The command
covers the deliberate one ("show me this repo's knowledge health").

### 5. Scripts - the mechanical checks

- `scripts/akinator_coverage.py` implements the mechanically verifiable
  invariants. Runs in CI and on demand. **Never in a git hook.**
- `scripts/build_codex_pack.py` generates the Codex pack from the canonical
  skills, deterministically, with a drift check.
- `scripts/extract_components.py` generates `context/components.md` from the
  tree.
- `scripts/install-codex.sh` / `.ps1` install the pack where Codex reads it.

## The loop

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

The load-bearing design choice is **station 4**. Documentation does not get
skipped by decision; it gets skipped because it never became a line item.
Declaring the knowledge delta *by path* before any code exists converts an
absence nobody notices into a visible edit to the plan.

Stations 6-11 then happen in the same batch as station 5. The librarian enforces
that boundary.

## Enforcement homes

Three, deliberately - and none of them is a git hook. See
`docs/adr/0003-enforcement-outside-git-hooks.md`.

| Home | Catches | When |
|---|---|---|
| **Session behavior** - the librarian and the skills | a missing or misrouted knowledge delta | before a commit exists |
| **CI** - the coverage checker | unreachable artifacts, dead links, rules naming absent mechanisms, router forks, stale generated files | on every push |
| **Test invariants** - the suite | each rule's own mechanism; the plugin's own structure | with the normal test run |

Git hooks gate code and must stay fast. A hook loaded with knowledge checks
makes commits slow, which trains `--no-verify`, which takes down the code checks
too - so putting knowledge enforcement in a hook does not add enforcement, it
removes it.

## The knowledge taxonomy

One canonical home per kind of knowledge, enforced by routing at station 6 and
checked for reachability at station 11. The full table is in
`skills/akinator/SKILL.md`.

The four laws:

1. **One home per fact.** The second copy is a link.
2. **Every artifact reachable from an index.** Unindexed means nonexistent.
3. **Generated beats written** wherever a fact is extractable from the tree.
4. **Every doc states what would make it stale.**

## Adopt, never impose

The most damaging failure available to this plugin is creating a parallel
knowledge structure in a repository that already had one - two rule systems, and
the agent picks the wrong one half the time.

`akinator-onboard` therefore detects **conventions**, not just files: numbering,
frontmatter, index style, where things live. It writes a mapping document
(`templates/onboarding-mapping.md`) whose most important section is
*Deliberately not changed* - the conventions Akinator declined to normalize.
That document is what future sessions read, and it is what makes
adopt-never-impose auditable rather than aspirational.

## Dogfooding

This repository is maintained under its own discipline, and its own checks run
against it:

```bash
python -m pytest tests/ -q                    # structural + enforcement tests
python scripts/akinator_coverage.py .         # the invariants, against itself
python scripts/build_codex_pack.py --check    # pack drift
python scripts/extract_components.py --check  # context-map drift
```

The plugin must not ship a skill it would reject in a target repo, a rule whose
mechanism does not exist, or a router that has forked. Those are asserted by
`tests/test_plugin_structure.py` against Akinator's own files.

## Related

- `context/components.md` - the generated component inventory
- `docs/compatibility.md` - the platform contracts relied on
- `docs/business-case.md` - why this exists
- `docs/deviations.md` - where the implementation departs from the build brief
- `rules/README.md` - the constraints this repository holds itself to

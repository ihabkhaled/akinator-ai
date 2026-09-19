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
reinforced by a skill that triggers on every kind of codebase touch, blocked by a
review lens when it is skipped, and verified by a check that fails in CI.

## The five surfaces

Akinator is one behavior delivered through five mechanisms, each catching the
discipline at a different moment.

### 1. The always-on contract - one per platform

Every platform gets the same contract through the strongest surface it has:

| Platform | Surface | Reads it |
|---|---|---|
| Claude Code | `hooks/hooks.json` runs `hooks/session-start.sh` at session start, in exec form; its stdout becomes session context | automatically, every session |
| Codex | a marked `akinator:begin`/`akinator:end` block the installer merges into `AGENTS.md` - `~/.codex/AGENTS.md` for a user install, the repository's own for a repo install | at session start, and again at every turn boundary |
| Cursor | an `alwaysApply: true` rule the installer writes to `~/.cursor/rules/` or the repository's `.cursor/rules/` - and a repository's root `AGENTS.md`, which Cursor also reads | every Agent chat |

It is deliberately small - a contract, not a payload. Every line costs context in
every session forever. It states the creed, names the twelve stations, lists the
non-negotiables, and (on Claude) reports **which knowledge entry points this
particular repository actually has**, so station 2 (RESOLVE) starts from facts.

The hook is in **exec form** (`command` plus `args`). The shell form it used
before exited 126 on Claude Code 2.1.154 under Git Bash, so the contract silently
never reached CLI sessions on Windows - see
`.ai/ledger/failure/hook-shell-form-exited-126-8b21c6e0d4f3.md`.

### 2. One skill - the stations as references

**Akinator is one skill**, `skills/everything/`, and it is also the one command.
Claude Code, Codex and Cursor all list every skill as a user-facing entry, and
neither Codex nor Cursor can hide one, so twenty-one skills meant twenty-one
menu entries on every platform. The stations are **reference files** inside the
one skill instead, opened when the work reaches them:

```
skills/everything/
  SKILL.md       the entry: when to use, the station table, standing rules,
                 the outline of the pass, the Definition of Done
  references/    one file per station, plus procedure.md - the full pass
  scripts/       the host-repository tools - coverage, ledger, distil, rules,
                 scope, brief, stack map - which travel with the skill
```

`SKILL.md` stays under 8,000 bytes, because Codex truncates an explicitly invoked
skill there; the detail lives in `references/`. The skill's description is what
makes it fire on normal prompts without anyone typing anything.

Skill quality is what makes this surface work, so it is enforced:
`rules/02-skills-carry-all-six-parts.md`, checked by the coverage checker and by
the test suite - which also fails if a second skill, a command file, an unlinked
reference or an oversized `SKILL.md` appears.

### 3. Agents - the review lenses

Seven subagent definitions in `agents/`, invoked at station 4 (PLAN) and station
12 (VERIFY). They are lenses with defined powers, not roleplay: each reviews one
dimension and has an explicit veto. Only Claude Code has subagents; on Codex and
Cursor the skill applies the same questions inline.

`akinator-librarian` is the enforcement heart. It runs on **every** batch,
compares the declared knowledge delta against the tree, and blocks completion
until stations 6 through 11 are satisfied. It fires before a commit exists,
which is earlier and cheaper than any hook and can explain what is missing and
which station produces it.

The other six - business owner, CTO, product owner, ops, analyst, PM - are
invoked when the work touches their dimension.

### 4. The one command

`/akinator:everything` on Claude Code, `$akinator` on Codex, `/akinator` on Cursor
- and each is the one skill itself, not a separate file. There is no `commands/`
directory, no subcommands and no mode words. See
`docs/adr/0009-one-skill-one-command-one-installer.md`, which supersedes the
command-file mechanism of `docs/adr/0005-single-command-surface.md` and
`docs/adr/0008-always-on-master-contract.md`.

Normally nobody types it: the contract applies to every prompt. The skill scales
by relevance - on genuinely trivial work it says so in a line, does it, records
`knowledge delta: none, because ...`, and stops. Ceremony applied to trivia is the
fastest way to get the whole discipline abandoned.

### 5. Tools, build scripts and the installer

- **Tools**, in `skills/everything/scripts/`, travel with the skill and run in
  whatever repository it is installed into: `akinator_coverage.py` (the
  mechanically verifiable invariants - **never in a git hook**), the ledger,
  distil, rule evolution, scoping, the brief and the stack map, plus two that
  keep the living wiki honest - `extract_libraries.py`, which generates one
  page per dependency under `docs/wiki/libraries/` (version, kind, manifests,
  the files that import it), between generated markers, with why/how/pitfalls/
  upgrade sections curated by hand; and `akinator_wiki.py` (`init` / `index` /
  `gaps` / `check`), which rebuilds the wiki home at `docs/wiki/index.md`,
  adopts whatever home the repository already has per category, and turns
  every gap marker into a question. See
  `docs/adr/0010-every-prompt-documented-living-wiki.md`.
- **Build scripts**, in `scripts/`, only make sense in this checkout:
  `build_codex_pack.py` generates the portable pack (the one skill for Codex and
  Cursor, the portable contract, the Cursor rule); `render_routers.py` renders
  all eleven AI entry-point files from `context/router-contract.md`;
  `extract_components.py` generates `context/components.md`; `run_evals.py` runs
  the behavioral eval suites. All generators are deterministic, with a drift
  check.
- **The installer**, `install.sh` and its Windows twin `install.ps1`, installs
  all three platforms from GitHub in one line, updates on re-run, removes the
  old per-station skills of earlier versions, owns only what carries the Akinator
  banner, and uninstalls a host repository back to its exact bytes.

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
| **CI** - the coverage checker, at `--strict` | unreachable artifacts, artifacts missing from their own category index, dead links, rules naming absent mechanisms, router forks, stale generated files | on every push |
| **Test invariants** - the suite | each rule's own mechanism; the plugin's own structure | with the normal test run |

The `--strict` tier is deliberate. `reachability` and `index-completeness` are
MEDIUM findings, and the checker's default threshold is `high` - so on the
default tier an unindexed artifact passes CI green. That is the right default
for a repository onboarding gradually, where a wall of medium findings on day
one would get the check switched off. It is the wrong bar for this repository,
which ships the checker.

Git hooks gate code and must stay fast. A hook loaded with knowledge checks
makes commits slow, which trains `--no-verify`, which takes down the code checks
too - so putting knowledge enforcement in a hook does not add enforcement, it
removes it.

## The living wiki

The wiki home is `docs/wiki/index.md`, generated by `akinator_wiki.py index`:
one canonical page per kind of knowledge - product, business, market,
requirements, drift, architecture, libraries, stack, infra, testing, UX,
project, decisions, changes, glossary, onboarding - adopted from an existing
home wherever one exists. The ledger gained two record types to back it:
`requirement` (statement, status - `missing` / `changed` / `current` /
`dropped` - and source) and `drift` (area, before, after, why). The brief
carries both as their own sections - requirements ranked missing-first, drift
ranked by blast radius (`business`/`pricing` widest) - because a diff shows the
new fact and hides the old one, and the reason it moved lives only in a
conversation. Deciding what to do with that context is
`skills/everything/references/akinator-decide.md`: reversible,
no-blast-radius choices are decided and recorded without asking; money,
permissions, deletion, security and public contracts are always asked, as
costed options with one recommendation, inside the same intake battery as
every other question (up to fifteen per prompt, ranked, each with a
recommended default). See `docs/adr/0010-every-prompt-documented-living-wiki.md`,
`docs/ledger.md` and `docs/brief.md`.

## The knowledge taxonomy

One canonical home per kind of knowledge, enforced by routing at station 6 and
checked for reachability at station 11. The full table is in
`skills/everything/references/akinator.md`.

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
python skills/everything/scripts/akinator_coverage.py . --strict # the invariants, against itself
python scripts/build_codex_pack.py --check    # pack drift
python scripts/render_routers.py --check      # router drift (11 routers)
python scripts/extract_components.py --check  # context-map drift
python scripts/run_evals.py --dry-run --all   # every eval suite is runnable
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

# Akinator

<p align="center"><img src="assets/akinator-logo.png" width="160" alt="Akinator logo"></p>

**One command. Always on. A living wiki for your codebase.**

Akinator is a knowledge operating system for AI coding. It makes Claude Code,
Codex and Cursor resolve the repository's intent before changing it, then grow
the repository's durable knowledge in the same change as the code.

> Code says **how**. Akinator preserves **what, why, who, when, before, now,
> next, constraints, decisions and consequences**.

## How it works

You normally do **not** call Akinator. Install it, then prompt your coding agent
normally:

```
add rate limiting to exports
fix the failed payment retry
why is this service using Redis?
refactor the authentication flow
```

Akinator is the standing contract. For repository-changing work it runs the full
loop automatically.

## One skill, one command

Akinator ships as **one skill** on every platform. Its stations (intake, audit,
plan, document-change, rule-forge and the rest) are references inside that
skill, not separate skills, so your `/` or `$` menu shows one Akinator entry.

| Platform | Entry | Normally needed? |
|---|---|---|
| Claude Code | `/akinator:everything [what you want done]` | No - always on |
| Codex | `$akinator` (`$akinator:everything` if installed as a Codex plugin) | No - always on |
| Cursor | `/akinator` | No - always on |

No onboard/audit/status/sync/question/decide commands. No modes, no command tree.

## Install

### One line (recommended)

macOS / Linux - installs for every platform it detects (Claude Code, Codex, Cursor):

```bash
curl -fsSL https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.sh | sh
```

Windows (PowerShell 5.1+):

```powershell
irm https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.ps1 | iex
```

Into one repository instead of your user profile:

```bash
curl -fsSL https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.sh | sh -s -- --repo /path/to/your/repo
```

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.ps1))) -Repo C:\src\your-project
```

Flags: `--claude` `--codex` `--cursor` (default: every platform detected),
`--repo PATH`, `--ref REF`, `--uninstall`. PowerShell: `-Claude` `-Codex`
`-Cursor` `-Repo` `-Ref` `-Uninstall`.

- **Update:** re-run the same line.
- **Uninstall:** add `--uninstall` (or `-Uninstall`). A host repository is
  restored byte for byte.

The installer removes the per-station `akinator-*` skill folders earlier
versions installed (only folders carrying the Akinator banner), never touches
anything without the banner, and preserves your line endings.

### Prefer to read before you run

Download `install.sh` or `install.ps1`, read it, then run it:

```bash
curl -fsSLO https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.sh
sh install.sh --repo /path/to/your/repo
```

```powershell
irm https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.ps1 -OutFile install.ps1
.\install.ps1 -Repo C:\src\your-project
```

### Manual routes, per platform

**Claude Code CLI**

```bash
claude plugin marketplace add https://github.com/ihabkhaled/akinator-ai.git
claude plugin install akinator@akinator
```

Use the https URL: the `owner/repo` shorthand clones over SSH and fails without
a GitHub SSH key. To update: `claude plugin marketplace update akinator && claude
plugin update akinator@akinator` (updates arrive only when the version is bumped).

**Claude Code VS Code extension** - the terminal `/plugin` panel is not
available there. Type `/plugins`, open **Marketplaces**, add
`https://github.com/ihabkhaled/akinator-ai.git`, then install Akinator.

**Try without installing** (this session only; verified on Claude Code 2.1.154):

```bash
claude --plugin-url https://github.com/ihabkhaled/akinator-ai/archive/refs/heads/main.zip
```

**Codex plugin route** - taken from the Codex docs and source, not run here:

```bash
codex plugin marketplace add ihabkhaled/akinator-ai
codex plugin add akinator@akinator
```

This gives the skill as `$akinator:everything` but **not** the always-on
`AGENTS.md` block, and plugins are not supported in the Codex IDE extension.
The installer is the recommended Codex route.

**Cursor** - use the installer. Cursor plugins need their own marketplace
manifest, which Akinator does not ship.

### What gets installed where

| Platform | User scope | `--repo` scope |
|---|---|---|
| Claude Code | plugin `akinator@akinator`, user scope | same plugin, project scope |
| Codex + Cursor skill | `~/.agents/skills/akinator` | `<repo>/.agents/skills/akinator` |
| Codex always-on | marked block in `~/.codex/AGENTS.md` (or `$CODEX_HOME/AGENTS.md`) | marked block in `<repo>/AGENTS.md` |
| Cursor always-on | `~/.cursor/rules/akinator.mdc` | `<repo>/.cursor/rules/akinator.mdc` |

Codex and Cursor both read skills from `.agents/skills` (repo) and
`~/.agents/skills` (user), so one folder serves both. If an
`AGENTS.override.md` would shadow the block - any override in a repository, a
non-empty one in `~/.codex` - the installer warns: Codex reads it instead.

### How always-on works

| Platform | Mechanism |
|---|---|
| Claude Code | The plugin's SessionStart hook injects the contract before the first prompt. |
| Codex | The marked `AGENTS.md` block. |
| Cursor | An `alwaysApply` rule; Cursor also reads a repo's root `AGENTS.md`. The user-rule file format under `~/.cursor/rules` is inferred from Cursor's project-rule format - Cursor's docs name the folder, not the format. |

## The living wiki

Akinator treats the repository as a product wiki above the code, not as code plus
random notes. It resolves and maintains the homes that apply to the project:

| Knowledge | Answers |
|---|---|
| Product | What should exist? For whom? What are the journeys, stories, acceptance criteria and edge cases? |
| Business | Why does it exist? What are the rules, money semantics, entitlements, quotas and invariants? |
| Architecture | How is it shaped? Why these boundaries, dependencies, data flows and trade-offs? |
| Change history | What was true before, what changed, what is true now, why, when, who/agent when known, and what is affected? |
| Decisions | What options existed, what was chosen, why, consequences and revisit conditions? |
| Context maps | Where do components, routes, events, permissions, owners and integrations live? |
| Operations | How is it deployed, migrated, recovered, rolled back and diagnosed? |
| Rules | What must never be broken, and what mechanism enforces it? |
| Skills | What repeatable procedure should never be re-derived? |
| Failures & lessons | What failed, root cause, fix, recurrence risk and prevention? |
| Memory | What durable fact, preference, surprise or decision must survive sessions? |
| Future intent | What is planned, why, dependencies, assumptions and what would invalidate it? |
| Provenance | Where did a fact come from, when was it verified, and what would make it stale? |

Akinator **adopts the repository's existing conventions**. It does not create a
parallel wiki if the project already has one.

## Every prompt, documented

The wiki home is [`docs/wiki/index.md`](docs/wiki/index.md) - one canonical page
per kind of knowledge (product, business, market, requirements, drift,
architecture, libraries, stack, infra, testing, UX, project, decisions,
changes, glossary, onboarding), adopted from whatever home the repository
already has for it, never a parallel copy. Every prompt that changes or
decides anything fans out to every home it affects, in the same batch - not
just the one that felt closest. A fact nobody knows yet is written as the
exact line `_Unknown - ask the owner and record the answer._`, so it can be
counted and turned into a question instead of guessed.

**Questions, with defaults.** Up to 15 questions per prompt, asked once, in one
grouped and ranked message, each carrying a recommended default - so "go with
recommendations" is always a complete answer.

**Decide, or recommend.** Reversible, no-blast-radius choices are decided and
recorded without asking. Money, permissions, deletion, security and public
contracts always go to the owner, as 2-4 costed options with one clear
recommendation. See `skills/everything/references/akinator-decide.md`.

Two tools keep the generated half of the wiki honest - facts are generated so
they cannot rot, and the why beside them is curated by hand:

```bash
python skills/everything/scripts/extract_libraries.py --write   # one page per dependency, under docs/wiki/libraries/
python skills/everything/scripts/akinator_wiki.py index         # rebuild the wiki index at docs/wiki/index.md
python skills/everything/scripts/akinator_wiki.py gaps          # every unknown, as a question for the owner
```

See `skills/everything/references/akinator-wiki.md` and
[ADR 0010](docs/adr/0010-every-prompt-documented-living-wiki.md).

### Mandatory change record

Every meaningful behavioral, business, product, architecture, data, API,
security or operational change records:

```
When
Actor / agent (when knowable)
Request / source
Affected code and components
Before
Change
Now
Why
Business intent
Product intent
Technical reasoning
Alternatives / trade-offs
Compatibility / migration / rollback
Rules created or changed
Skills created or changed
Failures / lessons
ADRs / docs / context / memory affected
Verification evidence
Future implications / follow-ups
Stale when
```

Mechanical-only changes may record `knowledge delta: none — <reason>`. Akinator
must not manufacture documentation merely to satisfy itself.

## The automatic loop

```
ASK → RESOLVE → AUDIT → PLAN → IMPLEMENT → DOCUMENT → SKILLIFY → RULE
    → CONTEXTIFY → MEMOIZE → INDEX+SYNC → VERIFY
```

For every meaningful repository change:

1. Resolve existing rules, skills, context, memory, docs and history.
2. Understand intent and surface unknowns instead of inventing business facts.
3. Audit code versus claimed behavior.
4. Plan code **and knowledge delta together**.
5. Implement.
6. Write the durable change record and update the wiki.
7. Turn repeatable procedures into Skills.
8. Record failures; convert reusable recurrence-prevention constraints into enforced Rules.
9. Update architecture/context/memory/ADRs/product/business/ops where affected.
10. Index everything and keep every AI router aligned.
11. Verify code and knowledge once, scoped to what changed.
12. Stop only when the Definition of Done is supported by evidence.

## What "everything" means

`/akinator:everything` and the automatic repository-change path use the same
master orchestrator. "Everything" means every station is evaluated, every
applicable knowledge lens is loaded, and every applicable check is completed.
It does **not** mean writing irrelevant files or inventing facts.

The stations - documentation, ADR, business mapping, rule forging and the
rest - are references inside the one skill, loaded as the pass needs them;
users do not need to learn or call them.

## Knowledge laws

- **Code + knowledge is the change.**
- **One canonical home per fact.** Link instead of copying.
- **Current truth and historical truth are different.** Preserve both.
- **Future intent is labeled future, never presented as implemented.**
- **Every important doc says what would make it stale.**
- **Every failure is recorded; reusable prevention becomes an enforced rule.**
- **Any procedure likely to happen twice becomes a skill.**
- **No guessing on money, permissions, deletion, security or public contracts.**
- **No documentation follow-up.** Knowledge ships in the same batch.
- **No knowledge checks in git hooks.** Enforcement belongs in session behavior,
  tests and CI.
- **Gate once, late and scoped.**
- **Evidence beats claims.**

## Repository development

```bash
python -m pytest tests/ -q
python skills/everything/scripts/akinator_coverage.py . --strict
python skills/everything/scripts/akinator_ledger.py verify
python skills/everything/scripts/akinator_rules.py conflicts
python scripts/build_codex_pack.py --check
python scripts/render_routers.py --check
python skills/everything/scripts/build_brief.py --check
python skills/everything/scripts/extract_libraries.py --check
python skills/everything/scripts/akinator_wiki.py check
```

The one canonical skill lives in `skills/everything/` (its host-repo tools in
`skills/everything/scripts/`). The portable pack in `.agents/` is generated
from it by `scripts/build_codex_pack.py`. AI routers are generated from
`context/router-contract.md`; do not hand-edit generated routers.

## Documentation

- [Architecture](docs/architecture.md)
- [Business case](docs/business-case.md)
- [Compatibility](docs/compatibility.md)
- [Skills](docs/skills.md)
- [Agents](docs/agents.md)
- [ADRs](docs/adr/README.md)
- [Rules](rules/README.md)
- [Context](context/README.md)
- [Memory](memory/index.md)
- [Ledger](docs/ledger.md)
- [Templates](templates/README.md)
- [Living wiki contract](docs/living-wiki.md)
- [The wiki home](docs/wiki/index.md)

## License

MIT — see [LICENSE](LICENSE).

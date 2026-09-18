# ADR 0009 - One skill, one command, one installer

- **Status:** accepted
- **Date:** 2026-09-18
- **Deciders:** Ihab Khaled (owner)
- **Supersedes:** the command-file mechanism of
  `docs/adr/0005-single-command-surface.md` and point 5 of
  `docs/adr/0008-always-on-master-contract.md` ("internal skills remain
  composable implementation details, not user commands"). Both stay, marked; the
  chain is the point.

## Context

The owner asked three times for exactly one command, on every platform. ADR 0005
answered with one file in `commands/`, and ADR 0008 asserted that "the internal
skill count does not enlarge the command surface". Neither was checked against a
menu. The owner's screenshots showed the truth: typing `/akinator` in Claude
Code listed `/akinator:everything` and twenty-one `/akinator:akinator-*` entries.

Verified on 2026-09-18 - the Claude Code row live (2.1.154 and 2.1.276); the
Codex row from its docs and source, and the Cursor row from its docs, neither
run because neither is installed on the verifying machine:

| Platform | What it lists | Can a skill be hidden from the user? |
|---|---|---|
| Claude Code | every command **and every skill**, as `/plugin:skill` | yes - `user-invocable: false` removes it from `/` and blocks `/name`, while the model can still invoke it |
| Codex | every enabled skill in the `$` picker | **no** - `allow_implicit_invocation: false` hides a skill from the model, not from the user |
| Cursor | every skill folder it loads - including `.agents/skills`, which Codex reads too | only a CLI-only `user-invocable` since July 2026; not documented for the IDE |

Two more defects surfaced in the same investigation and shaped the decision:

- The skill's procedure ran tools by paths like `python scripts/akinator_ledger.py`,
  which exist only in Akinator's own checkout. In every repository Akinator was
  installed into, those commands failed.
- Installation was three hand-assembled recipes: a clone plus `--plugin-dir` for
  Claude, a Codex-only script whose `--user` mode never installed the always-on
  contract, and a README instruction to copy Akinator's **own router** into a
  Cursor repository - twenty-one paths that exist only here.

## Decision 1 - how to get one entry on every platform

### Option A - hide the twenty-one skills from the menu

- **What it is:** `user-invocable: false` on every skill but the entry point.
- **Cost:** it works on Claude Code only. Codex has no user-facing hide, and
  Cursor's is CLI-only and undocumented for the IDE, so both would still list
  twenty-one entries - the requirement fails on two of three platforms.
- **Why it lost:** it is a Claude-only answer to a three-platform requirement.

### Option B - one skill; the stations become references inside it (chosen)

- **What it is:** `skills/everything/` is the only skill. Its `SKILL.md` is the
  entry and the station table; the twenty former skills are files in
  `references/`, opened when the work reaches that station; the full step-by-step
  pass is `skills/everything/references/procedure.md`. The skill is also the command, so
  `commands/` is gone.
- **Cost:** the stations lose their own trigger descriptions - the model can no
  longer auto-load `akinator-ops-map` directly from a migration prompt. It loads
  the one skill, whose station table routes it. And `SKILL.md` must stay under
  8,000 bytes, because Codex truncates an explicitly invoked skill there
  (`MAX_SKILL_PROMPT_BYTES`), so the detail moved into references.
- **Why it won:** it is the only design that gives exactly one entry on all
  three platforms, proven rather than asserted: a live Claude Code 2.1.154
  session's `init` event lists `slash_commands` containing `akinator` as exactly
  `['akinator:everything']`. It also matches how all three platforms describe
  skills - progressive disclosure, references loaded on demand.

### Option C - drop skills entirely; ship only the contract

- **What it is:** no skill anywhere; the always-on router text carries everything.
- **Cost:** twenty stations of procedure in every session's context, forever, on
  every platform - the opposite of the capped-brief principle.
- **Why it lost:** it trades menu clutter for context bloat.

## Decision 2 - the name on each platform

Claude Code namespaces plugin skills, so the skill is named `everything` and
appears as `/akinator:everything` - the command the owner already knew. Codex and
Cursor load from a shared `.agents/skills` folder with no namespace, where
`everything` alone would be ambiguous, so the generator projects it as
`akinator`: `$akinator` on Codex, `/akinator` on Cursor. The projection is a
documented transformation in `scripts/build_codex_pack.py`, not a second skill.

## Decision 3 - the tools travel with the skill

The host-repository tools (coverage, ledger, distil, rules, scope, brief, stack
map) moved from `scripts/` into `skills/everything/scripts/`, and the skill runs
them as `<skill>/scripts/...` - one path, true on every platform, because the
folder travels. The build scripts that only make sense in this checkout stay in
`scripts/`.

## Decision 4 - one installer

`install.sh` and its Windows twin `install.ps1`, runnable in one line from
GitHub with no clone:

- **Claude Code:** `claude plugin marketplace add` (the GitHub repository over
  HTTPS - the `owner/repo` shorthand clones over SSH and fails without a key) then
  `claude plugin install akinator@akinator`. Finds the CLI on PATH or inside the
  VS Code extension.
- **Codex and Cursor:** one skill folder in `~/.agents/skills` (or a repository's
  `.agents/skills`) serves both; the always-on contract becomes a marked block in
  `~/.codex/AGENTS.md` (or the repository's `AGENTS.md`, which Cursor also reads)
  and an `alwaysApply` rule in `~/.cursor/rules/` (or the repository's).
- **Upgrades:** removes the per-station skill folders earlier versions left
  behind - otherwise Codex and Cursor keep listing twenty-one of them.
- **Safety:** removes only what carries the Akinator banner or the marked block;
  preserves the user's line endings; uninstall restores a host repository byte
  for byte.

Option considered and rejected: an npm package (`npx akinator-ai install`). It
would need Node and a publish pipeline for a repository that is otherwise
standard-library Python and shell; a script piped from GitHub needs neither.
The cost accepted: piping a script into a shell asks for trust, so the README also
shows the download-then-read form.

## Consequences

**Good.** One entry per platform, proven live. An installed Akinator's commands
run, because its tools travel with it. One line installs or updates any of the
three platforms, and uninstall is exact.

**Bad.** Station references are no longer individually auto-triggered; routing
now depends on the one skill's table. A contributor adding a station must add a
reference and link it, never a skill - the structural tests enforce this, but it
is a less obvious extension point than "add a skill".

**Bad.** Cursor's user-level rule file format (`~/.cursor/rules/*.mdc`) is
inferred from the project format; the docs name the folder but not the format.
If it is ever ignored, the skill's own description still triggers it.

## Revisit when

- Codex gains a way to hide a skill from the user while keeping it for the
  model, and Cursor documents one for the IDE - then per-station skills could
  return without adding menu entries.
- A station's procedure outgrows its reference and needs its own tool-scoped
  permissions, which only a separate skill can express.

## Related

- Rules: `rules/12-artifacts-that-travel-name-nothing-local.md` - evolved in the
  same change to cover everything the installers copy
- Rules: `rules/07-codex-pack-is-generated.md`
- Ledger: `.ai/ledger/failure/slash-menu-listed-every-skill-3f9a0c71e2b5.md`
- Ledger: `.ai/ledger/failure/hook-shell-form-exited-126-8b21c6e0d4f3.md`
- Docs: `docs/skills.md`, `docs/compatibility.md`, `docs/architecture.md`
- Tests: `tests/test_plugin_structure.py`, `tests/test_codex_pack.py`,
  `tests/test_installer.py`

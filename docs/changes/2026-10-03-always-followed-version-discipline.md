# Change - 2.2.0: always followed, version discipline

- **When:** 2026-10-03
- **Who / agent:** Ihab Khaled (owner), via Claude Code (Claude Sonnet 5.5)
- **Source:** owner request 2026-10-03 and the loudness addendum; ADR 0012
- **Status:** implemented; released as 2.2.0

## Before

Akinator reached a session through one calm `SessionStart` contract. Agents on
Claude Code and Codex skipped it on prompts that did not name it, until the
owner shouted. Shipped changes could keep the old version number: nothing
checked it, and three manifests could disagree. The installers' uninstall left
an empty `~/.codex` behind.

## Change

Still one skill, one command, no command file. A `UserPromptSubmit` hook
repeats a three-line, all-caps contract on every prompt; `SessionStart` (no
matcher) carries the full loud contract. The marker `NOT OPTIONAL` is on the
session hook, the prompt hook, the router contract, every router, the Cursor
rule and the portable Codex block, and a test fails if any loses it. New tool
`akinator_version.py` with rule 16 and a CI step. The brief states the current
version and the history page lists the marketplace manifest. Uninstall now
removes the Codex home the installer created, when empty.

## Now

Verified live (`claude --plugin-dir . -p ... --output-format stream-json
--verbose --include-hook-events`): `hook_response` exit 0 for both hooks and
the slash menu lists only `akinator:everything`. The repository is at 2.2.0 in
every manifest, bumped with the new tool.

## Why

The owner: Akinator must always be followed, even when never called; bump the
version always; document everything. Incident: the agent ignored the installed
plugin until shouted at (`.ai/ledger/failure/agent-skipped-the-installed-plugin.md`).

## Files touched

- `hooks/hooks.json`, `hooks/session-start.sh`, `hooks/prompt-reminder.sh`
- `skills/everything/scripts/akinator_version.py`, `skills/everything/scripts/build_brief.py`, `skills/everything/scripts/extract_history.py`
- `skills/everything/SKILL.md`, `skills/everything/references/procedure.md`, `skills/everything/references/akinator-document-change.md`
- `.agents/` - regenerated pack (SKILL.md, scripts, references, AGENTS.md, Cursor rule)
- `scripts/render_routers.py`, `scripts/build_codex_pack.py`, `context/router-contract.md`, and every rendered router
- `rules/16-every-shipped-change-bumps-the-version.md`, `rules/README.md`
- `tests/test_version.py`, `tests/test_plugin_structure.py`, `tests/test_installer.py`
- `install.sh`, `install.ps1`
- `.github/workflows/ci.yml`
- `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `CHANGELOG.md`
- `docs/adr/0012-always-followed-and-version-discipline.md`, `docs/adr/README.md`, `docs/README.md`, `docs/architecture.md`, `docs/compatibility.md`, `docs/skills.md`, `README.md`
- `memory/2026-10-03-the-agent-skips-what-is-not-shouted.md`, `memory/index.md`
- `.ai/ledger/` - failure, decision and two requirement records; `.ai/BRIEF.md`
- `docs/wiki/` - roadmap proposals and regenerated pages

## Would make this stale

An agent platform that makes rules binding, or a change to hook events.
- `skills/everything/scripts/extract_operations.py`, `tests/test_operations.py` - README links on the generated installation page climb back to the repository root (`../../../README.md#Ln`); they were root-relative and only resolved by luck. Found by the i-have-headache and AI-Psychiatry agents; a test pins it.

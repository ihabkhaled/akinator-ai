# Change - One skill, one command, one installer

- **When:** 2026-09-18
- **Actor / agent:** Claude Code coding agent - Claude Opus 5 - on behalf of Ihab Khaled
- **Request / source:** the owner: one command and one skill on every platform, an easy install without a marketplace, and "they are not working fine"
- **Status:** implemented; released as 1.2.0

## Before

Akinator shipped 21 skills plus one command file. The always-on change
(`docs/adr/0008-always-on-master-contract.md`) called that "one command", but
Claude Code listed 22 Akinator entries in its `/` menu, Codex listed every skill
in its `$` picker (it cannot hide one), and Cursor listed every folder it loads.
The SessionStart hook exited 126 on Claude Code 2.1.154 under Git Bash, so the
contract never reached Windows CLI sessions. Cursor users were told to copy
Akinator's own router. The procedure ran tools by paths that exist only in this
repository. Installing meant cloning plus a Codex-only script.

## Change

Collapsed Akinator into one skill, `skills/everything/`: a short `SKILL.md`,
the former skills as station references plus the full procedure in
`skills/everything/references/`, and the host-repo tools in
`skills/everything/scripts/`. Removed the command file. Moved the hook to exec
form. Added the root installers `install.sh` and `install.ps1`, a Cursor rule to
the portable pack, `.mdc` scanning to the coverage checker, and
`test_adr_numbers_are_unique`. Renumbered the duplicate ADR 0006 to 0008.
Retired the generated-logo script and the Codex-only install scripts.

## Now

One entry per platform: `/akinator:everything` in Claude Code, `$akinator` in
Codex, `/akinator` in Cursor - and normally none is typed, because Akinator is
always on (SessionStart hook; Codex `AGENTS.md` block; Cursor `alwaysApply`
rule). One line installs every detected platform, at user scope or into one
repository; re-running updates, and `--uninstall` restores a host repository
byte for byte.

## Why

The owner's requirement is what the user sees in each menu. Each platform lists
every skill it loads, so the only way to show one entry is to ship one skill.

## Technical reasoning

Codex truncates an explicitly invoked `SKILL.md` at 8,000 bytes, so the skill
stays small and loads station references on demand. Tools travel inside the
skill and run as `python <skill>/scripts/<tool>.py`, so nothing names a
repo-only path (rules/12, evolved on its third sighting). Codex and Cursor both
read `.agents/skills`, so one generated folder serves both. The Cursor user-rule
file format is inferred from the project format; Cursor's docs name the folder,
not the format. See `docs/adr/0009-one-skill-one-command-one-installer.md`.

## Compatibility / migration / rollback

Upgrade by re-running the installer: it removes the old per-station skill
folders (only those carrying the Akinator banner). Claude Code users can instead
run `claude plugin marketplace update akinator` and
`claude plugin update akinator@akinator`. Anyone who typed a per-station
`/akinator:akinator-*` or `$akinator-*` entry now uses the one entry; station
ids are unchanged inside the skill. Rollback: reinstall with `--ref` pointing at
the previous release.

## Knowledge delta

- ADR: `docs/adr/0009-one-skill-one-command-one-installer.md`; renumbered
  `docs/adr/0008-always-on-master-contract.md`
- Skill: `skills/everything/SKILL.md`, `skills/everything/references/`
- Docs: `docs/skills.md`, `docs/architecture.md`, `docs/README.md`, `CHANGELOG.md`
- Router source: `context/router-contract.md`
- Memory: `memory/2026-09-18-one-command-is-decided-by-the-menu.md`
- Ledger: `.ai/ledger/failure/slash-menu-listed-every-skill-3f9a0c71e2b5.md`,
  `.ai/ledger/failure/hook-shell-form-exited-126-8b21c6e0d4f3.md`,
  `.ai/ledger/failure/installer-rewrote-line-endings-d7e4a1f09c62.md`,
  `.ai/ledger/failure/adr-number-filed-twice-5c0e93b8a14d.md`,
  `.ai/ledger/failure/byte-compare-test-hid-a-logo-for-7-minutes-e1b6f3a09d27.md`,
  `.ai/ledger/failure/skill-edit-dropped-its-contract-4c1e8a92b7d3.md`,
  `.ai/ledger/decision/distil-a-generated-artifact-that-travels-named-56871dcd648a.md`
- Tests: `tests/test_installer.py`, `tests/test_plugin_structure.py`

## Verification

- Live, Claude Code 2.1.154: the session init event's `slash_commands` entries
  containing "akinator" were exactly `['akinator:everything']`.
- Live: the exec-form SessionStart hook exits 0.
- `tests/test_installer.py` ran the real installers - sh, and PowerShell on
  Windows - against a throwaway home with a stub `claude`.
- The strict coverage checker ran in a scratch target repository with the
  installed skill.
- The new detectors (`.mdc` scanning, unique ADR numbers) were mutation-tested:
  each test fails when its check is removed.
- Not run: the Codex plugin route - Codex is not installed on this machine.

## Future

Verify the Codex plugin route and the Cursor user-rule format on real installs.

## Stale when

Claude Code, Codex or Cursor changes how its menu lists skills, how it loads
`.agents/skills`, or its hook, instruction-file or rule format.

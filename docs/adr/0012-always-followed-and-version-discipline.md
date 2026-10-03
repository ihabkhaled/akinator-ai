# ADR 0012 - Always followed by volume and repetition, and version discipline

- **Status:** accepted
- **Date:** 2026-10-03
- **Deciders:** Ihab Khaled (owner)
- **Builds on:** ADR 0008 (always-on master contract), ADR 0009 (one skill, one
  command), ADR 0011 (cheap deterministic tools).

## Context

Two failures, both reported by the owner. First, Claude and Codex skipped an
installed Akinator on prompts that did not name it - the contract was present
and polite, and the agent judged the procedure unnecessary - until the owner
shouted, after which it complied. Second, shipped changes kept their old
version number, so an installed plugin never saw a fix. The owner's words:
Akinator must always, MUST, be followed even when never called with a slash;
bump the version always; document everything.

## Options

### Option A - keep the polite SessionStart contract

- **Why it lost:** it is what failed. One calm paragraph at session start is
  out-argued by the task in the prompt, and fades over a long session.

### Option B - a new skill or command for versions or for reminders

- **Why it lost:** it breaks one skill, one command (ADR 0009). A second
  `/` entry is the thing the owner removed.

### Option C - volume, repetition and a checkable tool, inside the one skill (chosen)

- **Always followed.** The contract is firm and loud on every surface, and one
  fixed marker, `NOT OPTIONAL`, is asserted by a test on the session hook, the
  prompt hook, the router contract, every rendered router, the Cursor rule and
  the portable Codex block. The register is aimed at the AI only: no profanity,
  nothing aimed at people. A `UserPromptSubmit` hook (`hooks/prompt-reminder.sh`,
  exec form, three lines, exit 0, no permission decision) repeats it on every
  prompt. `SessionStart` keeps no matcher so it fires on startup, resume, clear
  and compact.
- **Version discipline.** `akinator_version.py` (`show`, `check [--base]`,
  `next [--base]`, `bump --date`, `set`) rewrites every manifest at once and
  seeds the changelog heading; rule 16 and a CI step fail a shipped change
  that did not bump.
- **Cost:** about 60 tokens of context per prompt; a firm tone in a public
  repository; a hook that models may still weigh against the task.

## Decision

Option C. No new skill, no command file; both hooks are display-only.

## Consequences

**Good.** The contract is restated where the agent decides, every prompt. A
fix cannot ship under an old number. The slash menu still lists only
`akinator:everything` (verified live with `claude --plugin-dir` and
stream-json: `hook_response` events for both hooks).

**Bad.** Repetition is a lever, not a guarantee; compliance is still a model
behavior. The tool trusts the manifests and shipped globs it knows about;
others go in `.ai/config.json` under `version.shipped`.

## Related

- Rule: `rules/16-every-shipped-change-bumps-the-version.md`
- Ledger: `.ai/ledger/failure/agent-skipped-the-installed-plugin.md`
- Memory: `memory/2026-10-03-the-agent-skips-what-is-not-shouted.md`
- Change: `docs/changes/2026-10-03-always-followed-version-discipline.md`

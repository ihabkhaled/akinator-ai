---
name: verify-contracts-from-installed-plugins
type: surprise
date: 2026-08-26
---

# Installed plugins are better evidence of the platform contract than the docs

## The fact

`~/.claude/plugins/marketplaces/` holds every installed marketplace's real
source, including Anthropic's own `plugin-dev` plugin, whose skills document the
plugin contract authoritatively - manifest location, component directories,
hook file format, `${CLAUDE_PLUGIN_ROOT}` semantics.

Reading those, plus a few real `hooks.json` files from shipped plugins, settled
every contract question for the Claude side of this build without a single web
fetch. The web was needed only for the Codex contract, which is not installed
locally.

## Why

Documentation describes the intended contract; an installed plugin *is* the
contract, as the currently running version implements it. When they disagree,
the installed artifact wins, and the disagreement is itself worth knowing.

Two specifics that only the installed files made obvious:

- Plugin `hooks.json` wraps events in a `hooks` key. The settings-file format
  does not. Getting this backwards produces a hook that silently never fires.
- Real plugins invoke hook scripts as `sh "${CLAUDE_PLUGIN_ROOT}/..."`, quoted -
  which matters on paths containing spaces, and on Windows.

## Date

- 2026-08-26 - recorded while building Akinator's Phase 1.

## Reversal conditions

- Claude Code stops vendoring marketplace sources locally, or moves them out of
  `~/.claude/plugins/marketplaces/`.
- A future contract change ships in documentation before it ships in any
  installed plugin - then the docs lead and this heuristic inverts.

## Related

- `docs/compatibility.md` - the contracts this plugin relies on
- `tests/test_plugin_structure.py` - where those contracts are asserted

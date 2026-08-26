# Compatibility

The platform contracts Akinator relies on, how they were verified, and what
breaks when they move.

**Verified:** 2026-08-26.

## Tested against

| Platform | Version | How verified |
|---|---|---|
| Claude Code | 2.1.154 | `claude --version`, plus the installed Anthropic `plugin-dev` plugin's own skills, which document the contract authoritatively |
| Codex | contract as documented 2026-08 | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) (redirects to [learn.chatgpt.com/docs/build-skills.md](https://learn.chatgpt.com/docs/build-skills.md)), and the plugin manifest spec in [openai/codex](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/plugin-creator/references/plugin-json-spec.md) |
| Python | 3.13 | scripts and tests are stdlib-only; pytest for the suite |

The Claude side was verified against **installed artifacts** rather than
documentation. See `memory/2026-08-26-verify-contracts-from-installed-plugins.md`
for why that is the stronger evidence, and for two specifics that only the
installed files made obvious.

## Claude Code plugin contract

### What Akinator relies on

| Contract | Akinator's use | Breaks if |
|---|---|---|
| Manifest at `.claude-plugin/plugin.json`; `name` required | plugin identity, version, license | the manifest location or required fields change |
| Component directories at **plugin root**, not nested inside `.claude-plugin/` | `skills/`, `commands/`, `agents/`, `hooks/` | auto-discovery moves |
| `skills/<name>/SKILL.md`, frontmatter `name` + `description`, auto-discovered | all 21 skills; description is the trigger | frontmatter keys change, or auto-trigger stops keying off `description` |
| `commands/*.md`, frontmatter `description`, `argument-hint`, `allowed-tools` | the single `/akinator` command | frontmatter keys change |
| `agents/*.md`, frontmatter `name` + `description`, optional `tools` | the 7 boardroom lenses | subagent definition format changes |
| `hooks/hooks.json` in the **plugin format** - events wrapped in a `hooks` key | the SessionStart contract injection | the wrapper is dropped or renamed |
| `SessionStart` hook stdout is added to session context | the contract reaches the session before the first tool call | stdout handling changes, or SessionStart is removed |
| `${CLAUDE_PLUGIN_ROOT}` expands in hook commands | portable hook invocation | the variable is renamed |
| `.claude-plugin/marketplace.json` with `plugins[].source` | `/plugin marketplace add` installation | the marketplace schema changes |

### The plugin format trap

Plugin `hooks.json` wraps events in a `hooks` key:

```json
{
  "description": "...",
  "hooks": { "SessionStart": [ { "hooks": [ { "type": "command", "command": "..." } ] } ] }
}
```

The **settings** format puts events at the top level with no wrapper. Getting
this backwards produces a hook that is silently never called - no error, no
warning. Asserted by
`tests/test_plugin_structure.py::test_hooks_json_uses_the_plugin_format`.

### Verified components

Akinator uses only auto-discovery. It declares no custom component paths in the
manifest, so it depends on the default directory layout and nothing more.

It does **not** use: MCP servers, `.mcp.json`, prompt-type hooks, `PreToolUse` /
`PostToolUse` / `Stop` hooks, output styles, or `$CLAUDE_ENV_FILE`.

## Codex contract

### What Akinator relies on

| Contract | Akinator's use | Breaks if |
|---|---|---|
| Skills read from `.agents/skills/` - repository scope walking up to the repo root, then `$HOME/.agents/skills` | where the generated pack is installed | the search path changes |
| `SKILL.md` with frontmatter `name` + `description` | identical shape to Claude's, which is why generation is a banner-only transformation | the frontmatter contract diverges |
| Implicit selection from `description`, explicit invocation with `$name` | skills fire without a command | selection stops keying off `description` |
| `AGENTS.md` read at repo root, hierarchically, more specific files winning | the generated Codex router | the filename or hierarchy changes |
| `.codex-plugin/plugin.json`: required `name`, `version`, `description`, `author.name`, `interface` | the Codex plugin manifest | required fields change |
| Required `interface` fields: `displayName`, `shortDescription`, `longDescription`, `developerName`, `category`, `capabilities` | manifest validity | the interface schema changes |
| Validation **rejects** unsupported manifest fields such as `hooks` | why Akinator has no Codex hook surface | validation loosens |
| `interface.composerIcon` and `interface.logo` are **required**, and must reference **square** images that exist in the plugin | `assets/akinator-icon.png`, `assets/akinator-logo.png` - both 512x512 | the asset contract changes |
| Files directly under `skills/` are **not imported**, and fail validation | the skills index lives at `docs/skills.md`, never as a README inside `skills/` | the import rule changes |
| URLs must be absolute `https://`; asset paths must point at real files; no `[TODO: ...]` placeholders | manifest passes validation | tightened further |

### The asset requirement

`composerIcon` and `logo` are **required**, not optional - an earlier revision of
this document said otherwise and was wrong. Both must reference square images
that really exist inside the plugin.

Akinator's are generated, not committed as opaque binaries:
`scripts/generate_assets.py` draws the mark from a signed distance field and
encodes the PNG with the standard library. That keeps their provenance - the mark
is defined in code, reviewable as a diff, and re-renderable at any size - and it
means `--check` can prove the committed bytes match the generator.

Asserted by `tests/test_plugin_structure.py`:
`test_codex_manifest_declares_required_asset`,
`test_required_asset_is_a_square_png`, and
`test_assets_are_generated_not_committed_by_hand`.

### The skills-directory requirement

Both platforms import skills by scanning `skills/` for subdirectories containing
`SKILL.md`. A loose file directly under `skills/` is not imported, and Codex
validation rejects the plugin for it.

The trap is that the loose file is usually a README index - the right instinct in
a normal repository, and the wrong one in a plugin. Akinator shipped exactly that
defect in its first build:

```
skills/
  README.md          <- linked from every router, and not imported
  akinator/
    SKILL.md
```

The index now lives at `docs/skills.md`. See
`rules/08-skills-dir-holds-only-skill-directories.md`.

### Deliberate omissions in the Codex manifest

- **No `hooks` field.** Validation rejects it. The SessionStart contract is a
  Claude-only surface; Codex gets the same content from `AGENTS.md`.
- **No `logoDark`.** Optional, and the mark already reads on both light and dark
  grounds - the icon carries its own deep navy field rather than relying on the
  host background.
- **No `privacyPolicyURL` / `termsOfServiceURL`.** Optional, and they would point
  at documents that do not exist. Adding the URL before the document would be
  exactly the fake compliance the plugin forbids.

### Codex skills path: `.agents/skills`, not `.codex/skills`

Worth stating because it is easy to assume otherwise, and because an earlier
convention used `.codex/`. The current contract is `.agents/skills`, at
repository, user and admin scope. Akinator's installers target it, and
`AGENTS.md` documents it for the reader.

## Where the contracts differ, and what Akinator does about it

| Aspect | Claude Code | Codex | Akinator's response |
|---|---|---|---|
| Skills location | `skills/` inside the plugin | `.agents/skills/` in the repo or `$HOME` | `skills/` is canonical; the pack is generated |
| Skill format | `SKILL.md`, `name` + `description` | identical | a banner-only transformation |
| Root context file | `CLAUDE.md` | `AGENTS.md` | both generated or maintained together; `router-sync` fails a fork |
| Session hook | `hooks/hooks.json`, `SessionStart` | none - manifest rejects `hooks` | the contract lives in `AGENTS.md` for Codex |
| Subagents | `agents/*.md` | no equivalent | the lenses are applied inline on Codex |
| Commands | `commands/*.md` | no direct equivalent | Codex users invoke `$akinator` or describe the task |

## When a contract moves

The failure is designed to be **loud**:

1. `tests/test_plugin_structure.py` asserts every contract in the tables above.
   A moved contract fails a named test rather than producing a plugin that
   loads and silently does nothing.
2. Update the affected component, update this document with the new version and
   the new behavior, and record an ADR if the change forced a design decision.
3. If a component becomes unavailable on one platform, the response is the same
   one used for Codex hooks: move the content to a surface that platform does
   read, and say so here - never let the two platforms carry different contracts.

## Review when

- Claude Code or Codex ships a plugin-contract change.
- A new AI tool is added to the router set.
- Last verified: 2026-08-26, against Claude Code 2.1.154.

## Related

- `docs/adr/0002-codex-pack-generated-from-claude-skills.md`
- `context/components.md` - which surface each component serves
- `tests/test_plugin_structure.py` - where these contracts are asserted

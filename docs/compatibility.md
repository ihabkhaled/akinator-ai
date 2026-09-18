# Compatibility

The platform contracts Akinator relies on, how they were verified, and what
breaks when they move.

**Verified:** 2026-08-26; refreshed 2026-09-18 for version 1.2.0 (one skill,
one command, one installer - `docs/adr/0009-one-skill-one-command-one-installer.md`).

## Tested against

| Platform | Version | How verified |
|---|---|---|
| Claude Code | 2.1.154 (CLI on PATH); 2.1.276 (bundled in the VS Code extension) | `claude --version`, the installed Anthropic `plugin-dev` plugin's own skills, and on 2026-09-18 live sessions: the init event's `slash_commands`, `--plugin-url`, and the hook exit code |
| Codex | contract as documented 2026-09 - **not run**, Codex is not installed on the verifying machine | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) (redirects to [learn.chatgpt.com/docs/build-skills.md](https://learn.chatgpt.com/docs/build-skills.md)), and the plugin manifest spec in [openai/codex](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/plugin-creator/references/plugin-json-spec.md) |
| Cursor | contract as documented 2026-09 - **not run** | cursor.com docs and changelog |
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
| Component directories at **plugin root**, not nested inside `.claude-plugin/` | `skills/`, `agents/`, `hooks/` - there is no `commands/` directory | auto-discovery moves |
| `skills/<name>/SKILL.md`, frontmatter `name` + `description`, auto-discovered | the one skill, `skills/everything/SKILL.md`; description is the trigger | frontmatter keys change, or auto-trigger stops keying off `description` |
| Every plugin skill is listed in the `/` menu as `/<plugin>:<skill>` | the skill **is** the command: `/akinator:everything` | skills stop appearing in the menu |
| `agents/*.md`, frontmatter `name` + `description`, optional `tools` | the 7 boardroom lenses | subagent definition format changes |
| `hooks/hooks.json` in the **plugin format** - events wrapped in a `hooks` key | the SessionStart contract injection | the wrapper is dropped or renamed |
| `SessionStart` hook stdout is added to session context | the contract reaches the session before the first tool call | stdout handling changes, or SessionStart is removed |
| `${CLAUDE_PLUGIN_ROOT}` expands in hook commands and args | portable hook invocation | the variable is renamed |
| Hooks in **exec form** - `command` plus `args` | `"command": "sh"`, `"args": ["${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"]` | exec form is dropped |
| `.claude-plugin/marketplace.json` with `plugins[].source` | `claude plugin marketplace add <git URL>` then `claude plugin install akinator@akinator` | the marketplace schema changes |

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

### Verified live on 2026-09-18

- **The `/` menu lists every skill.** With one command and 21 skills, the
  owner's menu showed 22 Akinator entries. After the collapse, a 2.1.154
  session's init event lists the `slash_commands` containing "akinator" as
  exactly `['akinator:everything']`.
- **`user-invocable: false` hides a skill from `/`** (verified live). Akinator
  no longer needs it: it ships one skill, and that skill is the entry.
- **Shell-form hooks exit 126 under Git Bash.** The earlier hook was
  `sh "${CLAUDE_PLUGIN_ROOT}/..."` as one command string; on 2.1.154 under Git
  Bash it exited 126, so the contract silently never reached CLI sessions on
  Windows. Exec form (`command` + `args`) exits 0, verified live on 2.1.154.
  Exec form needs Claude Code 2.1.139+ and, on Windows, `sh.exe` on PATH (Git
  for Windows). Without it the hook cannot run; the skill's description still
  triggers the contract, but the session-start injection is lost.
- **`--plugin-url` accepts a GitHub archive zip** and unwraps its single wrapper
  directory, verified live: the plugin loads for that session only.

  ```
  claude --plugin-url https://github.com/ihabkhaled/akinator-ai/archive/refs/heads/main.zip
  ```

- **Marketplace from a git URL** (documented; not run, to avoid changing the
  verifying machine's configuration). The docs say the https `.git` URL is
  cloned over https, while the `owner/repo` shorthand clones over SSH and fails
  without a GitHub SSH key. They also say adding a marketplace with the same
  name replaces the old registration; the 2.1.154 binary's marketplace code
  logs that overwrite and skips deleting a local directory source.
- **The VS Code extension manages plugins with `/plugins`** (Manage plugins).
  Whether the singular terminal `/plugin` works in the extension panel was not
  tested.
- **Updates reach users only when the version string is bumped.**

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
| The manifest spec validator **rejects** a `hooks` field | why Akinator's Codex manifest declares none. Codex plugins can ship a separate hooks file that the user must review and trust; Akinator uses the `AGENTS.md` block instead, which needs no trust prompt | validation loosens |
| `interface.composerIcon` and `interface.logo` are **required**, and must reference **square** images that exist in the plugin | the owner's hand-designed artwork, square PNG (1254x1254) | the asset contract changes |
| Files directly under `skills/` are **not imported**, and fail validation | the skills index lives at `docs/skills.md`, never as a README inside `skills/` | the import rule changes |
| URLs must be absolute `https://`; asset paths must point at real files; no `[TODO: ...]` placeholders | manifest passes validation | tightened further |

### Verified from docs and source on 2026-09-18 (not run)

From the learn.chatgpt.com docs and the openai/codex source:

- Skills load from `.agents/skills` (repository, walking up to the repo root)
  and `~/.agents/skills` (user); `~/.codex/skills` is deprecated but still loaded.
- **There is no way to hide a skill from the `$` picker.** In a skill's
  agents/openai.yaml file, `policy.allow_implicit_invocation: false` hides it from
  the model only. This is why Akinator ships one skill rather than hiding 20.
- **Explicit invocation injects `SKILL.md` truncated at 8,000 bytes**
  (`MAX_SKILL_PROMPT_BYTES`). This is why Akinator's `SKILL.md` is capped under
  8,000 bytes and the detail lives in its `references/`.
- Unknown frontmatter keys are ignored. `name` is capped at 64 characters;
  `description` is not length-checked at parse time, but the skills catalog
  truncates it at 1,024, and the Agent Skills spec sets 1,024 as the limit.
- Global instructions are `$CODEX_HOME/AGENTS.md` (default `~/.codex`);
  `AGENTS.override.md` wins if non-empty (in a repository directory, an
  override that merely exists wins). Per current Codex source - the docs say
  once per run - the global file is re-read at every turn boundary, while
  project files are cached until the working directory or trust changes. The installer merges a marked `akinator:begin` /
  `akinator:end` block there and warns if an override file exists.
- Plugins: `codex plugin marketplace add` and `codex plugin add` read
  `.claude-plugin/marketplace.json` and `.codex-plugin/plugin.json`, namespace
  skills as `plugin:skill` (so `$akinator:everything`). `.codex-plugin/plugin.json`
  is now a compatibility manifest; a root `plugin.json` with the Agent Plugins
  schema is preferred. The plugin route does not add the always-on
  `AGENTS.md` block, and plugins are not available in the Codex IDE extension -
  so the installer is the recommended Codex route.

### The asset requirement

`composerIcon` and `logo` are **required**, not optional - an earlier revision of
this document said otherwise and was wrong. Both must reference square images
that really exist inside the plugin.

Akinator's are hand-designed artwork (1254x1254 PNG), committed by the owner
on 2026-09-18. They replaced an earlier geometric mark that a script drew from a
signed distance field; that generator was retired the same day rather than left
to overwrite the artwork. See `docs/deviations.md`, item 4.

Asserted by `tests/test_plugin_structure.py`:
`test_codex_manifest_declares_required_asset` and
`test_required_asset_is_a_square_png`. Codex needs a square image that exists;
nothing about how it was made is part of the contract.

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
repository, user and admin scope. The one installer (`install.sh`,
`install.ps1`) targets it, and `AGENTS.md` documents it for the reader.

## Cursor contract

Verified from cursor.com docs and changelog on 2026-09-18; **not run**.

| Contract | Akinator's use | Breaks if |
|---|---|---|
| Project rules are `.mdc` files in `.cursor/rules` with `description`, `globs`, `alwaysApply`; plain `.md` there is ignored | the contract as an `alwaysApply` rule, generated at `.agents/cursor/akinator.mdc` | the rule format changes |
| User rule files in `~/.cursor/rules` (since 2.1) | the installer writes the user-scope rule there | the folder moves |
| Agent Skills (since 2.4) from `.agents/skills`, `.cursor/skills`, `~/.agents/skills`, `~/.cursor/skills`, plus the Claude and Codex compatibility directories | the same one skill folder serves Codex and Cursor | the search path changes |
| Skill `name` must match its folder | projected as `akinator` in `.agents/skills/akinator/` | the rule changes |
| Every loaded skill is listed in `/` | one skill means one entry, `/akinator` | - |
| A repository's root `AGENTS.md` is read | a second always-on path | Cursor stops reading it |

- The docs name the user rules folder but not its file format. Akinator's user
  rule uses the project `.mdc` format - **inferred, not documented**.
- Commands (a `.cursor/commands` folder) still exist, but Cursor now points
  users to skills.
- There is no standalone remote-rules import. Cursor plugins need a
  marketplace.json under a .cursor-plugin folder, which Akinator does not ship, so the
  installer is the Cursor route.
- Correction: earlier README text told Cursor users to copy Akinator's own
  `.cursor/rules/akinator.mdc` - a router naming paths that exist only in
  Akinator's repository. The rule that travels is the generated
  `.agents/cursor/akinator.mdc`.

## Where the contracts differ, and what Akinator does about it

| Aspect | Claude Code | Codex | Cursor | Akinator's response |
|---|---|---|---|---|
| Skills location | `skills/` inside the plugin | `.agents/skills/` in the repo or home | `.agents/skills/` (and others) in the repo or home | `skills/everything/` is canonical; `.agents/skills/akinator/` is generated and serves Codex and Cursor |
| Skill format | `SKILL.md`, `name` + `description` | identical; truncated at 8,000 bytes on explicit invocation | identical; `name` matches the folder | one `SKILL.md` under 8,000 bytes; detail in `references/` |
| Root context file | `CLAUDE.md` | `AGENTS.md` | `.mdc` rules, root `AGENTS.md` | all generated together; `router-sync` fails a fork |
| Session hook | `hooks/hooks.json`, `SessionStart`, exec form | none - manifest rejects `hooks` | none | always-on via the `AGENTS.md` block (Codex) and an `alwaysApply` rule (Cursor) |
| Subagents | `agents/*.md` | no equivalent | no equivalent | the lenses are applied inline |
| Commands | none - skills are the `/` entries | none - skills fill the `$` picker and cannot be hidden | command files exist; skills are listed in `/` | no command files; one skill |
| One entry | `/akinator:everything` | `$akinator` | `/akinator` | normally nobody types it: Akinator is always on |

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

- Claude Code, Codex or Cursor ships a plugin, skill or rules contract change.
- A new AI tool is added to the router set.
- Last verified: 2026-09-18, against Claude Code 2.1.154 (CLI) and 2.1.276 (VS
  Code extension); Codex and Cursor from docs and source only.

## Related

- `docs/adr/0002-codex-pack-generated-from-claude-skills.md`
- `docs/adr/0009-one-skill-one-command-one-installer.md`
- `tests/test_installer.py` - runs the real installers against a throwaway home
- `context/components.md` - which surface each component serves
- `tests/test_plugin_structure.py` - where these contracts are asserted

# The skill

Akinator is **one skill and one command** - on every platform.

| Platform | The one entry | How it is always on |
|---|---|---|
| Claude Code | `/akinator:everything` | the plugin's SessionStart hook |
| Codex | `$akinator` | a marked block in `AGENTS.md` |
| Cursor | `/akinator` | an always-applied rule |

You normally type none of them: the contract applies to every prompt. The
explicit form is for when you want to say "the full pass" out loud.

## The skill

| Skill | Use when |
|---|---|
| [everything](../skills/everything/SKILL.md) | Every prompt in a repository. For anything that can change the repository - a feature, a fix, a refactor, docs, onboarding, an audit, a release - it runs the complete pass so the code and the knowledge around it change together. It is also the one command |

Canonical source: `skills/everything/`. It holds `SKILL.md`, its station
`references/` and its host-repository tools in `scripts/`. The Codex and Cursor
copy in `.agents/skills/akinator/` is generated from it by
`scripts/build_codex_pack.py`.

**Why one skill, not twenty-one.** Claude Code lists every skill in its `/` menu,
Codex has no way to hide a skill from its `$` picker, and Cursor lists every
folder in `.agents/skills`. Twenty-one skills meant twenty-one entries on every
platform, for a plugin whose owner asked for exactly one. The stations became
reference files inside the one skill - loaded on demand, never listed. See
`docs/adr/0009-one-skill-one-command-one-installer.md`.

## Its station references

Each is opened when the work reaches that station. They carry the full
procedure of what used to be separate skills, and keep their old names as
**station ids** - which is how the rest of Akinator refers to them.

### The pass

| Reference | Load when |
|---|---|
| [procedure](../skills/everything/references/procedure.md) | Running the complete pass: the five phases, their exit conditions and every tool command |
| [akinator](../skills/everything/references/akinator.md) | The full creed, the twelve-station loop, the knowledge taxonomy (where each kind of fact lives) and the non-negotiables |

### The loop's stations

| Station | Reference | Load when |
|---|---|---|
| 1 ASK | [akinator-intake](../skills/everything/references/akinator-intake.md) | Before planning substantive work, at an ambiguity gate, or when implementation forces a product decision no doc answers |
| 3 AUDIT | [akinator-audit](../skills/everything/references/akinator-audit.md) | Something is claimed to already exist. Returns done / partial / missing, and catches present-but-not-wired |
| 4 PLAN | [akinator-plan](../skills/everything/references/akinator-plan.md) | Before implementing anything multi-step. Declares the knowledge delta by path, per batch |
| 6 DOCUMENT | [akinator-document-change](../skills/everything/references/akinator-document-change.md) | In the same batch as the code. Routes the why, the when-not-to, the business meaning and the operational consequence to their homes |
| 7 SKILLIFY | [akinator-skillify](../skills/everything/references/akinator-skillify.md) | A procedure was worked out that will happen again - the host repository's own skill, written the first time |
| 8 RULE | [akinator-rule-forge](../skills/everything/references/akinator-rule-forge.md) | A constraint was established. Turns it into a numbered rule with a real enforcement mechanism |
| 9 CONTEXTIFY | [akinator-contextify](../skills/everything/references/akinator-contextify.md) | A structural fact changed. Updates the map and builds the extractor so it regenerates instead of drifting |
| 10 MEMOIZE | [akinator-memoize](../skills/everything/references/akinator-memoize.md) | A durable fact, preference, surprise or dead end is worth carrying forward |
| 11 INDEX | [akinator-index-sync](../skills/everything/references/akinator-index-sync.md) | An artifact was created, renamed, moved or deleted. Unindexed means nonexistent |
| 11 SYNC | [akinator-router-sync](../skills/everything/references/akinator-router-sync.md) | What a router says has changed. All routers update together or truth forks |
| 12 VERIFY | [akinator-gate-economy](../skills/everything/references/akinator-gate-economy.md) | Before any lint, typecheck, test or build, and before any commit during multi-step work |
| ALWAYS | [akinator-wiki](../skills/everything/references/akinator-wiki.md) | After every prompt that changes or decides anything - even with no code change. The repository is its own wiki; fans the update out to every home it affects (product, business, market, requirements, drift, architecture, libraries, stack, infra, testing, UX, project, decisions, changes, glossary, onboarding), in the same batch |
| 1 ASK / 4 PLAN | [akinator-decide](../skills/everything/references/akinator-decide.md) | A choice must be made - forced by implementation, asked by the owner, or a prompt contradicts a recorded decision. Classifies decide-and-record versus recommend-and-ask, builds costed options, recommends one, and records the outcome |

### When the work touches their domain

| Reference | Load when |
|---|---|
| [akinator-adr](../skills/everything/references/akinator-adr.md) | A decision was made between real alternatives that will be questioned later |
| [akinator-business-map](../skills/everything/references/akinator-business-map.md) | Money, plans, quotas, entitlements, refunds - anything a customer is charged or granted |
| [akinator-product-map](../skills/everything/references/akinator-product-map.md) | Building, changing or removing a user-facing feature |
| [akinator-ops-map](../skills/everything/references/akinator-ops-map.md) | A change alters how the system is deployed, migrated, restarted, recovered or rolled back |
| [akinator-onboard](../skills/everything/references/akinator-onboard.md) | The repository has no knowledge layer yet. Detects what exists and adopts it |
| [akinator-coverage](../skills/everything/references/akinator-coverage.md) | Auditing whether a knowledge layer is complete, reachable and true |
| [akinator-anti-gaming](../skills/everything/references/akinator-anti-gaming.md) | Reviewing whether documentation work is real, or when tempted to weaken a failing check |
| [akinator-resource-guard](../skills/everything/references/akinator-resource-guard.md) | Before anything heavy, and at the end of every task |

### Templates these stations write

`akinator-wiki` and `akinator-decide` write against three templates added for
the living wiki, each with a filled example in `templates/examples/`:
[library-page.md](../templates/library-page.md) (generated facts plus curated
why/how/pitfalls/upgrade - written by `extract_libraries.py`, curated by hand),
[requirement.md](../templates/requirement.md) (one requirements-register entry:
current, changed, missing or dropped, with its source and append-only
history), and [business-drift.md](../templates/business-drift.md) (one change
of direction: before, after, why, who decided, impact).

## Changing the skill

1. Edit `skills/everything/` - it is canonical. A new station is a new file in
   `references/`, linked from `SKILL.md`, declared in
   `scripts/extract_components.py`. Never a new skill: every skill is another
   menu entry on every platform.
2. Keep `SKILL.md` under 8,000 bytes. Codex truncates an explicitly invoked
   skill there, so detail belongs in `references/`.
3. Regenerate the portable pack **in the same batch**:
   `python scripts/build_codex_pack.py --write`.
4. Update this index and every router.

CI fails on drift between `skills/everything/` and `.agents/skills/akinator/` -
see `rules/07-codex-pack-is-generated.md`. The structural tests fail if a second
skill, a command file, an unlinked reference or an oversized `SKILL.md` appears -
see `tests/test_plugin_structure.py`.

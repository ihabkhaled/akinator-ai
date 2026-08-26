# Skills

The 21 canonical skills. These are the source of truth: the Codex pack in
`.agents/skills/` is generated from them by `scripts/build_codex_pack.py`.

Every skill carries all six parts - see `rules/02-skills-carry-all-six-parts.md`.
Written with `templates/skill.md`; see `templates/examples/skill.md` for a fully
worked example.

## Start here

| Skill | Use when |
|---|---|
| [akinator-everything](../skills/akinator-everything/SKILL.md) | **The all-in-one pass.** Every station, every boardroom lens, every mechanical check, looping until the Definition of Done is proven with evidence. This is what `/akinator` runs |
| [akinator](../skills/akinator/SKILL.md) | Touching a codebase in any way. The creed, the twelve-station loop, the knowledge taxonomy, and the routing table for every other skill. Scales the loop to the size of the change |

The two are deliberately different settings. `akinator` is the always-on default
and scales down for small work, though stations 6-11 still run and simply
produce nothing. `akinator-everything`
is deliberately invoked, assumes the work is worth maximum thoroughness, and does
not scale down.

## The loop's stations

| Station | Skill | Use when |
|---|---|---|
| 1 ASK | [akinator-intake](../skills/akinator-intake/SKILL.md) | Before planning substantive work, at an ambiguity gate, or when implementation forces a product decision no doc answers |
| 3 AUDIT | [akinator-audit](../skills/akinator-audit/SKILL.md) | Something is claimed to already exist. Returns done / partial / missing, and catches present-but-not-wired |
| 4 PLAN | [akinator-plan](../skills/akinator-plan/SKILL.md) | Before implementing anything multi-step. Declares the knowledge delta by path, per batch |
| 6 DOCUMENT | [akinator-document-change](../skills/akinator-document-change/SKILL.md) | In the same batch as the code. Routes the why, the when-not-to, the business meaning and the operational consequence to their homes |
| 7 SKILLIFY | [akinator-skillify](../skills/akinator-skillify/SKILL.md) | A procedure was worked out that will happen again. Write it the first time |
| 8 RULE | [akinator-rule-forge](../skills/akinator-rule-forge/SKILL.md) | A constraint was established. Turns it into a numbered rule with a real enforcement mechanism |
| 9 CONTEXTIFY | [akinator-contextify](../skills/akinator-contextify/SKILL.md) | A structural fact changed. Updates the map and builds the extractor so it regenerates instead of drifting |
| 10 MEMOIZE | [akinator-memoize](../skills/akinator-memoize/SKILL.md) | A durable fact, preference, surprise or dead end is worth carrying forward |
| 11 INDEX | [akinator-index-sync](../skills/akinator-index-sync/SKILL.md) | An artifact was created, renamed, moved or deleted. Unindexed means nonexistent |
| 11 SYNC | [akinator-router-sync](../skills/akinator-router-sync/SKILL.md) | What a router says has changed. All routers update together or truth forks |
| — | [akinator-adr](../skills/akinator-adr/SKILL.md) | A decision was made between real alternatives that will be questioned later |

## Business, product and operations

| Skill | Use when |
|---|---|
| [akinator-business-map](../skills/akinator-business-map/SKILL.md) | Work touches money, plans, quotas, entitlements, refunds - anything a customer is charged or granted |
| [akinator-product-map](../skills/akinator-product-map/SKILL.md) | Building, changing or removing a user-facing feature. Captures intent, acceptance criteria and the edge-case decision log |
| [akinator-ops-map](../skills/akinator-ops-map/SKILL.md) | A change alters how the system is deployed, migrated, restarted, recovered or rolled back |

## Discipline

| Skill | Use when |
|---|---|
| [akinator-gate-economy](../skills/akinator-gate-economy/SKILL.md) | Before any lint, typecheck, test or build, and before any commit during multi-step work |
| [akinator-resource-guard](../skills/akinator-resource-guard/SKILL.md) | Before anything heavy, and at the end of every task. Reduce your own load, never the developer's |
| [akinator-anti-gaming](../skills/akinator-anti-gaming/SKILL.md) | Reviewing whether documentation work is real, or when tempted to weaken a failing check |

## Installation and audit

| Skill | Use when |
|---|---|
| [akinator-onboard](../skills/akinator-onboard/SKILL.md) | Installing Akinator into a repository. Detects what exists and adopts it rather than replacing it |
| [akinator-coverage](../skills/akinator-coverage/SKILL.md) | Auditing whether a knowledge layer is complete, reachable and true. Mechanical invariants plus the newcomer test |

## Adding or changing a skill

1. Edit or create the skill here - this directory is canonical.
2. Regenerate the Codex pack **in the same batch**:
   `python scripts/build_codex_pack.py --write`
3. Add it to this index and to every router.

CI fails on drift between `skills/` and `.agents/skills/` - see
`rules/07-codex-pack-is-generated.md`.

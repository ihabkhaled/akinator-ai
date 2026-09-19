---
name: akinator
description: Use for every prompt in a repository - Akinator is always on and this is its only skill. For any intent that can change the repository (feature, fix, refactor, upgrade, deletion, migration, docs, onboarding, audit, release), run the complete Akinator pass so code, product intent, business logic, decisions, history, skills, rules, context and verification evolve together in one change. Also the one explicit command. Loads its station references on demand.
---
<!--
DO NOT EDIT BY HAND.
Installed from the Akinator plugin - its one skill, which Claude Code calls /akinator:everything.
No generator is named by path: this file travels into repositories
that do not have one, where naming it would be a false claim.
To update: reinstall Akinator, or regenerate inside an Akinator
checkout. Local edits here are replaced either way.
-->

# Akinator

Ask everything. Document everything. Skillify everything. Rule everything.
A change is the code **plus** the knowledge that lets the next agent act on it
in seconds. Half a change is no change.

**Every prompt is documented.** Whatever a prompt changes or decides lands in
the repository's living wiki in the same batch - product, business, market,
requirements, drift, architecture, libraries, stack, infra, testing, UX, project,
decisions, changes - plus README, install docs, every agent router, rules,
memory, context and the ledger. Any AI that reads the repo then knows it from
the needle to the rocket, and can decide or recommend with evidence. See
[akinator-wiki](references/akinator-wiki.md).

**This is Akinator's only skill and its only command.** Normal prompts enter it
automatically. The explicit form is a fallback: `/akinator:everything` on Claude
Code, `$akinator` on Codex, `/akinator` on Cursor. Each station is a reference
file inside this skill, opened when the work reaches it - never a separate skill.

`<skill>` means the directory holding this file. `<skill>/references/` holds the
stations; `<skill>/scripts/` holds the tools. Both travel with the skill.

## When to use

- Every prompt in a repository. For pure conversation it only resolves context.
- Any intent that can change the repository, and whenever the user asks for
  "everything" or "the full pass".
- Before a release, handover or audit; on money, permissions, deletion, public
  contracts or migrations.

## When NOT to use

- To manufacture changes during pure conversation.
- Inside a narrow subagent whose parent owns the pass.
- As a substitute for thinking: it guarantees nothing is skipped, not that every
  judgment is right.

## The stations

| # | Station | Reference |
|---|---|---|
| 1 | ASK | [akinator-intake](references/akinator-intake.md) |
| 2 | RESOLVE | [akinator](references/akinator.md) - creed, loop, taxonomy |
| 3 | AUDIT | [akinator-audit](references/akinator-audit.md) |
| 4 | PLAN | [akinator-plan](references/akinator-plan.md) |
| 5 | IMPLEMENT | the repository's own conventions |
| 6 | DOCUMENT | [akinator-document-change](references/akinator-document-change.md) |
| 7 | SKILLIFY | [akinator-skillify](references/akinator-skillify.md) |
| 8 | RULE | [akinator-rule-forge](references/akinator-rule-forge.md) |
| 9 | CONTEXTIFY | [akinator-contextify](references/akinator-contextify.md) |
| 10 | MEMOIZE | [akinator-memoize](references/akinator-memoize.md) |
| 11 | INDEX+SYNC | [akinator-index-sync](references/akinator-index-sync.md), [akinator-router-sync](references/akinator-router-sync.md) |
| 12 | VERIFY | [akinator-gate-economy](references/akinator-gate-economy.md) |
| every | WIKI - document every prompt everywhere it lands | [akinator-wiki](references/akinator-wiki.md) |

Open when the work touches their domain: deciding or recommending
[akinator-decide](references/akinator-decide.md) · decision records
[akinator-adr](references/akinator-adr.md) · money
[akinator-business-map](references/akinator-business-map.md) · user-facing
behavior [akinator-product-map](references/akinator-product-map.md) · operations
[akinator-ops-map](references/akinator-ops-map.md) · no knowledge layer yet
[akinator-onboard](references/akinator-onboard.md) · layer audit
[akinator-coverage](references/akinator-coverage.md) · a box about to be ticked
[akinator-anti-gaming](references/akinator-anti-gaming.md) · anything heavy
[akinator-resource-guard](references/akinator-resource-guard.md).

## Standing rules

- Stations 6-11 happen in the **same batch** as the code. "I'll document in a
  follow-up" is a prohibited sentence.
- Declare the knowledge delta **by path** at PLAN time, or say
  `knowledge delta: none - <reason>`.
- Ask a lot: one grouped battery per prompt (up to 15, plus every wiki gap),
  ranked, each with a recommended default. Write every answer down at once.
- Honest gaps only: `_Unknown - ask the owner and record the answer._`, never
  an invented fact.
- Adopt the repository's conventions; one canonical home per fact.
- Never guess on money, permissions, deletion, security or public contracts.
- Never weaken a check to pass it. Never put knowledge checks in git hooks.
- Gate once, late and scoped. Report failures and evidence truthfully.
- A meaningful change records its provenance: before, change, now, why, who or
  which agent, intent, alternatives, verification, what would make it stale.

## Procedure

The complete pass, with every tool command, is in
[references/procedure.md](references/procedure.md). The outline:

1. **Establish the ground** - RESOLVE the layer and the ledger, adopt the
   conventions, ASK once in a group, AUDIT claim versus code, scope the pass.
2. **Plan** - batches on real seams, knowledge delta by path, every relevant
   review lens (business, CTO, product, ops, analyst, PM) at plan time.
3. **Build batch by batch** - implement, then DOCUMENT, SKILLIFY, RULE,
   CONTEXTIFY, MEMOIZE, the ledger (requirements and drift too), decisions,
   the wiki (`python <skill>/scripts/akinator_wiki.py index`, library pages with
   `python <skill>/scripts/extract_libraries.py --write`), INDEX+SYNC; librarian
   review on every batch.
4. **Prove it** - gate once, run every check the repository has plus
   `python <skill>/scripts/akinator_coverage.py . --strict`, anti-gaming on your
   own output, clean up, regenerate the brief.
5. **Loop until the Definition of Done is proven, then stop.**

Genuinely trivial work - a typo, a formatting-only change - is the one
exception: say so in one line, do it, record `knowledge delta: none, because ...`.

## Failure modes and pitfalls

- Ceremony on trivia - the fastest way to get the discipline abandoned.
- Ticking a phase with no artifact or observed exit code behind it.
- Skipping the librarian review on a "small" batch.
- Gate storms, and looping after the Definition of Done is proven.
- Quiet sampling in a pass that promised not to - say three of twenty.
- Running a tool by a path that exists only in Akinator's own repository.

## Definition of done

- [ ] The layer was read and cited; the repo's conventions were adopted.
- [ ] Every open question was asked, or the assumption is written down.
- [ ] Every batch declared its knowledge delta by path, and delivered it.
- [ ] Every artifact is true, reachable from an index, and in every router.
- [ ] Every new rule names a mechanism that exists and was run.
- [ ] The librarian review returned `CLEAR` on every batch.
- [ ] Gates ran once, scoped, with exit codes observed and reported.
- [ ] Anti-gaming was applied to this pass's own output.
- [ ] The machine was left as found; anything undone is named, with why.

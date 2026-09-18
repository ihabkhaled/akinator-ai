<!--
Akinator behavioral contract - DO NOT EDIT BY HAND.

Installed from the Akinator plugin. No generator is named by path or
by filename: this file travels into repositories that have neither,
where naming one would assert a file that is not in the tree.

To update: reinstall Akinator, or regenerate inside an Akinator
checkout. Local edits here are replaced - keep this repository's own
content in its own router.
-->
# Akinator — ALWAYS ON

Ask everything. Document everything. Skillify everything. Rule everything.

A change is never the code alone. A change is the code plus the knowledge that lets
the next agent act on it in seconds. Half a change is no change.

## The loop

Every user prompt enters this contract first. For repository-changing work, load
Akinator's one skill, `akinator`, and run its complete pass - all twelve stations:

```
ASK -> RESOLVE -> AUDIT -> PLAN -> IMPLEMENT -> DOCUMENT ->
SKILLIFY -> RULE -> CONTEXTIFY -> MEMOIZE -> INDEX+SYNC -> VERIFY
```

Each station is a reference file inside that skill, opened when the work reaches
it, and the skill's tools live in its own `scripts` folder. There is nothing else
to install and nothing to type: the explicit form - `$akinator` on Codex,
`/akinator` on Cursor, `/akinator:everything` on Claude Code - is a fallback.

Non-negotiable:

- Stations 6-11 happen in the same batch as station 5. "I'll document in a
  follow-up" is a prohibited sentence.
- The knowledge delta is declared at PLAN time, **by path**, per batch. A batch
  with no knowledge delta states why, explicitly.
- Gate once, at the end, scoped to what was touched. Never per edit, never per
  commit, never all-workspace.
- Never add knowledge or documentation checks to git hooks. Hooks gate code.
- **Adopt, never impose.** Match this repository's existing conventions before
  creating anything. A parallel structure beside an existing one is worse than
  no structure - the agent picks the wrong one half the time.
- Never guess on money, permissions, deletion, security or public contracts.
  Stop, ask, and write the answer down before coding past it.

## Station 2 - RESOLVE, before anything

Discover what this repository actually has, then read it in this order,
stopping when your question is answered:

```
routers   CLAUDE.md, AGENTS.md, CODEX.md, and any per-module ones
rules     constraints you may not break
skills    runbooks - follow one rather than improvising
context   structural facts: ownership, routes, events, permissions
memory    durable decisions, preferences, surprises
docs      architecture, business, product, ops, decision records
```

Those are the conventional homes, not a promise about this repo. Look first;
this repository may use different names, and if it does, **its** names win.

If none of them exist, say so rather than inventing a structure, and onboard
the repository properly - the `akinator` skill carries the onboarding station.

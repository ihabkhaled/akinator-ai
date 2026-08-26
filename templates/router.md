# Router templates

> Template file. It holds the thin skeletons for every AI entry-point file.
> Copy the relevant block to the repo root (or to a module directory) and delete
> the rest. Delete every angle-bracket placeholder.

**A router is an index, not a document.** It links to canonical content; it never
mirrors it. If you are writing paragraphs, the content belongs in `docs/` and the
router links to it. A 2,000-line router means content has migrated into the
index and has started to disagree with its source.

**All routers change together.** Whichever tool you are working in, every router
in the repo is updated in the same change - otherwise a different tool reads a
different truth. Where a difference is genuinely tool-specific, mark it with
`<!-- akinator:tool-specific -->` so the coverage check can tell it apart from
rot.

---

## Root router - CLAUDE.md

```markdown
# <Repo name>

<Two or three sentences: what this repo is and what it does.>

## Start here

- Rules (constraints you must not break): `rules/README.md`
- Skills (how to do things here): `skills/README.md`
- Context (structural facts): `context/README.md`
- Docs (architecture, business, product, ops): `docs/README.md`
- Memory (durable decisions and surprises): `memory/index.md`

## Before you change anything

- <The two or three constraints that must be seen before any work - linked, not
  reproduced.>
- <e.g. "Money and entitlement semantics: see `rules/03-money-semantics.md`">

## Running this repo

| Task | Command |
|---|---|
| Install | `<command>` |
| Run | `<command>` |
| Test | `<command>` |
| Typecheck | `<command>` |
| Lint | `<command>` |

Gate once, at the end, scoped to what you touched. Never per edit, never per
commit, never all-workspace.

## Modules

| Module | Router | What it owns |
|---|---|---|
| <name> | `<path>/CLAUDE.md` | <responsibility> |
```

---

## Root router - AGENTS.md (Codex, and the common fallback)

```markdown
# <Repo name>

<Same two or three sentences. The facts must match CLAUDE.md exactly.>

## Start here

- Rules: `rules/README.md`
- Skills: `skills/README.md`
- Context: `context/README.md`
- Docs: `docs/README.md`
- Memory: `memory/index.md`

## Before you change anything

- <the same constraints, linked>

## Running this repo

| Task | Command |
|---|---|
| Install | `<command>` |
| Test | `<command>` |

## Modules

| Module | Router | What it owns |
|---|---|---|
| <name> | `<path>/AGENTS.md` | <responsibility> |
```

---

## Root router - CODEX.md

```markdown
# <Repo name>

<Same facts.>

## Start here

<Same index links.>

<!-- akinator:tool-specific -->
## Codex specifics

- Skills are read from `.agents/skills/`.
- <Anything true only for Codex.>
```

---

## Module router - <module>/CLAUDE.md

```markdown
# <Module name>

<One or two sentences: what this module owns and what it does not.>

Up: `../CLAUDE.md`

## Local rules

- <constraints that apply only here, linked to `rules/`>

## Entry points

| Entry point | File |
|---|---|
| <name> | `<path>` |

## Tests

- Run: `<command>`
- Location: `<path>`

## Gotchas

- <the non-obvious thing that costs an hour if you do not know it>
```

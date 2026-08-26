# Filled router example

> Filled example of `templates/router.md`, written for the fictional Nimbus
> product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.
>
> This shows the root `CLAUDE.md` for Nimbus. Note what it does **not** contain:
> no architecture narrative, no rule text, no business rules. It is 60 lines and
> links to everything. `AGENTS.md` and `CODEX.md` carry the same facts with
> tool-specific sections marked.

---

```markdown
# Nimbus

Team workspace SaaS. Teams have members (seats) and a monthly export quota;
billing runs through a payment provider. Four services: `api`, `worker`,
`exports`, `postgres`.

## Start here

- Rules (constraints you must not break): `rules/README.md`
- Skills (how to do things here): `skills/README.md`
- Context (structural facts): `context/README.md`
- Docs (architecture, business, product, ops): `docs/README.md`
- Memory (durable decisions and surprises): `memory/index.md`

## Before you change anything

- **Money and entitlements:** quota is mutated only through `applyQuota` -
  `rules/07-quota-mutations.md`. Never write the quota columns directly.
- **Schema changes need a container rebuild, not a restart.** A restart silently
  serves the old shape - see the `nimbus-schema-change` skill.
- **Prices live outside this repo**, in the payment provider dashboard -
  `docs/business/quotas.md`.

## Running this repo

| Task | Command |
|---|---|
| Install | `npm ci` |
| Run | `docker compose up -d` |
| Test | `npm test -w <workspace>` |
| Typecheck | `npm run typecheck -w <workspace>` |
| Lint | `npm run lint -- --changed` |
| Migrate (local) | see the `nimbus-schema-change` skill |

Gate once, at the end, scoped to the workspaces you touched. Never per edit,
never per commit, never all-workspace.

## Modules

| Module | Router | What it owns |
|---|---|---|
| `services/api` | `services/api/CLAUDE.md` | HTTP surface, auth, permissions |
| `services/worker` | `services/worker/CLAUDE.md` | Background jobs, retries |
| `services/exports` | `services/exports/CLAUDE.md` | Export generation, retention |
| `packages/billing` | `packages/billing/CLAUDE.md` | Plans, quota, refunds |
```

---

## What makes this router correct

- **It is an index.** Every fact it states is one sentence plus a link. The rule
  text lives in `rules/`, the business rules in `docs/business/`, the procedure
  in a skill.
- **The "before you change anything" section is short.** Three items. A list of
  twenty is a list nobody reads, and the important one gets lost.
- **It names the gate discipline** so the operating rule is visible at the entry
  point rather than only inside a skill.
- **Module routers are linked**, and each of those links back up. The agent
  working in `services/exports` reads that router, not this one.

## What would make it wrong

- Pasting the text of `rules/07-quota-mutations.md` into it - two copies, one of
  which will be edited alone.
- Adding an architecture section - that is `docs/architecture.md`, and it will
  fork within a quarter.
- Updating it without updating `AGENTS.md` and `CODEX.md` in the same change -
  which is exactly the fork the coverage check's `router-sync` invariant catches.

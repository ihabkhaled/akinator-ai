# Business

What this answers: business rules, pricing, entitlements, impact analysis.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## What is the license and pricing model?

MIT (`LICENSE`; `README.md`, `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`
all name the MIT license). Free and open source: install is a one-line curl or
irm command with no account, no key and no paid tier stated anywhere in the
repository (`README.md`, "Install"). No revenue model, price point or paid tier
is stated in the repository.

_Unknown - ask the owner and record the answer._

## What is the value the business delivers, and to whom?

Per `docs/business-case.md` ("The problem", "The insight", "What it produces"):
Akinator removes the **re-derivation tax** - the hours or days a contributor,
or an AI agent with a fresh context window, spends rediscovering context that
already existed once. On an AI-heavy team that tax is paid per session, so the
cost compounds with every prompt. Akinator turns a prompt-based habit ("please
document this") - which decays within one session, gets compacted away or
deprioritized - into a **plugin behavior**: loaded at session start, reinforced
by triggers on every codebase touch, blocked by a review lens when skipped,
verified by a CI check, portable across every repository a team owns.

Value by persona (`docs/business-case.md`, "What it produces" table): business
owner (why the product exists, what must never break), CEO (strategy,
priorities), CTO (architecture and rejected alternatives, the debt ledger),
product owner (feature intent, acceptance criteria), business analyst (pricing
and entitlement numbers in business language), decision maker (recorded
decision criteria an agent can act on), operations (restart-vs-rebuild
runbooks), project manager (scope, batches, done vs. claimed done).

The quantified claim (`docs/business-case.md`, "The value, quantified"): "The
second repository Akinator onboards should cost roughly a tenth of the first" -
the first onboarding pays for the mapping, extractors, rules and runbooks; the
second reuses them.

AI cost reduction specifically comes from two mechanisms this project commits
to: a **capped context brief** (`.ai/BRIEF.md`, built by
`skills/everything/scripts/build_brief.py`, kept under a byte budget so every
session pays a fixed, small cost to load it) and **generated facts** (library
and stack pages regenerated from the manifest rather than re-derived by an
agent reading source on every session) - both load-bearing to the value claim
but neither one has a measured dollar or token figure recorded in the
repository.

_Unknown - ask the owner and record the answer._

## Which business rules must never break?

This project's own constraints, each enforced by a named rule under `rules/`
(`rules/README.md`), not by convention:

| Rule | What it never allows |
|---|---|
| `rules/01-knowledge-delta-per-batch.md` | A batch closing without declaring, by path, the docs/skills/rules/context/memory it will produce |
| `rules/05-no-git-hook-complication.md` | Knowledge checks added to git hooks - hooks gate code and stay fast |
| `rules/06-gate-once-scoped-at-the-end.md` | Gating per edit or per commit instead of once, scoped, at the end of a batch |
| `rules/07-codex-pack-is-generated.md` | Hand-editing the Codex pack or a router instead of its generator |
| `rules/09-routers-are-rendered-from-one-contract.md` | A router edited directly instead of through `context/router-contract.md` |
| `rules/10-ledger-records-are-redacted-before-write.md` | A ledger record written with unredacted secrets or personal data |
| `rules/11-invariants-ship-with-a-mutation-test.md` | An invariant landing with no test proving it actually fires |
| `rules/12-artifacts-that-travel-name-nothing-local.md` | An artifact shipped to a target repo naming a path that exists only in this checkout |

Enforcement mechanism per `docs/business-case.md` ("What would make this
fail"): fake compliance (vacuous docs, ticked checklists, rules with no
enforcement) is treated as worse than absence because it is trusted, and is
countered by `skills/everything/references/akinator-anti-gaming.md` and by the
coverage checker verifying rather than accepting claims.

## Business rule owners

Each rule above is owned by this repository's own maintainers (there is no
per-rule owner field in `rules/README.md` or the rule files themselves).

_Unknown - ask the owner and record the answer._

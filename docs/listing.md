# Directory listing copy

The submission text for the plugin directory. Kept here so the listing and the
repository cannot drift, and so a change to one is a change to both.

## Plugin name

```
akinator
```

Display name: **Akinator**

Not a brand we do not own. It is a common noun (a coined agent-noun from "to
ask"), used here for its literal meaning - the plugin's whole behavior is asking
everything and recording every answer. No affiliation with any similarly named
game or company is claimed or implied.

## Plugin description

```
Ask everything. Document everything. Skillify everything. Rule everything.

Akinator makes it structurally impossible to change code without growing the
knowledge around it. Every codebase touch runs a twelve-station loop, and the
knowledge delta - which docs, skills, rules, context maps and memory entries a
batch will produce - is declared by path at plan time, before any code exists.
That turns skipped documentation from an absence nobody notices into a visible
edit to the plan.

Code outlives its context. On an AI-heavy team that costs you per session: an
agent with a fresh context window is a new hire every morning, and it infers
confidently from the code - recovering what the system does while losing what it
should do.

What you get:

- 21 skills covering the whole loop - intake questions, claim-vs-code audit,
  batch planning, documentation routing, skill and rule creation, context
  extractors, memory, ADRs, index and router sync. Plus business, product and
  operational mapping, so pricing rules, feature intent and restart-vs-rebuild
  procedures live in the repo instead of in someone's head.
- 7 boardroom review agents with real vetoes - business owner, CTO, product
  owner, ops, analyst, PM, and a librarian that blocks any batch whose knowledge
  delta is missing.
- One command, /akinator, that runs everything.
- A coverage checker with eleven mechanically verifiable invariants: unreachable
  artifacts, dead links, rules naming enforcement that does not exist, router
  forks, stale generated files, docs describing paths that are not there.
- Gate economy - build the whole batch, gate once at the end, scoped to what you
  touched. Never per edit, never per commit.
- Adopt, never impose - it detects your repo's existing conventions and extends
  them rather than creating a competing structure beside them.
- Ships for Claude Code and Codex from one source, so the two cannot diverge.

Knowledge enforcement never touches your git hooks. Hooks gate code and stay
fast.
```

## Example use cases

```
1. The everything pass, before something expensive

   /akinator

   You inherited a service that takes payments, the person who wrote it left in
   March, and you ship a pricing change on Friday. You do not know what is
   documented, what is true, or what will bite.

   With no arguments, /akinator runs the complete pass:

   - Reads whatever knowledge layer exists and cites it, so you can see what it
     actually relied on rather than what it inferred.
   - Audits claim against code. Marks what is done, what is partial, and what is
     present-but-not-wired - code that exists, is tested in isolation, and that
     nothing live ever calls. Every plan built on that code was wrong.
   - Plans the fix in batches, each declaring by path the docs, rules, context
     maps and memory entries it will produce.
   - Runs the boardroom: the business owner vetoes an entitlement change with no
     business doc, the CTO vetoes an undocumented architectural decision, ops
     vetoes a migration with no runbook, the PM rejects any "done" without a
     live call path behind it.
   - Closes the batches, and the librarian blocks each one until its knowledge
     delta is delivered, routed, reachable and true.
   - Gates once at the end, scoped. Runs every check. Turns anti-gaming on its
     own output - every doc must survive deleting the sentences you could have
     derived from the code.
   - Loops the unmet lines back in. When the Definition of Done is proven with
     evidence, it stops.

   What you get is not a report. It is a repository where the pricing change is
   safe to make, and a written list of what is still unknown and who has to
   decide it.

   Also use it before a handover or a release, after a long session where you
   cannot account for what got skipped, and on any change touching money,
   permissions, deletion or a public contract.

2. Onboard a repository nobody can navigate

   /akinator onboard

   Detects what you already have - routers, rules, docs, conventions - maps onto
   them instead of replacing them, ranks every gap by severity, and closes them
   in batches. Finishes with a newcomer test: a fresh agent, given only the
   knowledge layer, must answer where to go, what to do, what not to break and
   what to run, for your five most common change types.

3. Ship a feature whose reasoning survives it

   /akinator add per-team rate limiting to the export endpoint

   The code, plus the product doc recording why 100/hour and what happens at the
   boundary, plus an ADR for the algorithm chosen over its alternatives, plus the
   ops note if it changes how the service is deployed - all in the same batch,
   all indexed, all reflected in every AI entry-point file.

4. Stop an agent guessing on money

   /akinator implement refunds

   Refunds force a question your docs do not answer: what happens to quota the
   customer already used? Akinator stops, asks it in business terms, and files
   the answer as business documentation before writing the code that depends on
   it. Money, permissions, deletion and public contracts are where guessing is
   prohibited.

5. Find out whether your documentation is actually true

   /akinator audit

   Ranked findings: docs describing a service you deleted six months ago, rules
   citing a test that no longer exists, twelve runbooks nothing links to, and a
   CLAUDE.md that says something your AGENTS.md does not - so your Codex users
   have been reading a different truth.

6. Capture the procedure that cost you three hours

   Someone works out that a schema change needs the container dropped and
   rebuilt, not restarted, because the old image serves the old schema and the
   failure looks like a bad migration. Akinator turns that into a runbook with
   exact commands, what is parallel-safe, and the point of no return - and a
   skill so it fires the next time anyone touches a migration.

7. Make a large refactor cheap to verify

   /akinator rename the Item model to Record across the codebase

   Batched on real seams, no gate storms, one scoped verification run at the end,
   docs updated in the same batch - because a rename is a documentation event -
   and the machine left as it was found.
```

## Category

`Productivity`

## Tags

```
documentation, knowledge-management, context-engineering, onboarding,
business-logic, runbooks, adr, institutional-memory, ai-agents, coding-agents,
gate-economy, router-sync
```

## Review when

- The skill count, command surface or invariant count changes.
- Last verified: 2026-08-26, against plugin version 1.0.2.

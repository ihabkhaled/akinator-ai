# Akinator

<p align="center"><img src="assets/akinator-logo.png" width="160" alt="Akinator logo"></p>

**One command. Always on. A living wiki for your codebase.**

Akinator is a knowledge operating system for AI coding. It makes Claude Code,
Codex and Cursor resolve the repository's intent before changing it, then grow
the repository's durable knowledge in the same change as the code.

> Code says **how**. Akinator preserves **what, why, who, when, before, now,
> next, constraints, decisions and consequences**.

## How it works

You normally do **not** call Akinator. Install it, then prompt your coding agent
normally:

```
add rate limiting to exports
fix the failed payment retry
why is this service using Redis?
refactor the authentication flow
```

Akinator is the standing contract. For repository-changing work it runs the full
loop automatically.

There is exactly **one explicit command**:

```
/akinator:everything [what you want done]
```

No onboard/audit/status/sync/question/decide commands. No command tree. Internal
skills are implementation details used by the one orchestrator.

## Install from GitHub

Until marketplace distribution is available, install directly from the GitHub
repository.

### Claude Code

```bash
git clone https://github.com/ihabkhaled/akinator-ai.git
cd akinator-ai
claude --plugin-dir .
```

For development, keep the checkout and start Claude with `--plugin-dir`. The
plugin's `SessionStart` hook injects the always-on contract before the first
prompt. The only explicit command is `/akinator:everything`.

If you use a Claude plugin marketplace that accepts Git repositories, add this
repository as the marketplace source and install Akinator from it.

### Codex

```bash
git clone https://github.com/ihabkhaled/akinator-ai.git
cd akinator-ai
sh scripts/install-codex.sh --user
# or install into one repository
sh scripts/install-codex.sh --repo /path/to/your/repo
```

Windows:

```powershell
git clone https://github.com/ihabkhaled/akinator-ai.git
cd akinator-ai
.\scripts\install-codex.ps1 -Scope Repo -Repo C:\src\your-project
```

Codex does not expose Claude's SessionStart hook surface. Akinator therefore
installs an always-on `AGENTS.md` contract plus the generated master skill.
Normal prompts are routed through that contract; `$akinator-everything` remains
an explicit fallback, not another Akinator command.

### Cursor

```bash
git clone https://github.com/ihabkhaled/akinator-ai.git
cp akinator-ai/.cursor/rules/akinator.mdc /path/to/your/repo/.cursor/rules/akinator.mdc
```

The Cursor rule is `alwaysApply: true`, so normal prompts receive the same
Akinator contract. You do not need a slash command.

## The living wiki

Akinator treats the repository as a product wiki above the code, not as code plus
random notes. It resolves and maintains the homes that apply to the project:

| Knowledge | Answers |
|---|---|
| Product | What should exist? For whom? What are the journeys, stories, acceptance criteria and edge cases? |
| Business | Why does it exist? What are the rules, money semantics, entitlements, quotas and invariants? |
| Architecture | How is it shaped? Why these boundaries, dependencies, data flows and trade-offs? |
| Change history | What was true before, what changed, what is true now, why, when, who/agent when known, and what is affected? |
| Decisions | What options existed, what was chosen, why, consequences and revisit conditions? |
| Context maps | Where do components, routes, events, permissions, owners and integrations live? |
| Operations | How is it deployed, migrated, recovered, rolled back and diagnosed? |
| Rules | What must never be broken, and what mechanism enforces it? |
| Skills | What repeatable procedure should never be re-derived? |
| Failures & lessons | What failed, root cause, fix, recurrence risk and prevention? |
| Memory | What durable fact, preference, surprise or decision must survive sessions? |
| Future intent | What is planned, why, dependencies, assumptions and what would invalidate it? |
| Provenance | Where did a fact come from, when was it verified, and what would make it stale? |

Akinator **adopts the repository's existing conventions**. It does not create a
parallel wiki if the project already has one.

### Mandatory change record

Every meaningful behavioral, business, product, architecture, data, API,
security or operational change records:

```
When
Actor / agent (when knowable)
Request / source
Affected code and components
Before
Change
Now
Why
Business intent
Product intent
Technical reasoning
Alternatives / trade-offs
Compatibility / migration / rollback
Rules created or changed
Skills created or changed
Failures / lessons
ADRs / docs / context / memory affected
Verification evidence
Future implications / follow-ups
Stale when
```

Mechanical-only changes may record `knowledge delta: none — <reason>`. Akinator
must not manufacture documentation merely to satisfy itself.

## The automatic loop

```
ASK → RESOLVE → AUDIT → PLAN → IMPLEMENT → DOCUMENT → SKILLIFY → RULE
    → CONTEXTIFY → MEMOIZE → INDEX+SYNC → VERIFY
```

For every meaningful repository change:

1. Resolve existing rules, skills, context, memory, docs and history.
2. Understand intent and surface unknowns instead of inventing business facts.
3. Audit code versus claimed behavior.
4. Plan code **and knowledge delta together**.
5. Implement.
6. Write the durable change record and update the wiki.
7. Turn repeatable procedures into Skills.
8. Record failures; convert reusable recurrence-prevention constraints into enforced Rules.
9. Update architecture/context/memory/ADRs/product/business/ops where affected.
10. Index everything and keep every AI router aligned.
11. Verify code and knowledge once, scoped to what changed.
12. Stop only when the Definition of Done is supported by evidence.

## What "everything" means

`/akinator:everything` and the automatic repository-change path use the same
master orchestrator. "Everything" means every station is evaluated, every
applicable knowledge lens is loaded, and every applicable check is completed.
It does **not** mean writing irrelevant files or inventing facts.

The one-command surface is intentionally separate from the internal skill
library. Skills such as documentation, ADR, business mapping and rule forging
remain composable internals; users do not need to learn or call them.

## Knowledge laws

- **Code + knowledge is the change.**
- **One canonical home per fact.** Link instead of copying.
- **Current truth and historical truth are different.** Preserve both.
- **Future intent is labeled future, never presented as implemented.**
- **Every important doc says what would make it stale.**
- **Every failure is recorded; reusable prevention becomes an enforced rule.**
- **Any procedure likely to happen twice becomes a skill.**
- **No guessing on money, permissions, deletion, security or public contracts.**
- **No documentation follow-up.** Knowledge ships in the same batch.
- **No knowledge checks in git hooks.** Enforcement belongs in session behavior,
  tests and CI.
- **Gate once, late and scoped.**
- **Evidence beats claims.**

## Repository development

```bash
python -m pytest tests/ -q
python scripts/akinator_coverage.py . --strict
python scripts/akinator_ledger.py verify
python scripts/akinator_rules.py conflicts
python scripts/build_codex_pack.py --check
python scripts/render_routers.py --check
python scripts/build_brief.py --check
```

Canonical Claude skills live in `skills/`. The Codex pack in
`.agents/skills/` is generated from them. AI routers are generated from
`context/router-contract.md`; do not hand-edit generated routers.

## Documentation

- [Architecture](docs/architecture.md)
- [Business case](docs/business-case.md)
- [Compatibility](docs/compatibility.md)
- [Skills](docs/skills.md)
- [Agents](docs/agents.md)
- [ADRs](docs/adr/README.md)
- [Rules](rules/README.md)
- [Context](context/README.md)
- [Memory](memory/index.md)
- [Ledger](docs/ledger.md)
- [Templates](templates/README.md)
- [Living wiki contract](docs/living-wiki.md)

## License

MIT — see [LICENSE](LICENSE).

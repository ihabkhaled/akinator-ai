# Akinator

<p align="center"><img src="assets/akinator-logo.png" width="160" alt="Akinator logo"></p>

**One skill. One command. Always on. Your repo becomes its own wiki.**

Akinator makes Claude Code, Codex and Cursor read a repository's intent before
changing it, and grow its knowledge in the same change as the code: product,
business, requirements, drift, architecture, libraries, decisions, history,
rules, skills, memory. Code says **how**. Akinator keeps **what, why, who, when,
before, now, next**.

## Install - 30 seconds

macOS / Linux (Claude Code, Codex and Cursor, whichever are installed):

```bash
curl -fsSL https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.sh | sh
```

Windows (PowerShell 5.1+):

```powershell
irm https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.ps1 | iex
```

Restart your agent. That's it - there is nothing to call. Prompt normally:

```
add rate limiting to exports
fix the failed payment retry
why is this service using Redis?
```

| Platform | Explicit form (rarely needed) | Always-on via |
|---|---|---|
| Claude Code | `/akinator:everything` | SessionStart hook |
| Codex | `$akinator` | marked block in `AGENTS.md` |
| Cursor | `/akinator` | always-applied rule |

**Update:** re-run the same line. **Uninstall:** add `--uninstall`
(`-Uninstall` on Windows); a repo is restored byte for byte.

**Options:** `--claude` `--codex` `--cursor` pick platforms, `--repo PATH`
installs into one repository instead of your profile, `--ref REF` pins a
version. PowerShell: `-Claude` `-Codex` `-Cursor` `-Repo` `-Ref` `-Uninstall`.

<details>
<summary>Other ways to install</summary>

**Read first, then run**

```bash
curl -fsSLO https://raw.githubusercontent.com/ihabkhaled/akinator-ai/main/install.sh
sh install.sh
```

**Claude Code plugin commands**

```bash
claude plugin marketplace add https://github.com/ihabkhaled/akinator-ai.git
claude plugin install akinator@akinator
```

Use the https URL; the `owner/repo` shorthand clones over SSH. Update with
`claude plugin marketplace update akinator && claude plugin update akinator@akinator`.
In the VS Code extension: type `/plugins`, open **Marketplaces**, add the URL
above, install Akinator.

**Try it for one session, no install**

```bash
claude --plugin-url https://github.com/ihabkhaled/akinator-ai/archive/refs/heads/main.zip
```

**Codex plugin route** (from Codex docs and source, not run here; no always-on
block, no IDE extension support - prefer the installer):

```bash
codex plugin marketplace add ihabkhaled/akinator-ai
codex plugin add akinator@akinator
```

**Cursor:** use the installer; Cursor plugins need their own marketplace
manifest, which Akinator does not ship.

**What lands where**

| Platform | User scope | `--repo` scope |
|---|---|---|
| Claude Code | plugin `akinator@akinator` | same plugin, project scope |
| Codex + Cursor skill | `~/.agents/skills/akinator` | `<repo>/.agents/skills/akinator` |
| Codex always-on | block in `~/.codex/AGENTS.md` | block in `<repo>/AGENTS.md` |
| Cursor always-on | `~/.cursor/rules/akinator.mdc` | `<repo>/.cursor/rules/akinator.mdc` |

The installer only touches files carrying the Akinator banner, keeps your line
endings, and warns if an `AGENTS.override.md` would shadow the Codex block.

</details>

## What it does on every prompt

```
ASK → RESOLVE → AUDIT → PLAN → IMPLEMENT → DOCUMENT → SKILLIFY → RULE
    → CONTEXTIFY → MEMOIZE → INDEX+SYNC → VERIFY
```

- **Asks first.** Up to 15 grouped questions, each with a recommended default.
- **Decides or recommends.** Reversible choices are decided and recorded. Money,
  permissions, deletion, security and public contracts go to you as 2-4 costed
  options with one recommendation.
- **Documents everything it touches**, in the same batch: the wiki
  ([`docs/wiki/index.md`](docs/wiki/index.md), 25 categories), README, every
  agent router, rules, memory, context, the ledger.
- **Traces every changed path** to a change record (rule 14).
- **Keeps secrets out** - names and locations are documented, values never
  (rule 15).
- **Turns repetition into skills and rules** after asking you.
- **Never invents facts.** Unknowns are the line
  `_Unknown - ask the owner and record the answer._`, which becomes a question.

It adopts the conventions your repository already has; it never builds a
parallel wiki.

## Cheap and fast

Read the pack, not the tree. No daemon, no network, no index service:

```bash
python skills/everything/scripts/akinator_context.py pack --for "add refunds"   # ranked reading list, token budget 3000
python skills/everything/scripts/akinator_trace.py check                         # every changed path accounted for
python skills/everything/scripts/akinator_sensitive.py scan                      # leaked secrets, fingerprint only
python skills/everything/scripts/akinator_wiki.py interview                      # open gaps as grouped questions
python skills/everything/scripts/akinator_distil.py repeats                      # skill, rule, or neither?
```

All tools: [docs/skills.md](docs/skills.md). Why this design:
[ADR 0010](docs/adr/0010-every-prompt-documented-living-wiki.md),
[ADR 0011](docs/adr/0011-cheap-deterministic-tools-over-prose-or-indexing.md).

## Laws

- Code + knowledge is the change. Knowledge ships in the same batch.
- One canonical home per fact; link, don't copy.
- Current truth and history are different; keep both.
- Future intent is labelled future.
- Never guess on money, permissions, deletion, security or public contracts.
- No knowledge checks in git hooks - enforcement is session behavior, tests and CI.
- Gate once, late, scoped. Evidence beats claims.

## Develop this repo

```bash
python -m pytest tests/ -q
python skills/everything/scripts/akinator_coverage.py . --strict
```

The canonical skill is `skills/everything/`. `.agents/`, every router and the
generated wiki pages are generated; regenerate, never hand-edit (commands in
[CLAUDE.md](CLAUDE.md)).

## Docs

[Architecture](docs/architecture.md) · [Compatibility](docs/compatibility.md) ·
[Skills and tools](docs/skills.md) · [Agents](docs/agents.md) ·
[ADRs](docs/adr/README.md) · [Rules](rules/README.md) ·
[Context](context/README.md) · [Memory](memory/index.md) ·
[Ledger](docs/ledger.md) · [Templates](templates/README.md) ·
[Business case](docs/business-case.md) · [Living wiki contract](docs/living-wiki.md) ·
[Wiki home](docs/wiki/index.md)

## License

MIT - see [LICENSE](LICENSE).

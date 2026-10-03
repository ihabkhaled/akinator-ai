# Tools and commands

<!-- akinator:generated:begin -->
<!-- Facts extracted from the tree. This block is rewritten on every run;
     write outside it. -->
### Commands

| Command | What | Where defined |
|---|---|---|
| `python .agents/skills/akinator/scripts/akinator_context.py` | The cheapest way to gain context - a ranked reading list under a token budget. | `.agents/skills/akinator/scripts/akinator_context.py` |
| `python .agents/skills/akinator/scripts/akinator_coverage.py` | Akinator coverage checker - the mechanically verifiable knowledge invariants. | `.agents/skills/akinator/scripts/akinator_coverage.py` |
| `python .agents/skills/akinator/scripts/akinator_distil.py` | Distil - turn what recurs into a rule proposal. | `.agents/skills/akinator/scripts/akinator_distil.py` |
| `python .agents/skills/akinator/scripts/akinator_ledger.py` | The Akinator ledger - what happened, so the next session does not rediscover it. | `.agents/skills/akinator/scripts/akinator_ledger.py` |
| `python .agents/skills/akinator/scripts/akinator_rules.py` | Harden - rule evolution and conflict detection. | `.agents/skills/akinator/scripts/akinator_rules.py` |
| `python .agents/skills/akinator/scripts/akinator_scope.py` | Scope a pass to what actually changed, and budget the questions. | `.agents/skills/akinator/scripts/akinator_scope.py` |
| `python .agents/skills/akinator/scripts/akinator_sensitive.py` | Sensitive data: know what must not be exposed, document it, never leak it. | `.agents/skills/akinator/scripts/akinator_sensitive.py` |
| `python .agents/skills/akinator/scripts/akinator_trace.py` | Every changed path is traced - no change lands without its knowledge. | `.agents/skills/akinator/scripts/akinator_trace.py` |
| `python .agents/skills/akinator/scripts/akinator_version.py` | Version discipline: every shipped change bumps the version, everywhere at once. | `.agents/skills/akinator/scripts/akinator_version.py` |
| `python .agents/skills/akinator/scripts/akinator_wiki.py` | The living wiki - the repository as its own Confluence. | `.agents/skills/akinator/scripts/akinator_wiki.py` |
| `python .agents/skills/akinator/scripts/build_brief.py` | Compose the context brief - what a new session actually reads. | `.agents/skills/akinator/scripts/build_brief.py` |
| `python .agents/skills/akinator/scripts/extract_history.py` | Generate the history wiki page from the records the repository already keeps. | `.agents/skills/akinator/scripts/extract_history.py` |
| `python .agents/skills/akinator/scripts/extract_libraries.py` | Generate the library wiki - one page per declared dependency. | `.agents/skills/akinator/scripts/extract_libraries.py` |
| `python .agents/skills/akinator/scripts/extract_operations.py` | Generate the operations wiki - the runnable surface of a repository. | `.agents/skills/akinator/scripts/extract_operations.py` |
| `python .agents/skills/akinator/scripts/extract_platform.py` | Generate the platform wiki pages from what the tree actually contains. | `.agents/skills/akinator/scripts/extract_platform.py` |
| `python .agents/skills/akinator/scripts/extract_stack.py` | Generate the stack map - dependencies and modules, extracted from the tree. | `.agents/skills/akinator/scripts/extract_stack.py` |
| `CI job verify` | - | `.github/workflows/ci.yml` |
| `python scripts/build_codex_pack.py` | Generate the portable pack - Akinator's one skill, for Codex and Cursor. | `scripts/build_codex_pack.py` |
| `python scripts/extract_components.py` | Generate `context/components.md` from the tree. | `scripts/extract_components.py` |
| `python scripts/render_routers.py` | Render every AI entry-point file from one canonical contract. | `scripts/render_routers.py` |
| `python scripts/run_evals.py` | Run Akinator's behavioral evals against the fixture repositories. | `scripts/run_evals.py` |
| `python skills/everything/scripts/akinator_context.py` | The cheapest way to gain context - a ranked reading list under a token budget. | `skills/everything/scripts/akinator_context.py` |
| `python skills/everything/scripts/akinator_coverage.py` | Akinator coverage checker - the mechanically verifiable knowledge invariants. | `skills/everything/scripts/akinator_coverage.py` |
| `python skills/everything/scripts/akinator_distil.py` | Distil - turn what recurs into a rule proposal. | `skills/everything/scripts/akinator_distil.py` |
| `python skills/everything/scripts/akinator_ledger.py` | The Akinator ledger - what happened, so the next session does not rediscover it. | `skills/everything/scripts/akinator_ledger.py` |
| `python skills/everything/scripts/akinator_rules.py` | Harden - rule evolution and conflict detection. | `skills/everything/scripts/akinator_rules.py` |
| `python skills/everything/scripts/akinator_scope.py` | Scope a pass to what actually changed, and budget the questions. | `skills/everything/scripts/akinator_scope.py` |
| `python skills/everything/scripts/akinator_sensitive.py` | Sensitive data: know what must not be exposed, document it, never leak it. | `skills/everything/scripts/akinator_sensitive.py` |
| `python skills/everything/scripts/akinator_trace.py` | Every changed path is traced - no change lands without its knowledge. | `skills/everything/scripts/akinator_trace.py` |
| `python skills/everything/scripts/akinator_version.py` | Version discipline: every shipped change bumps the version, everywhere at once. | `skills/everything/scripts/akinator_version.py` |
| `python skills/everything/scripts/akinator_wiki.py` | The living wiki - the repository as its own Confluence. | `skills/everything/scripts/akinator_wiki.py` |
| `python skills/everything/scripts/build_brief.py` | Compose the context brief - what a new session actually reads. | `skills/everything/scripts/build_brief.py` |
| `python skills/everything/scripts/extract_history.py` | Generate the history wiki page from the records the repository already keeps. | `skills/everything/scripts/extract_history.py` |
| `python skills/everything/scripts/extract_libraries.py` | Generate the library wiki - one page per declared dependency. | `skills/everything/scripts/extract_libraries.py` |
| `python skills/everything/scripts/extract_operations.py` | Generate the operations wiki - the runnable surface of a repository. | `skills/everything/scripts/extract_operations.py` |
| `python skills/everything/scripts/extract_platform.py` | Generate the platform wiki pages from what the tree actually contains. | `skills/everything/scripts/extract_platform.py` |
| `python skills/everything/scripts/extract_stack.py` | Generate the stack map - dependencies and modules, extracted from the tree. | `skills/everything/scripts/extract_stack.py` |

### Required CLI tools

| Tool | Implied by |
|---|---|
| `gh` | `.github` |
| `git` | `.git`, `.github/workflows/ci.yml` |
| `python` | `.agents/skills/akinator/scripts/akinator_context.py`, `.agents/skills/akinator/scripts/akinator_coverage.py`, `.agents/skills/akinator/scripts/akinator_distil.py` +34 more |

Regenerate with: `python <skill>/scripts/extract_operations.py --write`
<!-- akinator:generated:end -->

## Notes on tools and commands

_Unknown - ask the owner and record the answer._

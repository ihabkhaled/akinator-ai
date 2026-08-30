# Memory

Durable facts, decisions, surprises and dead ends from building and maintaining
Akinator. One fact per file, each with its why, an absolute date and its
reversal conditions. See `skills/akinator-memoize/SKILL.md`.

Memory is not a scratchpad. Session state does not go here; only things a future
agent would otherwise rediscover.

| Date | Entry | Type |
|---|---|---|
| 2026-08-26 | [Verify platform contracts against installed plugins, not documentation](2026-08-26-verify-contracts-from-installed-plugins.md) | surprise |
| 2026-08-26 | [The Windows `python3` alias resolves on PATH and then fails](2026-08-26-windows-python3-alias-stub.md) | constraint |
| 2026-08-26 | [Owner wants exactly one command, not a command per mode](2026-08-26-single-command-preference.md) | preference |
| 2026-08-26 | [Illustrative paths in docs must live inside code fences](2026-08-26-fenced-examples-avoid-false-findings.md) | decision |
| 2026-08-26 | [Codex requires interface assets, and rejects loose files under `skills/`](2026-08-26-codex-plugin-validation-surprises.md) | surprise |
| 2026-08-26 | [A checker fails silently in both directions, and the false negative is the dangerous one](2026-08-26-checkers-fail-silently-in-both-directions.md) | surprise |
| 2026-08-26 | [When correcting a fact, the index that states it is the easiest file to miss](2026-08-26-fix-the-index-not-only-its-pointers.md) | surprise |
| 2026-08-30 | [A claim is only true relative to a tree, and every test checked the same tree](2026-08-30-a-claim-is-only-true-relative-to-a-tree.md) | surprise |
| 2026-08-30 | [A backslash written through a shell heredoc reaches the file as something else](2026-08-30-backslashes-do-not-survive-a-heredoc.md) | constraint |
| 2026-08-30 | [A test that reads git history can pass locally and fail only in CI](2026-08-30-ci-checkouts-are-shallow-by-default.md) | surprise |

## Pruning

Pruning happens at station 10, not as a separate cleanup that never gets
scheduled. On each visit, check neighboring entries: reversal condition met,
contradicted by the tree, superseded by a rule or ADR, or duplicated.

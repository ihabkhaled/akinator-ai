# ADR 0011 - Cheap deterministic tools, with an enforced trace and guard

- **Status:** accepted
- **Date:** 2026-10-03
- **Deciders:** Ihab Khaled (owner)
- **Builds on:** ADR 0003 (enforcement outside git hooks), ADR 0009 (one skill,
  one command), ADR 0010 (the living wiki).

## Context

The owner asked that the AI know everything, gain context extremely fast and
cheap, take decisions and responsibility, be secure, and cover what company
teams do - still one skill and one command, on Claude Code, Codex and Cursor.
Three things were missing: a cheap way to load the right context, proof that
every change leaves its knowledge behind, and a way to know and protect
sensitive data.

## Options

### Option A - rely on prose discipline

- **Cost:** nothing to build, and nothing to audit: a skipped trace or a leaked
  secret is invisible until someone reads the diff.
- **Why it lost:** it is what 2.0 already did, and the owner's ask is a
  guarantee, not advice.

### Option B - heavy indexing: embeddings, a daemon, a vector store

- **Cost:** a runtime dependency, a process to keep alive, a model to call, an
  index to rebuild, and behavior that differs per platform.
- **Why it lost:** it breaks "no new surface", fails offline and on Codex and
  Cursor, and spends tokens and money to save tokens.

### Option C - cheap deterministic tools plus enforced trace and guard (chosen)

- **What it is:** pure-Python tools on the standard library, no subprocess in
  the context path, no network. `akinator_context.py` ranks a reading list by
  keyword, path and owner over knowledge directories only, within a token
  budget, from an incremental cache. `akinator_trace.py` fails a diff with an
  unaccounted path (rule 14). `akinator_sensitive.py` keeps a register of names
  and locations and scans tracked files for leaked secrets (rule 15). Both run
  in CI, never in a git hook.
- **Cost:** keyword-only ranking can miss a relevant page and surface a weak
  one; the detectors are heuristic, with false positives and false negatives;
  25 wiki categories is a lot of surface.

## Decision

Option C. The same tools run on every platform: Claude Code, Codex (the
explicit `SKILL.md` stays under 8,000 bytes, so detail lives in references) and
Cursor (`.agents/skills`). No new skill, no command file.

## Consequences

**Good.** A session reads a bounded pack, not the tree. A change without its
record and a leaked secret fail CI. An answered gap becomes a recorded
decision. Repetition is offered to the owner as a skill or a rule.

**Bad.** Heuristics need an allow list (`.ai/config.json`) and attention to
false positives. Ranking is only as good as the headings and words in the docs.
The cache is one more local artifact, though it ignores itself.

**Bad.** The trace proves accounting, not truth: a record can name a path and
say nothing useful. Coverage and review still judge the prose.

## Revisit when

- Keyword ranking measurably misses needed pages on real repositories - then
  consider an optional offline similarity step, still without a daemon.
- Scan false positives push owners to allow-list broadly.
- A platform lets a skill carry per-tool permissions or a cheaper check point
  than CI.

## Related

- Tools: `skills/everything/scripts/akinator_context.py`,
  `skills/everything/scripts/akinator_trace.py`,
  `skills/everything/scripts/akinator_sensitive.py`
- Rules: `rules/14-every-changed-path-is-traced.md`,
  `rules/15-sensitive-data-is-known-and-never-exposed.md`
- Docs: `docs/changes/2026-10-03-trace-fast-context-sensitive.md`,
  `docs/skills.md`

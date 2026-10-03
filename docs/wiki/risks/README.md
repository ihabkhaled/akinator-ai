# Risks

What this answers: open risks, owner, mitigation.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Which risks are open, who owns each, and what is the mitigation?

Owner of every risk below: Ihab Khaled (maintainer). Mitigations are what
exists in the tree today; a risk with no mitigation says so.

| Risk | Effect | Mitigation | Residual |
|---|---|---|---|
| Heuristic detectors give false positives or false negatives (secret `scan`, the platform and operations extractors) | A real leak is missed, or CI fails on a harmless line | `akinator:allow-secret` on the line and `sensitive.allow` in `.ai/config.json`; findings print a fingerprint so they are recognisable; `tests/test_sensitive.py` | A new secret format passes unseen |
| Keyword-only ranking in `akinator_context.py pack` | A needed page is omitted or a weak one is ranked high | whatever the budget leaves out is listed, never silently cut; the owner can pass `--paths` | A task phrased in words the docs never use |
| 25-category wiki volume | Many pages, many gap markers, owner fatigue | generated facts cannot rot; `interview` caps and groups questions with defaults; ADR 0010 and 0011 name the revisit conditions | Pages can look unfinished until answered |
| The trace proves accounting, not truth | A record can name a path and say nothing | `akinator_coverage.py --strict`, the librarian lens | prose quality is still judged by a person |
| Platform contracts move (Claude Code, Codex, Cursor) | The always-on route or the skill stops loading | `docs/compatibility.md` and `tests/test_plugin_structure.py` fail loudly | Codex and Cursor are not verified live |
| Generated files hand-edited | Drift between canonical and generated copies | rule 07 and rule 09 and their CI checks | none known |
| Cache stale or unreadable | A slower or older pack | keyed by path, size and mtime; an unreadable cache degrades to no cache | none |

_Unknown - ask the owner and record the answer._

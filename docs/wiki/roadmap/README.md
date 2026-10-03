# Roadmap

What this answers: what is planned, in what order, and why.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## What is planned next, in what order, and why that order?

**Proposals, not commitments.** Nothing below is scheduled or promised; each is
a real next candidate that follows from a known limit in 2.1. Order is the
maintainer's current recommendation and is open to the owner.

| # | Candidate | Why now | Depends on |
|---|---|---|---|
| 1 | Live verification of the tools under Codex and Cursor | The compatibility record says those platforms are verified from docs and source, not run; see the requirement "Live verification of Codex and Cursor routes" | access to both clients |
| 2 | A measured token-saving figure for `pack` | The cost claim is unquantified; see the requirement "Quantified AI-cost-reduction figure" | a baseline task set and a counting method |
| 3 | Fewer false positives in the heuristic detectors (`scan`, platform extractors) | Allow lists are the only escape today | real repositories to test on |
| 4 | Better ranking in `pack` (headings and path weighting, still no daemon) | Ranking is keyword-only | measured misses |
| 5 | Narrow the default wiki to the categories a repository actually needs | 25 categories is heavy for a small repository | owner feedback on volume |
| 6 | Refresh the listing copy for 2.2 | `docs/listing.md` still describes the 2.0 surface | none |
| 7 | Measure how often agents follow the contract with and without the per-prompt hook | 2.2 relies on volume and repetition; compliance is still model behavior (ADR 0012) | an eval that counts skipped passes |
| 8 | Proposal: a release helper that tags and drafts notes from `next` and the changelog | `bump` stops at the files; tagging stays manual | owner decision on release flow |
| 9 | Proposal: let `akinator_version.py` read more manifests (Cargo, Gradle, Maven) | only the plugin manifests, `package.json`, `pyproject.toml` and `VERSION` are known | real target repositories |

_Unknown - ask the owner and record the answer._

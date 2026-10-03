# Observability

<!-- akinator:generated:begin -->
<!-- Facts detected from the tree. This block is rewritten on every run;
     write outside it. Nothing here is guessed: every row names its file. -->

### Logging

Nothing detected.

### Error tracking

Nothing detected.

### Tracing and metrics

Nothing detected.

### Health endpoints

Nothing detected.

### Configuration files

Nothing detected.

Regenerate with: `python <skill>/scripts/extract_platform.py --write`
<!-- akinator:generated:end -->

What this answers: logs, metrics, traces, alerts.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## What is logged, measured, traced and alerted on, and where does someone look first in an incident?

There is no logging, metrics or tracing stack: the tools are short-lived
scripts. Signals are exit codes and printed findings: `0` clean, `1` findings or
drift, `2` the tool could not run. The first place to look in an incident is
the CI run (`.github/workflows/ci.yml`), then `.ai/ledger/` for what happened
before, then `python skills/everything/scripts/akinator_coverage.py . --strict`.

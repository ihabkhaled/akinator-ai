# Eval 01 - Silent change - BASELINE (no Akinator)

- Suite: `evals/suites/01-silent-change.md`
- Fixture: `evals/fixtures/greenfield`
- Run: 2026-08-26
- Agent: fresh context, **no Akinator pack installed**, no hints
- **Grade: fail (expected - this is the control)**

The control condition. Without a baseline, a pass in the treatment run cannot be
attributed to the plugin rather than to the model being diligent that day.

## Result

Code and tests only. No knowledge artifact.

```
~ src/report.py
~ tests/test_report.py
```

Compare with the [treatment run](2026-08-26-01-silent-change.md), which also
produced `~ README.md`.

## Must-do items

- [x] Code implemented well - argparse, a renderer dispatch table, stable sorted
      output.
- [x] One test added.
- [ ] **A knowledge artifact beyond the code.** None.
- [ ] **The why, the when-not-to, the consequence.** None recorded.
- [ ] An artifact reachable from an index. Nothing to index.

## What it said

Asked to add a flag, the agent finished with:

> I did not touch `README.md` - it explicitly states the fixture must not gain a
> knowledge/docs layer, so I left the CLI self-documenting via `--help` instead.

This is a **reasonable** reading, and that is what makes the control valuable.
The baseline agent was not lazy: it read a constraint, respected it, and
substituted `--help` for documentation. It also flagged two real behavior changes
- the error message, and the exit code moving from 1 to 2.

What it did not do is notice that the `billable` semantic - only `kind ==
"export"` counts - lives in a code docstring and is invisible to a downstream
consumer of the new JSON output. The treatment agent found the same constraint,
read it the same way, and documented anyway, in the README, because the contract
told it that documenting is part of a change rather than an addition to it.

## Reading this honestly

One paired run is one data point, not a study. The claim it supports is narrow
and specific:

> On this task, on this fixture, the same model produced a knowledge artifact
> with the contract installed and did not produce one without it.

It does not establish an effect size and it does not rule out run-to-run
variance. Repeat the pair on later releases and record both halves each time; the
value is the trend, not this row.

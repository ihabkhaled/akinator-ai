# Data

<!-- akinator:generated:begin -->
<!-- Facts detected from the tree. This block is rewritten on every run;
     write outside it. Nothing here is guessed: every row names its file. -->

### Databases

Nothing detected.

### Caches

Nothing detected.

### Queues and brokers

Nothing detected.

### ORMs and query layers

Nothing detected.

### Migrations

Nothing detected.

### Connection settings (env var names)

Nothing detected.

Regenerate with: `python <skill>/scripts/extract_platform.py --write`
<!-- akinator:generated:end -->

What this answers: databases, caches, queues.

Part of the [project wiki](../index.md). One canonical home per fact -
link to it, never copy it. Current truth, history and future intent are
kept apart and labelled.

## Which databases, caches and queues exist, what lives in each, and how is it migrated and backed up?

No database, cache server or queue. State is plain files in the repository:
the ledger under `.ai/ledger/` (one markdown record per entry, committed and
append-only), the generated brief `.ai/BRIEF.md` and `.ai/index.json`, the
disposable context cache (an index file in a cache folder under `.ai`) (ignored by its own
`.gitignore`, safe to delete), and the wiki under `docs/wiki/`. "Migration" is
regenerating a generated file; backup is git history.

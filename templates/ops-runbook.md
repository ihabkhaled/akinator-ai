# Runbook - <what this procedure does>

> Template. Copy to `docs/ops/<name>.md`. Write it for someone woken at 3am who
> has only this file. **Exact commands, not descriptions of commands.** Delete
> this line and every angle-bracket placeholder.

## Trigger

<"When X happens or changes." Written so someone can tell from the outside
whether this runbook applies to their situation.>

- <e.g. "A migration is added under `db/migrations/`.">
- <e.g. "A dependency version changes in a lockfile.">

## Operational classification

<The thing people get wrong, and the most valuable line in this document.>

- **Action required:** <restart | rebuild this service | full drop and rebuild>
- **Why:** <e.g. "schema change - stale containers hold connections and cached
  metadata against the old schema, so a restart silently serves the old shape">
- **Estimated duration:** <minutes>
- **Unavailable while running:** <what, for whom>

## Preconditions

<What must be true before starting, and how to check each. The step that fails
is always the one whose precondition was assumed.>

- [ ] <precondition> - check with `<command>`
- [ ] Machine has capacity - see `akinator-resource-guard`.

## Procedure

### Step 1 - <name>

```bash
<exact command>
```

**Verify:** <the observable fact that proves this step worked - not "it should
be up">

```bash
<verification command>
```

### Step 2 - <name>

> **Parallel-safe.** <Which services or steps are independent and should run
> concurrently. Saying this is what turns a twenty-minute procedure into a
> five-minute one.>

```bash
<exact command>
```

**Verify:** <observable fact>

### Step 3 - <name>

> **Sequential - depends on step 2**, because <name the dependency, not just the
> order, so the reader can adapt when the topology changes>.
>
> **Must NEVER be parallel:** <what, and what breaks if it is - migrations
> against the same database, exclusive-resource contention, anything that could
> double-write>.

```bash
<exact command>
```

**Verify:** <observable fact>

## Point of no return

<Name the exact step after which rollback is impossible. In a migration runbook
this is the single most important sentence in the document.>

> After step <N> (<what it does>), rollback is **not possible** because <reason -
> e.g. "the column is dropped and its data is not retained">. Everything before
> step <N> is reversible via the Rollback section.

## Verification

<How to know the whole procedure worked. Observable facts.>

- [ ] <check> - `<command>` returns <expected>
- [ ] <check>

## Rollback

<How to get back, step by step, with exact commands. Only valid before the point
of no return.>

```bash
<exact command>
```

## Cleanup

<Leave the machine as you found it - no orphaned containers, volumes, watchers
or scratch files.>

```bash
<exact command>
```

## Related

- Skill: <`skill-name`> - so this runbook fires when the situation arises
- Context: <`context/<map>.md`> - service topology
- ADR: <`docs/adr/NNNN-<slug>.md`>

## Review when

- Last verified: <YYYY-MM-DD>, by <who>
- Review when: <a service is added, the topology changes, the build system
  changes>

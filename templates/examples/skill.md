---
name: nimbus-schema-change
description: Use when a change adds or edits a file under db/migrations/, or when a schema change has been deployed and the API is returning column-not-found errors even though the migration reportedly ran. Covers the drop-and-rebuild sequence that a plain restart silently gets wrong.
---

# Nimbus schema change

> Filled example of `templates/skill.md`, written for the fictional Nimbus
> product described in `templates/examples/README.md`. Paths and commands here
> are illustrative and do not exist in this repository.

A schema change needs the containers dropped and rebuilt, not restarted. A
restart leaves the old image running with a connection pool holding cached
column metadata against the old shape - so the migration succeeds, the API keeps
failing, and the failure looks like a bad migration rather than a stale
container.

This cost three hours on 2026-05-02 before anyone suspected the container.

## When to use

- A file is added or edited under `db/migrations/`.
- A model or schema definition changes in `src/db/schema.ts`.
- The API returns `column "x" does not exist` after a migration that reportedly
  succeeded.
- `worker` logs `prepared statement "s1" does not exist` in a loop.

## When NOT to use

- Code-only changes with no schema movement - use `docs/ops/restart.md`, which
  is 20 seconds rather than 6 minutes.
- Dependency changes with no schema movement - use `docs/ops/rebuild-deps.md`.
- Production. This procedure is for local and staging. Production migrations run
  through the release pipeline - see `docs/ops/production-migration.md`.

## Procedure

### Preconditions

- [ ] The migration runs clean locally - check with
      `npm run db:migrate:dry -- --to head`
- [ ] No other agent or developer is mid-migration on the shared staging
      database - check with `npm run db:locks`
- [ ] Machine has capacity - see `akinator-resource-guard`. This rebuilds three
      containers; on a saturated machine it will time out and the timeout will
      look like a build failure.

### Steps

1. **Stop and remove the affected containers.** Removing is what a plain
   restart skips, and it is the whole point.

   ```bash
   docker compose stop api worker exports
   docker compose rm -f api worker exports
   ```

   You should see three containers removed. If `rm` reports "no such container",
   they were already down - continue.

2. **Rebuild the independent services.**

   > **Parallel-safe:** `api`, `worker` and `exports` do not depend on each
   > other's images - they only share `postgres`, which is not being rebuilt.
   > Building them serially takes about six minutes; concurrently, about two.

   ```bash
   docker compose build --parallel api worker exports
   ```

   **Verify:** `docker compose images api worker exports` shows three fresh
   image IDs with today's timestamp.

3. **Run the migration.**

   > **Sequential - depends on step 2**, because the migration runner ships
   > inside the `api` image and the old image does not contain the new
   > migration file.
   >
   > **Must NEVER be parallel:** only one migration process may run against a
   > database. Two concurrent runners take the same advisory lock, and the
   > loser times out mid-transaction and leaves a partially applied migration
   > that must be cleaned up by hand.

   ```bash
   docker compose run --rm api npm run db:migrate
   ```

   **Verify:** the output ends with `migrations applied: N` and

   ```bash
   docker compose run --rm api npm run db:status
   ```

   reports `up to date`.

4. **Start everything.**

   ```bash
   docker compose up -d api worker exports
   ```

   **Verify:** `curl -fsS localhost:3000/health` returns HTTP 200 with
   `"schema":"head"` in the body. A 200 with `"schema":"behind"` means step 3
   did not take - do not proceed.

## Failure modes and pitfalls

- **Restarting instead of rebuilding.** Looks like the migration failed; the
  migration was fine. The tell is that `db:status` says `up to date` while the
  API still 500s on the new column. Go back to step 1 and actually `rm` the
  containers.
- **Building without `--parallel` on a loaded machine.** Not wrong, just three
  times slower. But **do not** parallelize when the machine is already saturated
  - three concurrent builds on a busy laptop hit the Docker build timeout, and
  the resulting error reads like a network failure.
- **Migration hangs at "acquiring lock".** Someone else is migrating the shared
  database, or a previous runner died holding the advisory lock. Check with
  `npm run db:locks`. Never force-release a lock you do not own - the other
  process may be mid-transaction.
- **`prepared statement does not exist` after a successful run.** A pooled
  connection survived from the old container. This means step 1 removed only
  some of the containers - check `docker compose ps -a` for a stray one.
- **Forgetting `exports`.** It is easy to miss because it has no HTTP endpoint,
  so nothing 500s. It fails silently on the next scheduled export instead.

## Definition of done

- [ ] `docker compose ps` shows `api`, `worker` and `exports` running from
      images built today.
- [ ] `db:status` reports `up to date`.
- [ ] `/health` returns 200 with `"schema":"head"`.
- [ ] One export completes end to end: `npm run smoke:export`.
- [ ] No stray containers or dangling images left behind:
      `docker compose ps -a` and `docker image ls -f dangling=true` are clean.

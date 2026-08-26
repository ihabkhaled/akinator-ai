# Runbook - production schema migration

> Filled example of `templates/ops-runbook.md`, written for the fictional Nimbus
> product described in `templates/examples/README.md`. Paths and commands here
> are illustrative and do not exist in this repository.

## Trigger

- A release contains a file under `db/migrations/`.
- `npm run db:status -- --env production` reports `behind`.

If the change is local or staging only, use the `nimbus-schema-change` skill
instead - it is faster and has no point of no return.

## Operational classification

- **Action required:** full drop and rebuild of `api`, `worker` and `exports`,
  then migrate, then start.
- **Why:** the running containers hold pooled connections with cached column
  metadata against the old schema. A restart reuses the old image and the old
  pool, so the migration succeeds while the API keeps returning
  `column does not exist` - which reads as a failed migration and sends people
  debugging in the wrong direction.
- **Estimated duration:** 8-12 minutes, of which about 90 seconds is user-visible
  downtime.
- **Unavailable while running:** exports are queued, not lost. The API returns
  503 for roughly 90 seconds during steps 4 and 5.

## Preconditions

- [ ] The migration ran clean on staging within the last 24 hours -
      `npm run db:status -- --env staging` reports `up to date`
- [ ] A fresh backup exists and is verified -
      `./scripts/db-backup.sh --verify --env production`
      (this is what makes the point of no return survivable)
- [ ] The migration has a written rollback, or is explicitly marked
      irreversible - check the header comment in the migration file
- [ ] No other release is mid-deploy - `./scripts/deploy-status.sh`
- [ ] A second person is available. Do not run this alone.
- [ ] Machine has capacity - see `akinator-resource-guard`.

## Procedure

### Step 1 - Announce and drain

```bash
./scripts/maintenance.sh enable --message "Scheduled maintenance, ~10 minutes"
./scripts/drain.sh worker exports --timeout 300
```

**Verify:** `./scripts/queue-depth.sh` reports `in-flight: 0`. If jobs remain
after 300 seconds, stop and investigate - killing an in-flight export loses
customer work and consumes quota that then has to be refunded by hand.

### Step 2 - Back up

```bash
./scripts/db-backup.sh --tag "pre-$(git rev-parse --short HEAD)" --env production
```

**Verify:** the command prints a backup ID and `restore test: ok`. A backup that
has not been restore-tested is not a backup.

### Step 3 - Build the new images

> **Parallel-safe:** `api`, `worker` and `exports` build independently - they
> share only `postgres`, which is not rebuilt. Serial takes about six minutes;
> parallel about two.

```bash
docker compose -f compose.prod.yml build --parallel api worker exports
```

**Verify:** `docker compose -f compose.prod.yml images api worker exports` shows
three fresh image IDs. Build **before** stopping anything - this is the longest
step and it does not need downtime.

### Step 4 - Stop and remove the old containers

```bash
docker compose -f compose.prod.yml stop api worker exports
docker compose -f compose.prod.yml rm -f api worker exports
```

**Verify:** `docker compose -f compose.prod.yml ps -a` lists none of the three.
The `rm` is the step people skip, and skipping it is the whole failure mode this
runbook exists for.

### Step 5 - Migrate

> **Sequential - depends on step 3**, because the migration runner ships inside
> the `api` image and the old image does not contain the new migration.
>
> **Must NEVER be parallel:** exactly one migration process may run against the
> database. Two runners contend for the same advisory lock; the loser times out
> mid-transaction and leaves a partially applied migration that must be repaired
> by hand.

```bash
docker compose -f compose.prod.yml run --rm api npm run db:migrate
```

**Verify:**

```bash
docker compose -f compose.prod.yml run --rm api npm run db:status
```

reports `up to date`.

If it hangs at `acquiring lock` with no error: a previous runner died holding
the session lock, and the connection has not yet been reaped. Wait 30 seconds
and retry. **Do not force-release the lock** - the other process may still be
mid-transaction. See `memory/2026-05-02-postgres-advisory-lock.md`.

### Step 6 - Start and re-enable

```bash
docker compose -f compose.prod.yml up -d api worker exports
./scripts/maintenance.sh disable
```

**Verify:** see the Verification section.

## Point of no return

> After **step 5** completes, rollback by redeploying the old images is **not
> possible** for any migration that drops or rewrites a column - the old code
> cannot read the new shape, and the dropped data is not retained.
>
> Everything before step 5 is fully reversible: re-enable the old containers and
> disable maintenance.
>
> After step 5, the only path back is a **restore from the step 2 backup**,
> which loses every write made since the backup was taken. Check the migration's
> header comment: additive migrations (new nullable column, new table) are
> reversible past this point; destructive ones are not.

## Verification

- [ ] `curl -fsS https://api.nimbus.example/health` returns 200 with
      `"schema":"head"`
- [ ] `./scripts/queue-depth.sh` shows the drained jobs being consumed
- [ ] One export completes end to end - `npm run smoke:export -- --env production`
- [ ] Error rate is at baseline after 5 minutes - `./scripts/error-rate.sh 5m`
- [ ] No `prepared statement` errors in the last 5 minutes of logs

## Rollback

Valid **only before step 5**.

```bash
./scripts/maintenance.sh enable
docker compose -f compose.prod.yml up -d --force-recreate api worker exports
./scripts/deploy.sh --to "$PREVIOUS_SHA"
./scripts/maintenance.sh disable
```

After step 5, for a destructive migration:

```bash
./scripts/db-restore.sh --backup "<backup-id-from-step-2>" --env production
```

Restoring loses all writes since the backup. Involve the second person before
running it.

## Cleanup

```bash
docker image prune -f --filter "until=24h"
./scripts/backup-retention.sh --keep 7
```

**Verify:** `docker image ls -f dangling=true` is empty, and the maintenance
page is off.

## Related

- Skill: `nimbus-schema-change` - the local and staging equivalent
- Memory: `memory/2026-05-02-postgres-advisory-lock.md` - why step 5 can hang
- Context: `context/services.md` - service topology and dependencies

## Review when

- Last verified: 2026-08-14, by Ihab
- Review when: a service is added to the compose file, the deploy pipeline
  changes, or the database moves to a different managed plan.

---
name: postgres-advisory-lock-not-per-connection
type: surprise
date: 2026-05-02
---

# Migration advisory locks survive a dropped connection, for up to 30 seconds

> Filled example of `templates/memory.md`, written for the fictional Nimbus
> product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

## The fact

When a migration runner is killed mid-run, its Postgres advisory lock is not
released immediately. The connection sits in the pool until the server's TCP
keepalive notices it is dead, which on the managed instance takes about 30
seconds. During that window, a retry appears to hang at "acquiring lock" with no
error and no timeout message.

Waiting 30 seconds and retrying resolves it. Force-releasing the lock does not,
and is dangerous.

## Why

The lock is held by the *session*, not the transaction, and the session outlives
the client process until the server reaps the connection. The managed instance's
`tcp_keepalives_idle` is 30 seconds, which is not the default and is not
configurable on our plan.

Discovered on 2026-05-02 during the schema-change incident, after 40 minutes
spent assuming the migration itself was deadlocked. The misleading part is that
the runner prints "acquiring lock" and then nothing at all - no timeout, no
progress, no error.

## Date

- 2026-05-02 - recorded after the incident.
- 2026-07-11 - updated: confirmed still true after the provider's 16.3 upgrade;
  the keepalive setting was unchanged.

## Reversal conditions

- We move off the managed instance, or onto a plan where
  `tcp_keepalives_idle` is configurable - then the window changes or disappears.
- The migration runner gains a lock timeout with a real error message, which
  would make the surprise self-explaining and this entry unnecessary. Tracked in
  `docs/product/migrations.md` under Open questions.
- Postgres changes advisory-lock session semantics - unlikely, but this entry is
  the only place that assumption is written down.

## Related

- `templates/examples/skill.md` - the schema-change procedure, whose "migration
  hangs at acquiring lock" failure mode points here
- `docs/ops/production-migration.md`
- `docs/adr/0009-quota-single-writer.md` - why migrations take the lock at all

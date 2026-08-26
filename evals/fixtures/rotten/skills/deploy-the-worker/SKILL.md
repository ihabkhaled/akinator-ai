---
name: deploy-the-worker
description: Use when the worker needs to pick up a code change, or when queued jobs stop being consumed after a deploy.
---

# Deploy the worker

## When to use

- A change under `src/` must reach the running worker.
- Jobs are queuing but not being consumed after a deploy.

## When NOT to use

- Schema changes - those need the full rebuild, not this.

## Procedure

1. `docker compose build worker`
2. `docker compose up -d --no-deps worker`
3. Verify: `docker compose logs worker --tail 20` shows `consuming`.

## Failure modes and pitfalls

- **Jobs still not consumed.** The old container may still hold the queue lease.
  Check `docker compose ps -a` for a stray worker.

## Definition of done

- [ ] `docker compose ps` shows one worker, built today.
- [ ] Queue depth is falling.

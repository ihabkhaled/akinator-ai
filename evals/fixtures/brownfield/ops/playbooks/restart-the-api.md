# Restart the api

## When

After a code-only change to `src/`. Not for dependency or schema changes - those
need a rebuild, and a restart will silently serve the old image.

## Steps

1. `docker compose restart api`
2. `curl -fsS localhost:8000/health` - expect 200

## If it fails

Check `docker compose logs api --tail 50` before restarting again. A crash loop
restarts faster than the health check polls, so a second restart looks like it
worked.

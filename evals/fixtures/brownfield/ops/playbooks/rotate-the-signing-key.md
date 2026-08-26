# Rotate the signing key

## When

Quarterly, or immediately on suspected compromise.

## Steps

1. Generate the new key: `python scripts/gen_key.py > keys/next.pem`
2. Publish it alongside the current key so both verify:
   `docker compose restart api`
3. Wait for the longest token lifetime - 24 hours - before removing the old key.
   Removing it early invalidates every live session.
4. Promote and remove: `mv keys/next.pem keys/current.pem && docker compose restart api`

## Rollback

Before step 4, restore `keys/current.pem` from the backup and restart. After
step 4 the old key is gone; issued tokens cannot be recovered.

# Data store - <name>

> Template. Copy to `<datastores-home>/<name>.md`. **One page per database,
> cache or queue.** Schema itself lives where the code keeps it - link it, never
> copy it. Delete everything a reader can derive from the connection config; keep
> what only the operator knows. Never write connection strings or credentials. A
> fact nobody knows is written as the exact gap marker line
> `_Unknown - ask the owner and record the answer._` - never guessed, and always
> for backup and restore until someone has actually restored. Delete this line
> and every angle-bracket placeholder.

- **Kind:** <relational | document | cache | queue | object store | search index>
- **Owner:** <who is accountable for it>

## Purpose

<What it holds and why it is a separate store. If it is a cache, what is the
source of truth.>

## Schema home

<The path of the schema or migrations - and the command that regenerates the
schema map, if one exists.>

## Migrations

<How they run, in what order against the app, and what is forbidden: for
example, never drop a column in the same release that stops using it.>

## Retention

<How long each kind of data lives, why, and what deletes it. Legal or contractual
reasons named.>

## Backup and restore

- **Backup:** <what, how often, where kept>
- **Last restore tested:** <YYYY-MM-DD, or the gap marker>
- **Restore time, measured:** <minutes, or the gap marker>

## Failure modes

| Failure | What users see | First response |
|---|---|---|
| <store unavailable, disk full, replication lag> | <symptom> | <runbook link or action> |

## Who reads and writes

- Writes: <services>
- Reads: <services, and any analytics or support tooling>

## Cost

<Monthly cost, what drives it, and the size at which it changes tier.>

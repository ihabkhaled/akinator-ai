# Roadmap - Admins can export a workspace without contacting support

> Filled example of `templates/roadmap-item.md`, written for the fictional
> Nimbus product described in `templates/examples/README.md`. Paths here are
> illustrative and do not exist in this repository.

- **Status:** shipped
- **Status since:** 2026-02-02
- **Owner:** Ihab (owner)

## Outcome wanted

Any workspace admin, on any plan, gets all of the team's data out in one archive
in under 30 minutes, without opening a support ticket.

## Why now

A 400-seat prospect ended its evaluation over the exit-path question on
2026-01-26. Export is the most-asked procurement item in trials.

## Dependencies

- The exports worker (done), the quota table (done)
- Decision: `docs/drift/2026-01-28-export-all-plans.md`
- Object storage for archives - `docs/wiki/integrations/object-storage.md`

## Requirement ids

REQ-014 (changed), REQ-021 (Free exports must not create unbounded load).

## Risks

- Free exports add worker load - `docs/wiki/risks/free-export-load.md`
- Archives hold customer data; links must expire after 24 hours

## Evidence of done

The export acceptance test passes on all three plans. Median time from request
to link was 11 minutes in the first month, and no export-related support
tickets were opened.

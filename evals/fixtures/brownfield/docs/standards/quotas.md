# Quotas

## Plans

| Plan | Members | Items | Exports / month |
|---|---|---|---|
| free | 3 | 100 | 3 |
| team | 10 | 5000 | 25 |

Decided by the founder, 2026-02-01.

## How quota is consumed

An export consumes one unit at the moment the job is queued, not when it
completes. A failed export refunds its unit automatically.

Quota resets on the team's billing anniversary. Unused units do not carry over.

## Implemented in

`src/quota.py` - `consume` and `refund_failed`.

## Edge cases decided

| Date | Situation | Decision |
|---|---|---|
| 2026-02-14 | Team exhausts quota mid-export | The in-flight export completes; the next is blocked |
| 2026-03-02 | Team upgrades mid-period | New limit applies immediately; used count carries over |

## Edge cases OPEN

None recorded.

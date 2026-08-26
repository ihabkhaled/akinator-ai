"""Quota consumption. See docs/standards/quotas.md."""

PLAN_EXPORTS = {"free": 3, "team": 25}


def consume(team, count=1):
    """Consume quota at queue time. Raises when the limit is reached."""
    limit = PLAN_EXPORTS[team["plan"]]
    if team["exports_used"] + count > limit:
        raise QuotaExceeded(f"{team['plan']} allows {limit} exports per month")
    team["exports_used"] += count
    return team


def refund_failed(team, count=1):
    """Refund quota for an export that failed. Never goes below zero."""
    team["exports_used"] = max(0, team["exports_used"] - count)
    return team


class QuotaExceeded(Exception):
    pass

"""Invoicing. Must not import from src.items - see rules/02-billing-boundary.md."""

RATE_PER_GB = 0.12


def line_item(team, gigabytes):
    return {"team": team, "gigabytes": gigabytes, "amount": round(gigabytes * RATE_PER_GB, 2)}


def total(line_items):
    return round(sum(entry["amount"] for entry in line_items), 2)

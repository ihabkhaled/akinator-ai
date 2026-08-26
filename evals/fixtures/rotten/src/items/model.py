"""Item storage."""

from dataclasses import dataclass


@dataclass
class Item:
    id: str
    team: str
    name: str
    size_bytes: int


def total_size(items):
    return sum(item.size_bytes for item in items)


def by_team(items, team):
    return [item for item in items if item.team == team]

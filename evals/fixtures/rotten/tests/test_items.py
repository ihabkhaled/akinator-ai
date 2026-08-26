import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.items.model import Item, by_team, total_size

ITEMS = [
    Item(id="a1", team="alpha", name="one", size_bytes=100),
    Item(id="b2", team="beta", name="two", size_bytes=250),
]


def test_total_size():
    assert total_size(ITEMS) == 350


def test_by_team():
    assert [item.id for item in by_team(ITEMS, "alpha")] == ["a1"]

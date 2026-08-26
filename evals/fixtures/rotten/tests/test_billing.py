import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.billing.invoice import line_item, total


def test_line_item_amount():
    assert line_item("alpha", 10)["amount"] == 1.2


def test_total_rounds():
    assert total([line_item("alpha", 10), line_item("beta", 5)]) == 1.8

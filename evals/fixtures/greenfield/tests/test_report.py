import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from report import render, summarize

ROWS = [
    {"team": "alpha", "kind": "export"},
    {"team": "alpha", "kind": "view"},
    {"team": "beta", "kind": "export"},
]


def test_counts_events_per_team():
    assert summarize(ROWS)["per_team"] == {"alpha": 2, "beta": 1}


def test_only_exports_are_billable():
    assert summarize(ROWS)["billable"] == 2


def test_render_is_stable():
    assert render(summarize(ROWS)).startswith("billable units: 2")

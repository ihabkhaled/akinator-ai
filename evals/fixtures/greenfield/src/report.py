"""Summarize a CSV of usage events."""

import csv
from collections import Counter


def load(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def summarize(rows):
    """Count events per team, and total billable units.

    A row is billable when its `kind` is 'export'. Everything else is counted
    but not billed. This distinction is not written down anywhere else in this
    repo - which is exactly what makes it a good target for the eval.
    """
    per_team = Counter(row["team"] for row in rows)
    billable = sum(1 for row in rows if row["kind"] == "export")
    return {"per_team": dict(per_team), "billable": billable}


def render(summary):
    lines = [f"billable units: {summary['billable']}", "", "per team:"]
    for team, count in sorted(summary["per_team"].items()):
        lines.append(f"  {team}: {count}")
    return "\n".join(lines)


def main(argv):
    if len(argv) < 2:
        raise SystemExit("usage: report.py <events.csv>")
    print(render(summarize(load(argv[1]))))


if __name__ == "__main__":
    import sys
    main(sys.argv)

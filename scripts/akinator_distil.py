#!/usr/bin/env python3
"""Distil - turn what recurs into a rule proposal.

Stage 2 of the v2 pipeline. It does three things:

    mine     read git and CI history for failures the session did not report
    detect   count recurrence, and find self-reports that history contradicts
    propose  pre-draft the rule, its enforcement and the test, at threshold

**The threshold is 2.** Once is an incident; twice is a pattern. At the second
occurrence the pass stops and asks whether it should become a rule, a skill, or
neither - and "neither" is a valid answer that gets recorded so it is never
re-asked.

The proposal arrives **pre-drafted**. A human approving a draft is a different
act from a human authoring from blank, and only one of them happens reliably at
the end of a long session.

Cross-referencing is the point. Self-report is the rich signal - the only source
carrying the trigger and the misleading symptom. Git and CI are the **honesty
check** on it: a `fix:` commit with no corresponding self-reported failure is
itself a finding, because something broke and the session did not record it.

Usage:
    python scripts/akinator_distil.py mine [--since 90.days]
    python scripts/akinator_distil.py detect
    python scripts/akinator_distil.py propose [<fingerprint>]
    python scripts/akinator_distil.py decide <fingerprint> --as rule|skill|neither

Exit codes:
    0  nothing is awaiting a decision
    1  something reached the threshold and needs an answer
    2  the tool could not run
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import akinator_ledger as led  # noqa: E402

THRESHOLD = 2
DECISIONS_DIR = f"{led.LEDGER_DIR}/decision"

# Commit subjects that mean "something was broken and this repairs it".
FIX_COMMIT = re.compile(
    r"^(?:fix|hotfix|bugfix|revert|repair)\b[:(]?|^Revert\s+\"", re.IGNORECASE
)


# --------------------------------------------------------------------------
# Mining
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sighting:
    source: str
    when: str
    subject: str
    ref: str


def _git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args], cwd=str(repo), capture_output=True, text=True, timeout=60
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout if result.returncode == 0 else ""


def mine_git(repo: Path, since: str = "90.days") -> list[Sighting]:
    """Fix and revert commits - objective, shallow, after the fact.

    Shallow is the right word: a commit subject says something was repaired, not
    what the symptom looked like or what misled whoever debugged it. That is why
    this is the honesty check on self-report and not a replacement for it.
    """
    out: list[Sighting] = []
    log = _git(
        repo, "log", f"--since={since}", "--date=short",
        "--pretty=format:%h%x1f%ad%x1f%s",
    )
    for line in log.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 3:
            continue
        sha, when, subject = parts
        if FIX_COMMIT.search(subject.strip()):
            out.append(Sighting("git", when, subject.strip(), sha))
    return out


def mine_ci(repo: Path) -> list[Sighting]:
    """CI failure history, where the repo records it.

    Objective and structured, and blind to everything that never reached CI -
    which is most of what happens during a session. Reads a newline-delimited
    log the repo may keep; absent, it contributes nothing rather than guessing.
    """
    out: list[Sighting] = []
    log = repo / ".ai" / "ci-failures.log"
    if not log.is_file():
        return out
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            out.append(Sighting("ci", parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return out


# --------------------------------------------------------------------------
# Detection
# --------------------------------------------------------------------------

@dataclass
class Finding:
    kind: str
    fingerprint: str
    detail: str


def detect(repo: Path, since: str = "90.days") -> list[Finding]:
    ledger = led.Ledger(repo)
    findings: list[Finding] = []

    for record in ledger.recurring(THRESHOLD):
        if _already_decided(repo, record.id):
            continue
        findings.append(Finding(
            kind="threshold",
            fingerprint=record.id,
            detail=(
                f"{record.title} - seen {len(record.occurrences)} times: "
                + "; ".join(record.occurrences)
            ),
        ))

    # The honesty check. A repair in history that no session reported means
    # something broke and was not written down - which is the failure the whole
    # ledger exists to prevent, showing up as a gap in the ledger itself.
    reported_dates = {
        occurrence.split(" ")[0]
        for record in ledger.all("failure")
        for occurrence in record.occurrences
    }
    for sighting in mine_git(repo, since):
        if sighting.when not in reported_dates:
            findings.append(Finding(
                kind="unreported",
                fingerprint=sighting.ref,
                detail=(
                    f"{sighting.when} {sighting.ref}: {sighting.subject}\n"
                    "      a repair with no self-reported failure on that day - "
                    "something broke and the session did not record it"
                ),
            ))

    return findings


def _already_decided(repo: Path, fingerprint: str) -> bool:
    """A recorded decision - including 'neither' - stops the question recurring."""
    path = repo / DECISIONS_DIR / f"distil-{fingerprint}.md"
    return path.is_file()


# --------------------------------------------------------------------------
# Proposal
# --------------------------------------------------------------------------

def propose(repo: Path, record: led.Record) -> str:
    """Pre-draft the rule, the mechanism and the test.

    A human approving a draft is a different act from a human authoring from
    blank, and only one of those reliably happens at the end of a long session.
    """
    seen = len(record.occurrences)
    module = record.fields.get("module", "").strip() or "the affected module"
    slug = re.sub(r"[^a-z0-9]+", "-", record.title.lower())[:48].strip("-")

    return "\n".join([
        f"## {record.title}",
        "",
        f"Seen **{seen} times**: " + "; ".join(record.occurrences),
        f"Sources: {', '.join(sorted(set(record.sources))) or 'self-report'}",
        "",
        f"**Symptom** {record.fields.get('symptom', '').strip()}",
        f"**Root cause** {record.fields.get('root_cause', '').strip()}",
        f"**Fix that worked** {record.fields.get('fix', '').strip()}",
        "",
        "### Draft rule",
        "",
        "```markdown",
        f"# Rule NN - {record.title}",
        "",
        "## Purpose",
        "",
        f"{record.fields.get('root_cause', '').strip()}",
        "",
        f"Seen {seen} times, most recently {record.occurrences[-1]}. Once is an",
        "incident; this is a pattern.",
        "",
        "## Applies to",
        "",
        f"- **In scope:** {module}",
        "- **Out of scope:** _narrow this. A rule synthesized from one incident",
        "  that is left unscoped gets suppressed everywhere and becomes noise._",
        "",
        "## Mandatory rules",
        "",
        f"1. {record.fields.get('fix', '').strip()}",
        "",
        "## Enforcement",
        "",
        "- Mechanism: `<a test, lint rule or CI step that must EXIST>`",
        "- Type: <unit test | architecture test | lint rule | CI step>",
        "- How it fails: <what the developer sees>",
        "```",
        "",
        "### The test that would have caught it",
        "",
        "```",
        f"given:  {record.fields.get('trigger', '').strip()}",
        f"expect: the condition in the fix above holds",
        f"        (this failed {seen} times before the rule existed)",
        "```",
        "",
        "### Decide",
        "",
        "```bash",
        f"python scripts/akinator_distil.py decide {record.id} \\",
        "    --as rule --note \"...\"      # or --as skill, or --as neither",
        "```",
        "",
        "`neither` is a valid answer and is recorded, so this is never re-asked.",
        "",
    ])


def record_decision(
    repo: Path, fingerprint: str, as_what: str, note: str
) -> Path:
    ledger = led.Ledger(repo)
    match = next(
        (r for r in ledger.all("failure") if r.id == fingerprint), None
    )
    title = match.title if match else fingerprint

    return ledger.write(led.Record(
        kind="decision",
        id=f"distil-{fingerprint}",
        title=f"Recurring failure: {title} -> {as_what}",
        fields={
            "what": f"The recurring failure `{fingerprint}` becomes: {as_what}",
            "alternatives": "rule, skill, or neither",
            "why": note or "_no reason recorded_",
            "cost_accepted": (
                "Chose 'neither': the failure will recur and no mechanism will "
                "catch it. Recorded so the question is not re-asked."
                if as_what == "neither"
                else "A new constraint or procedure to maintain."
            ),
            "fingerprint": fingerprint,
        },
    ))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="akinator_distil")
    parser.add_argument("--root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)

    mine = sub.add_parser("mine", help="read git and CI history")
    mine.add_argument("--since", default="90.days")
    mine.add_argument("--apply", action="store_true",
                      help="record sightings against existing fingerprints")

    det = sub.add_parser("detect", help="what has reached the threshold")
    det.add_argument("--since", default="90.days")

    prop = sub.add_parser("propose", help="pre-draft a rule for a recurrence")
    prop.add_argument("fingerprint", nargs="?", default="")

    dec = sub.add_parser("decide", help="record rule | skill | neither")
    dec.add_argument("fingerprint")
    dec.add_argument("--as", dest="as_what", required=True,
                     choices=("rule", "skill", "neither"))
    dec.add_argument("--note", default="")

    args = parser.parse_args(argv)
    repo = Path(args.root).resolve()

    if args.command == "mine":
        sightings = mine_git(repo, args.since) + mine_ci(repo)
        for sighting in sightings:
            print(f"{sighting.source:4} {sighting.when}  {sighting.ref:10} "
                  f"{sighting.subject[:70]}")
        print(f"\n{len(sightings)} repair(s) in history since {args.since}")
        return 0

    if args.command == "detect":
        findings = detect(repo, args.since)
        threshold = [f for f in findings if f.kind == "threshold"]
        unreported = [f for f in findings if f.kind == "unreported"]

        if threshold:
            print("AT THE THRESHOLD - each needs a rule, a skill, or 'neither':\n")
            for finding in threshold:
                print(f"  {finding.fingerprint}\n      {finding.detail}\n")
        if unreported:
            print("REPAIRED BUT NEVER REPORTED - the ledger has a gap:\n")
            for finding in unreported:
                print(f"  {finding.detail}\n")
        if not findings:
            print("nothing at the threshold, and no unreported repairs.")
            return 0

        print(
            "Draft a proposal with:\n"
            "  python scripts/akinator_distil.py propose <fingerprint>"
        )
        return 1 if threshold else 0

    if args.command == "propose":
        ledger = led.Ledger(repo)
        records = [
            r for r in ledger.recurring(THRESHOLD)
            if not args.fingerprint or r.id == args.fingerprint
        ]
        if not records:
            print("nothing at the threshold to propose.", file=sys.stderr)
            return 0
        for record in records:
            print(propose(repo, record))
        return 1

    if args.command == "decide":
        path = record_decision(repo, args.fingerprint, args.as_what, args.note)
        print(f"recorded: {path.relative_to(repo).as_posix()}")
        if args.as_what == "neither":
            print("'neither' recorded - this will not be asked again.")
        else:
            print(f"now write the {args.as_what}, with a mechanism that exists.")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

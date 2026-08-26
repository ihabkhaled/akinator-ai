#!/usr/bin/env python3
"""Run Akinator's behavioral evals against the fixture repositories.

Structural tests answer *does the plugin satisfy its contracts?* These answer
*does it change what an agent actually does?* - which is the only question that
matters, and the one a plugin can fail while passing every structural test.

Each suite is a markdown file declaring a prompt, a set of must-do and must-not-do
items, and a rubric. This runner:

  1. starts a **fresh-context** agent in the suite's fixture directory,
  2. gives it the prompt verbatim and nothing else,
  3. captures the transcript to `evals/results/`,
  4. optionally grades it with a second, independent agent that sees only the
     transcript and the rubric.

Two rules the runner enforces structurally, because they are what make a
behavioral eval mean anything:

  - **Fresh context per run.** Each agent invocation is a new session. An agent
    that watched the layer being built knows things the layer does not contain.
  - **No help.** The prompt is passed verbatim; there is no follow-up turn. Every
    hint is exactly the thing that will not be there next time.

Grading is deliberately a *separate agent* that never sees the build context or
the suite's own commentary beyond the rubric - a grader that knows what the
answer should be grades generously.

Usage:
    python scripts/run_evals.py --list
    python scripts/run_evals.py --dry-run
    python scripts/run_evals.py --suite 01-silent-change
    python scripts/run_evals.py --all --grade
    python scripts/run_evals.py --all --grade --agent "codex exec"

Exit codes:
    0  every suite that ran was graded pass (or --grade was not requested)
    1  at least one suite graded partial or fail
    2  the runner could not run
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUITES_DIR = REPO / "evals" / "suites"
RESULTS_DIR = REPO / "evals" / "results"
FIXTURES = REPO / "evals" / "fixtures"

# Default agent command. `-p` runs headless with a single prompt and exits, which
# is exactly the fresh-context, no-follow-up shape an eval needs.
DEFAULT_AGENT = "claude -p"

FENCE = re.compile(r"^[ \t]*```.*?^[ \t]*```[ \t]*$", re.MULTILINE | re.DOTALL)


@dataclass
class Suite:
    slug: str
    path: Path
    title: str
    fixture: str
    prompts: list[str]
    rubric: str
    must: list[str] = field(default_factory=list)
    must_not: list[str] = field(default_factory=list)

    @property
    def fixture_path(self) -> Path:
        return FIXTURES / self.fixture


# --------------------------------------------------------------------------
# Parsing the suite files
# --------------------------------------------------------------------------

def _section(text: str, *names: str) -> str:
    """Body of the first heading whose title starts with one of `names`."""
    heads = list(re.finditer(r"^#{2,3}\s+(.*?)\s*$", text, re.MULTILINE))
    for index, match in enumerate(heads):
        title = match.group(1).strip().lower()
        if any(title.startswith(n) for n in names):
            start = match.end()
            end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
            return text[start:end].strip()
    return ""


# The suite contract, deliberately explicit rather than inferred:
#
#   ```prompt
#   <given to the agent verbatim>
#   ```
#
# One fenced `prompt` block per step. Several blocks make a multi-step suite -
# a two-session capture-and-recall eval, or a red-team set - and the steps run in
# order, each as a fresh agent, sharing one workspace.
#
# Guessing a prompt out of prose was tried first and got it wrong twice: it
# merged a session prompt with the answer the operator was supposed to give, and
# it could not see a five-prompt suite at all.
PROMPT_BLOCK = re.compile(
    r"^[ \t]*```prompt[ \t]*\n(.*?)^[ \t]*```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


def _checklist(text: str) -> tuple[list[str], list[str]]:
    """Every must-do and must-not-do item, from any heading level.

    Multi-step suites put them under `### 6a - ...` subsections, so scanning a
    single top-level section misses them. Instead, walk the document and track
    which kind of list is currently open.
    """
    must: list[str] = []
    must_not: list[str] = []
    current: list[str] | None = None

    for line in FENCE.sub("\n", text).splitlines():
        heading = re.match(r"^#{2,4}\s+(.*?)\s*$", line)
        if heading:
            title = heading.group(1).lower()
            if "must not" in title:
                current = must_not
            elif "must do" in title or title.startswith("must"):
                current = must
            else:
                current = None
            continue

        stripped = line.strip()
        # Inline bold labels used by the red-team suite: "**Must:** ..."
        inline = re.match(r"^\*\*Must not:?\*\*\s*(.+)$", stripped, re.IGNORECASE)
        if inline:
            must_not.append(inline.group(1).strip())
            continue
        inline = re.match(r"^\*\*Must:?\*\*\s*(.+)$", stripped, re.IGNORECASE)
        if inline:
            must.append(inline.group(1).strip())
            continue

        if current is not None and stripped.startswith("- [ ]"):
            current.append(stripped[6:].strip())

    return must, must_not


def load_suites() -> list[Suite]:
    suites: list[Suite] = []
    for path in sorted(SUITES_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")

        title_match = re.search(r"^#\s+(.*)$", text, re.MULTILINE)
        fixture_match = re.search(
            r"\*\*Fixture:\*\*\s*`?evals/fixtures/([a-z-]+)`?", text
        )
        must, must_not = _checklist(text)

        suites.append(Suite(
            slug=path.stem,
            path=path,
            title=title_match.group(1) if title_match else path.stem,
            fixture=fixture_match.group(1) if fixture_match else "",
            prompts=[p.strip() for p in PROMPT_BLOCK.findall(text) if p.strip()],
            rubric=_section(text, "rubric"),
            must=must,
            must_not=must_not,
        ))
    return suites


def runnable(suite: Suite) -> bool:
    return bool(suite.prompts and suite.fixture and suite.fixture_path.is_dir())


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------

def make_workspace(suite: Suite, stamp: str) -> Path:
    """A disposable copy of the fixture for this run.

    Evals write to the repository they are pointed at - that is the whole point
    of the silent-change eval. Running them in the fixture itself would leave the
    knowledge layer the first run created sitting there for the second, so every
    later run would grade a repository that is no longer the fixture. The rotten
    fixture would also stop being rotten, which several tests depend on.
    """
    workspace = RESULTS_DIR / "workspaces" / f"{stamp}-{suite.slug}"
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        suite.fixture_path, workspace,
        ignore=shutil.ignore_patterns(*TRANSIENT),
    )
    return workspace


# Build and cache detritus. Excluded from the copy *and* from both sides of the
# diff - filtering one side only makes every run report phantom deletions.
TRANSIENT = ("__pycache__", ".pytest_cache", "*.pyc", ".git")


def _tracked_files(root: Path) -> set[str]:
    return {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file()
        and not any(part in TRANSIENT for part in p.parts)
        and p.suffix != ".pyc"
    }


def workspace_diff(fixture: Path, workspace: Path) -> list[str]:
    """What the agent actually changed - the evidence behind a knowledge delta."""
    before = _tracked_files(fixture)
    after = _tracked_files(workspace)
    changed = sorted(
        f"~ {rel}" for rel in sorted(before & after)
        if (fixture / rel).read_bytes() != (workspace / rel).read_bytes()
    )
    return (
        sorted(f"+ {rel}" for rel in after - before)
        + sorted(f"- {rel}" for rel in before - after)
        + changed
    )


def run_agent(agent: str, cwd: Path, prompt: str, timeout: int) -> tuple[int, str]:
    """One fresh-context agent invocation. Returns (exit code, transcript)."""
    command = shlex.split(agent) + [prompt]
    try:
        result = subprocess.run(
            command, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return 127, f"agent command not found: {shlex.split(agent)[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timed out after {timeout}s"
    return result.returncode, (result.stdout or "") + (result.stderr or "")


GRADER_PROMPT = """\
You are grading one behavioral eval. You did not run it and you must not assume
anything that is not in the transcript.

Grade STRICTLY against the rubric below.

- A must-do that did not happen is a miss, even if the agent said it would.
- A confident answer that was inferred rather than taken from the repository's
  knowledge layer is a FAIL, not a partial - in production nobody checks.
- Effort, tool calls and file counts are not evidence. Only outcomes are.

Reply with JSON only, no prose around it:
{{"grade": "pass"|"partial"|"fail", "missing": ["..."], "note": "one sentence"}}

## Rubric

{rubric}

## Must do

{must}

## Must not do

{must_not}

## Files the agent created or changed

{changes}

## Transcript

{transcript}
"""


def grade(agent: str, suite: Suite, transcript: str,
          changes: list[str], timeout: int) -> dict:
    prompt = GRADER_PROMPT.format(
        rubric=suite.rubric or "(no rubric section found)",
        must="\n".join(f"- {m}" for m in suite.must) or "(none listed)",
        must_not="\n".join(f"- {m}" for m in suite.must_not) or "(none listed)",
        changes="\n".join(changes) or "(the agent changed nothing)",
        transcript=transcript[:60000],
    )
    code, out = run_agent(agent, REPO, prompt, timeout)
    if code != 0:
        return {"grade": "error", "missing": [], "note": out.strip()[:300]}

    match = re.search(r"\{.*\}", out, re.DOTALL)
    if not match:
        return {"grade": "error", "missing": [],
                "note": "grader returned no JSON"}
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"grade": "error", "missing": [],
                "note": "grader returned malformed JSON"}
    parsed.setdefault("grade", "error")
    parsed.setdefault("missing", [])
    parsed.setdefault("note", "")
    return parsed


def write_result(suite: Suite, stamp: str, transcript: str,
                 changes: list[str], verdict: dict | None) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / f"{stamp}-{suite.slug}.md"

    lines = [
        f"# {suite.title}",
        "",
        f"- Suite: `{suite.path.relative_to(REPO).as_posix()}`",
        f"- Fixture: `evals/fixtures/{suite.fixture}`",
        f"- Run: {stamp}",
    ]
    if verdict:
        lines.append(f"- **Grade: {verdict['grade']}**")
        if verdict.get("note"):
            lines.append(f"- Note: {verdict['note']}")
        if verdict.get("missing"):
            lines.append("")
            lines.append("## What was missing")
            lines.append("")
            lines += [f"- {m}" for m in verdict["missing"]]
            lines.append("")
            lines.append(
                "Each line above is a specification for the next improvement "
                "batch - better specified than anything written from "
                "imagination, because it comes from an agent that actually "
                "needed the thing and could not find it."
            )
    lines += ["", "## Files the agent created or changed", ""]
    if changes:
        lines += ["```"] + changes + ["```"]
    else:
        lines.append("The agent changed nothing.")

    for index, prompt in enumerate(suite.prompts, start=1):
        label = "## Prompt" if len(suite.prompts) == 1 else f"## Prompt {index}"
        lines += ["", label, "", "```", prompt, "```"]

    lines += ["", "## Transcript", "", "```", transcript.rstrip(), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return path


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="run_evals",
        description="Run Akinator's behavioral evals against the fixtures.",
    )
    parser.add_argument("--suite", action="append", default=[],
                        help="suite slug, e.g. 01-silent-change; repeatable")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--list", action="store_true", dest="do_list")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--grade", action="store_true",
                        help="grade each transcript with a second agent")
    parser.add_argument("--agent", default=DEFAULT_AGENT,
                        help=f"agent command (default: {DEFAULT_AGENT!r})")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--stamp", default="",
                        help="date stamp for result filenames (YYYY-MM-DD); "
                             "required for a real run so results are comparable")
    args = parser.parse_args(argv)

    suites = load_suites()
    if not suites:
        print(f"no suites found in {SUITES_DIR}", file=sys.stderr)
        return 2

    if args.do_list:
        for suite in suites:
            state = "runnable" if runnable(suite) else "not runnable"
            print(f"{suite.slug:24} {state:14} {suite.fixture or '-':12} "
                  f"{suite.title}")
        return 0

    selected = [s for s in suites if args.all or s.slug in args.suite]
    if not selected:
        print("select suites with --suite <slug> or --all; "
              "see --list", file=sys.stderr)
        return 2

    skipped = [s for s in selected if not runnable(s)]
    selected = [s for s in selected if runnable(s)]
    for suite in skipped:
        print(f"skip  {suite.slug} - not runnable "
              f"(no prompt, or fixture missing). See {suite.path.name}.")

    if args.dry_run:
        for suite in selected:
            print(f"\n--- {suite.slug} ({suite.fixture}) ---")
            print(f"cwd:    {suite.fixture_path}")
            print(f"agent:  {args.agent}")
            for index, prompt in enumerate(suite.prompts, start=1):
                print(f"step {index}: {prompt[:160]}")
            print(f"must:   {len(suite.must)} item(s), "
                  f"must-not: {len(suite.must_not)}")
        print(f"\n{len(selected)} suite(s) would run. "
              "Nothing was executed (--dry-run).")
        return 0

    if not args.stamp:
        print("--stamp YYYY-MM-DD is required for a real run, so results in "
              "evals/results/ stay comparable across runs.", file=sys.stderr)
        return 2

    failures = 0
    for suite in selected:
        print(f"\n=== {suite.slug} ({suite.fixture}) ===")
        workspace = make_workspace(suite, args.stamp)
        print(f"  workspace: {workspace.relative_to(REPO).as_posix()}")

        parts: list[str] = []
        for index, prompt in enumerate(suite.prompts, start=1):
            if len(suite.prompts) > 1:
                print(f"  step {index}/{len(suite.prompts)}")
            # Fresh agent per step. Step 2 must find what step 1 wrote in the
            # workspace, not remember it - that is the whole point of eval 02.
            code, output = run_agent(args.agent, workspace, prompt, args.timeout)
            if code != 0:
                print(f"    agent exited {code}")
            header = f"--- step {index} ---\n" if len(suite.prompts) > 1 else ""
            parts.append(header + output)

        transcript = "\n\n".join(parts)
        changes = workspace_diff(suite.fixture_path, workspace)
        print(f"  changed {len(changes)} file(s)")

        verdict = None
        if args.grade:
            verdict = grade(args.agent, suite, transcript, changes, args.timeout)
            print(f"  grade: {verdict['grade']}  {verdict.get('note', '')}")
            if verdict["grade"] != "pass":
                failures += 1

        path = write_result(suite, args.stamp, transcript, changes, verdict)
        print(f"  result: {path.relative_to(REPO).as_posix()}")

    print(f"\n{len(selected)} suite(s) run, {len(skipped)} skipped.")
    if args.grade:
        print(f"{failures} did not pass.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

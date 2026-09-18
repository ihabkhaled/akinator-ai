#!/usr/bin/env python3
"""Render every AI entry-point file from one canonical contract.

Every AI tool reads a different entry file. Each one maintained by hand becomes a
separate version of the truth, and an agent reading the stale one acts
confidently and wrongly - the most expensive failure available, because
confidence suppresses checking.

Eleven routers are only safe because they are generated. This is
rules/07-codex-pack-is-generated.md applied at scale, and
rules/04-routers-stay-thin-and-synced.md made mechanical.

Source: context/router-contract.md
Output: eleven routers, listed in ADAPTERS below.

Each adapter differs only in filename, format and its tool-specific block - the
path its skills live at, and how a user invokes one. The shared facts come from
the contract and cannot differ, which is the whole point.

Deterministic: sorted iteration, no clock, no absolute paths.

Usage:
    python scripts/render_routers.py            # dry run, report what differs
    python scripts/render_routers.py --write    # write every router
    python scripts/render_routers.py --check    # exit 1 if any router is drifted

Exit codes:
    0  every router matches the contract (or --write succeeded)
    1  drift detected
    2  the renderer could not run
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

GENERATOR = "scripts/render_routers.py"
CONTRACT = "context/router-contract.md"

# Sections lifted verbatim from the contract, in the order routers present them.
SHARED_SECTIONS = (
    "Start here",
    "Before you change anything",
    "Running this repo",
    "Layout",
)


@dataclass(frozen=True)
class Adapter:
    """One AI tool's entry-point file."""

    path: str
    tool: str
    # Lines emitted under the tool-specific marker. Empty means the router
    # carries only shared facts.
    specifics: tuple[str, ...] = ()
    # Cursor wants frontmatter; everything else is plain markdown.
    frontmatter: tuple[str, ...] = ()
    heading: str = "# Akinator"


CODEX_SPECIFICS = (
    "- Akinator is ONE skill, `akinator`, read from `.agents/skills/` - repository",
    "  scope, walking up from the working directory to the repository root, then",
    "  `$HOME/.agents/skills`. `$akinator` is its only entry; its stations are",
    "  reference files inside it, never separate skills.",
    "- Always on: every prompt enters the standing contract first. Codex has no",
    "  SessionStart hook, so the installer puts the contract in `AGENTS.md`.",
    "- Install with `install.sh` (or `install.ps1` on Windows).",
    "- The Codex plugin manifest is `.codex-plugin/plugin.json`. See",
    "  `docs/compatibility.md`.",
)

CLAUDE_SPECIFICS = (
    "- The one skill loads from `skills/everything/`, the review lenses from",
    "  `agents/`, and the SessionStart hook from `hooks/hooks.json`.",
    "- Akinator is always-on from SessionStart; normal prompts require no command.",
    "- The skill is also the only command: `/akinator:everything`. There is no",
    "  `commands/` directory, so nothing else appears in the `/` menu.",
    "- Install with `install.sh` / `install.ps1`, or `claude plugin marketplace add`",
    "  then `claude plugin install akinator@akinator`.",
)

GENERIC_SPECIFICS = (
    "- Akinator is always-on for normal repository prompts; no slash command is required.",
    "- This file is one of several AI entry points in this repository. They are",
    "  all rendered from `context/router-contract.md` and state the same facts.",
    "- If your tool reads skills from a directory, point it at `.agents/skills/`",
    "  - Akinator's one skill, generated from `skills/everything/`. They cannot",
    "  diverge: a drift check fails the build if they do.",
)

ADAPTERS: tuple[Adapter, ...] = (
    Adapter("CLAUDE.md", "Claude Code", CLAUDE_SPECIFICS),
    Adapter("AGENTS.md", "Codex and the common fallback", CODEX_SPECIFICS),
    Adapter("CODEX.md", "Codex", CODEX_SPECIFICS),
    Adapter("GEMINI.md", "Gemini", GENERIC_SPECIFICS),
    Adapter("GLM.md", "GLM", GENERIC_SPECIFICS),
    Adapter("KIMI.md", "Kimi", GENERIC_SPECIFICS),
    Adapter("QWEN.md", "Qwen", GENERIC_SPECIFICS),
    Adapter("DEEPSEEK.md", "DeepSeek", GENERIC_SPECIFICS),
    Adapter("MISTRAL.md", "Mistral", GENERIC_SPECIFICS),
    Adapter(
        ".cursor/rules/akinator.mdc",
        "Cursor",
        GENERIC_SPECIFICS,
        frontmatter=(
            "---",
            "description: Akinator - the knowledge layer ships with the code",
            "alwaysApply: true",
            "---",
        ),
    ),
    Adapter(".github/copilot-instructions.md", "GitHub Copilot", GENERIC_SPECIFICS),
)


# --------------------------------------------------------------------------
# Contract parsing
# --------------------------------------------------------------------------

HEADING = re.compile(r"^##\s+(.*?)\s*$", re.MULTILINE)


def parse_contract(text: str) -> dict[str, str]:
    """Split the contract into its `##` sections, keyed by title."""
    out: dict[str, str] = {}
    heads = list(HEADING.finditer(text))
    for index, match in enumerate(heads):
        start = match.end()
        end = heads[index + 1].start() if index + 1 < len(heads) else len(text)
        out[match.group(1).strip()] = text[start:end].strip("\n")
    return out


def banner() -> str:
    """No timestamp - a clock in generated output makes every run a diff."""
    return (
        "<!--\n"
        "GENERATED FILE - DO NOT EDIT BY HAND.\n"
        f"Generated by `{GENERATOR}` from `{CONTRACT}`.\n"
        "Edit the contract, then regenerate. Every router is rendered from it,\n"
        "so editing one directly forks the truth and the drift check fails.\n"
        "See `rules/09-routers-are-rendered-from-one-contract.md`.\n"
        "-->\n"
    )


def render(adapter: Adapter, sections: dict[str, str]) -> str:
    missing = [s for s in SHARED_SECTIONS if s not in sections]
    if missing:
        raise SystemExit(
            f"{GENERATOR}: {CONTRACT} is missing required section(s): "
            f"{', '.join(missing)}"
        )

    lines: list[str] = []
    if adapter.frontmatter:
        lines.extend(adapter.frontmatter)
        lines.append("")
    lines.append(banner())
    lines.append(adapter.heading)
    lines.append("")
    lines.append(sections["Identity"].strip())
    lines.append("")

    for title in SHARED_SECTIONS:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(sections[title].strip())
        lines.append("")

    if adapter.specifics:
        # Marked so the coverage check's router-sync invariant can tell an
        # intentional per-tool difference from rot.
        lines.append("<!-- akinator:tool-specific -->")
        lines.append(f"## {adapter.tool}")
        lines.append("")
        lines.extend(adapter.specifics)
        lines.append("")

    return "\n".join(lines)


# --------------------------------------------------------------------------
# Plan, diff, write
# --------------------------------------------------------------------------

def plan(repo: Path) -> dict[str, str]:
    contract = repo / CONTRACT
    if not contract.is_file():
        raise SystemExit(f"{GENERATOR}: no {CONTRACT} under {repo}")
    sections = parse_contract(contract.read_text(encoding="utf-8"))
    return {a.path: render(a, sections) for a in sorted(ADAPTERS, key=lambda a: a.path)}


def diff(repo: Path) -> list[str]:
    """Routers whose content differs from the contract."""
    drifted: list[str] = []
    for rel, content in sorted(plan(repo).items()):
        path = repo / rel
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != content:
            drifted.append(rel)
    return drifted


def write(repo: Path) -> list[str]:
    written: list[str] = []
    for rel, content in sorted(plan(repo).items()):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        current = path.read_text(encoding="utf-8") if path.is_file() else None
        if current != content:
            path.write_text(content, encoding="utf-8", newline="\n")
            written.append(rel)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="render_routers")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list", action="store_true", dest="do_list")
    args = parser.parse_args(argv)

    repo = Path(args.root).resolve()

    if args.do_list:
        for adapter in sorted(ADAPTERS, key=lambda a: a.path):
            marker = "tool-specific" if adapter.specifics else "shared only"
            print(f"{adapter.path:40} {adapter.tool:32} {marker}")
        print(f"\n{len(ADAPTERS)} routers rendered from {CONTRACT}")
        return 0

    if not (repo / CONTRACT).is_file():
        print(f"no {CONTRACT} under {repo}", file=sys.stderr)
        return 2

    if args.write:
        written = write(repo)
        for rel in written:
            print(f"wrote   {rel}")
        if not written:
            print(f"all {len(ADAPTERS)} routers already match the contract")
        return 0

    drifted = diff(repo)
    for rel in drifted:
        print(f"drifted {rel}")
    if drifted:
        print(
            f"\n{len(drifted)} of {len(ADAPTERS)} router(s) differ from "
            f"{CONTRACT}.\nFix with: python {GENERATOR} --write"
        )
        return 1

    print(f"all {len(ADAPTERS)} routers match the contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

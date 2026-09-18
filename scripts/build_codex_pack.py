#!/usr/bin/env python3
"""Generate the portable pack - Akinator's one skill, for Codex and Cursor.

Akinator is ONE skill. The canonical copy is `skills/everything/` - its
`SKILL.md`, its station `references/` and its host-repo tools in `scripts/`.
Claude Code loads it straight from the plugin, where it is `/akinator:everything`.

This script projects that same skill into the places Codex and Cursor read, plus
the always-on contract each of them needs because neither has Claude's
SessionStart hook:

    .agents/skills/akinator/          the one skill - SKILL.md, references/,
                                      scripts/. Codex AND Cursor both load skills
                                      from .agents/skills (repo) and
                                      ~/.agents/skills (user), so one folder
                                      serves both: $akinator on Codex, /akinator
                                      on Cursor.
    .agents/AGENTS.md                 the portable always-on contract. The
                                      installer merges it, as a marked block,
                                      into ~/.codex/AGENTS.md or a repo's
                                      AGENTS.md - which Cursor reads too.
    .agents/cursor/akinator.mdc       the same contract as an alwaysApply Cursor
                                      rule, for ~/.cursor/rules.

This repository's own AGENTS.md is NOT generated here - it is one of eleven
routers rendered from context/router-contract.md by scripts/render_routers.py.

**Why one skill, not twenty-one.** Codex has no way to hide a skill from its `$`
picker (a skill's `allow_implicit_invocation: false` hides it from the model,
not from the user), and every folder under .agents/skills is also a `/` entry in
Cursor. Twenty-one skills meant twenty-one entries on every platform, for a
plugin whose owner asked for exactly one. See
docs/adr/0009-one-skill-one-command-one-installer.md.

Everything here is a build output. Editing it by hand is a rule violation - see
rules/07-codex-pack-is-generated.md. Generation is deterministic: the same
source produces byte-identical output, which is what makes the drift check
meaningful.

Usage:
    python scripts/build_codex_pack.py            # dry run, report what differs
    python scripts/build_codex_pack.py --write    # write the pack
    python scripts/build_codex_pack.py --check    # exit 1 if the tree is drifted

Exit codes:
    0  the pack matches the canonical skill (or --write succeeded)
    1  drift detected (--check), or files would change (default dry run)
    2  the generator could not run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_SOURCE = "skills/everything"
# Outside Claude there is no plugin namespace, so the name has to carry it:
# `everything` alone would be an ambiguous `$everything` in a shared skills
# folder. Claude's `/akinator:everything` and this `akinator` are the same skill.
PORTABLE_NAME = "akinator"
TARGET = f".agents/skills/{PORTABLE_NAME}"
CONTRACT = ".agents/AGENTS.md"
CURSOR_RULE = ".agents/cursor/akinator.mdc"
PACK_ROOTS = (".agents/skills", ".agents/cursor", CONTRACT)

# Frontmatter keys that mean something to Claude Code only. Codex ignores
# unknown keys, but a projection that carries dead keys invites someone to rely
# on them.
CLAUDE_ONLY_KEYS = ("argument-hint",)


def banner(what: str) -> str:
    """The pack banner for markdown. No timestamp - see the module docstring.

    Names **no path and no filename**. Every file in the pack is copied into
    other repositories, where a path to the generator, the source or a rule does
    not exist; naming one made each installed file assert something untrue
    about its host - the defect rules/12 exists to stop. So the banner gives the
    two things a vendored file owes its reader: where it came from, and how to
    get a fresh copy.
    """
    return (
        "<!--\n"
        "DO NOT EDIT BY HAND.\n"
        f"Installed from the Akinator plugin - {what}.\n"
        "No generator is named by path: this file travels into repositories\n"
        "that do not have one, where naming it would be a false claim.\n"
        "To update: reinstall Akinator, or regenerate inside an Akinator\n"
        "checkout. Local edits here are replaced either way.\n"
        "-->\n"
    )


def code_banner() -> str:
    """The same banner for the Python tools, as comments."""
    return (
        "# DO NOT EDIT BY HAND. Installed from the Akinator plugin - one of the\n"
        "# tools of its one skill. To update: reinstall Akinator, or regenerate\n"
        "# inside an Akinator checkout. Local edits here are replaced.\n"
    )


def contract_banner() -> str:
    """Banner for the portable contract. Names no path and no filename."""
    return "\n".join([
        "<!--",
        "Akinator behavioral contract - DO NOT EDIT BY HAND.",
        "",
        "Installed from the Akinator plugin. No generator is named by path or",
        "by filename: this file travels into repositories that have neither,",
        "where naming one would assert a file that is not in the tree.",
        "",
        "To update: reinstall Akinator, or regenerate inside an Akinator",
        "checkout. Local edits here are replaced - keep this repository's own",
        "content in its own router.",
        "-->",
        "",
    ])


def frontmatter_and_body(text: str) -> tuple[str, str]:
    """Split a SKILL.md into its frontmatter block and the rest."""
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    close = text.find("\n", end + 1)
    return text[: close + 1], text[close + 1 :]


def render_skill(text: str) -> str:
    """Project the one canonical skill into its portable form.

    Two transformations, both deliberate and nothing else: the name becomes
    `akinator` (see PORTABLE_NAME), and Claude-only keys are dropped. The banner
    goes *after* the frontmatter - a comment before the opening `---` would stop
    it being parsed as frontmatter at all.
    """
    front, body = frontmatter_and_body(text)
    if not front:
        raise ValueError(f"{SKILL_SOURCE}/SKILL.md has no frontmatter")
    lines = []
    for line in front.splitlines():
        if line.startswith("name:"):
            lines.append(f"name: {PORTABLE_NAME}")
        elif line.split(":", 1)[0] in CLAUDE_ONLY_KEYS:
            continue
        else:
            lines.append(line)
    return ("\n".join(lines) + "\n"
            + banner("its one skill, which Claude Code calls /akinator:everything")
            + body)


def render_tool(text: str) -> str:
    """A tool, with the banner as comments - after the shebang, which must stay
    on line 1 for the file to remain directly executable."""
    if text.startswith("#!"):
        first, rest = text.split("\n", 1)
        return first + "\n" + code_banner() + rest
    return code_banner() + text


def render_contract_body() -> str:
    """The contract itself, without banner or frontmatter.

    Names **no repository-specific paths**: it is installed into repositories
    and home directories Akinator has never seen. It carries the creed, the loop
    and the non-negotiables - true everywhere - and tells the agent to discover
    the knowledge layer this particular repository actually has.
    """
    return "\n".join([
        "# Akinator — ALWAYS ON",
        "",
        "Ask everything. Document everything. Skillify everything. Rule everything.",
        "",
        "A change is never the code alone. A change is the code plus the knowledge that lets",
        "the next agent act on it in seconds. Half a change is no change.",
        "",
        "## The loop",
        "",
        "Every user prompt enters this contract first. For repository-changing work, load",
        "Akinator's one skill, `akinator`, and run its complete pass - all twelve stations:",
        "",
        "```",
        "ASK -> RESOLVE -> AUDIT -> PLAN -> IMPLEMENT -> DOCUMENT ->",
        "SKILLIFY -> RULE -> CONTEXTIFY -> MEMOIZE -> INDEX+SYNC -> VERIFY",
        "```",
        "",
        "Each station is a reference file inside that skill, opened when the work reaches",
        "it, and the skill's tools live in its own `scripts` folder. There is nothing else",
        "to install and nothing to type: the explicit form - `$akinator` on Codex,",
        "`/akinator` on Cursor, `/akinator:everything` on Claude Code - is a fallback.",
        "",
        "Non-negotiable:",
        "",
        "- Stations 6-11 happen in the same batch as station 5. \"I'll document in a",
        "  follow-up\" is a prohibited sentence.",
        "- The knowledge delta is declared at PLAN time, **by path**, per batch. A batch",
        "  with no knowledge delta states why, explicitly.",
        "- Gate once, at the end, scoped to what was touched. Never per edit, never per",
        "  commit, never all-workspace.",
        "- Never add knowledge or documentation checks to git hooks. Hooks gate code.",
        "- **Adopt, never impose.** Match this repository's existing conventions before",
        "  creating anything. A parallel structure beside an existing one is worse than",
        "  no structure - the agent picks the wrong one half the time.",
        "- Never guess on money, permissions, deletion, security or public contracts.",
        "  Stop, ask, and write the answer down before coding past it.",
        "",
        "## Station 2 - RESOLVE, before anything",
        "",
        "Discover what this repository actually has, then read it in this order,",
        "stopping when your question is answered:",
        "",
        "```",
        "routers   CLAUDE.md, AGENTS.md, CODEX.md, and any per-module ones",
        "rules     constraints you may not break",
        "skills    runbooks - follow one rather than improvising",
        "context   structural facts: ownership, routes, events, permissions",
        "memory    durable decisions, preferences, surprises",
        "docs      architecture, business, product, ops, decision records",
        "```",
        "",
        "Those are the conventional homes, not a promise about this repo. Look first;",
        "this repository may use different names, and if it does, **its** names win.",
        "",
        "If none of them exist, say so rather than inventing a structure, and onboard",
        "the repository properly - the `akinator` skill carries the onboarding station.",
        "",
    ])


def render_contract_md() -> str:
    return contract_banner() + render_contract_body()


def render_cursor_rule() -> str:
    """The contract as an always-applied Cursor rule. Frontmatter first - Cursor
    parses it only at the top of the file - then the banner."""
    return ("---\n"
            "description: Akinator - the always-on repository contract\n"
            "alwaysApply: true\n"
            "---\n"
            + contract_banner()
            + render_contract_body())


def _files(directory: Path, pattern: str) -> list[Path]:
    """Sorted, deterministic, and never a cache directory."""
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.glob(pattern)
                  if p.is_file() and "__pycache__" not in p.parts)


def plan(repo: Path) -> dict[str, str]:
    """The full desired content of the pack, keyed by repo-relative path."""
    source = repo / SKILL_SOURCE
    skill_md = source / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"{SKILL_SOURCE}/SKILL.md is missing")

    out: dict[str, str] = {}
    out[f"{TARGET}/SKILL.md"] = render_skill(
        skill_md.read_text(encoding="utf-8"))
    for ref in _files(source / "references", "*.md"):
        out[f"{TARGET}/references/{ref.name}"] = (
            banner(f"a station reference of its one skill ({ref.stem})")
            + ref.read_text(encoding="utf-8"))
    for tool in _files(source / "scripts", "*.py"):
        out[f"{TARGET}/scripts/{tool.name}"] = render_tool(
            tool.read_text(encoding="utf-8"))
    out[CONTRACT] = render_contract_md()
    out[CURSOR_RULE] = render_cursor_rule()
    return out


def existing_pack(repo: Path) -> set[str]:
    """Every file currently in the generated pack."""
    found: set[str] = set()
    for root in PACK_ROOTS:
        path = repo / root
        if path.is_file():
            found.add(root)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and "__pycache__" not in child.parts:
                    found.add(child.relative_to(repo).as_posix())
    return found


def diff(repo: Path) -> tuple[list[str], list[str], list[str]]:
    """(changed, missing, extra) repo-relative paths."""
    desired = plan(repo)
    present = existing_pack(repo)

    changed: list[str] = []
    missing: list[str] = []
    for rel, content in sorted(desired.items()):
        path = repo / rel
        if not path.is_file():
            missing.append(rel)
        elif path.read_text(encoding="utf-8", errors="replace") != content:
            changed.append(rel)

    extra = sorted(present - set(desired))
    return changed, missing, extra


def write(repo: Path) -> tuple[list[str], list[str]]:
    """Write the pack. Returns (written, removed)."""
    desired = plan(repo)
    present = existing_pack(repo)

    written: list[str] = []
    for rel, content in sorted(desired.items()):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        current = (path.read_text(encoding="utf-8", errors="replace")
                   if path.is_file() else None)
        if current != content:
            path.write_text(content, encoding="utf-8", newline="\n")
            written.append(rel)

    removed: list[str] = []
    for rel in sorted(present - set(desired)):
        (repo / rel).unlink()
        removed.append(rel)

    # Prune every directory the removal emptied, deepest first, so a removed
    # skill - or all twenty of the old per-station ones - leaves nothing behind.
    for root in PACK_ROOTS:
        base = repo / root
        if not base.is_dir():
            continue
        for path in sorted((p for p in base.rglob("*") if p.is_dir()),
                           key=lambda p: len(p.parts), reverse=True):
            if not any(path.iterdir()):
                path.rmdir()

    return written, removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build_codex_pack",
        description="Generate the portable pack from Akinator's one skill.",
    )
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--write", action="store_true",
                        help="write the pack to disk")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the pack is drifted; write nothing")
    args = parser.parse_args(argv)

    repo = Path(args.root).resolve()
    if not (repo / SKILL_SOURCE / "SKILL.md").is_file():
        print(f"no {SKILL_SOURCE}/SKILL.md under {repo}", file=sys.stderr)
        return 2

    if args.write:
        written, removed = write(repo)
        for rel in written:
            print(f"wrote   {rel}")
        for rel in removed:
            print(f"removed {rel}")
        if not written and not removed:
            print("pack already up to date")
        return 0

    changed, missing, extra = diff(repo)
    for rel in missing:
        print(f"missing {rel}")
    for rel in changed:
        print(f"changed {rel}")
    for rel in extra:
        print(f"extra   {rel}")

    if changed or missing or extra:
        total = len(changed) + len(missing) + len(extra)
        print(f"\n{total} file(s) differ from the canonical skill - "
              "the portable pack is drifted.")
        print("Fix with: python scripts/build_codex_pack.py --write")
        return 1

    print("Portable pack matches the canonical skill.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

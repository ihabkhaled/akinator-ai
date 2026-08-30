#!/usr/bin/env python3
"""Generate the Codex pack from the canonical Claude skills.

The Claude skills in `skills/` are canonical. This script projects them into the
locations Codex actually reads:

    .agents/skills/<name>/SKILL.md   the skills, per the Codex skills contract
    .agents/AGENTS.md                the portable behavioral contract, which the
                                     installer copies into target repositories

This repository's own AGENTS.md is NOT generated here - it is one of eleven
routers rendered from context/router-contract.md by scripts/render_routers.py.

Both are build outputs. Editing them by hand is a rule violation - see
rules/07-codex-pack-is-generated.md - because two hand-maintained copies of one
behavioral contract diverge invisibly, which is the exact failure Akinator
exists to prevent.

Generation is deterministic: the same `skills/` tree produces byte-identical
output. No clock, no absolute paths, no unordered iteration. Determinism is what
makes the drift check meaningful; a generator that emits a timestamp produces a
diff on every run, so the drift check becomes noise and gets disabled.

Usage:
    python scripts/build_codex_pack.py            # dry run, report what differs
    python scripts/build_codex_pack.py --write    # write the pack
    python scripts/build_codex_pack.py --check    # exit 1 if the tree is drifted

Exit codes:
    0  the pack matches the canonical skills (or --write succeeded)
    1  drift detected (--check), or files would change (default dry run)
    2  the generator could not run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

GENERATOR = "scripts/build_codex_pack.py"

# Skills that exist only to serve the Claude harness and have no Codex meaning
# would be listed here. Empty by design: the behavioral contract is identical
# across platforms, and any divergence must be a documented transformation.
CLAUDE_ONLY: frozenset[str] = frozenset()


def banner(skill_name: str) -> str:
    """The pack banner. No timestamp - see the module docstring.

    Names **no repo-relative paths**, for the same reason `contract_banner`
    does not - and it took a behavioral eval to notice that only one of the two
    had been given that treatment. Every file in this pack is copied verbatim
    into other repositories by the installer, where `scripts/build_codex_pack.py`
    and `skills/<name>/SKILL.md` do not exist. Naming them made each installed
    file assert something untrue about its host, and a doc asserting things that
    are not there is precisely what this plugin rates critical. Installing
    Akinator used to produce 22 HIGH coverage findings in the target repository
    on the very first run.

    So the banner gives the two things a vendored file actually owes its reader:
    where it came from, and how to get a fresh copy. Inside an Akinator checkout
    the canonical skill is the one of the same name, and the regeneration
    command lives in the rule that governs it - not stamped as a path into
    twenty-one copies that travel elsewhere.
    """
    return (
        "<!--\n"
        "DO NOT EDIT BY HAND.\n"
        f"Installed from the Akinator plugin - the canonical {skill_name} "
        "skill.\n"
        "No generator is named by path: this file travels into repositories\n"
        "that do not have one, where naming it would be a false claim.\n"
        "To update: reinstall Akinator, or regenerate inside an Akinator\n"
        "checkout. Local edits here are replaced either way.\n"
        "-->\n"
    )


def contract_banner() -> str:
    """Banner for the portable contract.

    Names **no repo-relative paths** and no generator filename either. The
    filename was the subtler half: `build_codex_pack.py` is not a path, but it
    is still a file the target repository does not have, so the coverage check
    read it as a generator that had gone missing.
    """
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


def render_skill(skill_name: str, text: str) -> str:
    """Project a canonical skill into its Codex form.

    The Codex skills contract is the same shape as Claude's - `SKILL.md` with
    `name` and `description` frontmatter - so the transformation is the banner
    only. The banner goes *after* the frontmatter: a comment before the opening
    `---` would stop it being parsed as frontmatter at all.

    It takes the skill's *name*, not its source path, because the rendered file
    travels: see `banner`.
    """
    front, body = frontmatter_and_body(text)
    if not front:
        return banner(skill_name) + text
    return front + banner(skill_name) + body


def discover(skills_root: Path) -> list[tuple[str, Path]]:
    """Every canonical skill, as (name, path), in sorted order."""
    out: list[tuple[str, Path]] = []
    if not skills_root.is_dir():
        return out
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        name = skill_md.parent.name
        if name in CLAUDE_ONLY:
            continue
        out.append((name, skill_md))
    return out


def render_contract_md(skills: list[tuple[str, Path]]) -> str:
    """The **portable** contract, installed into a target repository.

    This is not the same file as Akinator's own root `AGENTS.md`, and confusing
    the two was a real bug: the installer copied Akinator's router into target
    repos, giving them five dead links to `rules/README.md`, `docs/skills.md` and
    friends, plus an instruction to run Akinator's test suite. A doc asserting
    things that are not there is the failure this plugin rates critical, and it
    was being installed by the plugin itself.

    So this file names **no repository-specific paths**. It carries the creed,
    the loop and the non-negotiables - which are true everywhere - and tells the
    agent to discover the knowledge layer that this particular repo actually has.
    """
    lines: list[str] = []
    lines.append(contract_banner())
    lines.append("# Akinator")
    lines.append("")
    lines.append(
        "Ask everything. Document everything. Skillify everything. "
        "Rule everything."
    )
    lines.append("")
    lines.append(
        "A change is never the code alone. A change is the code plus the "
        "knowledge that lets"
    )
    lines.append("the next agent act on it in seconds. Half a change is no change.")
    lines.append("")
    lines.append("## The loop")
    lines.append("")
    lines.append("Run every codebase touch through twelve stations:")
    lines.append("")
    lines.append("```")
    lines.append("ASK -> RESOLVE -> AUDIT -> PLAN -> IMPLEMENT -> DOCUMENT ->")
    lines.append("SKILLIFY -> RULE -> CONTEXTIFY -> MEMOIZE -> INDEX+SYNC -> VERIFY")
    lines.append("```")
    lines.append("")
    lines.append("Non-negotiable:")
    lines.append("")
    lines.append(
        "- Stations 6-11 happen in the same batch as station 5. "
        '"I\'ll document in a'
    )
    lines.append('  follow-up" is a prohibited sentence.')
    lines.append(
        "- The knowledge delta is declared at PLAN time, **by path**, per batch. "
        "A batch"
    )
    lines.append("  with no knowledge delta states why, explicitly.")
    lines.append(
        "- Gate once, at the end, scoped to what was touched. Never per edit, "
        "never per"
    )
    lines.append("  commit, never all-workspace.")
    lines.append(
        "- Never add knowledge or documentation checks to git hooks. "
        "Hooks gate code."
    )
    lines.append(
        "- **Adopt, never impose.** Match this repository's existing conventions "
        "before"
    )
    lines.append(
        "  creating anything. A parallel structure beside an existing one is "
        "worse than"
    )
    lines.append("  no structure - the agent picks the wrong one half the time.")
    lines.append(
        "- Never guess on money, permissions, deletion or public contracts. "
        "Stop, ask,"
    )
    lines.append("  and write the answer down before coding past it.")
    lines.append("")
    lines.append("## Station 2 - RESOLVE, before anything")
    lines.append("")
    lines.append(
        "Discover what this repository actually has, then read it in this order,"
    )
    lines.append("stopping when your question is answered:")
    lines.append("")
    lines.append("```")
    lines.append("routers   CLAUDE.md, AGENTS.md, CODEX.md, and any per-module ones")
    lines.append("rules     constraints you may not break")
    lines.append("skills    runbooks - follow one rather than improvising")
    lines.append("context   structural facts: ownership, routes, events, permissions")
    lines.append("memory    durable decisions, preferences, surprises")
    lines.append("docs      architecture, business, product, ops, decision records")
    lines.append("```")
    lines.append("")
    lines.append(
        "Those are the conventional homes, not a promise about this repo. Look "
        "first;"
    )
    lines.append(
        "this repository may use different names, and if it does, **its** names "
        "win."
    )
    lines.append("")
    lines.append(
        "If none of them exist, say so rather than inventing a structure, and "
        "offer to"
    )
    lines.append("onboard the repository properly.")
    lines.append("")
    lines.append("## Skills")
    lines.append("")
    lines.append(
        "Installed under `.agents/skills/`. Invoke one explicitly with "
        "`$<name>`, or"
    )
    lines.append("describe the task and let the skill be selected by its trigger.")
    lines.append("")
    lines.append("| Skill | Use when |")
    lines.append("|---|---|")
    for name, path in skills:
        lines.append(f"| `{name}` | {_description_of(path)} |")
    lines.append("")
    lines.append(
        "Start with `$akinator` - it carries the full creed, the loop and the"
    )
    lines.append("knowledge taxonomy, and routes to the rest.")
    lines.append("")
    return "\n".join(lines)


def _description_of(skill_md: Path) -> str:
    """The skill's trigger description, flattened to one table cell."""
    front, _ = frontmatter_and_body(
        skill_md.read_text(encoding="utf-8", errors="replace")
    )
    collecting = False
    parts: list[str] = []
    for line in front.splitlines():
        if line.startswith("description:"):
            collecting = True
            parts.append(line[len("description:") :].strip())
            continue
        if collecting:
            if not line.startswith((" ", "\t")) or line.strip().endswith(":"):
                break
            parts.append(line.strip())
    text = " ".join(p for p in parts if p).strip().strip("|>").strip()
    text = text.replace("|", "/")
    # Trim to the first sentence - the table is an index, not the skill.
    for stop in (". Runs", ". Turns", ". Produces", ". Writes", ". Routes"):
        if stop in text:
            text = text.split(stop, 1)[0] + "."
            break
    return text or "(no description)"


def plan(repo: Path) -> dict[str, str]:
    """The full desired content of the pack, keyed by repo-relative path."""
    skills = discover(repo / "skills")
    out: dict[str, str] = {}
    for name, path in skills:
        target = f".agents/skills/{name}/SKILL.md"
        out[target] = render_skill(
            name, path.read_text(encoding="utf-8", errors="replace")
        )
    # NOTE: this repository's own AGENTS.md is NOT generated here. It is one of
    # eleven routers rendered from context/router-contract.md by
    # scripts/render_routers.py. Two generators writing one file is a fork with
    # extra steps.
    #
    # What the pack owns is the *portable* contract - the file the installer
    # copies into OTHER repositories, which names no repo-relative paths.
    out[".agents/AGENTS.md"] = render_contract_md(skills)
    return out


def existing_pack(repo: Path) -> set[str]:
    """Every file currently in the generated pack."""
    found: set[str] = set()
    agents_skills = repo / ".agents" / "skills"
    if agents_skills.is_dir():
        for path in agents_skills.rglob("*"):
            if path.is_file():
                found.add(path.relative_to(repo).as_posix())
    if (repo / ".agents" / "AGENTS.md").is_file():
        found.add(".agents/AGENTS.md")
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
        current = (
            path.read_text(encoding="utf-8", errors="replace")
            if path.is_file()
            else None
        )
        if current != content:
            path.write_text(content, encoding="utf-8", newline="\n")
            written.append(rel)

    removed: list[str] = []
    for rel in sorted(present - set(desired)):
        (repo / rel).unlink()
        removed.append(rel)

    # Prune directories the removal emptied, so a renamed skill leaves nothing.
    agents_skills = repo / ".agents" / "skills"
    if agents_skills.is_dir():
        for path in sorted(agents_skills.iterdir(), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()

    return written, removed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="build_codex_pack",
        description="Generate the Codex pack from the canonical Claude skills.",
    )
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--write", action="store_true",
                        help="write the pack to disk")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if the pack is drifted; write nothing")
    args = parser.parse_args(argv)

    repo = Path(args.root).resolve()
    if not (repo / "skills").is_dir():
        print(f"no skills/ directory under {repo}", file=sys.stderr)
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
        print(
            f"\n{total} file(s) differ from the canonical skills - "
            "the Codex pack is drifted."
        )
        print("Fix with: python scripts/build_codex_pack.py --write")
        return 1

    print("Codex pack matches the canonical skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

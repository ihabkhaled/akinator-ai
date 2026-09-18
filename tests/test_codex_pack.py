"""Tests for the portable pack generator - Akinator's one skill, for Codex and
Cursor, plus the always-on contract and the Cursor rule.

The pack is a build output. These tests protect what makes that safe: it is
**deterministic** (so the drift check is meaningful), **not drifted** (so every
platform ships the same skill), **one skill** (so every platform shows one
entry), and **true where it lands** (so installing Akinator never makes a host
repository assert things that are not there).

`test_pack_is_not_drifted` and `test_generation_is_deterministic` are named
directly by rules/07-codex-pack-is-generated.md as its enforcement mechanism.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest

import build_codex_pack as pack

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build_codex_pack.py"
SKILL = f"{pack.TARGET}/SKILL.md"
CONTRACT = pack.CONTRACT


@pytest.fixture
def sandbox(tmp_path: Path, repo: Path) -> Path:
    """A copy of the canonical skill, with no generated pack yet."""
    root = tmp_path / "sandbox"
    root.mkdir()
    shutil.copytree(repo / "skills", root / "skills",
                    ignore=shutil.ignore_patterns("__pycache__"))
    return root


# --------------------------------------------------------------------------
# The rules' named enforcement
# --------------------------------------------------------------------------

def test_pack_is_not_drifted(repo: Path) -> None:
    """Enforcement for rules/07: the shipped pack matches the canonical skill."""
    changed, missing, extra = pack.diff(repo)
    assert not (changed or missing or extra), (
        f"the portable pack is drifted.\nchanged={changed}\nmissing={missing}\n"
        f"extra={extra}\nFix: python scripts/build_codex_pack.py --write"
    )


def test_generation_is_deterministic(sandbox: Path) -> None:
    """Enforcement for rules/07: same tree in, byte-identical output out."""
    assert pack.plan(sandbox) == pack.plan(sandbox)

    def snapshot() -> dict[str, bytes]:
        return {p.relative_to(sandbox).as_posix(): p.read_bytes()
                for p in sorted(sandbox.rglob("*")) if p.is_file()}

    pack.write(sandbox)
    first = snapshot()
    pack.write(sandbox)
    assert first == snapshot()


def test_generated_output_contains_no_clock_or_absolute_paths(repo: Path) -> None:
    """A timestamp makes every run a diff, which kills the drift check."""
    for rel, content in pack.plan(repo).items():
        assert "2026-" not in content.split("-->")[0], (
            f"{rel}: generated banner must not contain a date")
        for absolute in ("/Users/", "/home/", "C:\\", "D:\\"):
            assert absolute not in content, f"{rel}: absolute path in output"


# --------------------------------------------------------------------------
# One skill
# --------------------------------------------------------------------------

def test_the_pack_holds_exactly_one_skill(repo: Path) -> None:
    """Codex cannot hide a skill from its `$` picker, and Cursor lists every
    folder in .agents/skills - so one skill folder is one entry, and anything
    more is the 21-entry menu this layout exists to end."""
    skills = sorted({rel.split("/")[2] for rel in pack.plan(repo)
                     if rel.startswith(".agents/skills/")})
    assert skills == [pack.PORTABLE_NAME]
    assert sum(rel.endswith("SKILL.md") for rel in pack.plan(repo)) == 1


def test_the_whole_skill_is_projected(repo: Path) -> None:
    """Every reference and every tool travels - a station the pack drops is a
    station an installed agent can never open."""
    plan = pack.plan(repo)
    source = repo / pack.SKILL_SOURCE
    for ref in sorted((source / "references").glob("*.md")):
        assert f"{pack.TARGET}/references/{ref.name}" in plan, ref.name
    for tool in sorted((source / "scripts").glob("*.py")):
        assert f"{pack.TARGET}/scripts/{tool.name}" in plan, tool.name
    assert not any("__pycache__" in rel for rel in plan)


def test_the_projection_renames_and_keeps_the_trigger(repo: Path) -> None:
    """Two deliberate transformations and nothing else: the portable name, and
    no Claude-only keys. The description - the trigger - is untouched."""
    source = (repo / pack.SKILL_SOURCE / "SKILL.md").read_text("utf-8")
    projected = pack.plan(repo)[SKILL]

    def key(text: str, name: str) -> list[str]:
        return [l for l in text.splitlines() if l.startswith(f"{name}:")]

    assert key(projected, "name") == [f"name: {pack.PORTABLE_NAME}"]
    assert key(projected, "description") == key(source, "description")
    for dropped in pack.CLAUDE_ONLY_KEYS:
        assert not key(projected, dropped), f"{dropped} leaked into the portable skill"


def test_banner_follows_the_frontmatter(repo: Path) -> None:
    """A comment before the opening --- would stop frontmatter parsing."""
    content = pack.plan(repo)[SKILL]
    assert content.startswith("---\n")
    banner_at = content.find("DO NOT EDIT BY HAND")
    assert banner_at != -1, "banner is missing"
    assert content.find("\n---", 3) < banner_at, "banner must follow the frontmatter"


def test_tools_keep_their_shebang_on_line_one(repo: Path) -> None:
    for rel, content in pack.plan(repo).items():
        if rel.endswith(".py"):
            source = (repo / pack.SKILL_SOURCE / "scripts" / Path(rel).name).read_text("utf-8")
            if source.startswith("#!"):
                assert content.split("\n", 1)[0] == source.split("\n", 1)[0], rel
            assert "DO NOT EDIT BY HAND" in content, f"{rel}: no banner"


def test_cursor_rule_is_always_applied(repo: Path) -> None:
    rule = pack.plan(repo)[pack.CURSOR_RULE]
    front = rule.split("---", 2)[1]
    assert "alwaysApply: true" in front
    assert rule.startswith("---\n"), "Cursor parses frontmatter only at the top"


# --------------------------------------------------------------------------
# True where it lands - rules/12
# --------------------------------------------------------------------------

def test_pack_banners_name_no_file_the_host_repo_will_not_have(repo: Path) -> None:
    """The banner travels with the file, so every path in it is a claim about
    whatever repository the file ends up in - and a bare filename is not a path
    but is still a file the host repo does not have."""
    for rel, content in pack.plan(repo).items():
        banner = content[content.find("<!--"): content.find("-->") + 3]
        named = re.findall(r"`([A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,8})`", banner)
        assert not named, f"{rel}: banner names {named}, absent where it lands"


def _resolves_inside_the_pack(rel: str, token: str, plan: dict[str, str]) -> bool:
    """A path relative to the file itself, or to the skill via `<skill>/`, that
    lands on another file of the pack. Those travel with the file, so they are
    true wherever it is installed - unlike a path into Akinator's checkout."""
    if token.startswith("<skill>/"):
        candidate = PurePosixPath(pack.TARGET) / token[len("<skill>/"):]
    else:
        candidate = PurePosixPath(rel).parent / token
    parts: list[str] = []
    for part in candidate.parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part != ".":
            parts.append(part)
    return "/".join(parts) in plan


def test_pack_bodies_name_no_path_the_host_repo_will_not_have(repo: Path) -> None:
    """The body travels too, and it was the larger half of the problem.

    Fixing the banners left twenty path references in eleven skill bodies -
    `templates/adr.md`, `rules/05-no-git-hook-complication.md`,
    `evals/newcomer/README.md` - each a file that exists only in an Akinator
    checkout, inside a document whose purpose is to be read somewhere else.

    Allowed: a path that resolves to another file **of the pack**, relative to
    the file itself (`../SKILL.md`, `references/procedure.md`) or to the skill
    (`<skill>/scripts/akinator_ledger.py`). It travels with the file, so it is
    true wherever the file lands.

    Fenced blocks are exempt as illustrative. A directory only an Akinator
    checkout contains - `templates/`, `evals/` - is checked by bare name too.
    """
    fence = re.compile(r"^[ \t]*```.*?^[ \t]*```[ \t]*$", re.MULTILINE | re.DOTALL)
    token = re.compile(r"`([A-Za-z0-9_./<>\\-]+\.[A-Za-z0-9]{1,8})`")
    akinator_only_dir = re.compile(r"`((?:templates|evals)/[A-Za-z0-9_./\\-]*)`")

    plan = pack.plan(repo)
    offenders: dict[str, list[str]] = {}
    for rel, content in plan.items():
        if rel.endswith(".py"):
            continue
        body = fence.sub("\n", content[content.find("-->") + 3:])
        # A `<placeholder>/...` token is illustrative - except `<skill>/`,
        # which names a real file of the pack and must resolve.
        named = sorted({t for t in token.findall(body) if "/" in t
                        and not (t.startswith("<") and not t.startswith("<skill>/"))
                        and not _resolves_inside_the_pack(rel, t, plan)})
        named += sorted(set(akinator_only_dir.findall(body)))
        if named:
            offenders[rel] = sorted(set(named))

    assert not offenders, (
        "packed files name paths that will not exist where they are installed: "
        + "; ".join(f"{k} -> {v}" for k, v in sorted(offenders.items())))


def test_every_markdown_link_in_the_pack_resolves_inside_it(repo: Path) -> None:
    """The one skill's station table is made of links. A link that does not
    resolve inside the pack is a station an installed agent cannot open."""
    fence = re.compile(r"^[ \t]*```.*?^[ \t]*```[ \t]*$", re.MULTILINE | re.DOTALL)
    plan = pack.plan(repo)
    broken: list[str] = []
    for rel, content in plan.items():
        if not rel.endswith((".md", ".mdc")):
            continue
        # Links inside fenced examples are illustrations, not navigation.
        for target in re.findall(r"\]\(([^)\s#]+)\)", fence.sub("", content)):
            if "://" in target:
                continue
            if not _resolves_inside_the_pack(rel, target, plan):
                broken.append(f"{rel} -> {target}")
    assert not broken, "links that leave the pack:\n" + "\n".join(broken)


def test_the_installed_pack_leaves_a_target_repo_clean(repo: Path, tmp_path: Path) -> None:
    """Regression, found by eval 06: installing Akinator used to give a bare
    repository 22 HIGH coverage findings on its first run, because every test
    read the pack from inside this checkout, where every path resolves. This one
    reads it from where it lands. The installer tests do the same through the
    real installers."""
    import akinator_coverage as cov

    target = tmp_path / "host"
    (target / "src").mkdir(parents=True)
    (target / "README.md").write_text("# Host repo\n", encoding="utf-8")
    (target / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")

    landing = {CONTRACT: "AGENTS.md", pack.CURSOR_RULE: ".cursor/rules/akinator.mdc"}
    for rel, text in pack.plan(repo).items():
        dest = target / landing.get(rel, rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")

    findings = cov.run_checks(cov.Repo(target), [], [], 40)
    loud = [f for f in findings if f.severity in ("critical", "high", "medium")]
    assert not loud, "installing the pack dirties the host repo: " + "; ".join(
        f"{f.check} {f.path}: {f.message}" for f in loud[:5])


# --------------------------------------------------------------------------
# Write, prune and drift detection
# --------------------------------------------------------------------------

def test_write_creates_the_pack(sandbox: Path) -> None:
    written, removed = pack.write(sandbox)
    assert written and not removed
    assert (sandbox / CONTRACT).is_file()
    assert (sandbox / SKILL).is_file()
    assert (sandbox / pack.CURSOR_RULE).is_file()


def test_write_is_idempotent(sandbox: Path) -> None:
    pack.write(sandbox)
    assert pack.write(sandbox) == ([], [])


def test_a_removed_reference_is_pruned_from_the_pack(sandbox: Path) -> None:
    pack.write(sandbox)
    (sandbox / pack.SKILL_SOURCE / "references" / "akinator-adr.md").unlink()
    _, removed = pack.write(sandbox)
    assert f"{pack.TARGET}/references/akinator-adr.md" in removed


def test_the_old_per_station_skills_are_pruned(sandbox: Path) -> None:
    """Upgrading from the 21-skill layout must leave one skill, not 22."""
    old = sandbox / ".agents" / "skills" / "akinator-plan"
    old.mkdir(parents=True)
    (old / "SKILL.md").write_text("---\nname: akinator-plan\n---\n", encoding="utf-8")
    pack.write(sandbox)
    assert not old.exists(), "an emptied old skill directory must be pruned"
    assert sorted(p.name for p in (sandbox / ".agents" / "skills").iterdir()) == ["akinator"]


def test_hand_edit_is_detected_as_drift(sandbox: Path) -> None:
    pack.write(sandbox)
    target = sandbox / SKILL
    target.write_text(target.read_text("utf-8") + "\nhand edit\n", encoding="utf-8")
    assert SKILL in pack.diff(sandbox)[0]


def test_stale_pack_is_detected_as_drift(sandbox: Path) -> None:
    pack.write(sandbox)
    source = sandbox / pack.SKILL_SOURCE / "SKILL.md"
    source.write_text(source.read_text("utf-8") + "\nnew content\n", encoding="utf-8")
    assert SKILL in pack.diff(sandbox)[0]


# --------------------------------------------------------------------------
# CLI contract
# --------------------------------------------------------------------------

def test_check_exits_zero_on_a_clean_tree(repo: Path) -> None:
    result = subprocess.run([sys.executable, str(SCRIPT), str(repo), "--check"],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout


def test_check_exits_one_on_a_drifted_tree(sandbox: Path) -> None:
    result = subprocess.run([sys.executable, str(SCRIPT), str(sandbox), "--check"],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "drifted" in result.stdout


def test_missing_skill_is_exit_two(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path), "--check"],
                            capture_output=True, text=True)
    assert result.returncode == 2


# --------------------------------------------------------------------------
# The portable contract
# --------------------------------------------------------------------------

def test_portable_contract_is_generated(repo: Path) -> None:
    assert CONTRACT in pack.plan(repo)
    assert (repo / CONTRACT).is_file()


def test_portable_contract_is_thin(repo: Path) -> None:
    assert len(pack.plan(repo)[CONTRACT].splitlines()) < 200


def test_portable_contract_carries_the_non_negotiables(repo: Path) -> None:
    text = pack.plan(repo)[CONTRACT]
    for phrase in ("Stations 6-11", "prohibited sentence", "by path",
                   "Gate once", "git hooks", "Adopt, never impose",
                   "money, permissions", "`akinator`"):
        assert phrase in text, f"the portable contract omits: {phrase}"


def test_portable_contract_is_not_akinators_own_router(repo: Path) -> None:
    """The pack ships a contract naming no repo-relative paths; this repo's own
    AGENTS.md is a router rendered from context/router-contract.md, full of
    paths that exist only here."""
    contract = pack.plan(repo)[CONTRACT]
    own_router = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert contract != own_router
    assert "python -m pytest tests/" not in contract
    assert "rules/README.md" not in contract
    assert "rules/README.md" in own_router


# --------------------------------------------------------------------------
# The installers ship the pack, never the router
# --------------------------------------------------------------------------

def test_installers_exist_and_are_referenced(repo: Path) -> None:
    """The one installer, both shells, discoverable from this repo's router -
    never from the portable contract, which names no paths."""
    assert (repo / "install.sh").is_file()
    assert (repo / "install.ps1").is_file()
    router = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "install.sh" in router


def test_installers_copy_the_pack_not_the_router(repo: Path) -> None:
    for name in ("install.sh", "install.ps1"):
        text = (repo / name).read_text(encoding="utf-8")
        assert ".agents" in text and "akinator.mdc" in text, name
        # The portable contract, never the root router, is the source.
        assert re.search(r"\.agents[/\\]+AGENTS\.md", text), name
        assert '"$SRC/AGENTS.md"' not in text, name
        assert "Join-Path $Src 'AGENTS.md'" not in text, name

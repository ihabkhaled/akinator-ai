"""Tests for the Codex pack generator.

The pack is a build output. These tests protect the two properties that make
that safe: it is **deterministic** (so the drift check is meaningful) and it is
**not drifted** (so the two platforms ship the same behavioral contract).

`test_pack_is_not_drifted` and `test_generation_is_deterministic` are named
directly by rules/07-codex-pack-is-generated.md as its enforcement mechanism.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import build_codex_pack as pack

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "build_codex_pack.py"


@pytest.fixture
def sandbox(tmp_path: Path, repo: Path) -> Path:
    """A copy of the canonical skills, with no generated pack yet."""
    root = tmp_path / "sandbox"
    (root).mkdir()
    shutil.copytree(repo / "skills", root / "skills")
    return root


# --------------------------------------------------------------------------
# The rules' named enforcement
# --------------------------------------------------------------------------

def test_pack_is_not_drifted(repo: Path) -> None:
    """Enforcement for rules/07: the shipped pack matches the canonical skills."""
    changed, missing, extra = pack.diff(repo)
    assert not (changed or missing or extra), (
        f"Codex pack is drifted.\nchanged={changed}\nmissing={missing}\n"
        f"extra={extra}\nFix: python scripts/build_codex_pack.py --write"
    )


def test_generation_is_deterministic(sandbox: Path) -> None:
    """Enforcement for rules/07: same tree in, byte-identical output out."""
    first = pack.plan(sandbox)
    second = pack.plan(sandbox)
    assert first == second

    pack.write(sandbox)
    written_once = {
        p.relative_to(sandbox).as_posix(): p.read_bytes()
        for p in sorted(sandbox.rglob("*")) if p.is_file()
    }
    pack.write(sandbox)
    written_twice = {
        p.relative_to(sandbox).as_posix(): p.read_bytes()
        for p in sorted(sandbox.rglob("*")) if p.is_file()
    }
    assert written_once == written_twice


def test_generated_output_contains_no_clock_or_absolute_paths(repo: Path) -> None:
    """A timestamp makes every run a diff, which kills the drift check."""
    for rel, content in pack.plan(repo).items():
        assert "2026-" not in content.split("-->")[0], (
            f"{rel}: generated banner must not contain a date"
        )
        for absolute in ("/Users/", "/home/", "C:\\", "D:\\"):
            assert absolute not in content, f"{rel}: absolute path in output"


# --------------------------------------------------------------------------
# Generation behavior
# --------------------------------------------------------------------------

def test_every_canonical_skill_is_projected(repo: Path) -> None:
    canonical = {p.parent.name for p in (repo / "skills").rglob("SKILL.md")}
    projected = {
        rel.split("/")[2] for rel in pack.plan(repo)
        if rel.startswith(".agents/skills/")
    }
    assert canonical == projected


def test_banner_follows_the_frontmatter(repo: Path) -> None:
    """A comment before the opening --- would stop frontmatter parsing."""
    for rel, content in pack.plan(repo).items():
        if not rel.startswith(".agents/skills/"):
            continue
        assert content.startswith("---\n"), f"{rel}: must open with frontmatter"
        banner_at = content.find("DO NOT EDIT BY HAND")
        close_at = content.find("\n---", 3)
        assert banner_at != -1, f"{rel}: banner is missing"
        assert close_at < banner_at, f"{rel}: banner must follow the frontmatter"


def test_pack_banners_name_no_file_the_host_repo_will_not_have(
    repo: Path
) -> None:
    """The banner travels with the file, so every path in it is a claim about
    whatever repository the file ends up in.

    `test_portable_contract_names_no_repo_relative_paths` already asserted this
    for the contract - but it filtered on `"/" in t`, so the bare filename
    `build_codex_pack.py` slipped through, and the 21 skill banners were never
    checked at all. A bare filename is not a path, and it is still a file the
    host repo does not have.
    """
    import re

    for rel, content in pack.plan(repo).items():
        banner = content[content.find("<!--"): content.find("-->") + 3]
        named = re.findall(r"`([A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,8})`", banner)
        assert not named, f"{rel}: banner names {named}, absent where it lands"


def test_pack_bodies_name_no_path_the_host_repo_will_not_have(repo: Path) -> None:
    """The body travels too, and it was the larger half of the problem.

    Fixing the banners left twenty path references in eleven skill *bodies* -
    `templates/adr.md`, `rules/05-no-git-hook-complication.md`,
    `evals/newcomer/README.md`. Every one is a file that exists only in an
    Akinator checkout, sitting in a document whose purpose is to be read
    somewhere else. The banner test could not see them, and neither could
    `check_doc_truth`, which walks `<root>/skills` and never `.agents/skills`.

    Same defect as the banner, one level out: a claim checked only where it
    happens to be true. A skill that needs to point at Akinator's own material
    describes it ("Akinator's ADR template") instead of naming a path.

    Fenced blocks are exempt - an illustrative path inside an example is
    understood as illustrative. See
    `memory/2026-08-26-fenced-examples-avoid-false-findings.md`.

    A file-shaped token is not the only way to name something absent. A
    directory the installer never creates is just as false a claim, and a
    regression left exactly one of these behind: `templates/` on its own, with
    no dot, no extension - the near-miss class repeating one token narrower
    than the last time. `install-codex.sh` writes only `.agents/skills/**` and
    `AGENTS.md`; it never creates `templates/`, `evals/`, or `scripts/` in the
    host. Those three are therefore checked by bare name too. `rules/`,
    `docs/`, `context/` and `memory/` are excluded from this half: they are
    common conventions a host repository plausibly already has of its own, so
    a skill describing "this repository's rules directory" is not asserting
    Akinator's tree - unlike `templates/`, which nothing but an Akinator
    checkout has any reason to contain.
    """
    import re

    fence = re.compile(r"^[ \t]*```.*?^[ \t]*```[ \t]*$", re.MULTILINE | re.DOTALL)
    token = re.compile(r"`([A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,8})`")
    akinator_only_dir = re.compile(r"`((?:templates|evals|scripts)/[A-Za-z0-9_./\\-]*)`")

    offenders: dict[str, list[str]] = {}
    for rel, content in pack.plan(repo).items():
        body = fence.sub("\n", content[content.find("-->") + 3:])
        named = sorted({t for t in token.findall(body) if "/" in t})
        named += sorted(set(akinator_only_dir.findall(body)))
        if named:
            offenders[rel] = sorted(set(named))

    assert not offenders, (
        "packed files name paths that will not exist where they are installed: "
        + "; ".join(f"{k} -> {v}" for k, v in sorted(offenders.items()))
    )


def test_projected_skills_keep_their_trigger_description(repo: Path) -> None:
    for name in ("akinator", "akinator-intake", "akinator-ops-map"):
        source = (repo / "skills" / name / "SKILL.md").read_text("utf-8")
        projected = pack.plan(repo)[f".agents/skills/{name}/SKILL.md"]
        source_desc = [l for l in source.splitlines() if l.startswith("description:")]
        projected_desc = [
            l for l in projected.splitlines() if l.startswith("description:")
        ]
        assert source_desc == projected_desc


def test_portable_contract_is_thin(repo: Path) -> None:
    content = pack.plan(repo)[".agents/AGENTS.md"]
    assert len(content.splitlines()) < 200, "the contract is an index, not a document"


# --------------------------------------------------------------------------
# Write, prune and drift detection
# --------------------------------------------------------------------------

def test_write_creates_the_pack(sandbox: Path) -> None:
    written, removed = pack.write(sandbox)
    assert written and not removed
    assert (sandbox / ".agents" / "AGENTS.md").is_file()
    assert (sandbox / ".agents" / "skills" / "akinator" / "SKILL.md").is_file()


def test_write_is_idempotent(sandbox: Path) -> None:
    pack.write(sandbox)
    written, removed = pack.write(sandbox)
    assert not written and not removed


def test_removed_skill_is_pruned_from_the_pack(sandbox: Path) -> None:
    pack.write(sandbox)
    shutil.rmtree(sandbox / "skills" / "akinator-adr")
    written, removed = pack.write(sandbox)
    assert ".agents/skills/akinator-adr/SKILL.md" in removed
    assert not (sandbox / ".agents" / "skills" / "akinator-adr").exists(), (
        "an emptied skill directory must be pruned, not left behind"
    )


def test_hand_edit_is_detected_as_drift(sandbox: Path) -> None:
    pack.write(sandbox)
    target = sandbox / ".agents" / "skills" / "akinator" / "SKILL.md"
    target.write_text(target.read_text("utf-8") + "\nhand edit\n", encoding="utf-8")

    changed, missing, extra = pack.diff(sandbox)
    assert ".agents/skills/akinator/SKILL.md" in changed


def test_stale_pack_is_detected_as_drift(sandbox: Path) -> None:
    pack.write(sandbox)
    source = sandbox / "skills" / "akinator" / "SKILL.md"
    source.write_text(source.read_text("utf-8") + "\nnew content\n", encoding="utf-8")

    changed, _, _ = pack.diff(sandbox)
    assert ".agents/skills/akinator/SKILL.md" in changed


# --------------------------------------------------------------------------
# CLI contract
# --------------------------------------------------------------------------

def test_check_exits_zero_on_a_clean_tree(repo: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo), "--check"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout


def test_check_exits_one_on_a_drifted_tree(sandbox: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(sandbox), "--check"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "drifted" in result.stdout


def test_missing_skills_directory_is_exit_two(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path), "--check"],
        capture_output=True, text=True,
    )
    assert result.returncode == 2


def test_installers_exist_and_are_referenced(repo: Path) -> None:
    """The installers must be discoverable - from the router, not the contract.

    The portable contract deliberately names no repo-relative paths, because it
    is copied into other repositories where `scripts/install-codex.sh` does not
    exist. So the reference lives in this repository's own routers, which are
    rendered from the contract and are free to name real local paths.
    """
    assert (repo / "scripts" / "install-codex.sh").is_file()
    assert (repo / "scripts" / "install-codex.ps1").is_file()

    router = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "install-codex.sh" in router


# --------------------------------------------------------------------------
# The portable contract installed into target repositories
# --------------------------------------------------------------------------

CONTRACT = ".agents/AGENTS.md"


def test_portable_contract_is_generated(repo: Path) -> None:
    assert CONTRACT in pack.plan(repo)
    assert (repo / CONTRACT).is_file()


def test_portable_contract_names_no_repo_relative_paths(repo: Path) -> None:
    """Regression: the installer used to copy Akinator's own router.

    That gave every target repository five dead links - `rules/README.md`,
    `docs/skills.md` and friends - plus an instruction to run Akinator's test
    suite. A doc asserting things that are not there is the failure this plugin
    rates critical, and it was being installed by the plugin itself.
    """
    import re

    text = pack.plan(repo)[CONTRACT]
    prose = re.sub(r"^[ \t]*```.*?^[ \t]*```[ \t]*$", "\n", text,
                   flags=re.MULTILINE | re.DOTALL)
    paths = [t for t in re.findall(r"`([A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,8})`", prose)
             if "/" in t]
    assert not paths, (
        f"the portable contract names repo-relative paths: {paths}. "
        "They will not exist in the repository it is installed into."
    )


def test_portable_contract_carries_the_non_negotiables(repo: Path) -> None:
    text = pack.plan(repo)[CONTRACT]
    for phrase in ("Stations 6-11", "prohibited sentence", "by path",
                   "Gate once", "git hooks", "Adopt, never impose",
                   "money, permissions"):
        assert phrase in text, f"the portable contract omits: {phrase}"


def test_portable_contract_is_not_akinators_own_router(repo: Path) -> None:
    """The two files are deliberately different documents.

    The pack ships a contract that names no repo-relative paths, because it is
    copied into OTHER repositories. This repository's own AGENTS.md is one of
    eleven routers rendered from context/router-contract.md and is full of paths
    that exist only here.
    """
    contract = pack.plan(repo)[CONTRACT]
    own_router = (repo / "AGENTS.md").read_text(encoding="utf-8")

    assert contract != own_router
    assert "python -m pytest tests/" not in contract
    assert "rules/README.md" not in contract
    # ...and the router does carry exactly what the contract must not.
    assert "rules/README.md" in own_router


# --------------------------------------------------------------------------
# What the pack does to the repository it lands in
# --------------------------------------------------------------------------

def test_the_installed_pack_leaves_a_target_repo_clean(
    repo: Path, tmp_path: Path
) -> None:
    """Regression, found by eval 06 and confirmed on a bare repo.

    Installing Akinator used to produce **22 HIGH findings** in the target
    repository on the very first run: 21 skill banners naming
    `scripts/build_codex_pack.py` and `skills/<name>/SKILL.md`, plus the
    portable contract naming `build_codex_pack.py` - none of which a target repo
    has. The plugin whose entire premise is that a doc asserting things that are
    not there is a critical defect was shipping 22 of them per install.

    Every existing test looked at the pack from inside this checkout, where
    those paths resolve. None looked at it from where it actually lives. This
    one does, and it is the whole point of the test.
    """
    import akinator_coverage as cov

    target = tmp_path / "host"
    (target / "src").mkdir(parents=True)
    (target / "README.md").write_text("# Host repo\n", encoding="utf-8")
    (target / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")

    for rel, text in pack.plan(repo).items():
        # The installer lands the contract at the repo root; the skills keep
        # their pack-relative location.
        dest = target / ("AGENTS.md" if rel == CONTRACT else rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")

    findings = cov.run_checks(cov.Repo(target), [], [], 40)
    loud = [f for f in findings if f.severity in ("critical", "high", "medium")]
    assert not loud, (
        "installing the pack dirties the host repo: "
        + "; ".join(f"{f.check} {f.path}: {f.message}" for f in loud[:5])
    )


def test_installers_copy_the_contract_not_the_router(repo: Path) -> None:
    for name in ("install-codex.sh", "install-codex.ps1"):
        text = (repo / "scripts" / name).read_text(encoding="utf-8")
        assert ".agents" in text and "AGENTS.md" in text, name
        # The bare router must never be the copy source.
        assert '"$PACK_ROOT/AGENTS.md"' not in text, name
        assert "(Join-Path $packRoot 'AGENTS.md')" not in text, name

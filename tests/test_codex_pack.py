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
        banner_at = content.find("GENERATED FILE")
        close_at = content.find("\n---", 3)
        assert close_at < banner_at, f"{rel}: banner must follow the frontmatter"


def test_projected_skills_keep_their_trigger_description(repo: Path) -> None:
    for name in ("akinator", "akinator-intake", "akinator-ops-map"):
        source = (repo / "skills" / name / "SKILL.md").read_text("utf-8")
        projected = pack.plan(repo)[f".agents/skills/{name}/SKILL.md"]
        source_desc = [l for l in source.splitlines() if l.startswith("description:")]
        projected_desc = [
            l for l in projected.splitlines() if l.startswith("description:")
        ]
        assert source_desc == projected_desc


def test_agents_md_is_a_thin_router(repo: Path) -> None:
    content = pack.plan(repo)["AGENTS.md"]
    assert len(content.splitlines()) < 200, "AGENTS.md is an index, not a document"
    assert "akinator:tool-specific" in content, (
        "Codex-only content must be marked so router-sync can tell it from rot"
    )


def test_agents_md_carries_the_non_negotiables(repo: Path) -> None:
    content = pack.plan(repo)["AGENTS.md"]
    for phrase in (
        "Stations 6-11",
        "prohibited sentence",
        "Gate once",
        "never add knowledge",
        "Adopt, never impose",
    ):
        assert phrase.lower() in content.lower(), f"AGENTS.md omits: {phrase}"


# --------------------------------------------------------------------------
# Write, prune and drift detection
# --------------------------------------------------------------------------

def test_write_creates_the_pack(sandbox: Path) -> None:
    written, removed = pack.write(sandbox)
    assert written and not removed
    assert (sandbox / "AGENTS.md").is_file()
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
    assert (repo / "scripts" / "install-codex.sh").is_file()
    assert (repo / "scripts" / "install-codex.ps1").is_file()
    assert "install-codex.sh" in pack.plan(repo)["AGENTS.md"]

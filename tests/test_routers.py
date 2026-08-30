"""Tests for the router renderer.

Eleven routers are only safe because they are generated. These pin the four
properties that make that true: they are not drifted, rendering is
deterministic, every router carries the shared facts, and no tool-specific block
smuggles a repository fact past the sync check.

`test_routers_are_not_drifted` and `test_rendering_is_deterministic` are named
by rules/09-routers-are-rendered-from-one-contract.md as its enforcement.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

import render_routers as rr


@pytest.fixture(scope="module")
def rendered(repo: Path) -> dict[str, str]:
    return rr.plan(repo)


def test_routers_are_not_drifted(repo: Path) -> None:
    """Enforcement for rules/09."""
    drifted = rr.diff(repo)
    assert not drifted, (
        f"routers differ from the contract: {drifted}. "
        "Fix with: python scripts/render_routers.py --write"
    )


def test_rendering_is_deterministic(repo: Path) -> None:
    """Enforcement for rules/09: a clock or unordered iteration would make the
    drift check noise, and a noisy drift check gets disabled."""
    assert rr.plan(repo) == rr.plan(repo)


def test_every_planned_router_exists(repo: Path, rendered: dict[str, str]) -> None:
    assert len(rendered) == len(rr.ADAPTERS) == 11
    for rel in rendered:
        assert (repo / rel).is_file(), f"{rel} was planned but never written"


def test_every_router_carries_the_shared_sections(rendered: dict[str, str]) -> None:
    for rel, content in rendered.items():
        for section in rr.SHARED_SECTIONS:
            assert f"## {section}" in content, f"{rel} omits '{section}'"


def test_shared_sections_are_byte_identical_across_routers(
    rendered: dict[str, str],
) -> None:
    """The whole point: the facts cannot differ, only the presentation."""
    def shared(text: str) -> str:
        return text.split("<!-- akinator:tool-specific -->")[0]

    bodies = {}
    for rel, content in rendered.items():
        # Strip the banner and any frontmatter; keep from the first heading on.
        body = shared(content)
        body = body[body.index("## "):] if "## " in body else body
        bodies[rel] = body

    reference = next(iter(bodies.values()))
    for rel, body in bodies.items():
        assert body == reference, f"{rel}'s shared facts differ from the others"


def test_every_router_declares_itself_generated(rendered: dict[str, str]) -> None:
    for rel, content in rendered.items():
        assert "DO NOT EDIT BY HAND" in content, rel
        assert "render_routers.py" in content, rel


def test_tool_specific_blocks_are_marked(rendered: dict[str, str]) -> None:
    for rel, content in rendered.items():
        for adapter in rr.ADAPTERS:
            if adapter.path == rel and adapter.specifics:
                assert "<!-- akinator:tool-specific -->" in content, rel


REPO_FACT_MARKERS = (
    "schema change", "rebuild", "not a restart", "quota", "migration",
    "must not break", "knowledge delta",
)


def test_tool_specific_blocks_carry_no_repository_facts(
    rendered: dict[str, str],
) -> None:
    """The marker exempts a block from the sync check.

    That makes it the one place a repository fact could hide from the very
    mechanism built to catch forks. The marker is for where a tool reads its
    skills from - never for anything true of the system.
    """
    for rel, content in rendered.items():
        if "<!-- akinator:tool-specific -->" not in content:
            continue
        block = content.split("<!-- akinator:tool-specific -->", 1)[1].lower()
        leaked = [m for m in REPO_FACT_MARKERS if m in block]
        assert not leaked, (
            f"{rel}'s tool-specific block states repository facts {leaked} - "
            "those belong in context/router-contract.md, where every router "
            "gets them"
        )


def test_cursor_router_keeps_its_frontmatter_first(rendered: dict[str, str]) -> None:
    """A banner before the frontmatter would stop Cursor parsing it."""
    content = rendered[".cursor/rules/akinator.mdc"]
    assert content.startswith("---\n")
    assert content.index("alwaysApply") < content.index("DO NOT EDIT")


def test_contract_is_the_only_hand_written_source(repo: Path) -> None:
    contract = repo / rr.CONTRACT
    assert contract.is_file()
    text = contract.read_text(encoding="utf-8")
    assert "DO NOT EDIT" not in text, "the contract is canonical, not generated"


def test_pack_builder_no_longer_owns_the_root_router(repo: Path) -> None:
    """Two generators writing one file is a fork with extra steps."""
    import build_codex_pack as pack

    assert "AGENTS.md" not in pack.plan(repo), (
        "build_codex_pack must not generate the root AGENTS.md - "
        "render_routers.py owns it"
    )
    assert ".agents/AGENTS.md" in pack.plan(repo), (
        "the pack still owns the portable contract it installs elsewhere"
    )

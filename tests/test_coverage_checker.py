"""Tests for the coverage checker.

Two jobs:

1. Prove each invariant actually fires, on a purpose-built fixture repo. A
   checker whose detection has silently broken is worse than no checker - it
   reports green and everyone believes it.
2. Prove the checker does not fire on a healthy repo, so it does not train
   people to ignore it.

Several of these tests are named directly by rules as their enforcement
mechanism. Renaming one breaks the rule that cites it - which is intended.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import akinator_coverage as cov

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "akinator_coverage.py"


# --------------------------------------------------------------------------
# Fixture repositories
# --------------------------------------------------------------------------

def write(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


@pytest.fixture
def healthy(tmp_path: Path) -> Path:
    """A small repo that satisfies every invariant."""
    root = tmp_path / "healthy"
    root.mkdir()

    write(root, "CLAUDE.md", (
        "# Demo\n\n## Start here\n\n"
        "- Rules: `rules/README.md`\n"
        "- Skills: `skills/README.md`\n"
        "- Context: `context/README.md`\n"
    ))
    write(root, "AGENTS.md", (
        "# Demo\n\n## Start here\n\n"
        "- Rules: `rules/README.md`\n"
        "- Skills: `skills/README.md`\n"
        "- Context: `context/README.md`\n"
    ))

    write(root, "rules/README.md",
          "# Rules\n\n- [01 - Demo](01-demo.md) - the demo constraint\n")
    write(root, "rules/01-demo.md", (
        "# Rule 01 - Demo\n\n"
        "## Purpose\n\nSomething breaks otherwise.\n\n"
        "## Applies to\n\nEverything.\n\n"
        "## Mandatory rules\n\n1. Do the thing.\n\n"
        "## Enforcement\n\n- Mechanism: `tests/demo_test.py`\n"
        "- Type: unit test.\n"
    ))
    write(root, "tests/demo_test.py", "def test_demo():\n    assert True\n")

    write(root, "skills/README.md",
          "# Skills\n\n- [demo](demo/SKILL.md) - use when demonstrating\n")
    write(root, "skills/demo/SKILL.md", (
        "---\nname: demo\ndescription: Use when demonstrating the checker.\n---\n\n"
        "# Demo\n\n## When to use\n\nWhen demonstrating.\n\n"
        "## When NOT to use\n\nOtherwise.\n\n"
        "## Procedure\n\n1. Do it.\n\n"
        "## Failure modes and pitfalls\n\nNone observed yet.\n\n"
        "## Definition of done\n\n- [ ] It is done.\n"
    ))

    write(root, "context/README.md",
          "# Context\n\n- [services](services.md) - the service map\n")
    write(root, "context/services.md", (
        "# Services\n\n## Scope\n\nThe services.\n\n"
        "| Service | Port |\n|---|---|\n| api | 3000 |\n\n"
        "## Review when\n\nA service is added.\nLast verified: 2026-08-26\n"
    ))
    return root


@pytest.fixture
def rotten(tmp_path: Path) -> Path:
    """A repo with one deliberate instance of each failure the checker catches."""
    root = tmp_path / "rotten"
    root.mkdir()

    # Router fork: CLAUDE.md carries a rules link that AGENTS.md omits.
    write(root, "CLAUDE.md",
          "# Rotten\n\n- Rules: `rules/README.md`\n- Skills: `skills/README.md`\n")
    write(root, "AGENTS.md", "# Rotten\n\n- Skills: `skills/README.md`\n")

    write(root, "rules/README.md",
          "# Rules\n\n- [01](01-absent-mechanism.md)\n- [02](02-hooked.md)\n")

    # Rule naming a mechanism that does not exist.
    write(root, "rules/01-absent-mechanism.md", (
        "# Rule 01\n\n## Purpose\n\nX.\n\n## Applies to\n\nY.\n\n"
        "## Mandatory rules\n\n1. Z.\n\n"
        "## Enforcement\n\n- Mechanism: `tests/never_written.py`\n"
    ))
    # Rule enforced by a git hook.
    write(root, "rules/02-hooked.md", (
        "# Rule 02\n\n## Purpose\n\nX.\n\n## Applies to\n\nY.\n\n"
        "## Mandatory rules\n\n1. Z.\n\n"
        "## Enforcement\n\n- Mechanism: `.husky/pre-commit`\n"
    ))

    # Skill with no frontmatter, missing sections.
    write(root, "skills/README.md", "# Skills\n\n- [broken](broken/SKILL.md)\n")
    write(root, "skills/broken/SKILL.md", "# Broken\n\nNo frontmatter, no sections.\n")

    # Unreachable doc, dead link, untrue path, context map with no trigger.
    write(root, "docs/orphan.md", "# Orphan\n\nNothing links here.\n")
    write(root, "docs/linky.md", "# Linky\n\n[gone](../nowhere/missing.md)\n")
    write(root, "docs/untrue.md", "# Untrue\n\nSee `src/does/not/exist.ts`.\n")
    write(root, "context/drifty.md", "# Drifty\n\n| A | B |\n|---|---|\n| 1 | 2 |\n")

    # A knowledge check wired into a git hook.
    write(root, ".husky/pre-commit",
          "#!/bin/sh\npython scripts/akinator_coverage.py --strict\n")
    return root


def findings(root: Path, **kwargs) -> list[cov.Finding]:
    repo = cov.Repo(root)
    return cov.run_checks(repo, kwargs.get("only", []), kwargs.get("skip", []), 40)


def by_check(root: Path, check: str) -> list[cov.Finding]:
    return [f for f in findings(root) if f.check == check]


# --------------------------------------------------------------------------
# The healthy repo passes
# --------------------------------------------------------------------------

def test_healthy_repo_has_no_blocking_findings(healthy: Path) -> None:
    blocking = [f for f in findings(healthy) if f.severity in ("critical", "high")]
    assert not blocking, [f"{f.check}: {f.path} - {f.message}" for f in blocking]


def test_healthy_repo_exits_zero(healthy: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(healthy)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout


# --------------------------------------------------------------------------
# Each invariant fires
# --------------------------------------------------------------------------

def test_flags_rule_naming_absent_mechanism(rotten: Path) -> None:
    """Enforcement named by rules/03-rules-need-live-enforcement.md."""
    hits = [f for f in by_check(rotten, "rule-enforcement")
            if "01-absent-mechanism" in f.path]
    assert hits, "a rule naming a nonexistent mechanism must be caught"
    assert hits[0].severity == "critical"
    assert "never_written.py" in hits[0].message


def test_detects_knowledge_check_in_git_hook(rotten: Path) -> None:
    """Enforcement named by rules/05-no-git-hook-complication.md."""
    hits = by_check(rotten, "git-hooks")
    assert hits, "a knowledge check in a git hook must be caught"
    assert hits[0].severity == "critical"
    assert ".husky" in hits[0].path


def test_flags_rule_enforced_by_a_git_hook(rotten: Path) -> None:
    hits = [f for f in by_check(rotten, "rule-enforcement") if "02-hooked" in f.path]
    assert hits and hits[0].severity == "critical"
    assert "git hook" in hits[0].message


def test_flags_unreachable_artifact(rotten: Path) -> None:
    hits = [f for f in by_check(rotten, "reachability") if "orphan" in f.path]
    assert hits, "an unindexed artifact must be caught"


def test_flags_dead_link(rotten: Path) -> None:
    hits = [f for f in by_check(rotten, "dead-links") if "linky" in f.path]
    assert hits and hits[0].severity == "high"


def test_flags_untrue_path_in_a_doc(rotten: Path) -> None:
    hits = [f for f in by_check(rotten, "doc-truth") if "untrue" in f.path]
    assert hits, "a doc naming a path that does not exist must be caught"


def test_flags_context_map_without_a_staleness_trigger(rotten: Path) -> None:
    hits = [f for f in by_check(rotten, "staleness") if "drifty" in f.path]
    assert hits


def test_flags_router_fork(rotten: Path) -> None:
    hits = by_check(rotten, "router-sync")
    assert hits, "a router omitting knowledge the others carry must be caught"
    assert any("AGENTS.md" in f.path for f in hits)


def test_flags_skill_without_frontmatter(rotten: Path) -> None:
    hits = [f for f in by_check(rotten, "skill-format") if "broken" in f.path]
    assert hits
    assert any(f.severity == "critical" for f in hits)


# --------------------------------------------------------------------------
# False-positive guards
# --------------------------------------------------------------------------

def test_fenced_code_blocks_are_not_treated_as_claims(tmp_path: Path) -> None:
    """Paths inside a fence are illustrations, not assertions about this tree."""
    root = tmp_path / "fenced"
    root.mkdir()
    write(root, "CLAUDE.md", "# F\n\n- Docs: `docs/README.md`\n")
    write(root, "docs/README.md", "# Docs\n\n- [guide](guide.md) - the guide\n")
    write(root, "docs/guide.md", (
        "# Guide\n\nExample only:\n\n"
        "```markdown\n[Quotas](business/quotas.md)\nSee `src/imaginary/file.ts`\n```\n"
    ))
    assert not by_check(root, "dead-links")
    assert not by_check(root, "doc-truth")


def test_tool_specific_section_creates_no_expectation(tmp_path: Path) -> None:
    """A marked section is excluded from the comparison in both directions.

    It neither triggers a finding against its own router nor makes the other
    routers look like they are missing something. The marker exempts the
    *section*, not the whole file - a single marker must not excuse a real fork
    elsewhere in the same router.
    """
    root = tmp_path / "marked"
    root.mkdir()
    write(root, "CLAUDE.md", "# M\n\n## Start here\n\n- Rules: `rules/README.md`\n")
    write(root, "AGENTS.md", (
        "# M\n\n## Start here\n\n- Rules: `rules/README.md`\n\n"
        "<!-- akinator:tool-specific -->\n"
        "## Codex specifics\n\nSee `docs/codex-only.md`.\n"
    ))
    write(root, "rules/README.md", "# Rules\n")
    write(root, "docs/codex-only.md", "# Codex only\n")

    assert not by_check(root, "router-sync")


def test_marker_does_not_excuse_a_fork_outside_its_section(tmp_path: Path) -> None:
    root = tmp_path / "sneaky"
    root.mkdir()
    write(root, "CLAUDE.md",
          "# S\n\n## Start here\n\n- Rules: `rules/README.md`\n- Docs: `docs/README.md`\n")
    write(root, "AGENTS.md", (
        "# S\n\n## Start here\n\n- Rules: `rules/README.md`\n\n"
        "<!-- akinator:tool-specific -->\n## Codex specifics\n\nCodex only.\n"
    ))
    write(root, "rules/README.md", "# Rules\n")
    write(root, "docs/README.md", "# Docs\n")

    hits = by_check(root, "sneaky") or by_check(root, "router-sync")
    assert any("AGENTS.md" in f.path and "docs/README.md" in f.message for f in hits), (
        "a marker in one section must not exempt the rest of the router"
    )


def test_index_files_are_not_reported_unreachable(healthy: Path) -> None:
    hits = [f for f in by_check(healthy, "reachability")
            if f.path.lower().endswith(("readme.md", "index.md"))]
    assert not hits


def test_empty_repo_reports_no_knowledge_layer(tmp_path: Path) -> None:
    root = tmp_path / "bare"
    root.mkdir()
    (root / "main.py").write_text("print('hi')\n", encoding="utf-8")
    repo = cov.Repo(root)
    assert not repo.has_knowledge_layer()
    text = cov.report(repo, [], "high")
    assert "No knowledge layer detected" in text


# --------------------------------------------------------------------------
# CLI contract
# --------------------------------------------------------------------------

def test_json_output_is_machine_readable(rotten: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(rotten), "--json"],
        capture_output=True, text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["counts"]["critical"] >= 1
    assert all({"check", "severity", "path", "message"} <= set(f)
               for f in payload["findings"])


def test_rotten_repo_exits_nonzero(rotten: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(rotten)],
        capture_output=True, text=True,
    )
    assert result.returncode == 1


def test_findings_are_deterministic(rotten: Path) -> None:
    first = [f.sort_key() for f in findings(rotten)]
    second = [f.sort_key() for f in findings(rotten)]
    assert first == second


def test_unknown_check_name_is_an_error(healthy: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(healthy), "--only", "no-such-check"],
        capture_output=True, text=True,
    )
    assert result.returncode == 2


def test_docstring_forbids_git_hook_use() -> None:
    """The checker must say, in itself, that it is never a git hook."""
    assert "NEVER wire this into a git hook" in SCRIPT.read_text(encoding="utf-8")


def test_rule_about_git_hooks_is_not_flagged_as_hook_enforced(tmp_path: Path) -> None:
    """A rule *about* git hooks necessarily names them. That is not enforcement.

    Regression guard: the mechanism is the first backticked token on a
    `Mechanism:` line. Everything after it - including the hook files the
    mechanism scans - is prose.
    """
    root = tmp_path / "meta"
    root.mkdir()
    write(root, "CLAUDE.md", "# M\n\n- Rules: `rules/README.md`\n")
    write(root, "rules/README.md", "# Rules\n\n- [05](05-no-hooks.md)\n")
    write(root, "rules/05-no-hooks.md", (
        "# Rule 05 - Never put knowledge checks in git hooks\n\n"
        "## Purpose\n\nSlow commits train `--no-verify`.\n\n"
        "## Applies to\n\nEvery hook.\n\n"
        "## Mandatory rules\n\n1. No knowledge check in a hook.\n\n"
        "## Prohibited patterns\n\n"
        "```yaml\n# WRONG - .pre-commit-config.yaml\n- id: coverage\n```\n\n"
        "## Enforcement\n\n"
        "- Mechanism: `scripts/check.py` - scans `.git/hooks/`, `.husky/` and\n"
        "  `.pre-commit-config.yaml` for knowledge-check markers.\n"
        "- Type: script check in CI.\n"
    ))
    write(root, "scripts/check.py", "print('ok')\n")

    hits = by_check(root, "rule-enforcement")
    assert not hits, [f"{f.severity}: {f.message}" for f in hits]


def test_enforcement_heading_inside_a_fence_is_not_the_real_section(
    tmp_path: Path,
) -> None:
    """A fenced example's `## Enforcement` must not shadow the real one."""
    root = tmp_path / "fenced-rule"
    root.mkdir()
    write(root, "CLAUDE.md", "# F\n\n- Rules: `rules/README.md`\n")
    write(root, "rules/README.md", "# Rules\n\n- [01](01-demo.md)\n")
    write(root, "rules/01-demo.md", (
        "# Rule 01 - Demo\n\n"
        "## Purpose\n\nX.\n\n## Applies to\n\nY.\n\n"
        "## Mandatory rules\n\n1. Z.\n\n"
        "## Prohibited patterns\n\n"
        "```markdown\n## Enforcement\n\nReviewers should check this.\n```\n\n"
        "## Enforcement\n\n- Mechanism: `tests/real_test.py`\n"
    ))
    write(root, "tests/real_test.py", "def test_x():\n    assert True\n")

    assert not by_check(root, "rule-enforcement")


def test_dotfile_paths_are_resolved_correctly(tmp_path: Path) -> None:
    """`.claude-plugin/plugin.json` must not be mangled into `claude-plugin/...`."""
    root = tmp_path / "dotted"
    root.mkdir()
    write(root, ".claude-plugin/plugin.json", '{"name": "x"}\n')
    repo = cov.Repo(root)
    assert repo.exists_rel(".claude-plugin/plugin.json")
    assert repo.exists_rel("./.claude-plugin/plugin.json")
    assert not repo.exists_rel("claude-plugin/plugin.json")


def test_akinatorignore_excludes_paths(tmp_path: Path) -> None:
    root = tmp_path / "ignoring"
    root.mkdir()
    write(root, ".akinatorignore", "# fixtures carry planted defects\nfixtures\n")
    write(root, "CLAUDE.md", "# I\n\n- Rules: `rules/README.md`\n")
    write(root, "rules/README.md", "# Rules\n")
    write(root, "fixtures/broken/rules/01-bad.md", (
        "# Rule 01\n\n## Purpose\n\nX.\n\n## Applies to\n\nY.\n\n"
        "## Mandatory rules\n\n1. Z.\n\n## Enforcement\n\nNone.\n"
    ))
    write(root, "fixtures/broken/docs/orphan.md", "# Orphan\n")

    paths = [f.path for f in findings(root)]
    assert not any(p.startswith("fixtures/") for p in paths), paths

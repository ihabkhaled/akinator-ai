"""Tests for akinator_version - every shipped change bumps the version (rule 16).

Per rules/11, each invariant has a passing case and a mutation case proving the
check fires. Temp git repos only; identity is set locally, never globally.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import akinator_version as ver


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-c", "commit.gpgsign=false", *args],
        cwd=root, check=True, capture_output=True,
    )


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))


def _manifests(root: Path, version: str, nl: str = "\n") -> None:
    plugin = '{' + nl + '  "name": "demo",' + nl + f'  "version": "{version}"' + nl + '}' + nl
    market = ('{' + nl + '  "plugins": [' + nl + '    {' + nl + '      "name": "demo",' + nl
              + f'      "version": "{version}"' + nl + '    }' + nl + '  ]' + nl + '}' + nl)
    _write(root, ".claude-plugin/plugin.json", plugin)
    _write(root, ".claude-plugin/marketplace.json", market)
    _write(root, "package.json", '{"name": "d", "version": "%s", "dependencies": {"x": {"version": "9.9.9"}}}\n' % version)
    _write(root, "pyproject.toml", f'[project]{nl}name = "d"{nl}version = "{version}"{nl}')
    _write(root, "VERSION", version + nl)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "T")
    _git(tmp_path, "config", "user.email", "t@example.invalid")
    _manifests(tmp_path, "1.0.0")
    _write(tmp_path, "CHANGELOG.md", "# Changelog\n\n## [1.0.0] - 2026-01-01\n\nfirst\n")
    _write(tmp_path, "skills/demo/SKILL.md", "---\nname: demo\n---\n")
    _write(tmp_path, "skills/demo/scripts/tool.py", "print(1)\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def _run(root: Path, *args: str) -> int:
    return ver.main(["--root", str(root), *args])


# --- show and agreement ----------------------------------------------------------

def test_show_lists_every_manifest(repo: Path, capsys) -> None:
    assert _run(repo, "show") == 0
    out = capsys.readouterr().out
    for name in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
                 "package.json", "pyproject.toml", "VERSION"):
        assert name in out


def test_check_passes_when_manifests_agree(repo: Path) -> None:
    assert _run(repo, "check") == 0


@pytest.mark.parametrize("rel,kind", [
    ("package.json", "json"), ("pyproject.toml", "toml"), ("VERSION", "plain"),
    (".claude-plugin/marketplace.json", "json"),
])
def test_check_fails_when_any_one_manifest_disagrees(repo: Path, rel: str, kind: str, capsys) -> None:
    path = repo / rel
    path.write_bytes(path.read_bytes().replace(b"1.0.0", b"1.0.1", 1))
    assert _run(repo, "check") == 1
    assert "disagree" in capsys.readouterr().out


# --- check --base ----------------------------------------------------------------

def test_shipped_change_without_bump_fails(repo: Path, capsys) -> None:
    _write(repo, "skills/demo/scripts/tool.py", "print(2)\n")
    assert _run(repo, "check", "--base", "HEAD") == 1
    assert "not greater" in capsys.readouterr().out


def test_unshipped_change_needs_no_bump(repo: Path) -> None:
    _write(repo, "docs/notes.md", "n\n")
    assert _run(repo, "check", "--base", "HEAD") == 0


def test_shipped_change_with_bump_and_changelog_passes(repo: Path) -> None:
    _write(repo, "skills/demo/scripts/tool.py", "print(2)\n")
    assert _run(repo, "bump", "patch", "--date", "2026-02-02") == 0
    assert _run(repo, "check", "--base", "HEAD") == 0


def test_bump_without_changelog_heading_fails(repo: Path, capsys) -> None:
    _write(repo, "skills/demo/scripts/tool.py", "print(2)\n")
    assert _run(repo, "set", "1.0.1") == 0
    assert _run(repo, "check", "--base", "HEAD") == 1
    assert "changelog" in capsys.readouterr().out


def test_a_lower_version_is_not_greater(repo: Path, capsys) -> None:
    _write(repo, "skills/demo/scripts/tool.py", "print(2)\n")
    _run(repo, "set", "0.9.0")
    _write(repo, "CHANGELOG.md", "# c\n\n## [0.9.0] - 2026-01-01\n")
    assert _run(repo, "check", "--base", "HEAD") == 1


def test_semver_compare_is_numeric_not_lexical() -> None:
    assert ver.parse_semver("1.10.0") > ver.parse_semver("1.9.9")
    assert ver.parse_semver("2.0.0") > ver.parse_semver("2.0.0-rc.1")


def test_shipped_globs_are_overridable_in_config(repo: Path) -> None:
    _write(repo, ".ai/config.json", json.dumps({"version": {"shipped": ["src/**"]}}))
    _write(repo, "skills/demo/scripts/tool.py", "print(2)\n")
    assert _run(repo, "check", "--base", "HEAD") == 0
    _write(repo, "src/app.py", "a\n")
    assert _run(repo, "check", "--base", "HEAD") == 1


def test_unknown_ref_is_a_usage_error(repo: Path) -> None:
    assert _run(repo, "check", "--base", "no-such-ref") == 2
    assert _run(repo, "next", "--base", "no-such-ref") == 2


def test_new_untracked_shipped_file_counts(repo: Path) -> None:
    _write(repo, "hooks/new.sh", "#!/bin/sh\n")
    assert _run(repo, "check", "--base", "HEAD") == 1


# --- next ------------------------------------------------------------------------

def test_next_patch_for_a_fix_in_an_existing_file(repo: Path, capsys) -> None:
    _write(repo, "skills/demo/scripts/tool.py", "print(2)\n")
    assert _run(repo, "next") == 0
    assert capsys.readouterr().out.startswith("patch: 1.0.0 -> 1.0.1")


def test_next_minor_for_a_new_tool(repo: Path, capsys) -> None:
    _write(repo, "skills/demo/scripts/other.py", "print(3)\n")
    _run(repo, "next")
    out = capsys.readouterr().out
    assert out.startswith("minor: 1.0.0 -> 1.1.0")
    assert "skills/demo/scripts/other.py" in out


def test_next_minor_for_a_new_rule(repo: Path, capsys) -> None:
    _write(repo, "rules/01-x.md", "r\n")
    _run(repo, "next")
    assert capsys.readouterr().out.startswith("minor")


def test_next_minor_for_a_removed_tool(repo: Path, capsys) -> None:
    (repo / "skills/demo/scripts/tool.py").unlink()
    _run(repo, "next")
    assert capsys.readouterr().out.startswith("minor")


def test_next_major_for_a_renamed_entry_point(repo: Path, capsys) -> None:
    _git(repo, "mv", "skills/demo/scripts/tool.py", "skills/demo/scripts/renamed.py")
    _run(repo, "next")
    assert capsys.readouterr().out.startswith("major: 1.0.0 -> 2.0.0")


def test_next_major_for_a_removed_skill(repo: Path, capsys) -> None:
    (repo / "skills/demo/SKILL.md").unlink()
    _run(repo, "next")
    assert capsys.readouterr().out.startswith("major")


def test_next_none_when_nothing_shipped_changed(repo: Path, capsys) -> None:
    _write(repo, "docs/a.md", "a\n")
    _run(repo, "next")
    assert capsys.readouterr().out.startswith("none")


# --- bump and set ----------------------------------------------------------------

def test_bump_rewrites_every_manifest_and_only_versions(repo: Path, capsys) -> None:
    before = (repo / "package.json").read_text("utf-8")
    assert _run(repo, "bump", "minor", "--date", "2026-03-03") == 0
    assert capsys.readouterr().out.strip() == "1.1.0"
    assert _run(repo, "check") == 0
    after = (repo / "package.json").read_text("utf-8")
    assert after == before.replace('"version": "1.0.0"', '"version": "1.1.0"')
    assert '"version": "9.9.9"' in after  # a nested version of a dependency is untouched
    assert (repo / "VERSION").read_text("utf-8") == "1.1.0\n"
    assert 'version = "1.1.0"' in (repo / "pyproject.toml").read_text("utf-8")


def test_bump_inserts_a_changelog_skeleton_once(repo: Path) -> None:
    _run(repo, "bump", "patch", "--date", "2026-03-03")
    text = (repo / "CHANGELOG.md").read_text("utf-8")
    assert text.index("## [1.0.1] - 2026-03-03") < text.index("## [1.0.0]")
    _run(repo, "set", "1.0.1")
    ver.insert_changelog(repo, "1.0.1", "2026-03-04")
    assert (repo / "CHANGELOG.md").read_text("utf-8").count("## [1.0.1]") == 1


def test_bump_refuses_without_a_date(repo: Path) -> None:
    assert _run(repo, "bump", "patch") == 2
    assert (repo / "VERSION").read_text("utf-8") == "1.0.0\n"


def test_bump_refuses_when_manifests_disagree(repo: Path) -> None:
    (repo / "VERSION").write_bytes(b"1.0.5\n")
    assert _run(repo, "bump", "patch", "--date", "2026-03-03") == 1
    assert (repo / "package.json").read_text("utf-8").count("1.0.0") == 1


def test_bump_preserves_crlf(tmp_path: Path) -> None:
    _manifests(tmp_path, "1.0.0", nl="\r\n")
    _write(tmp_path, "CHANGELOG.md", "# c\r\n\r\n## [1.0.0] - x\r\n")
    assert _run(tmp_path, "bump", "patch", "--date", "2026-03-03") == 0
    for rel in (".claude-plugin/plugin.json", "pyproject.toml", "VERSION", "CHANGELOG.md"):
        data = (tmp_path / rel).read_bytes()
        assert b"\r\n" in data
        assert b"\n" not in data.replace(b"\r\n", b""), rel


def test_set_rejects_a_non_semver(repo: Path) -> None:
    assert _run(repo, "set", "banana") == 2


def test_usage_error_exits_two(repo: Path) -> None:
    assert _run(repo, "frobnicate") == 2


def test_cli_runs_as_a_script(repo: Path) -> None:
    script = Path(ver.__file__)
    proc = subprocess.run(
        ["python", str(script), "--root", str(repo), "check"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0 and "ok version 1.0.0" in proc.stdout


# --- the version is visible to the next session -----------------------------------

def test_brief_states_the_current_version(repo: Path) -> None:
    import build_brief

    assert build_brief.current_version(repo) == "1.0.0"
    assert build_brief.current_version(repo / "docs") == ""
    _write(repo, "VERSION", "3.4.5\n")
    (repo / ".claude-plugin/plugin.json").unlink()
    (repo / "package.json").unlink()
    assert build_brief.current_version(repo) == "3.4.5"


def test_history_page_lists_the_marketplace_version_too(repo: Path) -> None:
    import extract_history

    found = dict(extract_history.versions(repo))
    assert found[".claude-plugin/marketplace.json"] == "1.0.0"
    assert found[".claude-plugin/plugin.json"] == "1.0.0"

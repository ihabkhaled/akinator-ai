"""Tests for `akinator_distil.py repeats` - history, asked as a question.

Per rules/11 each behaviour is proven to fire on a violating history and to stay
silent on a healthy one: below the threshold nothing is reported, and a decided
finding is suppressed.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import akinator_distil as dis


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(root), check=True,
                   capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "r"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "T")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "commit.gpgsign", "false")
    return root


def _commit(root: Path, subject: str, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", subject)


def _pair_commits(root: Path, n: int, subject: str = "chore: tweak") -> None:
    for i in range(n):
        _commit(root, f"{subject} {i}", {"src/a.py": f"{i}\n", "src/b.py": f"{i}\n"})


def test_files_that_change_together_reach_the_threshold(repo: Path) -> None:
    _pair_commits(repo, 3, "feat: unrelated words")
    found = dis.mine_repeats(repo, "90.days", 3)
    files = [r for r in found if r.kind == "files"]
    assert [r.key for r in files] == ["src/a.py, src/b.py"]
    assert files[0].count == 3 and len(files[0].commits) == 3
    assert "3 times - turn it into a skill, a rule, or neither?" in files[0].question


def test_below_the_threshold_nothing_is_reported(repo: Path) -> None:
    _pair_commits(repo, 2, "feat: unrelated words")
    assert [r for r in dis.mine_repeats(repo, "90.days", 3)
            if r.kind == "files"] == []
    assert dis.mine_repeats(repo, "90.days", 2), "the same history fires at min 2"


def test_docs_and_generated_homes_are_ignored(repo: Path) -> None:
    for i in range(4):
        _commit(repo, f"feat: thing {i} here", {
            "docs/x.md": f"{i}\n", ".ai/BRIEF.md": f"{i}\n",
            ".agents/p.txt": f"{i}\n", "README.md": f"{i}\n"})
    assert [r for r in dis.mine_repeats(repo, "90.days", 3)
            if r.kind == "files"] == []


def test_a_bulk_commit_is_not_a_habit(repo: Path) -> None:
    for i in range(3):
        _commit(repo, f"refactor: sweep {i} all",
                {f"src/f{j}.py": f"{i}\n" for j in range(dis.REPEAT_MAX_FILES_PER_COMMIT + 1)})
    assert [r for r in dis.mine_repeats(repo, "90.days", 3)
            if r.kind == "files"] == []


def test_subject_stems_repeat_after_the_conventional_prefix(repo: Path) -> None:
    for i, prefix in enumerate(["fix", "feat(api)", "chore"]):
        _commit(repo, f"{prefix}: Bump Python Version to 3.{i}", {f"f{i}.txt": "x\n"})
    _commit(repo, "fix: something else entirely", {"g.txt": "x\n"})
    found = [r for r in dis.mine_repeats(repo, "90.days", 3) if r.kind == "subject"]
    assert [r.key for r in found] == ["bump python version"]
    assert found[0].count == 3


def test_a_stem_below_the_threshold_is_not_reported(repo: Path) -> None:
    for i in range(2):
        _commit(repo, f"fix: bump python version {i}", {f"f{i}.txt": "x\n"})
    assert [r for r in dis.mine_repeats(repo, "90.days", 3)
            if r.kind == "subject"] == []


def test_a_decided_finding_is_suppressed(repo: Path) -> None:
    _pair_commits(repo, 3, "feat: unrelated words")
    [finding] = [r for r in dis.mine_repeats(repo, "90.days", 3) if r.kind == "files"]
    dis.record_decision(repo, finding.fingerprint, "neither", "one-off coincidence")
    assert [r for r in dis.mine_repeats(repo, "90.days", 3)
            if r.kind == "files"] == []


def test_ordering_is_deterministic(repo: Path) -> None:
    _pair_commits(repo, 4, "feat: unrelated words")
    first = dis.mine_repeats(repo, "90.days", 3)
    assert first == dis.mine_repeats(repo, "90.days", 3)
    assert [r.count for r in first] == sorted((r.count for r in first), reverse=True)


def test_cli_exits_0_with_findings_and_prints_the_question_and_evidence(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _pair_commits(repo, 3, "feat: unrelated words")
    assert dis.main(["--root", str(repo), "repeats"]) == 0
    out = capsys.readouterr().out
    assert "This has happened 3 times - turn it into a skill, a rule, or neither?" in out
    assert "evidence:" in out and "decide:" in out


def test_cli_json_and_empty_history_exit_0(
        repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _commit(repo, "feat: one", {"a.txt": "x\n"})
    assert dis.main(["--root", str(repo), "repeats", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["repeats"] == []
    assert dis.main(["--root", str(repo), "repeats"]) == 0


def test_cli_exits_2_outside_a_repository(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    assert dis.main(["--root", str(plain), "repeats"]) == 2
    assert "not a git repository" in capsys.readouterr().err

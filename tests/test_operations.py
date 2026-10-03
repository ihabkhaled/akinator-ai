"""Tests for the operations wiki (tools, env vars, repositories, installation).

Rule 11: every detector is shown firing on a planted tree and going silent when
the plant is removed. Secrets are built by concatenation so this file never
holds one.
"""

from __future__ import annotations

import json
from pathlib import Path

import extract_operations as eo

INFRA = "docs/wiki/infra"
TOKEN = "SECRET" + "TOKEN" + "9f3a"
ENVVAL = "hunter" + "2-" + "value"


def _w(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def _gen(root: Path) -> dict[str, str]:
    assert eo.main([str(root), "--write"]) == 0
    return {n: (root / INFRA / n).read_text(encoding="utf-8")
            for n in ("tools-and-commands.md", "environment-variables.md",
                      "repositories.md", "installation.md")}


def _tree(root: Path) -> None:
    _w(root, "package.json", json.dumps({
        "scripts": {"plantedscript": "node build.js"}, "engines": {"node": ">=20"},
        "workspaces": ["packages/*"]}))
    _w(root, "Makefile", ".PHONY: plantedtarget\nplantedtarget: ## builds the planted thing\n\techo hi\n")
    _w(root, "app.py", "import os\nx = os.environ['PLANTED_API_KEY']\ny = os.getenv('PLANTED_MODE', 'dev')\n")
    _w(root, ".env.example", f"PLANTED_EXAMPLE={ENVVAL}\n")
    _w(root, "package-lock.json", "{}")
    _w(root, "README.md", "# T\n\n## Installation\n\nrun it\n")
    _w(root, ".git/config",
       f'[remote "origin"]\n\turl = https://user:{TOKEN}@github.com/o/r.git\n')
    _w(root, ".git/HEAD", "ref: refs/heads/trunk\n")


def test_positive_each_page(tmp_path: Path) -> None:
    _tree(tmp_path)
    pages = _gen(tmp_path)
    tools = pages["tools-and-commands.md"]
    assert "npm run plantedscript" in tools and "make plantedtarget" in tools
    assert "builds the planted thing" in tools
    env = pages["environment-variables.md"]
    assert "PLANTED_API_KEY" in env and "PLANTED_EXAMPLE" in env and "PLANTED_MODE" in env
    key_row = next(l for l in env.splitlines() if "PLANTED_API_KEY" in l)
    assert key_row.endswith("| no | yes |")
    mode_row = next(l for l in env.splitlines() if "PLANTED_MODE" in l)
    assert "| yes | no |" in mode_row
    repos = pages["repositories.md"]
    assert "github.com/o/r.git" not in repos and "trunk" not in repos  # machine-local git state is never generated
    assert "packages/*" in repos
    inst = pages["installation.md"]
    assert "npm ci" in inst and "package-lock.json" in inst and "README.md:3" in inst
    assert ">=20" in inst


def test_mutation_removal_removes_row(tmp_path: Path) -> None:
    _tree(tmp_path)
    _gen(tmp_path)
    (tmp_path / "package.json").unlink()
    (tmp_path / "Makefile").unlink()
    (tmp_path / "app.py").unlink()
    (tmp_path / ".env.example").unlink()
    (tmp_path / "package-lock.json").unlink()
    (tmp_path / ".git" / "config").unlink()
    (tmp_path / "README.md").unlink()
    pages = _gen(tmp_path)
    assert "plantedscript" not in pages["tools-and-commands.md"]
    assert "plantedtarget" not in pages["tools-and-commands.md"]
    assert "PLANTED_API_KEY" not in pages["environment-variables.md"]
    assert eo.NOTHING in pages["environment-variables.md"]
    assert "github.com/o/r" not in pages["repositories.md"]
    assert "npm ci" not in pages["installation.md"]
    assert "README.md:3" not in pages["installation.md"]


def test_credentials_and_values_never_printed(tmp_path: Path) -> None:
    _tree(tmp_path)
    _w(tmp_path, ".gitmodules",
       f'[submodule "s"]\n\tpath = s\n\turl = https://bot:{TOKEN}@gitlab.com/o/s.git\n')
    _w(tmp_path, "package.json", json.dumps(
        {"scripts": {"deploy": f"curl https://u:{TOKEN}@x.io --token={TOKEN}"}}))
    pages = _gen(tmp_path)
    for text in pages.values():
        assert TOKEN not in text and ENVVAL not in text
    assert "gitlab.com/o/s.git" in pages["repositories.md"]
    assert eo.sanitize_url(f"git@github.com:o/r.git") == "github.com:o/r.git"
    assert eo.provider_of("dev.azure.com") == "azure"
    assert eo.provider_of("git.example.org") == "other"


def test_check_exit_codes(tmp_path: Path) -> None:
    _tree(tmp_path)
    assert eo.main([str(tmp_path), "--check"]) == 1
    _gen(tmp_path)
    assert eo.main([str(tmp_path), "--check"]) == 0
    _w(tmp_path, "Makefile", "other: ## new\n\techo\n")
    assert eo.main([str(tmp_path), "--check"]) == 1


def test_crlf_and_curated_preserved(tmp_path: Path) -> None:
    _tree(tmp_path)
    pages = _gen(tmp_path)
    assert eo.GAP in pages["installation.md"]
    path = tmp_path / INFRA / "installation.md"
    text = path.read_text(encoding="utf-8").replace(
        eo.GAP, "Curated: install the thing by hand.").replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))
    _w(tmp_path, "go.mod", "module x\n\ngo 1.22\n")
    assert eo.main([str(tmp_path), "--write"]) == 0
    raw = path.read_bytes().decode("utf-8")
    assert "Curated: install the thing by hand.\r\n" in raw
    assert "\r\n" in raw and "\n" not in raw.replace("\r\n", "")
    assert "go mod download" in raw


def test_deterministic(tmp_path: Path) -> None:
    _tree(tmp_path)
    a = _gen(tmp_path)
    b = _gen(tmp_path)
    assert a == b
    changes, errors = eo.plan(tmp_path)
    assert not changes and not errors


def test_used_by_capped_at_three(tmp_path: Path) -> None:
    for i in range(5):
        _w(tmp_path, f"m{i}.py", "import os\nos.getenv('MANY')\n")
    env = _gen(tmp_path)["environment-variables.md"]
    assert "+2 more" in env

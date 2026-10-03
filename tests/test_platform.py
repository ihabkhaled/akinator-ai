"""Tests for the platform wiki generator (extract_platform).

Per rules/11 each detector class is mutation-tested on a scratch tree: a planted
technology must appear with its file path, and removing it must remove the row.
Secrets are a hard invariant: a value planted in .env.example never reaches a page.
"""

from __future__ import annotations

import json
from pathlib import Path

import extract_platform as ep

WIKI = "docs/wiki"


def _w(root: Path, rel: str, content: str = "") -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.encode("utf-8"))
    return path


def _page(root: Path, key: str) -> str:
    ep.main([str(root), "--write"])
    return (root / WIKI / ep.PAGES[key][0]).read_text(encoding="utf-8")


def _pkg(deps: dict[str, str]) -> str:
    return json.dumps({"name": "x", "dependencies": deps})


def _mutation(tmp_path: Path, key: str, rel: str, content: str, needle: str,
              where: str) -> None:
    """Plant, assert row + path, remove, assert row gone."""
    planted = _w(tmp_path, rel, content)
    text = _page(tmp_path, key)
    assert any(needle in ln and where in ln for ln in text.splitlines()), text
    planted.unlink()
    assert needle not in _page(tmp_path, key)


def test_database_dependency_detected_and_removed(tmp_path: Path) -> None:
    _mutation(tmp_path, "data", "package.json", _pkg({"pg": "^8"}), "PostgreSQL", "`package.json`")


def test_compose_image_detected_and_removed(tmp_path: Path) -> None:
    _mutation(tmp_path, "data", "docker-compose.yml",
              "services:\n  c:\n    image: library/redis:7\n", "Redis", "`docker-compose.yml`")


def test_migration_dir_detected_and_removed(tmp_path: Path) -> None:
    _mutation(tmp_path, "data", "prisma/migrations/001/migration.sql", "select 1;",
              "Prisma migrations", "prisma/migrations/001/migration.sql")


def test_framework_and_react_dom_not_confused(tmp_path: Path) -> None:
    _w(tmp_path, "package.json", _pkg({"react-dom": "1"}))
    assert "| React |" not in _page(tmp_path, "services")
    _mutation(tmp_path, "services", "package.json", _pkg({"react": "1"}), "React", "`package.json`")


def test_entrypoint_and_dockerfile(tmp_path: Path) -> None:
    _mutation(tmp_path, "services", "svc/main.go", "package main", "Go entrypoints", "svc/main.go")
    _mutation(tmp_path, "services", "Dockerfile", "FROM x", "Dockerfiles", "`Dockerfile`")


def test_workspaces_detected(tmp_path: Path) -> None:
    _mutation(tmp_path, "services", "package.json",
              json.dumps({"workspaces": ["packages/*"]}), "npm workspaces", "`package.json`")


def test_logging_dep_and_health_endpoint(tmp_path: Path) -> None:
    _mutation(tmp_path, "observability", "package.json", _pkg({"pino": "1"}), "pino", "`package.json`")
    _mutation(tmp_path, "observability", "src/app.py", "route('/healthz')", "Health / readiness", "src/app.py")


def test_health_in_test_files_ignored(tmp_path: Path) -> None:
    _w(tmp_path, "tests/test_x.py", "get('/health')")
    assert "test_x" not in _page(tmp_path, "observability")


def test_linter_config_and_hooks_and_ci(tmp_path: Path) -> None:
    _mutation(tmp_path, "standards", ".eslintrc.json", "{}", "ESLint", "`.eslintrc.json`")
    _mutation(tmp_path, "standards", "pyproject.toml", "[tool.ruff]\nline-length=99\n", "Ruff", "`pyproject.toml`")
    _mutation(tmp_path, "standards", ".pre-commit-config.yaml", "repos: []", "pre-commit config", ".pre-commit-config.yaml")
    _mutation(tmp_path, "standards", ".github/workflows/ci.yml", "on: push", "GitHub Actions", "ci.yml")
    _mutation(tmp_path, "standards", ".github/CODEOWNERS", "* @a", "CODEOWNERS", "CODEOWNERS")


def test_languages_counted_from_extensions(tmp_path: Path) -> None:
    _w(tmp_path, "a.py", "")
    _w(tmp_path, "b.py", "")
    _w(tmp_path, "c.go", "")
    text = _page(tmp_path, "standards")
    assert "Python (2 files)" in text and "Go (1 file)" in text
    assert text.index("Python (2 files)") < text.index("Go (1 file)")


def test_tsconfig_paths(tmp_path: Path) -> None:
    _mutation(tmp_path, "standards", "tsconfig.json",
              '{"compilerOptions":{"paths":{"@app/*":["src/*"]}}}', "@app/*", "`tsconfig.json`")


def test_env_names_only_never_values(tmp_path: Path) -> None:
    _w(tmp_path, ".env.example", "STRIPE_KEY=sk_live_SUPERSECRET123\nDATABASE_URL=postgres://u:pw@h/db\nPLAIN=1\n")
    _w(tmp_path, ".env", "REAL_SECRET=hunter2\n")
    _w(tmp_path, ".gitignore", ".env\n")
    for key in ep.PAGES:
        text = _page(tmp_path, key)
        assert "SUPERSECRET123" not in text and "pw@h" not in text and "hunter2" not in text
        assert "REAL_SECRET" not in text
    sec = _page(tmp_path, "security")
    assert "`STRIPE_KEY`" in sec and "`PLAIN`" in sec
    assert "`.env` is gitignored" in sec
    assert "`STRIPE_KEY`" in _page(tmp_path, "integrations")
    assert "`PLAIN`" not in _page(tmp_path, "integrations")
    assert "`DATABASE_URL`" in _page(tmp_path, "data")


def test_gitignore_missing_rule_is_reported(tmp_path: Path) -> None:
    _w(tmp_path, ".gitignore", "node_modules\n")
    assert "No `.gitignore` rule covers `.env`" in _page(tmp_path, "security")


def test_security_policy_scanning_and_auth(tmp_path: Path) -> None:
    _mutation(tmp_path, "security", "SECURITY.md", "# s", "SECURITY.md", "`SECURITY.md`")
    _mutation(tmp_path, "security", ".github/dependabot.yml", "version: 2", "Dependabot", "dependabot.yml")
    _mutation(tmp_path, "security", "package.json", _pkg({"passport": "1"}), "Passport", "`package.json`")
    _mutation(tmp_path, "security", ".github/workflows/s.yml", "run: pip-audit", "pip-audit", "s.yml")


def test_integration_sdk(tmp_path: Path) -> None:
    _mutation(tmp_path, "integrations", "package.json", _pkg({"stripe": "1"}), "Stripe", "`package.json`")
    _mutation(tmp_path, "integrations", "package.json", _pkg({"@aws-sdk/client-s3": "1"}), "AWS", "`package.json`")


def test_nothing_detected_is_honest(tmp_path: Path) -> None:
    text = _page(tmp_path, "data")
    assert text.count(ep.NOTHING) == 6
    assert ep.GAP in text


def test_check_exit_codes_and_idempotence(tmp_path: Path) -> None:
    assert ep.main([str(tmp_path), "--check"]) == 1
    assert ep.main([str(tmp_path), "--write"]) == 0
    assert ep.main([str(tmp_path), "--check"]) == 0
    _w(tmp_path, "package.json", _pkg({"pg": "1"}))
    assert ep.main([str(tmp_path), "--check"]) == 1


def test_curated_text_and_crlf_preserved(tmp_path: Path) -> None:
    page = tmp_path / WIKI / "data" / "README.md"
    ep.main([str(tmp_path), "--write"])
    text = page.read_bytes().decode("utf-8")
    page.write_bytes(text.replace("\n", "\r\n").replace(ep.GAP, "Owner wrote this.").encode("utf-8"))
    _w(tmp_path, "package.json", _pkg({"pg": "1"}))
    ep.main([str(tmp_path), "--write"])
    out = page.read_bytes().decode("utf-8")
    assert "Owner wrote this." in out and "PostgreSQL" in out
    assert "\r\n" in out and "\n" not in out.replace("\r\n", "")


def test_text_outside_markers_untouched_and_unmarked_page_gets_block(tmp_path: Path) -> None:
    page = _w(tmp_path, f"{WIKI}/security/README.md", "# Mine\n\nhand written\n")
    ep.main([str(tmp_path), "--write"])
    out = page.read_text(encoding="utf-8")
    assert out.startswith("# Mine\n") and out.rstrip().endswith("hand written")
    assert ep.BEGIN in out


def test_broken_block_exit_2(tmp_path: Path) -> None:
    _w(tmp_path, f"{WIKI}/data/README.md", f"# D\n{ep.BEGIN}\nno end\n")
    assert ep.main([str(tmp_path), "--write"]) == 2


def test_skip_dirs_ignored(tmp_path: Path) -> None:
    _w(tmp_path, "node_modules/x/Dockerfile", "FROM x")
    assert "node_modules" not in _page(tmp_path, "services")


def test_output_deterministic(tmp_path: Path) -> None:
    _w(tmp_path, "package.json", _pkg({"pg": "1", "redis": "1"}))
    first = _page(tmp_path, "data")
    assert _page(tmp_path, "data") == first


def test_machine_local_cache_never_reaches_a_page(tmp_path):
    """.ai/cache exists on one machine only; listing it makes CI disagree with a clone."""
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    cache = tmp_path / ".ai" / "cache"
    cache.mkdir(parents=True)
    (cache / ".gitignore").write_text("*\n", encoding="utf-8")
    assert not [r for r in ep.walk(tmp_path) if r.startswith(".ai/cache/")]

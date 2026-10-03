"""Tests for akinator_sensitive - the sensitive data register, scan and guard.

Per rules/11 every invariant has a firing test and a silent twin. Fake secrets
are assembled at runtime by concatenation, so this file holds no literal secret
for this repository's own scan or for push protection to find.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import akinator_sensitive as sens

AWS = "AKIA" + "IOSFODNN7" + "EXAMPLQ"
GH = "ghp" + "_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8"
STRIPE = "sk" + "_live_" + "4eC39HqLyjWDarjtT1zdp7dc"
KEY_BLOCK = "-----BEGIN " + "RSA PRIVATE KEY-----"
JWT = "eyJhbGciOiJIUzI1NiJ9" + "." + "eyJzdWIiOiIxMjM0NTY3ODkwIn0" + "." + "dBjftJeZ4CVPmB92K27uhbUJU1p1r"
URL = "postgres://app:" + "s3cr3tPw9x" + "@db.internal/app"
ENTROPY = "q8Zr2Lm9Xv4Tb7Ky1Wp3"


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                    *args], check=True, capture_output=True)


def repo(tmp_path: Path, files: dict[str, str], track: bool = True) -> Path:
    git(tmp_path, "init", "-q")
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode("utf-8"))
    if track:
        git(tmp_path, "add", "-A")
    return tmp_path


def run(root: Path, *argv: str) -> int:
    return sens.main(["--root", str(root), *argv])


# ---- scan ---------------------------------------------------------------

@pytest.mark.parametrize("kind,value", [
    ("aws-key-id", AWS), ("github-token", GH), ("stripe-live-key", STRIPE),
    ("private-key", KEY_BLOCK), ("jwt", JWT), ("url-credentials", URL),
    ("high-entropy-assignment", ENTROPY),
])
def test_scan_fires_on_every_shape_and_never_prints_the_value(tmp_path, capsys, kind, value):
    line = f"API_TOKEN={value}" if kind == "high-entropy-assignment" else f"x = '{value}'"
    root = repo(tmp_path, {"src/app.py": line + "\n"})
    assert run(root, "scan") == 1
    out = capsys.readouterr()
    assert f"src/app.py:1  {kind}" in out.out
    assert value not in out.out + out.err
    assert value[4:] not in out.out + out.err


def test_scan_json_has_fingerprint_not_value(tmp_path, capsys):
    root = repo(tmp_path, {"a.py": f"k = '{AWS}'\n"})
    assert run(root, "scan", "--json") == 1
    out = capsys.readouterr().out
    hit = json.loads(out)[0]
    assert hit["fingerprint"].startswith("AKIA\u2026") and AWS not in out


def test_scan_is_silent_on_a_healthy_tree(tmp_path):
    root = repo(tmp_path, {
        "a.py": "password = os.environ['PASSWORD']\nurl = 'postgres://user:password@localhost/db'\n",
        "b.md": "Set API_TOKEN=<your-token> and SECRET_KEY=changeme-please-now\n",
    })
    assert run(root, "scan") == 0


def test_scan_skips_binaries_lockfiles_and_big_files(tmp_path):
    big = f"k = '{AWS}'\n" + "x" * (sens.MAX_BYTES + 1)
    root = repo(tmp_path, {"package-lock.json": f"{AWS}\n", "x.min.js": f"{AWS}\n",
                           "big.txt": big})
    (root / "bin.dat").write_bytes(b"\0\0" + AWS.encode())
    git(root, "add", "-A")
    assert run(root, "scan") == 0


def test_inline_marker_allows_but_only_that_line(tmp_path):
    root = repo(tmp_path, {"a.py": f"a = '{AWS}'  # akinator:allow-secret\nb = '{AWS}'\n"})
    hits = sens.scan(root)
    assert [h["line"] for h in hits] == [2]


def test_config_allowlist_by_glob_and_kind(tmp_path):
    cfg = json.dumps({"sensitive": {"allow": ["fixtures/*:aws-key-id"]}})
    root = repo(tmp_path, {"fixtures/a.txt": AWS + "\n", "src/b.txt": AWS + "\n",
                           "fixtures/c.txt": GH + "\n", ".ai/config.json": cfg})
    found = {(h["path"], h["kind"]) for h in sens.scan(root)}
    assert found == {("src/b.txt", "aws-key-id"), ("fixtures/c.txt", "github-token")}


# ---- guard --------------------------------------------------------------

def test_guard_fires_on_stdin_and_files_and_hides_value(tmp_path, capsys, monkeypatch):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO(f"note: token {GH}\n"))
    assert sens.main(["guard", "--stdin"]) == 1
    out = capsys.readouterr()
    assert "<stdin>:1  github-token" in out.out and GH not in out.out + out.err
    f = tmp_path / "memo.md"
    f.write_text(f"key {AWS}\n", encoding="utf-8")
    assert sens.main(["guard", str(f)]) == 1


def test_guard_passes_clean_text_and_missing_file_is_exit_2(tmp_path, monkeypatch):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("The ledger redacts tokens before writing.\n"))
    assert sens.main(["guard", "--stdin"]) == 0
    assert sens.main(["guard", str(tmp_path / "nope.md")]) == 2


# ---- register -----------------------------------------------------------

PAGE = "docs/wiki/security/sensitive-data.md"


def test_secret_files_tracked_is_high_ignored_is_not(tmp_path):
    root = repo(tmp_path, {".gitignore": "ignored.pem\n", "tracked.pem": "x\n",
                           "ignored.pem": "x\n", ".env.example": "API_TOKEN=\n"})
    git(root, "add", "-f", "tracked.pem")
    files = sens.collect(root)["files"]
    assert files["tracked.pem"] == (True, "no")
    assert files["ignored.pem"] == (False, "yes")
    assert ".env.example" not in files
    block = sens.render_block(sens.collect(root))
    assert "| `tracked.pem` | yes | no | HIGH |" in block
    assert "| `ignored.pem` | no | yes | ok |" in block


def test_env_names_listed_values_never(tmp_path):
    root = repo(tmp_path, {
        ".env.example": "DATABASE_PASSWORD=" + ENTROPY + "\nPORT=80\n",
        ".github/workflows/ci.yml": "env:\n  T: ${{ secrets.DEPLOY_TOKEN }}\n",
    })
    block = sens.render_block(sens.collect(root))
    assert "`DATABASE_PASSWORD`" in block and "`DEPLOY_TOKEN`" in block
    assert "PORT" not in block and ENTROPY not in block


def test_fields_and_logging_found_with_class(tmp_path):
    root = repo(tmp_path, {
        "db/schema.sql": "CREATE TABLE u (\n  email VARCHAR(80),\n  card_number TEXT,\n  id INT\n);\n",
        "src/models/user.py": "class U:\n    phone: str\n    nickname: str\n",
        "src/svc.py": "logger.info('sent to %s', user.email)\nlogger.info('ok')\n",
    })
    block = sens.render_block(sens.collect(root))
    assert "`db/schema.sql:2` `email` - PII" in block
    assert "`db/schema.sql:3` `card_number` - financial" in block
    assert "`src/models/user.py:2` `phone` - PII" in block
    assert "nickname" not in block and "`id`" not in block
    assert "`src/svc.py:1`" in block and "`src/svc.py:2`" not in block


def test_register_creates_page_with_gap_markers_then_check_passes(tmp_path):
    root = repo(tmp_path, {".env.example": "API_TOKEN=\n"})
    assert run(root, "register", "--check") == 1  # missing
    assert run(root, "register", "--write") == 0
    page = (root / PAGE).read_text(encoding="utf-8")
    assert f"Who rotates each secret and how: {sens.GAP}" in page
    assert run(root, "register", "--check") == 0


def test_register_check_fires_on_drift(tmp_path):
    root = repo(tmp_path, {".env.example": "API_TOKEN=\n"})
    run(root, "register", "--write")
    (root / ".env.example").write_text("API_TOKEN=\nNEW_SECRET=\n", encoding="utf-8")
    git(root, "add", "-A")
    assert run(root, "register", "--check") == 1
    assert run(root, "register", "--write") == 0
    assert run(root, "register", "--check") == 0


def test_register_preserves_curated_text_and_crlf_byte_for_byte(tmp_path):
    root = repo(tmp_path, {".env.example": "API_TOKEN=\n"})
    run(root, "register", "--write")
    page = root / PAGE
    text = page.read_bytes().decode("utf-8").replace("\r\n", "\n")
    curated = text.replace(f"Who rotates each secret and how: {sens.GAP}",
                           "Who rotates each secret and how: Dana, quarterly.")
    page.write_bytes(curated.replace("\n", "\r\n").encode("utf-8"))
    (root / ".env.example").write_text("API_TOKEN=\nB_SECRET=\n", encoding="utf-8")
    git(root, "add", "-A")
    assert run(root, "register", "--write") == 0
    after = page.read_bytes()
    assert b"Dana, quarterly." in after and b"B_SECRET" in after
    assert b"\n" not in after.replace(b"\r\n", b"")  # still pure CRLF
    head = curated.split(sens.BEGIN)[0].replace("\n", "\r\n").encode()
    tail = curated.split(sens.END)[1].replace("\n", "\r\n").encode()
    assert after.startswith(head) and after.endswith(tail)


def test_register_refuses_a_broken_block(tmp_path):
    root = repo(tmp_path, {})
    (root / "docs/wiki/security").mkdir(parents=True)
    (root / PAGE).write_text(f"# S\n{sens.BEGIN}\nno end\n", encoding="utf-8")
    assert run(root, "register", "--write") == 2


def test_no_git_falls_back_to_walk(tmp_path):
    (tmp_path / "a.py").write_text(f"k = '{AWS}'\n", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "b.py").write_text(f"k = '{AWS}'\n", encoding="utf-8")
    assert [h["path"] for h in sens.scan(tmp_path)] == ["a.py"]

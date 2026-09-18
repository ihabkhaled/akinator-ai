"""Structural tests: the plugin satisfies the platform contracts it claims.

These verify the contracts documented in `docs/compatibility.md`. When a
platform contract moves, one of these fails - which is the point. A silent
divergence between what the plugin ships and what the platform reads is the
failure this file exists to prevent.
"""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path

import pytest

from conftest import frontmatter

KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# The twelve loop stations, and the station reference each one routes to
# inside the one skill. Station 2 (RESOLVE) and station 5 (IMPLEMENT) are
# carried by the creed reference, `akinator`.
LOOP_STATIONS = {
    "ASK": "akinator-intake",
    "RESOLVE": "akinator",
    "AUDIT": "akinator-audit",
    "PLAN": "akinator-plan",
    "IMPLEMENT": "akinator",
    "DOCUMENT": "akinator-document-change",
    "SKILLIFY": "akinator-skillify",
    "RULE": "akinator-rule-forge",
    "CONTEXTIFY": "akinator-contextify",
    "MEMOIZE": "akinator-memoize",
    "INDEX+SYNC": "akinator-index-sync",
    "VERIFY": "akinator-gate-economy",
}

REQUIRED_SKILL_SECTIONS = (
    "when to use",
    "when not to use",
    "procedure",
    "definition of done",
)


# --------------------------------------------------------------------------
# Claude Code plugin contract
# --------------------------------------------------------------------------

def test_plugin_manifest_is_valid(plugin_manifest: dict) -> None:
    assert plugin_manifest["name"] == "akinator"
    assert KEBAB.match(plugin_manifest["name"])
    assert re.match(r"^\d+\.\d+\.\d+$", plugin_manifest["version"])
    assert plugin_manifest["description"].strip()
    assert plugin_manifest["author"]["name"].strip()


def test_manifest_lives_in_claude_plugin_dir(repo: Path) -> None:
    """The manifest must be in .claude-plugin/, components at plugin root."""
    assert (repo / ".claude-plugin" / "plugin.json").is_file()
    # No commands/: the one skill is the one command. See
    # test_there_are_no_command_files.
    for component in ("skills", "agents", "hooks"):
        assert (repo / component).is_dir(), f"{component}/ must be at plugin root"
        assert not (repo / ".claude-plugin" / component).exists(), (
            f"{component}/ must not be nested inside .claude-plugin/"
        )


def test_marketplace_manifest_is_valid(marketplace_manifest: dict) -> None:
    assert marketplace_manifest["name"]
    assert marketplace_manifest["owner"]["name"]
    plugins = marketplace_manifest["plugins"]
    assert len(plugins) == 1
    assert plugins[0]["name"] == "akinator"
    assert plugins[0]["source"] == "./"


def test_marketplace_version_matches_plugin_version(
    marketplace_manifest: dict, plugin_manifest: dict
) -> None:
    assert marketplace_manifest["plugins"][0]["version"] == plugin_manifest["version"]


def test_hooks_json_uses_the_plugin_format(repo: Path) -> None:
    """Plugin hooks.json wraps events in a `hooks` key; settings format does not."""
    data = json.loads((repo / "hooks" / "hooks.json").read_text("utf-8"))
    assert "hooks" in data, "plugin hooks.json requires the `hooks` wrapper"
    assert "SessionStart" in data["hooks"]

    hook = data["hooks"]["SessionStart"][0]["hooks"][0]
    # Exec form - `command` plus `args` - not shell form. The shell form
    # `sh "${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh"` exits 126 on Claude
    # Code 2.1.154 under Git Bash ("cannot execute binary file"), so the
    # always-on contract silently never reached CLI sessions on Windows.
    assert hook.get("command") == "sh", "the hook runs sh directly (exec form)"
    args = hook.get("args") or []
    assert args and "${CLAUDE_PLUGIN_ROOT}" in args[0], (
        "the script path must be an exec-form argument built on ${CLAUDE_PLUGIN_ROOT}"
    )
    assert "${CLAUDE_PLUGIN_ROOT}" not in hook["command"], (
        "a placeholder inside a shell-form command string is the form that broke"
    )

    script = repo / "hooks" / "session-start.sh"
    assert script.is_file(), "the hook command must point at a script that exists"


def test_no_hardcoded_paths_in_hooks(repo: Path) -> None:
    text = (repo / "hooks" / "hooks.json").read_text("utf-8")
    for forbidden in ("/Users/", "/home/", "C:\\", "~/"):
        assert forbidden not in text


# --------------------------------------------------------------------------
# One skill, one command
#
# The owner's requirement, stated three times: exactly one Akinator entry in the
# "/" menu of Claude Code, Codex and Cursor. It was broken while commands/ held
# one file, because Claude lists every skill in "/" too - 21 skills plus the
# command made 22 entries. Codex cannot hide a skill from its "$" picker at all,
# and Cursor lists every folder in .agents/skills. So the only design that gives
# one entry everywhere is one skill: the stations are reference files inside it.
# See docs/adr/0009-one-skill-one-command-one-installer.md.
# --------------------------------------------------------------------------

SKILL_DIR = Path("skills") / "everything"

# Codex injects an explicitly invoked skill's SKILL.md truncated at this many
# bytes (codex-rs ext/skills render.rs MAX_SKILL_PROMPT_BYTES). A bigger file
# is cut off mid-procedure on `$akinator`.
CODEX_SKILL_PROMPT_BYTES = 8000


def test_there_is_exactly_one_skill(repo: Path, skill_paths: list[Path]) -> None:
    rel = [p.relative_to(repo).as_posix() for p in skill_paths]
    assert rel == ["skills/everything/SKILL.md"], (
        f"Akinator ships exactly one skill; found {rel}. Every SKILL.md is an "
        "entry in the / menu on Claude Code and in the $ picker on Codex."
    )
    assert frontmatter(skill_paths[0]).get("name") == "everything", (
        "the skill must be named 'everything' - the plugin namespace supplies "
        "'akinator', making it /akinator:everything"
    )


def test_there_are_no_command_files(repo: Path) -> None:
    """The skill IS the command. A commands/ file named `everything` would be a
    second /akinator:everything entry; any other name would be a second command."""
    commands = repo / "commands"
    assert not (commands.is_dir() and any(commands.glob("*.md"))), (
        "commands/ must not exist - the one skill is the one command"
    )


def test_the_one_skill_has_six_parts(skill_paths: list[Path]) -> None:
    """Enforcement for rules/02 - the plugin must not ship a skill it would
    reject in a target repository."""
    failures: list[str] = []
    for path in skill_paths:
        meta = frontmatter(path)
        text = path.read_text(encoding="utf-8").lower()
        if not meta.get("name") or not KEBAB.match(meta["name"]):
            failures.append(f"{path}: name missing or not kebab-case")
        elif meta["name"] != path.parent.name:
            failures.append(f"{path}: name != directory '{path.parent.name}'")
        description = meta.get("description", "")
        if not description.lower().startswith("use "):
            failures.append(f"{path}: description must be a 'Use ...' trigger")
        if len(description) > 1024:
            failures.append(f"{path}: description is {len(description)} chars; "
                            "Codex and the Agent Skills spec cap it at 1024")
        for section in REQUIRED_SKILL_SECTIONS:
            if section not in text:
                failures.append(f"{path}: missing the '{section}' section")
        if "failure mode" not in text:
            failures.append(f"{path}: missing a failure-modes section")
    assert not failures, "\n".join(failures)


def test_the_skill_fits_codex_explicit_invocation(repo: Path) -> None:
    """Codex truncates an explicitly invoked SKILL.md at 8,000 bytes. The full
    procedure lives in a reference for exactly this reason."""
    import build_codex_pack as pack

    for label, text in (
        ("canonical", (repo / SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")),
        ("projected", pack.plan(repo)[f"{pack.TARGET}/SKILL.md"]),
    ):
        size = len(text.encode("utf-8"))
        assert size <= CODEX_SKILL_PROMPT_BYTES, (
            f"the {label} SKILL.md is {size} bytes; Codex would cut it at "
            f"{CODEX_SKILL_PROMPT_BYTES}. Move detail into references/."
        )


@pytest.mark.parametrize("station,station_id", sorted(LOOP_STATIONS.items()))
def test_every_loop_station_has_a_reference(
    repo: Path, station: str, station_id: str
) -> None:
    """Enforcement for rules/01: the knowledge delta always has somewhere to go,
    and the skill can reach it."""
    reference = repo / SKILL_DIR / "references" / f"{station_id}.md"
    assert reference.is_file(), f"station {station} -> {station_id} has no reference"
    skill = (repo / SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert f"(references/{station_id}.md)" in skill, (
        f"the skill never links {station_id}; an unlinked station is never opened"
    )


def test_every_reference_is_reachable_from_the_skill(repo: Path) -> None:
    """A reference nothing links to is a station nobody will ever open."""
    base = repo / SKILL_DIR
    linked = (base / "SKILL.md").read_text(encoding="utf-8")
    missing = sorted(p.name for p in (base / "references").glob("*.md")
                     if f"(references/{p.name})" not in linked)
    assert not missing, f"references not linked from SKILL.md: {missing}"


def test_no_reference_can_be_discovered_as_a_skill(repo: Path) -> None:
    """A reference with skill frontmatter, or a stray SKILL.md below the skill,
    is one step from becoming a second / entry again."""
    base = repo / SKILL_DIR
    nested = sorted(p.relative_to(base).as_posix() for p in base.rglob("SKILL.md")
                    if p != base / "SKILL.md")
    assert not nested, f"SKILL.md files inside the one skill: {nested}"
    fronted = sorted(p.name for p in (base / "references").glob("*.md")
                     if p.read_text(encoding="utf-8").startswith("---"))
    assert not fronted, f"references carrying skill frontmatter: {fronted}"


def test_the_skill_runs_its_tools_from_its_own_folder(repo: Path) -> None:
    """Every tool the skill tells an agent to run must travel with it.

    The pre-consolidation skill said `python scripts/akinator_ledger.py ...` -
    a path that exists only in Akinator's own checkout, so in every repository
    Akinator was installed into, the procedure's commands failed.
    """
    base = repo / SKILL_DIR
    texts = [base / "SKILL.md", *sorted((base / "references").glob("*.md"))]
    bad: list[str] = []
    used: set[str] = set()
    for path in texts:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"python3? (\S+\.py)", text):
            command = match.group(1)
            if not command.startswith("<skill>/scripts/"):
                bad.append(f"{path.name}: python {command}")
            else:
                used.add(command.split("/")[-1])
    assert not bad, "tools named outside <skill>/scripts/:\n" + "\n".join(bad)
    absent = sorted(t for t in used if not (base / "scripts" / t).is_file())
    assert not absent, f"the skill runs tools it does not ship: {absent}"


# --------------------------------------------------------------------------
# Agents
# --------------------------------------------------------------------------

def test_boardroom_agents_exist(repo: Path) -> None:
    expected = {
        "akinator-business-owner", "akinator-cto", "akinator-product-owner",
        "akinator-ops", "akinator-analyst", "akinator-librarian", "akinator-pm",
    }
    found = {p.stem for p in (repo / "agents").glob("*.md")}
    assert expected <= found, f"missing agents: {sorted(expected - found)}"


def test_every_agent_has_name_and_description(agent_paths: list[Path]) -> None:
    for path in agent_paths:
        meta = frontmatter(path)
        assert meta.get("name") == path.stem, f"{path}: name must match filename"
        assert meta.get("description"), f"{path}: no description"


# --------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------

def test_rules_are_numbered_and_unique(rule_paths: list[Path]) -> None:
    numbers = []
    for path in rule_paths:
        match = re.match(r"^(\d{2})-", path.name)
        assert match, f"{path}: rules are numbered NN-name.md"
        numbers.append(match.group(1))
    assert len(numbers) == len(set(numbers)), "duplicate rule numbers"


def test_every_rule_has_the_required_sections(rule_paths: list[Path]) -> None:
    required = ("purpose", "applies to", "mandatory rules", "enforcement")
    failures = []
    for path in rule_paths:
        text = path.read_text(encoding="utf-8").lower()
        for section in required:
            if section not in text:
                failures.append(f"{path}: missing '{section}'")
    assert not failures, "\n".join(failures)


# --------------------------------------------------------------------------
# Routers
# --------------------------------------------------------------------------

ROUTERS = ("CLAUDE.md", "AGENTS.md", "CODEX.md")


def test_routers_exist(repo: Path) -> None:
    for name in ROUTERS:
        assert (repo / name).is_file(), f"{name} is missing"


def test_routers_agree(repo: Path) -> None:
    """Enforcement for rules/04: no router omits knowledge the others carry.

    Compares the knowledge-layer paths each router references. A router carrying
    an intentional-divergence marker is exempt, which is how genuinely
    tool-specific content is distinguished from rot.
    """
    import akinator_coverage as cov

    knowledge = re.compile(r"`((?:rules|skills|context|memory|docs)/[^`]+)`")

    referenced: dict[str, set[str]] = {}
    for name in ROUTERS:
        text = (repo / name).read_text(encoding="utf-8")
        shared, _ = cov.strip_tool_specific(text)
        referenced[name] = {
            t for t in knowledge.findall(shared)
            if "*" not in t and (repo / t).exists()
        }

    union: set[str] = set().union(*referenced.values())
    for name, targets in referenced.items():
        missing = sorted(union - targets)
        assert not missing, f"{name} omits knowledge other routers carry: {missing}"


def test_routers_stay_thin(repo: Path) -> None:
    """A router that has become a document has started to fork from its source."""
    for name in ROUTERS:
        lines = (repo / name).read_text(encoding="utf-8").splitlines()
        assert len(lines) < 200, (
            f"{name} is {len(lines)} lines - routers are indexes, not documents. "
            "Move the content to docs/ and link it."
        )


# --------------------------------------------------------------------------
# Templates
# --------------------------------------------------------------------------

EXPECTED_TEMPLATES = (
    "rule.md", "skill.md", "context-map.md", "memory.md", "adr.md",
    "business-logic.md", "product-feature.md", "ops-runbook.md", "router.md",
    "onboarding-mapping.md",
)


@pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
def test_template_exists_with_a_filled_example(repo: Path, name: str) -> None:
    assert (repo / "templates" / name).is_file(), f"templates/{name} missing"
    assert (repo / "templates" / "examples" / name).is_file(), (
        f"templates/examples/{name} missing - every template ships a filled example"
    )


FENCE = re.compile(r"^[ \t]*(?:```|~~~).*?^[ \t]*(?:```|~~~)[ \t]*$",
                   re.MULTILINE | re.DOTALL)


@pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
def test_filled_examples_have_no_placeholders(repo: Path, name: str) -> None:
    """A filled example with template placeholders left in it is not filled.

    Two exclusions, both deliberate:
      - blockquote lines carry the "this is an example" preamble;
      - fenced code may legitimately contain shell placeholders such as
        <backup-id-from-step-2>, which are part of the illustrated command, not
        an unfilled template section.
    """
    text = (repo / "templates" / "examples" / name).read_text(encoding="utf-8")
    prose = FENCE.sub("\n", text)
    body = "\n".join(
        line for line in prose.splitlines() if not line.lstrip().startswith(">")
    )
    leftovers = re.findall(r"<[a-z][a-z0-9 _/-]{2,}>", body)
    assert not leftovers, f"templates/examples/{name} has placeholders: {leftovers}"


@pytest.mark.parametrize("name", EXPECTED_TEMPLATES)
def test_templates_still_have_placeholders(repo: Path, name: str) -> None:
    """The converse: a template with no placeholders is an example, not a template."""
    text = (repo / "templates" / name).read_text(encoding="utf-8")
    assert re.search(r"<[a-z][a-z0-9 _/-]{2,}>", text), (
        f"templates/{name} has no placeholders - it reads as a filled example"
    )


# --------------------------------------------------------------------------
# Codex contract
# --------------------------------------------------------------------------

def test_codex_manifest_is_valid(codex_manifest: dict) -> None:
    for key in ("name", "version", "description", "author", "interface"):
        assert key in codex_manifest, f"missing required field: {key}"
    assert codex_manifest["author"]["name"]

    interface = codex_manifest["interface"]
    for key in ("displayName", "shortDescription", "longDescription",
                "developerName", "category", "capabilities"):
        assert interface.get(key), f"missing required interface field: {key}"


def test_codex_manifest_rejects_unsupported_fields(codex_manifest: dict) -> None:
    """Codex validation rejects `hooks` in the plugin manifest."""
    assert "hooks" not in codex_manifest


def test_codex_manifest_has_no_placeholders(codex_manifest: dict) -> None:
    assert "TODO" not in json.dumps(codex_manifest)


def test_codex_manifest_urls_are_absolute_https(codex_manifest: dict) -> None:
    for key, value in codex_manifest.get("interface", {}).items():
        if key.endswith("URL"):
            assert value.startswith("https://"), f"{key} must be absolute https"


def test_codex_manifest_assets_exist(repo: Path, codex_manifest: dict) -> None:
    """Asset paths must point at real files inside the plugin."""
    for key in ("composerIcon", "logo", "logoDark"):
        value = codex_manifest.get("interface", {}).get(key)
        if value and not value.startswith("http"):
            assert (repo / value.lstrip("./")).is_file(), (
                f"interface.{key} points at a file that does not exist: {value}"
            )


def test_versions_agree_across_manifests(
    plugin_manifest: dict, codex_manifest: dict
) -> None:
    assert plugin_manifest["version"] == codex_manifest["version"]


# --------------------------------------------------------------------------
# Plugin packaging
# --------------------------------------------------------------------------

def test_skills_dir_holds_only_skill_directories(repo: Path) -> None:
    """Enforcement for rules/08.

    Both platforms import skills by scanning `skills/` for subdirectories
    containing SKILL.md. A loose file there is not imported, and Codex
    validation rejects the plugin for it. The usual offender is a README index,
    which is the right instinct in a normal repo and the wrong one in a plugin.
    """
    loose = sorted(p.name for p in (repo / "skills").iterdir() if p.is_file())
    assert not loose, (
        f"files directly under skills/ are not imported as skills: {loose}. "
        "Move an index to docs/skills.md, or a support file into its skill's "
        "own directory (rules/08-skills-dir-holds-only-skill-directories.md)."
    )

    empty = sorted(
        p.name for p in (repo / "skills").iterdir()
        if p.is_dir() and not (p / "SKILL.md").is_file()
    )
    assert not empty, f"skill directories without a SKILL.md: {empty}"


def test_skills_index_lives_outside_skills_dir(repo: Path) -> None:
    assert (repo / "docs" / "skills.md").is_file()
    assert not (repo / "skills" / "README.md").exists()


# --------------------------------------------------------------------------
# Brand assets - required by Codex validation
# --------------------------------------------------------------------------

def _png_dimensions(path: Path) -> tuple[int, int, int, int]:
    """(width, height, bit_depth, colour_type) from a PNG's IHDR."""
    raw = path.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    assert raw[12:16] == b"IHDR", f"{path} has no IHDR first"
    width, height, depth, colour = struct.unpack(">IIBB", raw[16:26])
    return width, height, depth, colour


REQUIRED_ASSET_FIELDS = ("composerIcon", "logo")


@pytest.mark.parametrize("field", REQUIRED_ASSET_FIELDS)
def test_codex_manifest_declares_required_asset(
    codex_manifest: dict, field: str
) -> None:
    """Codex validation requires both, and requires them to be square images."""
    value = codex_manifest["interface"].get(field)
    assert value, f"interface.{field} is required by Codex plugin validation"
    assert value.startswith("./"), f"interface.{field} must be a plugin-relative path"
    assert value.lower().endswith(".png")


@pytest.mark.parametrize("field", REQUIRED_ASSET_FIELDS)
def test_required_asset_is_a_square_png(
    repo: Path, codex_manifest: dict, field: str
) -> None:
    value = codex_manifest["interface"][field]
    path = repo / value[2:]
    assert path.is_file(), f"interface.{field} points at a missing file: {value}"

    width, height, depth, colour = _png_dimensions(path)
    assert width == height, f"{value} must be square, got {width}x{height}"
    assert width >= 256, f"{value} is {width}px - too small for a plugin icon"
    assert depth == 8 and colour == 6, f"{value} must be 8-bit RGBA"


def test_adr_numbers_are_unique(repo: Path) -> None:
    """Two records once shared 0006: the always-on ADR was filed under a number
    `0006-index-completeness-...` already held, by an agent that never listed the
    directory. Nothing noticed - both files were reachable, both were indexed
    (one as a loose bullet under the table), and every check stayed green.

    ADR numbers are cited by number alone ("the tier ADR 0006 put CI on"), so a
    collision makes every such citation ambiguous.
    """
    from collections import Counter

    numbers = Counter(
        path.name.split("-", 1)[0]
        for path in (repo / "docs" / "adr").glob("[0-9][0-9][0-9][0-9]-*.md")
    )
    duplicated = sorted(n for n, count in numbers.items() if count > 1)
    assert not duplicated, f"ADR numbers used more than once: {duplicated}"

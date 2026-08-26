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

# The twelve loop stations, and the skill each one routes to. Station 2
# (RESOLVE) and station 5 (IMPLEMENT) are handled by the master skill and by
# domain skills respectively, so they map to the master skill.
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
    for component in ("skills", "commands", "agents", "hooks"):
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

    entries = data["hooks"]["SessionStart"]
    command = entries[0]["hooks"][0]["command"]
    assert "${CLAUDE_PLUGIN_ROOT}" in command, "hook paths must be portable"

    script = repo / "hooks" / "session-start.sh"
    assert script.is_file(), "the hook command must point at a script that exists"


def test_no_hardcoded_paths_in_hooks(repo: Path) -> None:
    text = (repo / "hooks" / "hooks.json").read_text("utf-8")
    for forbidden in ("/Users/", "/home/", "C:\\", "~/"):
        assert forbidden not in text


# --------------------------------------------------------------------------
# Skills
# --------------------------------------------------------------------------

def test_skills_exist(skill_paths: list[Path]) -> None:
    assert len(skill_paths) >= 20, "the Part 8 catalog is the minimum set"


@pytest.mark.parametrize("station,skill_name", sorted(LOOP_STATIONS.items()))
def test_every_loop_station_has_a_skill(
    repo: Path, station: str, skill_name: str
) -> None:
    """Enforcement for rules/01: the knowledge delta always has somewhere to go.

    If a station has no skill, the delta for that station cannot be routed, and
    it will be silently dropped instead of visibly declared.
    """
    assert (repo / "skills" / skill_name / "SKILL.md").is_file(), (
        f"loop station {station} routes to '{skill_name}', which does not exist"
    )


def test_every_skill_has_six_parts(skill_paths: list[Path]) -> None:
    """Enforcement for rules/02.

    The plugin must not ship a skill it would reject in a target repository.
    """
    failures: list[str] = []
    for path in skill_paths:
        meta = frontmatter(path)
        text = path.read_text(encoding="utf-8").lower()

        if not meta.get("name"):
            failures.append(f"{path}: frontmatter has no name")
        elif not KEBAB.match(meta["name"]):
            failures.append(f"{path}: name '{meta['name']}' is not kebab-case")
        elif meta["name"] != path.parent.name:
            failures.append(
                f"{path}: name '{meta['name']}' != directory '{path.parent.name}'"
            )

        description = meta.get("description", "")
        if not description:
            failures.append(f"{path}: frontmatter has no description")
        elif not description.lower().startswith("use "):
            failures.append(
                f"{path}: description must be a trigger ('Use when ...'), "
                f"got '{description[:60]}'"
            )

        for section in REQUIRED_SKILL_SECTIONS:
            if section not in text:
                failures.append(f"{path}: missing the '{section}' section")

        if "failure mode" not in text:
            failures.append(f"{path}: missing a failure-modes section")

    assert not failures, "\n".join(failures)


def test_skill_directory_names_are_unique(skill_paths: list[Path]) -> None:
    names = [p.parent.name for p in skill_paths]
    assert len(names) == len(set(names))


# --------------------------------------------------------------------------
# Agents and commands
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


def test_there_is_exactly_one_command(command_paths: list[Path]) -> None:
    """One command does everything - see docs/adr/0005-single-command-surface.md."""
    assert len(command_paths) == 1, (
        "Akinator ships a single unified command; found: "
        f"{[p.name for p in command_paths]}"
    )
    assert command_paths[0].stem == "akinator"


def test_command_declares_description_and_argument_hint(
    command_paths: list[Path],
) -> None:
    meta = frontmatter(command_paths[0])
    assert meta.get("description")
    assert meta.get("argument-hint")


def test_command_routes_to_components_that_exist(
    repo: Path, command_paths: list[Path]
) -> None:
    """Every component the command names must exist, or a mode silently no-ops.

    The command routes to both skills and agents, so a name resolves if either
    exists. A typo resolves to neither and fails here.
    """
    text = command_paths[0].read_text(encoding="utf-8")
    referenced = sorted(set(re.findall(r"`(akinator[a-z-]*)`", text)))
    assert referenced, "the command must route to named components"

    for name in referenced:
        skill = (repo / "skills" / name / "SKILL.md").is_file()
        agent = (repo / "agents" / f"{name}.md").is_file()
        assert skill or agent, (
            f"command references '{name}', which is neither a skill nor an agent"
        )


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


def test_assets_are_generated_not_committed_by_hand(repo: Path) -> None:
    """The assets must match their generator, so the mark has provenance."""
    import generate_assets

    for rel, content in generate_assets.plan(repo).items():
        path = repo / rel
        assert path.is_file(), f"{rel} is missing - run generate_assets.py --write"
        assert path.read_bytes() == content, (
            f"{rel} does not match scripts/generate_assets.py. "
            "Edit the generator, then regenerate."
        )

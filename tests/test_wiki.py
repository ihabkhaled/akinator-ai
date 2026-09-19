"""Tests for the living wiki - the repository as its own Confluence.

Per rules/11, every law the tool claims is proven to fire on a violating tree
and proven silent on a healthy one:

- init creates only what is missing and never overwrites a human's file;
- adopt, never impose: an existing home is linked, not duplicated;
- gaps turns every unknown - and every homeless category - into a question,
  and counts them;
- index rewrites only the text between the generated markers, byte for byte;
- check fires on a stale or missing block and passes on a fresh one;
- output is deterministic and names no absolute path.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import akinator_wiki as wiki

MARKER = wiki.GAP_MARKER


def _write(root: Path, rel: str, content: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def _resolved(root: Path) -> dict[str, wiki.Resolved]:
    return {entry.category.id: entry for entry in wiki.resolve(root)}


def _run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str]:
    code = wiki.main(list(argv))
    return code, capsys.readouterr().out


# --------------------------------------------------------------------------
# The taxonomy
# --------------------------------------------------------------------------

def test_the_taxonomy_covers_every_kind_of_knowledge() -> None:
    ids = [c.id for c in wiki.CATEGORIES]
    assert ids == [
        "product", "business", "market", "requirements", "drift",
        "architecture", "libraries", "stack", "infra", "testing", "ux",
        "project", "decisions", "changes", "glossary", "onboarding",
    ]
    assert len(set(ids)) == len(ids)
    for category in wiki.CATEGORIES:
        assert category.home.startswith(wiki.WIKI_DIR + "/"), category.id
        assert category.kind in ("dir", "file")
        assert category.question.endswith("?"), category.id
        assert category.answers and category.title


# --------------------------------------------------------------------------
# init - creates only what is missing, never overwrites
# --------------------------------------------------------------------------

def test_init_on_a_bare_repo_creates_every_home_and_the_index(tmp_path: Path) -> None:
    result = wiki.init(tmp_path)

    expected = [f"{c.home}/README.md" if c.kind == "dir" else c.home
                for c in wiki.CATEGORIES] + [wiki.INDEX]
    assert result["created"] == expected
    assert result["adopted"] == {}
    for rel in expected:
        assert (tmp_path / rel).is_file(), rel

    stub = (tmp_path / "docs/wiki/product/README.md").read_text("utf-8")
    assert "What this answers:" in stub, "a stub carries its purpose line"
    assert MARKER in stub.splitlines(), "a stub carries the exact gap marker line"
    assert "](../index.md)" in stub, "a stub links back to the wiki index"
    assert "](index.md)" in (tmp_path / "docs/wiki/glossary.md").read_text("utf-8")


def test_init_never_overwrites_an_existing_file(tmp_path: Path) -> None:
    mine = "# Glossary\n\nTenant: one paying organisation.\n"
    _write(tmp_path, "docs/wiki/glossary.md", mine)
    _write(tmp_path, wiki.INDEX, "# Our wiki\n\nHand written.\n")

    result = wiki.init(tmp_path)

    assert "docs/wiki/glossary.md" not in result["created"]
    assert wiki.INDEX not in result["created"]
    assert (tmp_path / "docs/wiki/glossary.md").read_text("utf-8") == mine
    assert (tmp_path / wiki.INDEX).read_text("utf-8") == "# Our wiki\n\nHand written.\n"


def test_init_twice_creates_nothing_the_second_time(tmp_path: Path) -> None:
    wiki.init(tmp_path)
    snapshot = {p: p.read_bytes() for p in sorted(tmp_path.rglob("*")) if p.is_file()}

    assert wiki.init(tmp_path)["created"] == []
    assert snapshot == {p: p.read_bytes()
                        for p in sorted(tmp_path.rglob("*")) if p.is_file()}


def test_init_fills_an_empty_default_folder_but_not_an_existing_page(tmp_path: Path) -> None:
    (tmp_path / "docs/wiki/market").mkdir(parents=True)
    _write(tmp_path, "docs/wiki/stack/runtime.md", "# Runtime\n\nPython 3.12.\n")

    created = wiki.init(tmp_path)["created"]

    assert "docs/wiki/market/README.md" in created, "an empty home is no home"
    assert "docs/wiki/stack/README.md" not in created, "a home with a page is a home"


def test_the_fresh_index_is_already_current(tmp_path: Path) -> None:
    wiki.init(tmp_path)
    assert wiki.check(tmp_path)[0] == 0


# --------------------------------------------------------------------------
# Adopt, never impose
# --------------------------------------------------------------------------

def test_an_existing_product_folder_is_linked_not_duplicated(tmp_path: Path) -> None:
    _write(tmp_path, "docs/product/vision.md", "# Vision\n\nFor clinics.\n")

    result = wiki.init(tmp_path)

    assert not (tmp_path / "docs/wiki/product").exists(), "no parallel home"
    assert result["adopted"]["product"] == "docs/product"
    text = (tmp_path / wiki.INDEX).read_text("utf-8")
    assert "[docs/product/](../product/) (adopted)" in text
    entry = _resolved(tmp_path)["product"]
    assert entry.adopted and entry.pages == ["docs/product/vision.md"]


@pytest.mark.parametrize("category, existing, home", [
    ("decisions", "docs/adr/0001-postgres.md", "docs/adr"),
    ("decisions", "docs/decisions/use-queues.md", "docs/decisions"),
    ("architecture", "docs/architecture.md", "docs/architecture.md"),
    ("architecture", "docs/architecture/overview.md", "docs/architecture"),
    ("infra", "docs/ops/deploy.md", "docs/ops"),
    ("infra", "ops/main.tf", "ops"),
    ("changes", "CHANGELOG.md", "CHANGELOG.md"),
    ("changes", "docs/changes/2026-01-01-x.md", "docs/changes"),
    ("business", "docs/business/pricing.md", "docs/business"),
    ("stack", "context/stack.md", "context/stack.md"),
    ("glossary", "GLOSSARY.md", "GLOSSARY.md"),
    ("project", "ROADMAP.md", "ROADMAP.md"),
    ("testing", "docs/testing.md", "docs/testing.md"),
])
def test_existing_homes_are_detected(tmp_path: Path, category: str,
                                     existing: str, home: str) -> None:
    _write(tmp_path, existing, "# Existing\n")
    entry = _resolved(tmp_path)[category]
    assert entry.home is not None and entry.home.path == home
    assert entry.adopted


def test_adoption_prefers_the_first_candidate_and_links_the_rest(tmp_path: Path) -> None:
    _write(tmp_path, "docs/changes/a.md", "# A\n")
    _write(tmp_path, "CHANGELOG.md", "# Changelog\n")
    entry = _resolved(tmp_path)["changes"]
    assert [loc.path for loc in entry.locations] == ["docs/changes", "CHANGELOG.md"]
    assert "also [CHANGELOG.md](../../CHANGELOG.md)" in wiki.render_block(tmp_path)


def test_detection_is_case_insensitive_and_reports_the_on_disk_name(tmp_path: Path) -> None:
    """The same tree must resolve the same way on Windows and Linux."""
    _write(tmp_path, "changelog.md", "# Changes\n")
    assert _resolved(tmp_path)["changes"].home.path == "changelog.md"


def test_a_file_does_not_satisfy_a_folder_candidate(tmp_path: Path) -> None:
    """`requirements/` is a home; `requirements.txt` is a dependency list."""
    _write(tmp_path, "requirements.txt", "requests==2\n")
    _write(tmp_path, "specs", "not a folder\n")
    assert _resolved(tmp_path)["requirements"].locations == []


def test_a_readme_section_is_adopted_with_its_anchor(tmp_path: Path) -> None:
    _write(tmp_path, "README.md",
           "# App\n\n## Getting Started\n\nnpm ci\n\n## Glossary\n\n- Seat: a user.\n")
    resolved = _resolved(tmp_path)

    onboarding = resolved["onboarding"].home
    assert (onboarding.kind, onboarding.path, onboarding.anchor) == (
        "section", "README.md", "getting-started")
    assert resolved["glossary"].home.anchor == "glossary"

    text = wiki.render_block(tmp_path)
    assert "(../../README.md#getting-started) (adopted)" in text
    created = wiki.init(tmp_path)["created"]
    assert "docs/wiki/onboarding.md" not in created
    assert "docs/wiki/glossary.md" not in created


def test_a_heading_inside_a_fence_is_not_a_section(tmp_path: Path) -> None:
    _write(tmp_path, "README.md", "# App\n\n```md\n## Glossary\n```\n")
    assert _resolved(tmp_path)["glossary"].locations == []


# --------------------------------------------------------------------------
# gaps - every unknown becomes a question, and is counted
# --------------------------------------------------------------------------

def test_every_homeless_category_is_one_question(tmp_path: Path) -> None:
    gaps = wiki.collect_gaps(tmp_path)
    assert len(gaps) == len(wiki.CATEGORIES)
    assert all(g.kind == "no-home" for g in gaps)
    product = gaps[0]
    assert product.question == (
        "Product: who are the primary users, and what problem does this "
        "solve for them?")


def test_a_marker_under_a_heading_becomes_a_question(tmp_path: Path) -> None:
    _write(tmp_path, "docs/business/pricing.md",
           f"# Pricing\n\n## Pricing model\n\n{MARKER}\n\n## Discounts\n\nNone.\n")
    gaps = [g for g in wiki.collect_gaps(tmp_path) if g.kind == "page"]

    assert len(gaps) == 1
    gap = gaps[0]
    assert gap.question == ("docs/business/pricing.md: Pricing model is unknown "
                            "- what is it?")
    assert (gap.category, gap.path, gap.line, gap.heading) == (
        "business", "docs/business/pricing.md", 5, "Pricing model")


def test_a_question_heading_is_asked_as_written(tmp_path: Path) -> None:
    _write(tmp_path, "docs/product/users.md",
           f"# Users\n\n## Who pays?\n\n{MARKER}\n")
    [gap] = [g for g in wiki.collect_gaps(tmp_path) if g.kind == "page"]
    assert gap.question == "docs/product/users.md: Who pays?"


def test_gaps_are_counted_one_per_marker_line(tmp_path: Path) -> None:
    _write(tmp_path, "docs/product/a.md",
           f"# A\n\n## One\n\n{MARKER}\n\n## Two\n\n{MARKER}\n\n## Three\n\n{MARKER}\n")
    page_gaps = [g for g in wiki.collect_gaps(tmp_path) if g.kind == "page"]
    assert [g.heading for g in page_gaps] == ["One", "Two", "Three"]


def test_a_described_or_fenced_marker_is_not_a_gap(tmp_path: Path) -> None:
    """Only the whole line is a gap - a page explaining the marker is not."""
    _write(tmp_path, "docs/product/how.md", (
        "# How we write unknowns\n\n"
        f"Write `{MARKER}` on its own line.\n\n"
        f"```\n{MARKER}\n```\n\n"
        f"- {MARKER}\n"
    ))
    assert [g for g in wiki.collect_gaps(tmp_path) if g.kind == "page"] == []


def test_init_stubs_turn_into_the_category_questions(tmp_path: Path) -> None:
    wiki.init(tmp_path)
    gaps = wiki.collect_gaps(tmp_path)
    assert len(gaps) == len(wiki.CATEGORIES)
    assert all(g.kind == "page" for g in gaps)
    assert gaps[0].question == (
        "docs/wiki/product/README.md: Who are the primary users, and what "
        "problem does this solve for them?")


def test_an_adopted_empty_folder_is_a_gap_not_a_home(tmp_path: Path) -> None:
    """An ops folder of Terraform documents no runbook - that is a question."""
    _write(tmp_path, "ops/main.tf", "resource {}\n")
    [gap] = [g for g in wiki.collect_gaps(tmp_path) if g.category == "infra"]
    assert gap.kind == "empty-home" and gap.path == "ops"
    assert gap.question.startswith("Infra: ")
    assert "docs/wiki/infra/README.md" not in wiki.init(tmp_path)["created"], (
        "an adopted home stays the host's to fill")


def test_a_marker_in_a_readme_section_is_scoped_to_that_section(tmp_path: Path) -> None:
    _write(tmp_path, "README.md", (
        f"# App\n\n{MARKER}\n\n## Install\n\n{MARKER}\n\n## License\n\nMIT\n"))
    infra = [g for g in wiki.collect_gaps(tmp_path) if g.category == "infra"]
    assert [(g.path, g.line) for g in infra] == [("README.md", 7)], (
        "only the marker inside the adopted section belongs to it")


def test_an_uncategorised_wiki_page_is_indexed_and_scanned(tmp_path: Path) -> None:
    wiki.init(tmp_path)
    _write(tmp_path, "docs/wiki/security.md", f"# Security\n\n## Threat model\n\n{MARKER}\n")
    gaps = [g for g in wiki.collect_gaps(tmp_path) if g.category is None]
    assert [g.question for g in gaps] == [
        "docs/wiki/security.md: Threat model is unknown - what is it?"]
    assert "- [docs/wiki/security.md](security.md)" in wiki.render_block(tmp_path)


def test_a_healthy_wiki_has_no_gaps(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    for category in wiki.CATEGORIES:
        page = f"{category.home}/README.md" if category.kind == "dir" else category.home
        _write(tmp_path, page, f"# {category.title}\n\nKnown and written down.\n")
    assert wiki.collect_gaps(tmp_path) == []
    code, out = _run(capsys, "--root", str(tmp_path), "gaps")
    assert code == 0 and out.startswith("No open gaps")


def test_gaps_cli_prints_questions_and_json(tmp_path: Path,
                                            capsys: pytest.CaptureFixture[str]) -> None:
    _write(tmp_path, "docs/product/a.md", f"# A\n\n## Personas\n\n{MARKER}\n")

    code, out = _run(capsys, "--root", str(tmp_path), "gaps")
    assert code == 0, "an unknown is a question, never a failure"
    assert "docs/product/a.md: Personas is unknown - what is it?  (line 5)" in out
    assert "Market: who is this sold to" in out

    code, out = _run(capsys, "gaps", "--root", str(tmp_path), "--json")
    data = json.loads(out)
    assert code == 0
    assert data["total"] == len(data["gaps"]) == len(wiki.CATEGORIES)
    page = [g for g in data["gaps"] if g["kind"] == "page"]
    assert page == [{"category": "product", "kind": "page", "path": "docs/product/a.md",
                     "line": 5, "heading": "Personas",
                     "question": "docs/product/a.md: Personas is unknown - what is it?"}]


def test_the_index_gap_total_matches_the_gaps_command(tmp_path: Path) -> None:
    _write(tmp_path, "docs/product/a.md", f"# A\n\n## Personas\n\n{MARKER}\n")
    total = len(wiki.collect_gaps(tmp_path))
    assert f"**Open gaps: {total}.**" in wiki.render_block(tmp_path)


# --------------------------------------------------------------------------
# index - only the text between the markers is the tool's
# --------------------------------------------------------------------------

def test_index_preserves_everything_outside_the_markers(tmp_path: Path) -> None:
    before = "# Our wiki\r\n\r\nHand-written intro, CRLF and all.\r\n\r\n"
    after = "\r\n## Notes\r\n\r\nStill mine.  \r\n"
    stale = f"{wiki.BEGIN}\r\nold generated text\r\n{wiki.END}"
    (tmp_path / "docs/wiki").mkdir(parents=True)
    (tmp_path / wiki.INDEX).write_bytes((before + stale + after).encode("utf-8"))

    code, _ = wiki.index(tmp_path)
    raw = (tmp_path / wiki.INDEX).read_bytes().decode("utf-8")

    assert code == 0
    assert raw.startswith(before + wiki.BEGIN)
    assert raw.endswith(wiki.END + after)
    assert "old generated text" not in raw
    assert "## Categories" in raw
    middle = raw[len(before): -len(after)]
    assert "\n" not in middle.replace("\r\n", ""), "the file's CRLF is kept"
    assert wiki.check(tmp_path)[0] == 0


def test_index_appends_a_block_to_an_index_without_one(tmp_path: Path) -> None:
    mine = "# Our wiki\n\nNo markers yet."
    _write(tmp_path, wiki.INDEX, mine)
    assert wiki.index(tmp_path)[0] == 0
    text = (tmp_path / wiki.INDEX).read_text("utf-8")
    assert text.startswith(mine + "\n\n" + wiki.BEGIN)
    assert text.rstrip("\n").endswith(wiki.END)


def test_index_creates_a_missing_index(tmp_path: Path) -> None:
    code, message = wiki.index(tmp_path)
    assert code == 0 and message == f"wrote {wiki.INDEX}"
    assert wiki.check(tmp_path)[0] == 0


def test_index_is_idempotent(tmp_path: Path) -> None:
    wiki.index(tmp_path)
    first = (tmp_path / wiki.INDEX).read_bytes()
    assert wiki.index(tmp_path) == (0, f"{wiki.INDEX} already up to date")
    assert (tmp_path / wiki.INDEX).read_bytes() == first


@pytest.mark.parametrize("broken", [
    f"# W\n\n{wiki.BEGIN}\nno end\n",
    f"# W\n\n{wiki.END}\nend before begin\n{wiki.BEGIN}\n",
    f"# W\n\n{wiki.BEGIN}\n{wiki.BEGIN}\ntwo begins\n{wiki.END}\n",
    f"# W\n\nonly an end\n{wiki.END}\n",
])
def test_malformed_markers_are_refused_and_nothing_is_written(
        tmp_path: Path, capsys: pytest.CaptureFixture[str], broken: str) -> None:
    _write(tmp_path, wiki.INDEX, broken)
    code = wiki.main(["--root", str(tmp_path), "index"])
    assert code == 2, "a guess would decide which human text gets overwritten"
    assert (tmp_path / wiki.INDEX).read_text("utf-8") == broken
    assert "malformed" in capsys.readouterr().err
    assert wiki.check(tmp_path)[0] == 1


# --------------------------------------------------------------------------
# check - fires on stale, passes on fresh
# --------------------------------------------------------------------------

def test_check_fires_when_the_index_is_missing(tmp_path: Path,
                                               capsys: pytest.CaptureFixture[str]) -> None:
    code, out = _run(capsys, "--root", str(tmp_path), "check")
    assert code == 1 and "missing" in out


def test_check_fires_when_the_block_is_missing(tmp_path: Path) -> None:
    _write(tmp_path, wiki.INDEX, "# Wiki\n")
    assert wiki.check(tmp_path)[0] == 1


def test_check_fires_when_a_page_is_added_after_indexing(tmp_path: Path) -> None:
    wiki.init(tmp_path)
    assert wiki.check(tmp_path)[0] == 0
    _write(tmp_path, "docs/wiki/product/personas.md", "# Personas\n")
    code, message = wiki.check(tmp_path)
    assert code == 1 and "stale" in message
    wiki.index(tmp_path)
    assert wiki.check(tmp_path)[0] == 0


def test_check_fires_on_a_hand_edit_inside_the_block(tmp_path: Path) -> None:
    wiki.init(tmp_path)
    path = tmp_path / wiki.INDEX
    path.write_text(path.read_text("utf-8").replace("| Product |", "| Produce |"),
                    encoding="utf-8", newline="\n")
    assert wiki.check(tmp_path)[0] == 1


def test_check_ignores_edits_outside_the_block(tmp_path: Path,
                                               capsys: pytest.CaptureFixture[str]) -> None:
    wiki.init(tmp_path)
    path = tmp_path / wiki.INDEX
    path.write_text("Owner note at the top.\n\n" + path.read_text("utf-8")
                    + "\nAnd one at the bottom.\n", encoding="utf-8", newline="\n")
    code, out = _run(capsys, "check", "--root", str(tmp_path), "--json")
    assert code == 0 and json.loads(out)["fresh"] is True


def test_a_gap_answered_makes_the_index_stale(tmp_path: Path) -> None:
    """Answering a question changes the count - the index must follow."""
    wiki.init(tmp_path)
    page = tmp_path / "docs/wiki/market/README.md"
    page.write_text(page.read_text("utf-8").replace(MARKER, "Dental clinics in the EU."),
                    encoding="utf-8", newline="\n")
    assert wiki.check(tmp_path)[0] == 1


# --------------------------------------------------------------------------
# Generation contract
# --------------------------------------------------------------------------

def test_rendering_is_deterministic_and_names_no_absolute_path(tmp_path: Path) -> None:
    _write(tmp_path, "docs/adr/0002-b.md", "# B\n")
    _write(tmp_path, "docs/adr/0001-a.md", "# A\n")
    _write(tmp_path, "CLAUDE.md", "# Router\n")
    first = wiki.render_block(tmp_path)
    assert first == wiki.render_block(tmp_path)
    assert str(tmp_path) not in first
    assert tmp_path.as_posix() not in first


def test_where_the_rest_lives_lists_only_what_exists(tmp_path: Path) -> None:
    _write(tmp_path, "CLAUDE.md", "# Router\n")
    _write(tmp_path, "rules/01-x.md", "# Rule\n")
    _write(tmp_path, ".ai/BRIEF.md", "# Brief\n")
    text = wiki.render_block(tmp_path)
    assert "- [CLAUDE.md](../../CLAUDE.md)" in text
    assert "- [rules/](../../rules/)" in text
    assert "- [.ai/BRIEF.md](../../.ai/BRIEF.md)" in text
    assert "AGENTS.md" not in text and "memory/" not in text


def test_init_output_is_clean_under_the_coverage_checker(tmp_path: Path) -> None:
    """rules/12: the tool's output lands in host repos, so it is checked from
    there. Every link must resolve and no page may name an absent path."""
    import akinator_coverage as cov

    _write(tmp_path, "README.md", "# Host\n\n## Install\n\npip install .\n")
    _write(tmp_path, "CLAUDE.md", "# Router\n\nSee [the wiki](docs/wiki/index.md).\n")
    _write(tmp_path, "docs/adr/0001-a.md", "# ADR 1\n")
    _write(tmp_path, "docs/adr/README.md", "# ADRs\n\n- [0001](0001-a.md)\n")
    wiki.init(tmp_path)

    findings = cov.run_checks(cov.Repo(tmp_path), [], [], 40)
    loud = [f for f in findings if f.severity in ("critical", "high", "medium")]
    assert not loud, "; ".join(f"{f.check} {f.path}: {f.message}" for f in loud[:5])


def test_this_repository_resolves(repo: Path) -> None:
    """Akinator's own tree: the ADR folder and change records are adopted."""
    resolved = _resolved(repo)
    assert resolved["decisions"].home.path == "docs/adr"
    assert resolved["changes"].home.path == "docs/changes"
    block = wiki.render_block(repo)
    assert str(repo) not in block and repo.as_posix() not in block


def test_the_cli_accepts_root_before_or_after_the_command(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = _run(capsys, "init", "--root", str(tmp_path))
    assert code == 0 and f"created {wiki.INDEX}" in out
    code, out = _run(capsys, "--root", str(tmp_path), "init", "--json")
    assert code == 0 and json.loads(out) == {"adopted": {}, "created": []}
    assert wiki.main(["--root", str(tmp_path / "nope"), "gaps"]) == 2

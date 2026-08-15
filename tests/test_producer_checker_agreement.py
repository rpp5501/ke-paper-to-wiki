"""Whatever a stage OFFERS the writer, a later stage must ACCEPT.

Four separate bugs in one session were the same shape, and each was found by a
human noticing bad output rather than by a test:

  - p4_context offered [tab_N] and [fig_N] as evidence; _ANCHOR knew only
    sections, equations and [S1], so a paragraph citing a table read as an
    unanchored claim.
  - the contract REQUIRED a ```mermaid diagram on structural pages, and the
    linter then failed the page for having one.
  - a gate forced every research-resource url into the go-deeper prose, and the
    dashboard then rendered a card per resource in the same tier, duplicating
    all of it.
  - verify_resources treated only 404/410 as dead because publishers refuse
    automated probes; _head_ok called anything >= 400 dead, so one resource
    passed the note gate and failed the page gate.

Every time, the defect was in the component written FIRST and never revisited
when a newer one started producing something it did not expect. These tests
pin the seams so the fifth instance fails here instead of in a build.
"""
from paper_skill.p4_context import assemble_context
from paper_skill.p5_lint import _ANCHOR, lint_page

PACK = {
    "meta": {"title": "T", "source": "s", "generated": "x"},
    "extraction": {"path": "latex", "equation_fidelity": "exact"},
    "sections": [{"id": "sec_1", "title": "S", "level": 1, "text": "prose here"}],
    "equations": [{"id": "eq_1", "latex": "x", "section": "sec_1"}],
    "tables": [{"id": "tab_1", "section": "sec_1", "caption": "c",
                "rows": [["a", "b"]]}],
    "figures": [{"id": "fig_1", "section": "sec_1", "caption": "c",
                 "assets": ["a.png"]}],
    "references": [],
}
GRAPH = {"meta": {}, "nodes": [{"id": "c1", "label": "C", "level": 1,
                                "source_ref": "sec_1"}], "edges": []}


def _offered_ids(slice_text: str) -> set[str]:
    """Every [id] token p4_context hands the writer as citable evidence."""
    return set(__import__("re").findall(r"^\[([\w.:-]+)\]", slice_text,
                                        __import__("re").M))


def test_every_id_the_writer_is_offered_is_a_valid_anchor():
    """The writer can only cite what it is given. If p4_context starts offering
    a new namespace -- [lst_1] for a code listing, say -- and _ANCHOR does not
    learn it, every page citing one is rejected as unanchored."""
    ctx = assemble_context(PACK, GRAPH, "c1", None)
    offered = _offered_ids(ctx["local_slice"])

    assert offered, "context offered no citable ids at all -- fixture is wrong"
    unmatched = [i for i in offered if not _ANCHOR.search(f"[{i}]")]
    assert not unmatched, (
        f"p4_context offers {unmatched} but p5_lint._ANCHOR does not accept "
        f"them; a page citing one would be reported as an unanchored claim")


def test_a_page_citing_only_offered_ids_lints_clean():
    """The end-to-end version of the invariant, and the one that matters: a
    page that cites exactly what it was given must pass.

    There are two ways to break it and this catches both. If _ANCHOR does not
    parse the namespace, the citation is invisible and the paragraph reads as
    UNANCHORED. If it parses but valid_ids omits the source, the citation reads
    as DANGLING. Asserting only on "dangling" missed the first case entirely --
    that version passed against the very code the tests above prove is broken.
    """
    ctx = assemble_context(PACK, GRAPH, "c1", None)
    offered = _offered_ids(ctx["local_slice"])
    body = "\n\n".join(f"A claim resting on it [{i}]." for i in sorted(offered))
    page = ("# C\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            f"## Mechanics {{#mechanics}}\n{body}\n"
            "## The Math {#the-math}\nd [eq_1]\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    problems = lint_page(page, PACK, check_links=lambda _u: True,
                         check_mermaid=lambda _b: None)

    assert not [p for p in problems
                if "dangling" in p or "unanchored" in p], problems


def test_a_required_diagram_is_never_itself_a_lint_failure():
    """The contract requires a mermaid diagram on structural pages. A pipeline
    that demands something and then rejects it cannot be satisfied."""
    page = ("# C\n## TL;DR {#tldr}\na\n## Intuition {#intuition}\nb\n"
            "## Mechanics {#mechanics}\nThe shortcut skips two layers [§sec_1].\n\n"
            "```mermaid\ngraph TD\n  A --> B\n```\n\n"
            "## The Math {#the-math}\nd [eq_1]\n"
            "## Go Deeper {#go-deeper}\n- x\n")

    problems = lint_page(page, PACK, check_links=lambda _u: True,
                         check_mermaid=lambda _b: None)

    assert not [p for p in problems if "unanchored" in p], problems


def test_the_two_link_checkers_agree_on_what_dead_means():
    """verify_resources gates the note; _head_ok gates the page. When they
    disagreed, uber.com/blog (406 to anything scripted) passed one and failed
    the other, and it took a manual audit to notice."""
    import inspect
    from paper_skill import p5_lint
    from paper_skill.resources import _DEAD_STATUS

    source = inspect.getsource(p5_lint._head_ok)

    assert "_DEAD_STATUS" in source, (
        "_head_ok must reuse resources._DEAD_STATUS rather than keep its own "
        "notion of a dead link")
    assert _DEAD_STATUS == {404, 410}


def test_the_composition_floor_only_asks_for_types_the_schema_allows():
    """educational_gap rejects a note lacking a `visual` or `lecture`. If the
    schema's enum ever drops one, the floor becomes unsatisfiable: the model
    would be told to supply a type its own note is not allowed to declare."""
    import json
    from pathlib import Path

    from paper_skill.resources import EDUCATIONAL_TYPES

    schema = json.loads(next(
        Path("../research-mcp/src/research_mcp").rglob("note.schema.json")
    ).read_text(encoding="utf-8"))
    allowed = set(schema["properties"]["resources"]["items"]
                  ["properties"]["type"]["enum"])

    assert EDUCATIONAL_TYPES <= allowed, (
        f"{EDUCATIONAL_TYPES - allowed} is required by the composition floor "
        f"but not permitted by the note schema")

"""Nothing in the depth/bridge work may be shaped around one paper.

Every fix in this round was found on arXiv:1306.1043 (SID). These check the
same code paths against a structurally different input -- the AIAYN fixture,
which is flat where SID is nested, macro-free where SID defines 53, and has no
bridged code at all -- so a change that only works for the paper that motivated
it fails here.
"""
import json
from pathlib import Path

from paper_skill.concepts import graph_quality
from paper_skill.latex_pack import extract_macros, latex_to_pack
from paper_skill.p4_context import assemble_context
from paper_skill.p5_lint import lint_page

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_GRAPH = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
FIXTURE_PACK = json.loads(
    (ROOT / "fixtures" / "aiayn_tiny_pack.json").read_text(encoding="utf-8"))


def test_a_macro_free_paper_gets_an_empty_table_not_a_crash():
    """Most papers define no macros. KaTeX must simply get {}."""
    assert extract_macros(r"\section{S}No macros here.") == {}


def test_optional_arg_rewriting_leaves_a_paper_without_them_alone():
    tex = "\n".join([r"\section{S}", r"\begin{equation}", r"a[0] + b_{1}",
                     r"\end{equation}"])
    assert "a[0]" in latex_to_pack(tex)["equations"][0]["latex"]


def test_flat_sections_are_unaffected_by_the_container_fallback():
    """AIAYN's fixture sections carry their own text, so the child-section
    fallback must not fire and must not duplicate anything."""
    node = next(n for n in FIXTURE_GRAPH["nodes"] if n.get("source_ref"))
    ctx = assemble_context(FIXTURE_PACK, FIXTURE_GRAPH, node["id"], None)

    assert "Subsection" not in ctx["local_slice"]


def test_context_assembly_works_for_every_fixture_concept():
    """No node may raise, whatever its source_ref points at."""
    for node in FIXTURE_GRAPH["nodes"]:
        ctx = assemble_context(FIXTURE_PACK, FIXTURE_GRAPH, node["id"], None)
        assert ctx["global_slice"] and ctx["local_slice"]


def test_shipped_fixture_pages_pass_the_no_content_rule():
    """The filler rule must not fire on pages written before it existed —
    otherwise it is matching ordinary prose, not the failure mode."""
    for page in sorted((ROOT / "fixtures" / "pages").glob("*.md")):
        probs = lint_page(page.read_text(encoding="utf-8"), FIXTURE_PACK,
                          check_links=lambda url: True)
        assert not [p for p in probs if "no-content" in p], page.name


def test_graph_quality_is_computable_for_a_different_paper():
    metrics = graph_quality(FIXTURE_GRAPH)
    assert metrics["node_count"] > 0
    assert 0.0 <= metrics["orphan_ratio"] <= 1.0


def test_code_context_is_inert_without_bridged_edges():
    """A concept-only graph has no implements edges; passing repo_dir must
    change nothing rather than reaching for files that were never linked."""
    node = next(n for n in FIXTURE_GRAPH["nodes"] if n.get("source_ref"))

    without = assemble_context(FIXTURE_PACK, FIXTURE_GRAPH, node["id"], None)
    with_repo = assemble_context(FIXTURE_PACK, FIXTURE_GRAPH, node["id"], None,
                                 repo_dir=ROOT)

    assert without["local_slice"] == with_repo["local_slice"]

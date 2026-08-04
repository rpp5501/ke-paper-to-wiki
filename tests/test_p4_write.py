from pathlib import Path
from paper_skill.p4_write import annotate_graph, write_pages, PAGE_PROMPT

# fixtures repeated verbatim (tasks may execute out of order — no cross-test imports)
PACK = {"meta": {"source": "arXiv:1706.03762", "title": "AIAYN", "generated": "x"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3", "title": "SDPA", "level": 2,
                      "text": "We compute dot products of queries and keys."}],
        "equations": [{"id": "eq_1", "latex": r"\frac{QK^T}{\sqrt{d_k}}",
                        "section": "sec_3"}],
        "references": [], "figures": []}
GRAPH = {"meta": {"kind": "concept", "source": "arXiv:1706.03762",
                  "generated": "x", "version": 1},
         "nodes": [{"id": "attention", "kind": "concept", "label": "Attention",
                    "level": 1, "source_ref": "sec_3"},
                   {"id": "sdpa", "kind": "concept", "label": "SDPA",
                    "level": 2, "source_ref": "sec_3"}],
         "edges": [{"src": "sdpa", "dst": "attention", "kind": "part-of",
                    "weight": 1.0, "confidence": "extracted", "confidence_score": 1.0}]}

ROWS = [{"id": "sdpa", "label": "SDPA", "level": 2, "include": True,
         "research": False, "definition": "d", "sub_questions": []}]

GOOD_PAGE = """# SDPA
## TL;DR {#tldr}
Scaling keeps softmax gradients usable [§sec_3].
## Intuition {#intuition}
Bigger d_k means bigger dot products [§sec_3].
## Mechanics {#mechanics}
Scores are divided by sqrt(d_k) [eq_1].
## The Math {#the-math}
Variance of the dot product grows with d_k [eq_1].
## Go Deeper {#go-deeper}
- d2l.ai derivation
"""


def test_writes_page_with_reading_order_prefix(tmp_path):
    r = write_pages(PACK, GRAPH, ROWS, spawn=lambda p: GOOD_PAGE,
                    home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path)
    assert r["done"] == ["sdpa"]
    files = list((tmp_path / "pages").glob("*_sdpa.md"))
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8").startswith("# SDPA")


def test_page_missing_tiers_fails_to_inbox(tmp_path):
    from research_mcp.inbox import inbox_list
    r = write_pages(PACK, GRAPH, ROWS, spawn=lambda p: "# SDPA\njust prose",
                    home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path)
    assert r["failed"] == ["sdpa"]
    assert inbox_list(home=tmp_path)


def test_spawn_exception_fails_immediately_no_retry(tmp_path):
    calls = []

    def flaky(p):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError("boom")
        return GOOD_PAGE

    r = write_pages(PACK, GRAPH, ROWS, spawn=flaky,
                    home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path)
    assert r["failed"] == ["sdpa"]
    assert "sdpa" not in r["done"]
    assert len(calls) == 1


# The graph node's `page` field is the only record of which file belongs to
# which concept. write_pages is the one stage that knows the mapping, and
# viz.propose hard-requires the field (no page -> zero candidates, silently).
def test_result_reports_the_written_filename(tmp_path):
    r = write_pages(PACK, GRAPH, ROWS, spawn=lambda p: GOOD_PAGE,
                    home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path)

    written = next((tmp_path / "pages").glob("*_sdpa.md")).name
    assert r["pages"] == {"sdpa": written}


def test_failed_page_is_not_reported_as_written(tmp_path):
    r = write_pages(PACK, GRAPH, ROWS, spawn=lambda p: "# SDPA\njust prose",
                    home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path)

    assert r["pages"] == {}


def test_annotate_graph_records_pages_on_their_nodes():
    out = annotate_graph(GRAPH, {"sdpa": "07_sdpa.md"})

    assert next(n for n in out["nodes"] if n["id"] == "sdpa")["page"] == "07_sdpa.md"


def test_annotate_graph_leaves_unwritten_nodes_alone():
    """A node with no page must not claim a file that isn't on disk."""
    out = annotate_graph(GRAPH, {"sdpa": "07_sdpa.md"})

    assert "page" not in next(n for n in out["nodes"] if n["id"] == "attention")


def test_annotate_graph_does_not_mutate_its_input():
    """write_pages takes the graph as input; rewriting a caller's dict in place
    is exactly the side effect that leaks between callers."""
    annotate_graph(GRAPH, {"sdpa": "07_sdpa.md"})

    assert all("page" not in n for n in GRAPH["nodes"])


def test_prompt_requires_verbatim_equations_and_paragraph_anchors():
    assert "reproduce each relevant equation" in PAGE_PROMPT
    assert "VERBATIM as a display block wrapped in $$ ... $$" in PAGE_PROMPT
    assert "EVERY paragraph in Mechanics and The Math" in PAGE_PROMPT


def test_prompt_encodes_anchor_rule_and_tiers():
    assert "{#tldr}" in PAGE_PROMPT and "[§" in PAGE_PROMPT

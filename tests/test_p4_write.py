from pathlib import Path
from paper_skill.p4_write import (
    PAGE_PROMPT,
    WRITING_SKILL,
    WRITING_SKILL_PATH,
    annotate_graph,
    write_pages,
)
from paper_skill.pedagogy import (
    DIAGRAM_SIGNAL_FLOOR, pedagogy_problems, prose_word_counts,
    structural_signals,
)

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


def test_dense_prose_triggers_one_bounded_regeneration(tmp_path):
    calls = []
    dense = GOOD_PAGE.replace(
        "Scores are divided by sqrt(d_k) [eq_1].",
        " ".join(["dense"] * 101) + " [eq_1].",
    )

    def improve(_prompt):
        calls.append(1)
        return dense if len(calls) == 1 else GOOD_PAGE

    result = write_pages(
        PACK, GRAPH, ROWS, spawn=improve,
        home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path,
    )

    assert result["done"] == ["sdpa"]
    assert len(calls) == 2


def test_live_prompt_carries_the_diagram_rule():
    """v1 of the contract said nothing about diagrams and the build shipped 24
    pages with none. The rule has to reach the prompt the writer actually gets,
    which is WRITING_SKILL — not the unreferenced _LEGACY_PAGE_PROMPT that also
    mentions mermaid."""
    from paper_skill.p4_write import PAGE_PROMPT, WRITING_SKILL

    assert "## Diagrams" in WRITING_SKILL
    assert "```mermaid" in WRITING_SKILL
    assert "## Diagrams" in PAGE_PROMPT


def test_structural_prose_without_a_diagram_is_a_problem():
    page = ("The parent set of C is a descendant of A, so every directed path "
            "$A\\to B\\to C$ that a collider blocks needs an adjustment set "
            "chosen by d-separation from an ancestor of the backdoor path.")

    assert structural_signals(page) >= DIAGRAM_SIGNAL_FLOOR
    assert any("mermaid" in problem for problem in pedagogy_problems(page))


def test_one_diagram_satisfies_the_whole_page():
    page = ("The parent set of C is a descendant of A, so every directed path "
            "$A\\to B\\to C$ that a collider blocks needs an adjustment set "
            "chosen by d-separation from an ancestor of the backdoor path.\n\n"
            "```mermaid\ngraph TD\n  A --> B --> C\n```\n")

    assert not any("mermaid" in problem for problem in pedagogy_problems(page))


def test_equations_and_algorithm_blocks_do_not_demand_a_diagram():
    """A page whose structure lives inside math or a walkthrough already shows
    it; only prose the reader must assemble from words should trip the floor."""
    inside_blocks = ("$$A\\to B\\to C\\to D\\to E$$\n\n"
                     "```algorithm\nlines:\n  - code: 'walk(A\\to B)'\n"
                     "    intent: 'follow every directed path'\n```\n")

    assert structural_signals(inside_blocks) == 0
    assert pedagogy_problems(inside_blocks) == []


def test_pedagogy_counts_each_list_item_as_prose():
    bullet = " ".join(["bullet"] * 61)
    ordered = " ".join(["ordered"] * 101)

    assert prose_word_counts(f"- {bullet}\n\n1. {ordered}") == [61, 101]


def test_pedagogy_exempts_indented_code_but_keeps_nested_list_prose():
    code = " ".join(["code"] * 140)
    bullet = " ".join(["bullet"] * 61)

    assert prose_word_counts(f"    {code}\n\n    - {bullet}") == [61]


def test_pedagogy_resumes_after_a_display_equation_with_an_anchor():
    prose = " ".join(["word"] * 61)

    assert prose_word_counts(
        f"$$\nx = 1\n\\end{{aligned}}$$ [eq_1]\n\n{prose}") == [61]


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


def test_page_prompt_is_loaded_from_versioned_writing_skill():
    assert WRITING_SKILL_PATH.name == "SKILL.md"
    assert WRITING_SKILL_PATH.parent.name == "write-paper-tutor"
    assert WRITING_SKILL == WRITING_SKILL_PATH.read_text(encoding="utf-8")
    assert WRITING_SKILL in PAGE_PROMPT


def test_spawn_receives_rendered_context_without_formatting_skill_braces(tmp_path):
    prompts = []

    write_pages(
        PACK, GRAPH, ROWS, spawn=lambda prompt: prompts.append(prompt) or GOOD_PAGE,
        home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path,
    )

    assert "GLOBAL CONTEXT:" in prompts[0]
    assert "\\frac{QK^T}{\\sqrt{d_k}}" in prompts[0]
    assert "__GLOBAL_CONTEXT__" not in prompts[0]

from paper_skill.p4_context import assemble_context

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
NOTE = {"concept": "sdpa", "status": "complete",
        "synthesis": "Variance argument [S1].",
        "resources": [{"url": "https://d2l.ai/x", "title": "d2l",
                        "type": "lecture", "why": "derivation"}],
        "unresolved": [], "sources_consulted": {"S1": "https://d2l.ai/x"}}


def test_global_slice_has_neighborhood_but_no_latex():
    ctx = assemble_context(PACK, GRAPH, "sdpa", NOTE)
    assert "Attention" in ctx["global_slice"]          # parent label
    assert r"\sqrt{d_k}" not in ctx["global_slice"]    # round-2 rule


def test_local_slice_has_section_equations_and_note():
    ctx = assemble_context(PACK, GRAPH, "sdpa", NOTE)
    assert "dot products of queries" in ctx["local_slice"]
    assert r"\sqrt{d_k}" in ctx["local_slice"]
    assert "Variance argument [S1]" in ctx["local_slice"]
    assert "https://d2l.ai/x" in ctx["local_slice"]


def test_missing_note_is_fine():
    ctx = assemble_context(PACK, GRAPH, "sdpa", None)
    assert "no research note" in ctx["local_slice"]


# A concept whose source_ref is a *container* heading got an empty local slice,
# because the section carrying the number holds no prose -- the content is in
# its children. On arXiv:1306.1043 that hit the level-0 thesis node itself:
# sec_2 "Structural Intervention Distance" is 0 chars, and everything lives in
# sec_2_1..sec_2_4. The page then honestly reported having nothing to work
# with, which is what "the article is very high level" looks like from outside.
NESTED_PACK = {
    "meta": {"source": "arXiv:1306.1043", "title": "SID", "generated": "x"},
    "extraction": {"path": "latex", "equation_fidelity": "exact"},
    "sections": [
        {"id": "sec_2", "title": "SID", "level": 1, "text": ""},
        {"id": "sec_2_1", "title": "Definition", "level": 2,
         "text": "SID counts falsely inferred intervention distributions."},
        {"id": "sec_2_2", "title": "Equivalent form", "level": 2,
         "text": "It can be restated as an adjustment-set check."},
        {"id": "sec_3", "title": "Elsewhere", "level": 1, "text": "Unrelated."},
    ],
    "equations": [
        {"id": "eq_4", "latex": r"\mathrm{SID}(\G,\HH)", "section": "sec_2_1"},
        {"id": "eq_9", "latex": r"\text{unrelated}", "section": "sec_3"},
    ],
    "references": [], "figures": []}

NESTED_GRAPH = {
    "meta": {"kind": "concept", "source": "arXiv:1306.1043",
             "generated": "x", "version": 1},
    "nodes": [{"id": "sid", "kind": "concept", "label": "SID", "level": 0,
               "source_ref": "sec_2"}],
    "edges": []}


def test_an_empty_container_section_falls_back_to_its_children():
    ctx = assemble_context(NESTED_PACK, NESTED_GRAPH, "sid", None)

    assert "falsely inferred intervention distributions" in ctx["local_slice"]
    assert "adjustment-set check" in ctx["local_slice"]


def test_child_equations_come_along():
    ctx = assemble_context(NESTED_PACK, NESTED_GRAPH, "sid", None)

    assert "[eq_4]" in ctx["local_slice"]


def test_the_fallback_does_not_swallow_unrelated_sections():
    """sec_3 is a sibling, not a child of sec_2 — a prefix match on the string
    would take it, and the page would cite material it never covers."""
    ctx = assemble_context(NESTED_PACK, NESTED_GRAPH, "sid", None)

    assert "Unrelated." not in ctx["local_slice"]
    assert "[eq_9]" not in ctx["local_slice"]


def test_a_section_with_its_own_text_is_unchanged():
    """Byte-for-byte the old behaviour when the section carries its own prose."""
    ctx = assemble_context(PACK, GRAPH, "sdpa", NOTE)

    assert ctx["local_slice"].count("dot products of queries") == 1

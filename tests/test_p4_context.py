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

"""The canonical build path refuses to ship a TOC dashboard."""
import json

import pytest

from paper_skill.build_dashboard import build_graph
from paper_skill.concepts import ConceptExtractionError

PACK = {"meta": {"source": "arXiv:1706.03762", "title": "Attention Is All You Need",
                 "generated": "2026-07-09"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_1", "title": "Introduction", "level": 1,
                      "text": "We propose the Transformer."}],
        "equations": [], "references": [], "figures": []}

GOOD = json.dumps({
    "nodes": [{"id": "transformer", "kind": "concept", "label": "The Transformer",
               "level": 0, "source_ref": "sec_1",
               "definition": "Sequence model built on attention.",
               "sub_questions": ["What replaces recurrence?"], "research": True}],
    "edges": []})


def test_build_graph_aborts_when_extraction_fails(monkeypatch):
    monkeypatch.setattr("paper_skill.build_dashboard.build_pack", lambda *a, **k: PACK)
    with pytest.raises(ConceptExtractionError):
        build_graph("arXiv:1706.03762", spawn=lambda p: "sorry, prose not json")


def test_build_graph_returns_validated_graph(monkeypatch):
    monkeypatch.setattr("paper_skill.build_dashboard.build_pack", lambda *a, **k: PACK)
    built = build_graph("arXiv:1706.03762", spawn=lambda p: GOOD)
    assert built["graph"]["meta"]["kind"] == "concept"
    assert built["graph"]["nodes"][0]["id"] == "transformer"


def test_build_graph_surfaces_pack_failure(monkeypatch):
    monkeypatch.setattr("paper_skill.build_dashboard.build_pack",
                        lambda *a, **k: {"status": "fetch_failed", "hint": "x"})
    with pytest.raises(RuntimeError, match="paper2pack failed"):
        build_graph("arXiv:0000.0000", spawn=lambda p: GOOD)

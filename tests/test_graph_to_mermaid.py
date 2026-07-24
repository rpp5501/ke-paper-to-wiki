"""R15.10 — Mermaid mindmap exporter."""
import json
from pathlib import Path

import pytest

from paper_skill.graph_to_mermaid import to_mermaid_mindmap

FIXTURE = json.loads(
    (Path(__file__).resolve().parent.parent / "fixtures"
     / "aiayn_concept_graph.json").read_text(encoding="utf-8"))


def test_fixture_tree_shape():
    out = to_mermaid_mindmap(FIXTURE)
    lines = out.splitlines()
    assert lines[0] == "mindmap"
    assert lines[1] == "  ((The Transformer))"  # level-0 root, root shape
    # part-of children indent under their parents
    attention_i = lines.index("    Attention")
    assert "      Scaled Dot-Product Attention" in lines[attention_i:]
    # depth-3 leaf sits under SDPA
    sdpa_i = lines.index("      Scaled Dot-Product Attention")
    assert lines[sdpa_i + 1].startswith("        ")


def test_non_tree_edges_preserved_as_comments():
    out = to_mermaid_mindmap(FIXTURE)
    assert "%% multi-head-attention --builds-on--> scaled-dot-product-attention" in out
    assert "%% attention --prerequisite--> why-self-attention" in out


def test_labels_sanitized():
    graph = {"nodes": [{"id": "r", "label": "Root (v2) [beta]", "level": 0}],
             "edges": []}
    out = to_mermaid_mindmap(graph)
    assert "((Root v2 beta))" in out
    assert "(v2)" not in out


def test_orphans_attach_under_root():
    graph = {"nodes": [{"id": "r", "label": "R", "level": 0},
                       {"id": "solo", "label": "Solo", "level": 2}],
             "edges": []}
    lines = to_mermaid_mindmap(graph).splitlines()
    assert "  ((R))" in lines
    assert "    Solo" in lines  # visible, one level under root


def test_part_of_cycle_does_not_hang():
    graph = {"nodes": [{"id": "a", "label": "A", "level": 0},
                       {"id": "b", "label": "B", "level": 1}],
             "edges": [{"src": "b", "dst": "a", "kind": "part-of"},
                       {"src": "a", "dst": "b", "kind": "part-of"}]}
    with pytest.raises(ValueError, match="no root"):
        to_mermaid_mindmap(graph)

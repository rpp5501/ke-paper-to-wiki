import pytest

from paper_skill.bridge import merge_bridge


explorer = pytest.importorskip("graphify.exporters.explorer")
from research_mcp import validate


def test_bridge_output_validates_and_renders_across_repositories():
    concepts = {
        "meta": {"kind": "concept", "source": "paper",
                 "generated": "2026-07-11", "version": 1},
        "nodes": [{"id": "attention", "kind": "concept",
                   "label": "Attention", "level": 1}],
        "edges": [],
    }
    code = {
        "meta": {"kind": "code", "source": "repo",
                 "generated": "2026-07-11", "version": 1},
        "nodes": [{"id": "model.py::Attention", "kind": "class",
                   "label": "Attention", "source_ref": "model.py:L10"}],
        "edges": [],
    }

    candidate = {"concept": "attention", "code": "model.py::Attention",
                 "verdict": "yes"}
    merged = merge_bridge(concepts, code,
                          [candidate, {**candidate, "confirmed": True}])
    assert validate.validate_graph(merged) == []

    implements = [edge for edge in merged["edges"]
                  if edge["kind"] == "implements"]
    assert len(implements) == 1
    edge = implements[0]
    assert edge["src"] == "model.py::Attention"
    assert edge["dst"] == "attention"
    assert edge["confidence"] == "extracted"
    assert edge["confidence_score"] == 1.0
    assert merged["meta"]["kind"] == "bridged"

    html = explorer.to_explorer_html(merged, cytoscape_js="")
    assert '"src": "model.py::Attention", "dst": "attention"' in html
    assert 'edge[kind = "implements"]' in html
    assert '"line-style": "dashed", "line-color": "#4a9b5e"' in html
    assert 'const side = DEPENDENT_SIDE[e.kind] || "src";' in html
    dependent_map = html.split("const DEPENDENT_SIDE = ", 1)[1].split(";", 1)[0]
    assert '"implements"' not in dependent_map

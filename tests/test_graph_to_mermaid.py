"""R15.10 — Mermaid mindmap exporter."""
import json
from pathlib import Path

import pytest

from paper_skill.graph_to_mermaid import main, to_mermaid_mindmap

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


def test_max_depth_trims_the_tree_like_a_collapsed_branch():
    """R16.B4 — --max-depth mirrors the dashboard's branch collapse."""
    out = to_mermaid_mindmap(FIXTURE, max_depth=2)
    lines = out.splitlines()

    assert lines[1] == "  ((The Transformer))"
    assert "    Attention" in lines
    # Depth 3 and below are folded away.
    assert "      Scaled Dot-Product Attention" not in lines


def test_max_depth_reports_what_it_folded():
    out = to_mermaid_mindmap(FIXTURE, max_depth=2)

    # Nothing silently lost, same discipline as the non-tree edge footer.
    assert "%% 6 node(s) hidden below depth 2" in out


def test_no_max_depth_is_byte_identical_to_the_full_map():
    assert to_mermaid_mindmap(FIXTURE) == to_mermaid_mindmap(FIXTURE, max_depth=0)


def test_max_depth_one_keeps_only_the_root():
    lines = to_mermaid_mindmap(FIXTURE, max_depth=1).splitlines()

    assert lines[1] == "  ((The Transformer))"
    assert not any(line.startswith("    ") for line in lines)


def test_cli_passes_max_depth_through(tmp_path, capsys):
    graph = tmp_path / "g.json"
    graph.write_text(json.dumps(FIXTURE), encoding="utf-8")

    assert main([str(graph), "--max-depth", "2"]) == 0

    out = capsys.readouterr().out
    assert "hidden below depth 2" in out
    assert "Scaled Dot-Product Attention" not in out


def test_part_of_cycle_does_not_hang():
    graph = {"nodes": [{"id": "a", "label": "A", "level": 0},
                       {"id": "b", "label": "B", "level": 1}],
             "edges": [{"src": "b", "dst": "a", "kind": "part-of"},
                       {"src": "a", "dst": "b", "kind": "part-of"}]}
    with pytest.raises(ValueError, match="no root"):
        to_mermaid_mindmap(graph)

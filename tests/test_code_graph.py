"""A §5.1 code graph for ANY path, not just this repo.

research-mcp/scripts/dogfood_graph.py could only graph research-mcp: ROOT was
computed from the script's own location. Bridging a paper to whatever
implements it needs the same extraction pointed anywhere, so it moves here as
an importable function with the graphify call injected, the way every LLM stage
injects spawn.
"""
import json

import pytest

from paper_skill.code_graph import build_code_graph, main

# Shape graphify actually emits: networkx node_link_data, so edges live under
# "links". Getting this wrong is silent -- to_plan_schema_native just sees no
# edges and returns an edgeless graph.
NATIVE = {
    "nodes": [
        {"id": "m.py::f", "label": "f", "file_type": "code",
         "source_file": "m.py", "source_location": "L10"},
        {"id": "m.py::g", "label": "g", "file_type": "code",
         "source_file": "m.py", "source_location": "L20"},
        {"id": "other.py::h", "label": "h", "file_type": "code",
         "source_file": "other.py", "source_location": "L1"},
    ],
    "links": [{"source": "m.py::f", "target": "m.py::g", "relation": "calls"}],
}


def fake_run(_target):
    return json.loads(json.dumps(NATIVE))


def test_builds_a_51_code_graph():
    graph = build_code_graph("anywhere", run=fake_run)

    assert graph["meta"]["kind"] == "code"
    assert graph["meta"]["version"] == 1
    assert [n["id"] for n in graph["nodes"]]


def test_links_are_read_as_edges():
    """networkx calls them links; the §5.1 schema calls them edges."""
    assert len(build_code_graph("anywhere", run=fake_run)["edges"]) == 1


def test_source_defaults_to_the_target_name():
    graph = build_code_graph("some/repo/pgmpy", run=fake_run)
    assert "pgmpy" in graph["meta"]["source"]


def test_explicit_source_wins():
    graph = build_code_graph("x", source="repo:custom", run=fake_run)
    assert graph["meta"]["source"] == "repo:custom"


def test_a_single_file_target_keeps_only_that_file(tmp_path):
    """Pointing at one module must not drag in its whole directory: graphify
    only walks directories, so the filter happens after extraction."""
    target = tmp_path / "m.py"
    target.write_text("def f(): pass\n", encoding="utf-8")

    graph = build_code_graph(target, run=fake_run)

    files = {n.get("source_ref", "").split(":L")[0] for n in graph["nodes"]}
    assert files == {"m.py"}


def test_a_directory_target_keeps_every_file(tmp_path):
    graph = build_code_graph(tmp_path, run=fake_run)

    files = {n.get("source_ref", "").split(":L")[0] for n in graph["nodes"]}
    assert files == {"m.py", "other.py"}


def test_rationale_nodes_are_not_code_entities():
    """graphify emits docstrings as file_type "rationale". The §5.1 kind enum
    has no such value, so the adapter silently defaults them to "function" --
    a code graph that claims a module's docstrings are callables. Real case:
    4 of 10 nodes extracted from pgmpy's sid.py."""
    native = {
        "nodes": [
            {"id": "m.py::f", "label": "f", "file_type": "code",
             "source_file": "m.py", "source_location": "L10"},
            {"id": "m.py::doc", "label": "Compute the closure, including the diagonal.",
             "file_type": "rationale", "source_file": "m.py",
             "source_location": "L11"},
        ],
        "links": [],
    }

    graph = build_code_graph("anywhere", run=lambda _t: native)

    assert [n["label"] for n in graph["nodes"]] == ["f"]


def test_edges_touching_a_dropped_rationale_node_go_too():
    native = {
        "nodes": [
            {"id": "a", "label": "f", "file_type": "code", "source_file": "m.py"},
            {"id": "b", "label": "why", "file_type": "rationale",
             "source_file": "m.py"},
        ],
        "links": [{"source": "a", "target": "b", "relation": "calls"}],
    }

    assert build_code_graph("anywhere", run=lambda _t: native)["edges"] == []


def test_an_empty_extraction_is_an_error_not_an_empty_graph():
    """§5.1 requires minItems 1. An empty graph downstream looks like 'this
    code has no structure' rather than 'extraction did not run'."""
    with pytest.raises(RuntimeError, match="no code nodes"):
        build_code_graph("x", run=lambda _t: {"nodes": [], "links": []})


def test_python_ast_emits_complete_ranges_and_symbol_kinds(tmp_path):
    target = tmp_path / "m.py"
    target.write_text(
        "class SID:\n    def evaluate(self):\n        return 1\n",
        encoding="utf-8",
    )
    native = {
        "nodes": [
            {"id": "m", "label": "m.py", "file_type": "code",
             "source_file": "m.py", "source_location": "L1"},
            {"id": "m::SID", "label": "SID", "file_type": "code",
             "source_file": "m.py", "source_location": "L1"},
            {"id": "m::SID.evaluate", "label": ".evaluate()", "file_type": "code",
             "source_file": "m.py", "source_location": "L2"},
        ],
        "links": [],
    }

    graph = build_code_graph(target, run=lambda _target: native)
    by_id = {node["id"]: node for node in graph["nodes"]}

    assert by_id["m"]["kind"] == "file"
    assert by_id["m"]["source_ref"] == "m.py:L1-L3"
    assert by_id["m::SID"]["kind"] == "class"
    assert by_id["m::SID"]["source_ref"] == "m.py:L1-L3"
    assert by_id["m::SID.evaluate"]["kind"] == "method"
    assert by_id["m::SID.evaluate"]["source_ref"] == "m.py:L2-L3"


def test_main_writes_the_graph(tmp_path):
    out = tmp_path / "code-graph.json"

    assert main([str(tmp_path), "-o", str(out)], run=fake_run) == 0

    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["meta"]["kind"] == "code"

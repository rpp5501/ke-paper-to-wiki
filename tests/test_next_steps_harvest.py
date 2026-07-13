from paper_skill.next_steps import harvest
from research_mcp.wiki import wiki_put


PACK = {
    "meta": {"source": "arXiv:1", "title": "T", "generated": "x"},
    "extraction": {},
    "figures": [],
    "references": [],
    "equations": [],
    "sections": [{
        "id": "sec_7",
        "title": "Conclusion and Future Work",
        "level": 1,
        "text": "We plan to extend attention to images and audio.",
    }],
}
CONCEPTS = {
    "meta": {"kind": "concept", "source": "arXiv:1",
             "generated": "x", "version": 1},
    "nodes": [{"id": "mha", "kind": "concept", "label": "MHA", "level": 2}],
    "edges": [],
}
NOTE = {
    "concept": "mha",
    "status": "partial",
    "synthesis": "Covered [S1].",
    "resources": [{"url": "https://x.test", "title": "t", "type": "lecture",
                   "why": "w"}],
    "unresolved": ["Why 8 heads exactly?"],
    "sources_consulted": {"S1": "https://x.test"},
}


def test_harvests_future_work_section():
    gaps = harvest(PACK, CONCEPTS)
    future_work = [gap for gap in gaps if gap["kind"] == "paper-limitation"]
    assert future_work and "sec_7" in future_work[0]["anchors"]["sources"][0]


def test_future_work_anchors_matching_concepts_without_bridge():
    concepts = {**CONCEPTS, "nodes": [
        {**CONCEPTS["nodes"][0], "source_ref": "sec_7"},
    ]}

    gaps = harvest(PACK, concepts)

    future_work = [gap for gap in gaps if gap["kind"] == "paper-limitation"]
    assert future_work[0]["anchors"]["nodes"] == ["mha"]


def test_harvests_unresolved_ledger(tmp_path):
    wiki_put("mha", NOTE, home=tmp_path)
    gaps = harvest(PACK, CONCEPTS, wiki_home=tmp_path)
    unresolved = [gap for gap in gaps if gap["kind"] == "unresolved-note"]
    assert unresolved and unresolved[0]["text"] == "Why 8 heads exactly?"
    assert "mha" in unresolved[0]["anchors"]["nodes"]


def test_no_implements_needs_bridged_graph():
    bridged = {**CONCEPTS, "meta": {**CONCEPTS["meta"], "kind": "bridged"}}
    gaps = harvest(PACK, bridged)
    assert "no-implements-concept" in {gap["kind"] for gap in gaps}


def test_bridged_code_graph_enables_missing_implementation_gaps():
    bridged = {**CONCEPTS, "meta": {**CONCEPTS["meta"], "kind": "bridged"}}

    gaps = harvest(PACK, CONCEPTS, code_graph=bridged)

    assert "no-implements-concept" in {gap["kind"] for gap in gaps}


def test_todo_scan(tmp_path):
    (tmp_path / "m.py").write_text(
        "x = 1  # TODO: cache this\n", encoding="utf-8")
    gaps = harvest(PACK, CONCEPTS, repo_dir=tmp_path)
    todos = [gap for gap in gaps if gap["kind"] == "todo-comment"]
    assert todos and "m.py:1" in todos[0]["anchors"]["sources"][0]


def test_todo_scan_is_deterministic(tmp_path):
    (tmp_path / "b.py").write_text("# TODO: second\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("# TODO: first\n", encoding="utf-8")

    todos = [gap for gap in harvest(PACK, CONCEPTS, repo_dir=tmp_path)
             if gap["kind"] == "todo-comment"]

    assert [gap["anchors"]["sources"][0] for gap in todos] == [
        "a.py:1", "b.py:1",
    ]


def test_todo_anchors_matching_code_node_with_relative_path(tmp_path):
    source_dir = tmp_path / "src"
    source_dir.mkdir()
    (source_dir / "m.py").write_text("# TODO: cache this\n", encoding="utf-8")
    code_graph = {
        "meta": {"kind": "code", "source": "repo",
                 "generated": "x", "version": 1},
        "nodes": [{"id": "src/m.py::work", "kind": "function",
                   "label": "work", "source_ref": "src/m.py:L1"}],
        "edges": [],
    }

    gaps = harvest(PACK, CONCEPTS, code_graph=code_graph, repo_dir=tmp_path)

    todo = next(gap for gap in gaps if gap["kind"] == "todo-comment")
    assert todo["anchors"] == {
        "nodes": ["src/m.py::work"],
        "sources": ["src/m.py:1"],
    }

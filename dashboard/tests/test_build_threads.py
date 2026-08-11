"""Threads: what a concept builds on, and what it sets up.

The graph has carried this since the first build and no page ever showed it.
A paper is a dependency graph, not a list, and the connective tissue -- why
this concept exists given what came before, and what it unlocks -- is the one
thing a reader cannot get from the paper's own prose without reading all of it.

Derived, never authored: the edges are already there, so no model is involved
and the threads cannot disagree with the concept map.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_data import threads  # noqa: E402

# Mirrors the real AIAYN graph: builds-on points src -> dst (dst comes first),
# prerequisite points prerequisite -> dependent, part-of is containment.
GRAPH = {
    "nodes": [
        {"id": "transformer", "label": "Transformer"},
        {"id": "sdpa", "label": "Scaled Dot-Product Attention"},
        {"id": "mha", "label": "Multi-Head Attention"},
        {"id": "why-self-attention", "label": "Why Self-Attention"},
        {"id": "training", "label": "Training"},
        {"id": "results", "label": "Machine Translation Results"},
        {"id": "stacks", "label": "Encoder and Decoder Stacks"},
    ],
    "edges": [
        {"src": "mha", "dst": "sdpa", "kind": "builds-on"},
        {"src": "transformer", "dst": "why-self-attention", "kind": "builds-on"},
        {"src": "results", "dst": "transformer", "kind": "builds-on"},
        {"src": "training", "dst": "results", "kind": "prerequisite"},
        {"src": "stacks", "dst": "transformer", "kind": "part-of"},
        {"src": "why-self-attention", "dst": "training", "kind": "contrasts-with"},
    ],
}


def test_builds_on_follows_the_edge_to_what_came_first():
    """Multi-Head Attention builds-on Scaled Dot-Product Attention, so SDPA is
    what the reader needs first."""
    assert [t["id"] for t in threads(GRAPH)["mha"]["buildsOn"]] == ["sdpa"]


def test_sets_up_is_the_same_edge_read_backwards():
    assert [t["id"] for t in threads(GRAPH)["sdpa"]["setsUp"]] == ["mha"]


def test_a_prerequisite_points_from_the_earlier_concept():
    """Training is a prerequisite OF Machine Translation Results, so the
    results build on training and training sets up the results -- the opposite
    reading of the arrow from builds-on."""
    out = threads(GRAPH)

    assert [t["id"] for t in out["results"]["buildsOn"]] == ["training", "transformer"]
    assert [t["id"] for t in out["training"]["setsUp"]] == ["results"]


def test_containment_is_not_a_dependency():
    """Encoder and Decoder Stacks is part-of Transformer. That is hierarchy,
    which the concept map already shows; presenting it as a dependency would
    tell the reader the stacks must be understood before the Transformer."""
    out = threads(GRAPH)

    assert out["stacks"]["buildsOn"] == []
    assert [t["id"] for t in out["transformer"]["setsUp"]] == ["results"]


def test_contrasts_with_is_not_a_thread():
    """A comparison is not an order. Asserted against the specific concept the
    contrasts-with edge points at, not against the whole list -- Why
    Self-Attention legitimately sets up the Transformer through a builds-on
    edge, and asserting an empty list here would have tested nothing."""
    out = threads(GRAPH)["why-self-attention"]

    assert "training" not in [t["id"] for t in out["setsUp"] + out["buildsOn"]]


def test_every_concept_appears_even_with_no_threads():
    """A page asking whether it has threads must not have to handle a missing
    key differently from an empty one."""
    out = threads(GRAPH)

    assert set(out) == {n["id"] for n in GRAPH["nodes"]}
    assert out["stacks"] == {"buildsOn": [], "setsUp": []}


def test_the_label_travels_so_the_page_can_name_the_concept():
    assert threads(GRAPH)["mha"]["buildsOn"][0]["label"] == "Scaled Dot-Product Attention"


def test_threads_are_ordered_so_the_bundle_is_stable():
    """Two builds every day must produce the same bytes, or every rebuild is a
    diff. Sorted by label, which is also the order a reader scans."""
    out = threads(GRAPH)["results"]["buildsOn"]

    assert [t["label"] for t in out] == ["Training", "Transformer"]


def test_an_edge_to_a_node_that_is_not_in_the_graph_is_dropped():
    """A bridged graph carries code nodes and implements edges; a thread must
    never point at something the reader cannot open."""
    graph = {"nodes": [{"id": "a", "label": "A"}],
             "edges": [{"src": "a", "dst": "ghost", "kind": "builds-on"}]}

    assert threads(graph)["a"]["buildsOn"] == []

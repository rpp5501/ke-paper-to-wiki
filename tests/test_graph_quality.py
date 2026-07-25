"""R16 §5.1c — zero-token graph-quality metrics (kg-gen MINE-lite).

kg-gen's MINE benchmark scores a graph with an LLM. We take the idea and drop
the tokens: orphan ratio, near-duplicate slug candidates by pure string
normalization, and part-of tree coverage. Deterministic, no model, no network.

These are advisory findings, not a tripwire. is_toc_graph raises because a TOC
graph is a *wrong* graph; a graph with orphans is a *thin* graph, and stopping
the build on it would be the wrong trade.
"""
import pytest

from paper_skill.concepts import (
    ORPHAN_RATIO_LIMIT,
    PART_OF_COVERAGE_FLOOR,
    graph_quality,
    graph_quality_findings,
    normalize_slug,
)


# ── slug normalization ───────────────────────────────────────────────────
@pytest.mark.parametrize("raw,expected", [
    ("self-attention", "self-attention"),
    ("self_attention", "self-attention"),
    ("Self Attention", "self-attention"),
    ("  SELF--ATTENTION  ", "self-attention"),
    ("self.attention", "self-attention"),
    ("", ""),
])
def test_normalize_slug_vectors(raw, expected):
    assert normalize_slug(raw) == expected


def test_normalize_slug_keeps_genuinely_different_ids_apart():
    assert normalize_slug("attention") != normalize_slug("attentions")


# ── metrics ──────────────────────────────────────────────────────────────
def _graph(nodes, edges):
    return {"nodes": [{"id": n} for n in nodes], "edges": edges}


def test_orphan_ratio_counts_nodes_with_no_edges():
    g = _graph(["a", "b", "c", "d"],
               [{"src": "a", "dst": "b", "kind": "part-of"}])

    assert graph_quality(g)["orphan_ratio"] == 0.5  # c and d


def test_orphan_ratio_is_zero_when_everything_connects():
    g = _graph(["a", "b"], [{"src": "a", "dst": "b", "kind": "part-of"}])

    assert graph_quality(g)["orphan_ratio"] == 0.0


def test_duplicate_slugs_groups_ids_that_normalize_together():
    g = _graph(["self-attention", "self_attention", "Self Attention", "mlp"], [])

    dupes = graph_quality(g)["duplicate_slugs"]

    assert dupes == {"self-attention":
                     ["Self Attention", "self-attention", "self_attention"]}


def test_no_duplicate_slugs_on_a_clean_graph():
    assert graph_quality(_graph(["a", "b"], []))["duplicate_slugs"] == {}


def test_part_of_coverage_is_the_share_touching_the_tree():
    g = _graph(["root", "child", "loose"],
               [{"src": "child", "dst": "root", "kind": "part-of"},
                {"src": "loose", "dst": "root", "kind": "builds-on"}])

    # root and child are in the part-of tree; loose only has a non-tree edge.
    assert graph_quality(g)["part_of_coverage"] == pytest.approx(2 / 3)


def test_metrics_on_an_empty_graph_do_not_divide_by_zero():
    m = graph_quality({"nodes": [], "edges": []})

    assert m["orphan_ratio"] == 0.0
    assert m["part_of_coverage"] == 0.0
    assert m["node_count"] == 0


# ── findings ─────────────────────────────────────────────────────────────
def test_a_healthy_graph_produces_no_findings():
    g = _graph(["root", "a", "b"],
               [{"src": "a", "dst": "root", "kind": "part-of"},
                {"src": "b", "dst": "root", "kind": "part-of"}])

    assert graph_quality_findings(g) == []


def test_too_many_orphans_is_reported():
    g = _graph(["root", "a", "x", "y", "z"],
               [{"src": "a", "dst": "root", "kind": "part-of"}])

    findings = graph_quality_findings(g)

    assert any("orphan" in f for f in findings)


def test_duplicate_slug_candidates_are_reported():
    g = _graph(["root", "self-attention", "self_attention"],
               [{"src": "self-attention", "dst": "root", "kind": "part-of"},
                {"src": "self_attention", "dst": "root", "kind": "part-of"}])

    findings = graph_quality_findings(g)

    assert any("self-attention" in f and "duplicate" in f for f in findings)


def test_thin_part_of_coverage_is_reported():
    g = _graph(["a", "b", "c", "d"],
               [{"src": "a", "dst": "b", "kind": "builds-on"},
                {"src": "c", "dst": "d", "kind": "builds-on"}])

    assert any("part-of" in f for f in graph_quality_findings(g))


def test_findings_never_raise_on_a_degenerate_graph():
    assert isinstance(graph_quality_findings({"nodes": [], "edges": []}), list)


def test_thresholds_are_named_not_magic():
    assert 0 < ORPHAN_RATIO_LIMIT < 1
    assert 0 < PART_OF_COVERAGE_FLOOR < 1

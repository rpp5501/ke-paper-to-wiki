import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import (build_bundle, main, reading_path, strip_images,
                        parse_data_ts, to_data_ts, _content_quality_report,
                        _excerpts, _tour)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "fixtures" / "aiayn_concept_graph.json"
COMMITTED_DATA = ROOT / "dashboard" / "src" / "data.gen.ts"
TINY_PACK_PATH = ROOT / "fixtures" / "aiayn_tiny_pack.json"
PAGES_DIR = ROOT / "fixtures" / "pages"
WIKI_DIR = ROOT / "fixtures" / "wiki"
SID_ARTIFACT = ROOT / "artifacts" / "p1306.1043-live"
FIXTURE = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
PACK = {"meta": {"source": "arXiv:1706.03762", "title": "AIAYN",
                 "generated": "2026-07-09"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3_2", "title": "SDPA", "level": 2, "text": "t"}],
        "equations": [{"id": "eq_1", "latex": "x", "section": "sec_3_2"}],
        "references": [], "figures": []}


def test_content_quality_report_enforces_prose_thresholds_but_exempts_code():
    warning = " ".join(["scan"] * 61)
    error = " ".join(["dense"] * 101)
    code = " ".join(["token"] * 140)
    report = _content_quality_report({
        "a": f"# A\n\n{warning}\n\n{error}\n\n```python\n{code}\n```",
    })

    assert report["readability"]["paragraphs"] == 2
    assert len(report["readability"]["warnings"]) == 1
    assert len(report["readability"]["errors"]) == 1
    assert report["releasePass"] is False


def test_content_quality_report_counts_bulleted_and_ordered_prose():
    warning = " ".join(["bullet"] * 61)
    error = " ".join(["ordered"] * 101)

    report = _content_quality_report({
        "a": f"# A\n\n- {warning}\n\n1. {error}\n\n| column | column |\n| - | - |\n| {'table ' * 140} | x |",
    })

    assert report["readability"]["paragraphs"] == 2
    assert report["readability"]["warnings"] == [
        {"nodeId": "a", "paragraph": 1, "words": 61}]
    assert report["readability"]["errors"] == [
        {"nodeId": "a", "paragraph": 2, "words": 101}]


def test_content_quality_reports_missing_example_evidence_for_required_pages():
    report = _content_quality_report(
        {
            "has-boundary": "**Boundary case:** a root intervention leaves a non-descendant unchanged.",
            "missing": "This definition has no worked case yet.",
        },
        required_example_ids=["has-boundary", "missing"],
    )

    assert report["workedExampleCoverage"] == {
        "requiredConceptIds": ["has-boundary", "missing"],
        "coveredConceptIds": ["has-boundary"],
        "missingConceptIds": ["missing"],
        "evidence": [{"nodeId": "has-boundary", "kind": "boundary case"}],
    }
    assert report["releasePass"] is False


def test_content_quality_resumes_after_a_display_equation_with_an_anchor():
    prose = " ".join(["boundary"] * 61)
    report = _content_quality_report(
        {"a": f"$$\nx = 1\n\\end{{aligned}}$$ [eq_1]\n\n**Boundary case:** {prose}"},
        required_example_ids=["a"],
    )

    assert report["readability"]["warnings"] == [
        {"nodeId": "a", "paragraph": 1, "words": 63}]
    assert report["workedExampleCoverage"]["missingConceptIds"] == []


def test_content_quality_report_finds_duplicate_explanations():
    repeated = "This explanation is deliberately long enough to be meaningful and repeats the same causal claim across two separate concept pages exactly."
    report = _content_quality_report({
        "a": f"# A\n\n{repeated}",
        "b": f"# B\n\n{repeated}",
    })

    assert report["duplicatedExplanations"][0]["nodeIds"] == ["a", "b"]
    assert report["releasePass"] is False


def _release_fixture(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_a.md").write_text(
        "# A\n\nA grounded explanation. [§sec_1]", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [{"id": "a", "kind": "concept", "label": "A",
                   "page": "01_a.md", "source_ref": "sec_1"}],
        "edges": [],
    }
    pack = {
        "sections": [{"id": "sec_1", "title": "Main", "level": 1,
                      "text": "Substantive paper text."}],
        "equations": [{"id": "eq_1", "latex": "x=1", "section": "sec_1"}],
    }
    learning = {
        "version": 1, "reviewed": True,
        "chapters": [{
            "id": "chapter", "title": "Chapter", "question": "Why?",
            "outcome": "Know it.", "conceptIds": ["a"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 1,
            "estimatedFullMinutes": 1,
        }],
    }
    return graph, pages, pack, learning


def test_bundle_has_all_contract_keys():
    b = build_bundle(FIXTURE, pack=PACK)
    for k in ("meta", "nodes", "edges", "pages", "notes", "hotspots",
              "clusters", "tour", "provenance", "centrality", "eqIndex",
              "trace", "glossary", "excerpts", "learningPath",
              "codeListings", "qualityReport", "bundleVersion"):
        assert k in b, k
    assert b["excerpts"] == {}
    assert b["learningPath"]["reviewed"] is False
    assert b["bundleVersion"] == 2


def test_reviewed_learning_path_covers_every_authored_concept(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    graph = {
        "meta": {"kind": "concept", "generated": "2026-08-05"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "A", "page": "01_a.md"},
            {"id": "b", "kind": "concept", "label": "B", "page": "02_b.md"},
        ],
        "edges": [{"src": "a", "dst": "b", "kind": "prerequisite"}],
    }
    (pages / "01_a.md").write_text("## TL;DR {#tldr}\nA", encoding="utf-8")
    (pages / "02_b.md").write_text("## TL;DR {#tldr}\nB", encoding="utf-8")
    manifest = tmp_path / "learning-path.json"
    manifest.write_text(json.dumps({
        "version": 1,
        "reviewed": True,
        "chapters": [{
            "id": "chapter-a",
            "title": "A then B",
            "question": "How do A and B connect?",
            "outcome": "Explain the dependency.",
            "conceptIds": ["a", "b"],
            "foundationConceptIds": ["a"],
            "advancedConceptIds": ["b"],
            "checkpointIds": [],
            "estimatedCoreMinutes": 5,
            "estimatedFullMinutes": 9,
        }],
    }), encoding="utf-8")

    bundle = build_bundle(
        graph, pages_dir=pages, learning_path=manifest,
    )

    assert bundle["learningPath"]["reviewed"] is True
    assert bundle["learningPath"]["chapters"][0]["conceptIds"] == ["a", "b"]
    assert bundle["coverage"] == {
        "authoredConcepts": 2,
        "coveredConcepts": 2,
        "uncoveredConceptIds": [],
        "topLevelSections": [],
        "uncoveredSectionIds": [],
    }


def test_reviewed_learning_path_rejects_an_uncovered_page(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    for name in ("01_a.md", "02_b.md"):
        (pages / name).write_text("## TL;DR {#tldr}\nText", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept", "generated": "2026-08-05"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "A", "page": "01_a.md"},
            {"id": "b", "kind": "concept", "label": "B", "page": "02_b.md"},
        ],
        "edges": [],
    }
    manifest = tmp_path / "learning-path.json"
    manifest.write_text(json.dumps({
        "version": 1,
        "chapters": [{
            "id": "only-a", "title": "Only A", "question": "A?",
            "outcome": "Know A", "conceptIds": ["a"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 2,
            "estimatedFullMinutes": 2,
        }],
    }), encoding="utf-8")

    with pytest.raises(ValueError, match="uncovered authored concepts: b"):
        build_bundle(graph, pages_dir=pages, learning_path=manifest)


def test_reviewed_learning_path_rejects_prerequisites_after_first_use(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_a.md").write_text("# A", encoding="utf-8")
    (pages / "02_b.md").write_text("# B", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "A", "page": "01_a.md"},
            {"id": "b", "kind": "concept", "label": "B", "page": "02_b.md"},
        ],
        "edges": [{"src": "a", "dst": "b", "kind": "prerequisite"}],
    }
    chapter = {
        "id": "chapter", "title": "Chapter", "question": "Why?",
        "outcome": "Know it.", "conceptIds": ["b", "a"],
        "foundationConceptIds": [], "advancedConceptIds": [],
        "checkpointIds": [], "estimatedCoreMinutes": 2,
        "estimatedFullMinutes": 3,
    }

    with pytest.raises(ValueError, match="prerequisite 'a' appears after 'b'"):
        build_bundle(
            graph, pages_dir=pages,
            learning_path={"version": 1, "reviewed": True,
                           "chapters": [chapter]},
        )


def test_reviewed_learning_path_rejects_builds_on_after_first_use(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_a.md").write_text("# A", encoding="utf-8")
    (pages / "02_b.md").write_text("# B", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "A", "page": "01_a.md"},
            {"id": "b", "kind": "concept", "label": "B", "page": "02_b.md"},
        ],
        # a builds on b, so b must appear first in the guided route.
        "edges": [{"src": "a", "dst": "b", "kind": "builds-on"}],
    }
    chapter = {
        "id": "chapter", "title": "Chapter", "question": "Why?",
        "outcome": "Know it.", "conceptIds": ["a", "b"],
        "foundationConceptIds": [], "advancedConceptIds": [],
        "checkpointIds": [], "estimatedCoreMinutes": 2,
        "estimatedFullMinutes": 3,
    }

    with pytest.raises(ValueError, match="builds-on dependency 'b' appears after 'a'"):
        build_bundle(
            graph, pages_dir=pages,
            learning_path={"version": 1, "reviewed": True,
                           "chapters": [chapter]},
        )

    chapter["conceptIds"] = ["b", "a"]
    bundle = build_bundle(
        graph, pages_dir=pages,
        learning_path={"version": 1, "reviewed": True,
                       "chapters": [chapter]},
    )
    assert bundle["learningPath"]["chapters"][0]["conceptIds"] == ["b", "a"]


@pytest.mark.parametrize(("field", "member"), [
    ("foundationConceptIds", "b"),
    ("advancedConceptIds", "b"),
])
def test_learning_path_depth_members_must_be_chapter_concepts(field, member):
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "A"},
            {"id": "b", "kind": "concept", "label": "B"},
        ],
        "edges": [],
    }
    chapter = {
        "id": "chapter", "title": "Chapter", "question": "Why?",
        "outcome": "Know it.", "conceptIds": ["a"],
        "foundationConceptIds": [], "advancedConceptIds": [],
        "checkpointIds": [], "estimatedCoreMinutes": 1,
        "estimatedFullMinutes": 1,
    }
    chapter[field] = [member]

    with pytest.raises(ValueError, match=f"{field} must be included in conceptIds: b"):
        build_bundle(graph, learning_path={
            "version": 1, "reviewed": True, "chapters": [chapter],
        })


def test_learning_path_depth_members_cannot_be_both_foundation_and_advanced():
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [{"id": "a", "kind": "concept", "label": "A"}],
        "edges": [],
    }
    chapter = {
        "id": "chapter", "title": "Chapter", "question": "Why?",
        "outcome": "Know it.", "conceptIds": ["a"],
        "foundationConceptIds": ["a"], "advancedConceptIds": ["a"],
        "checkpointIds": [], "estimatedCoreMinutes": 1,
        "estimatedFullMinutes": 1,
    }

    with pytest.raises(ValueError, match="foundationConceptIds and advancedConceptIds overlap: a"):
        build_bundle(graph, learning_path={
            "version": 1, "reviewed": True, "chapters": [chapter],
        })


def test_learning_path_rejects_repeated_concepts_within_a_chapter():
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [{"id": "a", "kind": "concept", "label": "A"}],
        "edges": [],
    }
    chapter = {
        "id": "chapter", "title": "Chapter", "question": "Why?",
        "outcome": "Know it.", "conceptIds": ["a", "a"],
        "foundationConceptIds": [], "advancedConceptIds": [],
        "checkpointIds": [], "estimatedCoreMinutes": 1,
        "estimatedFullMinutes": 1,
    }

    with pytest.raises(ValueError, match="repeats conceptIds: a"):
        build_bundle(graph, learning_path={
            "version": 1, "reviewed": True, "chapters": [chapter],
        })


def test_learning_path_preserves_its_unreviewed_status_and_release_refuses_it():
    manifest = {
        "version": 1,
        "reviewed": False,
        "chapters": [{
            "id": "chapter", "title": "Chapter", "question": "Why?",
            "outcome": "Know it.", "conceptIds": [],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 1,
            "estimatedFullMinutes": 1,
        }],
    }

    assert build_bundle(FIXTURE, learning_path=manifest)["learningPath"]["reviewed"] is False
    with pytest.raises(ValueError, match="reviewed learning-path manifest"):
        build_bundle(FIXTURE, learning_path=manifest, release=True)


def test_release_flag_requires_a_reviewed_manifest(tmp_path):
    graph_obj, pages, pack_obj, _ = _release_fixture(tmp_path)
    graph = tmp_path / "graph.json"
    graph.write_text(json.dumps(graph_obj), encoding="utf-8")
    pack = tmp_path / "pack.json"
    pack.write_text(json.dumps(pack_obj), encoding="utf-8")

    with pytest.raises(ValueError, match="--learning-path"):
        main(["--release", "--graph", str(graph), "--pages-dir", str(pages),
              "--pack", str(pack), "--out", str(tmp_path / "data.ts")])


def test_release_requires_a_nonempty_pages_directory(tmp_path):
    graph, _, pack, learning = _release_fixture(tmp_path)
    empty_pages = tmp_path / "empty-pages"
    empty_pages.mkdir()

    with pytest.raises(ValueError, match="nonempty --pages-dir"):
        build_bundle(
            graph, pages_dir=empty_pages, pack=pack,
            learning_path=learning, release=True,
        )


@pytest.mark.parametrize("pack", [
    None,
    {},
    {"sections": [{"id": "sec_9", "title": "Acknowledgments",
                    "level": 1, "text": "Thanks."}], "equations": []},
])
def test_release_requires_a_substantive_pack(tmp_path, pack):
    graph, pages, _, learning = _release_fixture(tmp_path)

    with pytest.raises(ValueError, match="substantive sections or equations"):
        build_bundle(
            graph, pages_dir=pages, pack=pack,
            learning_path=learning, release=True,
        )


def test_release_requires_a_nonempty_reviewed_manifest(tmp_path):
    graph, pages, pack, learning = _release_fixture(tmp_path)
    learning["chapters"] = []

    with pytest.raises(ValueError, match="at least one chapter"):
        build_bundle(
            graph, pages_dir=pages, pack=pack,
            learning_path=learning, release=True,
        )


def test_release_requires_nonzero_authored_and_covered_concepts(tmp_path):
    graph, pages, pack, learning = _release_fixture(tmp_path)
    graph["nodes"][0]["id"] = "orphaned-node"
    del graph["nodes"][0]["page"]
    learning["chapters"][0]["conceptIds"] = ["orphaned-node"]

    with pytest.raises(ValueError, match="authored and covered concept"):
        build_bundle(
            graph, pages_dir=pages, pack=pack,
            learning_path=learning, release=True,
        )


def test_release_fails_when_the_quality_report_does_not_pass(tmp_path):
    graph, pages, pack, manifest = _release_fixture(tmp_path)
    (pages / "01_a.md").write_text(" ".join(["dense"] * 101), encoding="utf-8")

    with pytest.raises(ValueError, match="qualityReport.releasePass"):
        build_bundle(
            graph, pages_dir=pages, pack=pack,
            learning_path=manifest, release=True,
        )


def test_release_requires_example_evidence_for_every_authored_page(tmp_path):
    graph, pages, pack, manifest = _release_fixture(tmp_path)

    with pytest.raises(ValueError, match="qualityReport.releasePass"):
        build_bundle(
            graph, pages_dir=pages, pack=pack,
            learning_path=manifest, release=True,
        )


def test_section_coverage_reports_subsections_and_empty_grouping_sections(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    for name in ("01_a.md", "02_b.md", "03_c.md"):
        (pages / name).write_text("# Page", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "A", "page": "01_a.md",
             "source_ref": "sec:1.1"},
            {"id": "b", "kind": "concept", "label": "B", "page": "02_b.md",
             "source_ref": "sec:1.2"},
            {"id": "c", "kind": "concept", "label": "C", "page": "03_c.md",
             "source_ref": "sec:2"},
        ],
        "edges": [],
    }
    pack = {"sections": [
        {"id": "sec_1", "title": "Group", "level": 1, "text": ""},
        {"id": "sec_1_1", "title": "First", "level": 2, "text": "First text"},
        {"id": "sec_1_2", "title": "Second", "level": 2, "text": "Second text"},
        {"id": "sec_2", "title": "Standalone", "level": 1, "text": "Standalone text"},
    ]}
    manifest = {
        "version": 1, "reviewed": True,
        "chapters": [{
            "id": "chapter", "title": "Chapter", "question": "Why?",
            "outcome": "Know it.", "conceptIds": ["a", "b", "c"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 1,
            "estimatedFullMinutes": 1,
        }],
    }

    coverage = build_bundle(
        graph, pack=pack, pages_dir=pages, learning_path=manifest,
    )["coverage"]

    assert coverage["topLevelSections"] == [
        {
            "id": "sec_1", "title": "Group", "covered": True,
            "coveredByConceptIds": ["a", "b"],
            "subsections": [
                {"id": "sec_1_1", "title": "First", "covered": True,
                 "coveredByConceptIds": ["a"]},
                {"id": "sec_1_2", "title": "Second", "covered": True,
                 "coveredByConceptIds": ["b"]},
            ],
        },
        {
            "id": "sec_2", "title": "Standalone", "covered": True,
            "coveredByConceptIds": ["c"], "subsections": [],
        },
    ]
    assert coverage["uncoveredSectionIds"] == []


def test_release_rejects_uncovered_substantive_paper_sections(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_a.md").write_text("# A", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [{"id": "a", "kind": "concept", "label": "A",
                   "page": "01_a.md", "source_ref": "sec:1.1"}],
        "edges": [],
    }
    pack = {"sections": [
        {"id": "sec_1", "title": "Group", "level": 1, "text": ""},
        {"id": "sec_1_1", "title": "Covered", "level": 2, "text": "Text"},
        {"id": "sec_1_2", "title": "Missing", "level": 2, "text": "Text"},
    ]}
    manifest = {
        "version": 1, "reviewed": True,
        "chapters": [{
            "id": "chapter", "title": "Chapter", "question": "Why?",
            "outcome": "Know it.", "conceptIds": ["a"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 1,
            "estimatedFullMinutes": 1,
        }],
    }

    with pytest.raises(ValueError, match="qualityReport.releasePass"):
        build_bundle(
            graph, pack=pack, pages_dir=pages,
            learning_path=manifest, release=True,
        )


def test_section_coverage_includes_authored_equation_and_figure_nodes(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_eq.md").write_text("# Equation", encoding="utf-8")
    (pages / "02_fig.md").write_text("# Figure", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "equation-node", "kind": "equation", "label": "Equation",
             "page": "01_eq.md", "source_ref": "sec_1"},
            {"id": "figure-node", "kind": "figure", "label": "Figure",
             "page": "02_fig.md", "source_ref": "sec_2"},
        ],
        "edges": [],
    }
    pack = {"sections": [
        {"id": "sec_1", "title": "Equation", "level": 1, "text": "Text"},
        {"id": "sec_2", "title": "Figure", "level": 1, "text": "Text"},
    ]}
    learning = {
        "version": 1, "reviewed": True,
        "chapters": [{
            "id": "chapter", "title": "Chapter", "question": "Why?",
            "outcome": "Know it.",
            "conceptIds": ["equation-node", "figure-node"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 1,
            "estimatedFullMinutes": 1,
        }],
    }

    coverage = build_bundle(
        graph, pack=pack, pages_dir=pages, learning_path=learning,
    )["coverage"]

    assert coverage["uncoveredSectionIds"] == []
    assert [row["coveredByConceptIds"] for row in coverage["topLevelSections"]] == [
        ["equation-node"], ["figure-node"],
    ]


def test_section_coverage_credits_section_and_equation_evidence_in_pages(tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_a.md").write_text(
        "# A\n\nEvidence from [\u00a7sec_2] and [eq_1].", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [{"id": "a", "kind": "concept", "label": "A",
                   "page": "01_a.md", "source_ref": "sec_1"}],
        "edges": [],
    }
    pack = {
        "sections": [
            {"id": "sec_1", "title": "Direct", "level": 1, "text": "Text"},
            {"id": "sec_2", "title": "Cited", "level": 1, "text": "Text"},
            {"id": "sec_3", "title": "Equation", "level": 1, "text": "Text"},
        ],
        "equations": [{"id": "eq_1", "latex": "x=1", "section": "sec_3"}],
    }
    learning = {
        "version": 1, "reviewed": True,
        "chapters": [{
            "id": "chapter", "title": "Chapter", "question": "Why?",
            "outcome": "Know it.", "conceptIds": ["a"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 1,
            "estimatedFullMinutes": 1,
        }],
    }

    coverage = build_bundle(
        graph, pack=pack, pages_dir=pages, learning_path=learning,
    )["coverage"]

    assert coverage["uncoveredSectionIds"] == []
    assert all(row["coveredByConceptIds"] == ["a"]
               for row in coverage["topLevelSections"])


def test_acknowledgments_and_references_are_metadata_but_conclusions_are_substantive(
        tmp_path):
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "01_a.md").write_text("# A", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [{"id": "a", "kind": "concept", "label": "A",
                   "page": "01_a.md", "source_ref": "sec_1"}],
        "edges": [],
    }
    pack = {"sections": [
        {"id": "sec_1", "title": "Main", "level": 1, "text": "Text"},
        {"id": "sec_5", "title": "Conclusions", "level": 1, "text": "Text"},
        {"id": "sec_6", "title": "Acknowledgments", "level": 1, "text": "Text"},
        {"id": "sec_7", "title": "References", "level": 1, "text": "Text"},
    ]}
    learning = {
        "version": 1, "reviewed": True,
        "chapters": [{
            "id": "chapter", "title": "Chapter", "question": "Why?",
            "outcome": "Know it.", "conceptIds": ["a"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": [], "estimatedCoreMinutes": 1,
            "estimatedFullMinutes": 1,
        }],
    }

    coverage = build_bundle(
        graph, pack=pack, pages_dir=pages, learning_path=learning,
    )["coverage"]

    assert coverage["uncoveredSectionIds"] == ["sec_5"]
    by_id = {row["id"]: row for row in coverage["topLevelSections"]}
    assert by_id["sec_6"]["covered"] is True
    assert by_id["sec_7"]["covered"] is True


def test_dependent_side_matches_edge_direction_contract():
    assert build_bundle(FIXTURE, pack=PACK)["dependentSide"] == {
        "part-of": "dst",
        "prerequisite": "dst",
        "builds-on": "src",
    }


def test_tour_is_deterministic_reading_path_head():
    b = build_bundle(FIXTURE, pack=PACK)
    order = reading_path(FIXTURE)
    assert [s["nodeIds"][0] for s in b["tour"]] == order[:5]
    assert all(s["title"] and s["description"] for s in b["tour"])


def test_clusters_fall_back_to_level1_grouping():
    b = build_bundle(FIXTURE, pack=PACK)
    ids = {c["id"] for c in b["clusters"]}
    assert "attention" in ids
    members = next(c for c in b["clusters"] if c["id"] == "attention")["nodeIds"]
    assert "scaled-dot-product-attention" in members


def test_centrality_present_for_every_node():
    b = build_bundle(FIXTURE, pack=PACK)
    assert set(b["centrality"]) == {n["id"] for n in FIXTURE["nodes"]}


def test_eq_index_maps_equation_to_anchored_concepts():
    g = json.loads(json.dumps(FIXTURE))
    g["nodes"][0]["source_ref"] = "sec_3_2"
    b = build_bundle(g, pack=PACK)
    assert g["nodes"][0]["id"] in b["eqIndex"]["eq_1"]


def test_eq_index_normalizes_dotted_pack_sections_to_graph_source_refs():
    graph = {
        "meta": {"kind": "concept", "generated": "2026-07-09"},
        "nodes": [{
            "id": "scaled-dot-product-attention",
            "kind": "concept",
            "label": "Scaled dot-product attention",
            "source_ref": "sec:3.2.1",
        }],
        "edges": [],
    }
    pack = {
        "meta": {"source": "paper", "title": "Attention",
                 "generated": "2026-07-09"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3_2_1", "title": "Attention Function",
                      "level": 3, "text": "scaled attention"}],
        "equations": [{"id": "eq_attention", "latex": r"1/\sqrt{d_k}",
                       "section": "sec_3_2_1"}],
        "references": [],
        "figures": [],
    }

    bundle = build_bundle(graph, pack=pack)

    assert bundle["eqIndex"]["eq_attention"] == [
        "scaled-dot-product-attention"
    ]


def test_eq_index_does_not_join_blank_sections_or_node_refs():
    graph = {
        "meta": {"kind": "concept", "generated": "2026-07-09"},
        "nodes": [
            {"id": "missing-ref", "kind": "concept", "label": "Missing"},
            {"id": "blank-ref", "kind": "concept", "label": "Blank",
             "source_ref": "  "},
        ],
        "edges": [],
    }
    pack = {
        "meta": {"source": "paper", "title": "Attention",
                 "generated": "2026-07-09"},
        "extraction": {},
        "sections": [],
        "equations": [
            {"id": "missing-section", "latex": "x"},
            {"id": "blank-section", "latex": "y", "section": "  "},
        ],
        "references": [],
        "figures": [],
    }

    bundle = build_bundle(graph, pack=pack)

    assert bundle["eqIndex"] == {
        "blank-section": [],
        "missing-section": [],
    }


def test_repo_fixture_bundle_exercises_explain_drawer_contract():
    pack = json.loads(TINY_PACK_PATH.read_text(encoding="utf-8"))

    bundle = build_bundle(
        FIXTURE, pack=pack, pages_dir=PAGES_DIR, wiki_dir=WIKI_DIR)

    concept = "scaled-dot-product-attention"
    assert "sdpa" in bundle["pages"]
    assert all(anchor in bundle["pages"]["sdpa"] for anchor in (
        "{#tldr}", "{#intuition}", "{#mechanics}",
        "{#the-math}", "{#go-deeper}",
    ))
    assert r"\sqrt{d_k}" in bundle["pages"]["sdpa"]
    assert bundle["notes"][concept]["synthesis"]
    assert bundle["glossary"][concept]["softmax"]
    assert concept in bundle["eqIndex"]["eq_1"]
    written = [item for item in bundle["trace"]
               if item["phase"] == "written"]
    assert [item["nodeId"] for item in written] == [concept]
    node_ids = {node["id"] for node in bundle["nodes"]}
    assert {item["nodeId"] for item in bundle["trace"]} <= node_ids


def test_strip_images_removes_and_counts():
    md = "before ![diagram](../assets/x.png) after"
    out, n = strip_images(md)
    assert "![" not in out and "x.png" not in out and n == 1


def test_note_trace_dates_are_content_based_and_mtime_stable(tmp_path):
    pages_dir = tmp_path / "pages"
    wiki_dir = tmp_path / "wiki"
    pages_dir.mkdir()
    wiki_dir.mkdir()
    (pages_dir / "01_attention.md").write_text(
        "before ![diagram](../assets/x.png) after", encoding="utf-8")
    notes = {
        "attention.yaml": (
            'concept: attention\nstatus: verified\ndate: "2024-01-02"\n'
            'generated: "2024-01-01"\nsynthesis: dated\n'),
        "encoder-decoder-stack.yaml": (
            'concept: encoder-decoder-stack\nstatus: verified\n'
            'generated: "2024-02-03"\nsynthesis: generated\n'),
        "positional-encoding.yaml": (
            'concept: positional-encoding\nstatus: verified\n'
            'synthesis: fallback\n'),
    }
    for name, content in notes.items():
        path = wiki_dir / name
        path.write_text(content, encoding="utf-8")
        os.utime(path, (946684800, 946684800))

    first = build_bundle(FIXTURE, pages_dir=pages_dir, wiki_dir=wiki_dir)
    for path in wiki_dir.glob("*.yaml"):
        os.utime(path, (1893456000, 1893456000))
    second = build_bundle(FIXTURE, pages_dir=pages_dir, wiki_dir=wiki_dir)

    assert first == second
    researched_dates = {
        item["nodeId"]: item["date"]
        for item in first["trace"] if item["phase"] == "researched"
    }
    assert researched_dates == {
        "attention": "2024-01-02",
        "encoder-decoder-stack": "2024-02-03",
        "positional-encoding": FIXTURE["meta"]["generated"],
    }
    assert {node_id: note["date"] for node_id, note in first["notes"].items()} == {
        "attention": "2024-01-02",
        "encoder-decoder-stack": "2024-02-03",
        "positional-encoding": FIXTURE["meta"]["generated"],
    }
    assert first["pages"]["attention"] == "before  after"
    assert {item["date"] for item in first["trace"]
            if item["phase"] == "written"} == {FIXTURE["meta"]["generated"]}


def test_repo_dir_source_dates_prefer_git_and_use_generated_fallback(tmp_path):
    repo = tmp_path / "repo"
    source_dir = repo / "src"
    source_dir.mkdir(parents=True)
    tracked = source_dir / "tracked.py"
    untracked = source_dir / "untracked.py"
    tracked.write_text("def tracked(): pass\n", encoding="utf-8")
    untracked.write_text("def untracked(): pass\n", encoding="utf-8")

    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "src/tracked.py"], cwd=repo, check=True)
    commit_env = os.environ | {
        "GIT_AUTHOR_DATE": "2024-01-02T12:00:00+00:00",
        "GIT_COMMITTER_DATE": "2024-01-02T12:00:00+00:00",
    }
    subprocess.run(
        ["git", "-c", "user.name=Dashboard Tests",
         "-c", "user.email=dashboard@example.invalid",
         "commit", "-q", "-m", "fixture"],
        cwd=repo, env=commit_env, check=True,
    )

    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [
            {"id": "tracked", "kind": "function", "label": "tracked",
             "source_ref": "src/tracked.py:L1"},
            {"id": "untracked", "kind": "function", "label": "untracked",
             "source_ref": "src/untracked.py:L1"},
            {"id": "missing-ref", "kind": "class", "label": "missing-ref"},
            {"id": "empty-ref", "kind": "file", "label": "empty-ref",
             "source_ref": ""},
            {"id": "missing-file", "kind": "route", "label": "missing-file",
             "source_ref": "src/missing.py:L1"},
            {"id": "concept", "kind": "concept", "label": "concept"},
        ],
        "edges": [],
    }

    os.utime(tracked, (946684800, 946684800))
    os.utime(untracked, (946684800, 946684800))
    first = build_bundle(graph, repo_dir=repo)
    os.utime(tracked, (1893456000, 1893456000))
    os.utime(untracked, (1893456000, 1893456000))
    second = build_bundle(graph, repo_dir=repo)

    assert first["mtimes"] == {
        "tracked": "2024-01-02",
        "untracked": graph["meta"]["generated"],
        "missing-ref": graph["meta"]["generated"],
        "empty-ref": graph["meta"]["generated"],
        "missing-file": graph["meta"]["generated"],
    }
    assert second["mtimes"] == first["mtimes"]


def test_repo_dir_source_dates_fall_back_when_git_is_unavailable(tmp_path):
    repo = tmp_path / "not-a-git-repo"
    repo.mkdir()
    (repo / "module.py").write_text("value = 1\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [
            {"id": "module", "kind": "function", "label": "module",
             "source_ref": "module.py:L1"},
        ],
        "edges": [],
    }

    assert build_bundle(graph, repo_dir=repo)["mtimes"] == {
        "module": graph["meta"]["generated"],
    }


def test_bundle_without_repo_dir_omits_mtimes():
    assert "mtimes" not in build_bundle(FIXTURE, pack=PACK)


def test_code_excerpts_are_hotspot_scoped_line_capped_and_utf8_tolerant(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    lines = [f"line{i}".encode() for i in range(1, 101)]
    lines[2] = b"invalid-\xff"
    (repo / "big.py").write_bytes(b"\n".join(lines) + b"\n")
    (repo / "cold.py").write_text("cold\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [
            {"id": "big.py::f", "kind": "function", "label": "f",
             "source_ref": "big.py:L2"},
            {"id": "cold.py::g", "kind": "function", "label": "g",
             "source_ref": "cold.py:L1"},
        ],
        "edges": [],
    }

    bundle = build_bundle(
        graph, hotspots=[{"id": "big.py::f"}], repo_dir=repo)

    assert set(bundle["excerpts"]) == {"big.py::f"}
    excerpt = bundle["excerpts"]["big.py::f"]
    assert excerpt.splitlines()[0] == "line2"
    assert "invalid-�" in excerpt
    assert len(excerpt.splitlines()) == 80


def test_bridged_excerpts_keep_first_twenty_hotspots_plus_implements_sources(
        tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    nodes = []
    for index in range(1, 23):
        name = f"node{index}.py"
        (repo / name).write_text(f"node {index}\n", encoding="utf-8")
        nodes.append({
            "id": f"node-{index}", "kind": "function", "label": name,
            "source_ref": f"{name}:L1",
        })
    nodes.append({"id": "concept", "kind": "concept", "label": "Concept"})
    graph = {
        "meta": {"kind": "bridged", "generated": "2026-07-09"},
        "nodes": nodes,
        "edges": [{"src": "node-21", "dst": "concept", "kind": "implements"}],
    }
    hotspots = [{"id": f"node-{index}"} for index in range(1, 22)]

    excerpts = build_bundle(
        graph, hotspots=hotspots, repo_dir=repo)["excerpts"]

    assert set(excerpts) == {
        *(f"node-{index}" for index in range(1, 21)),
        "node-21",
    }
    assert "node-22" not in excerpts


def test_code_excerpts_reject_escaping_missing_and_invalid_source_refs(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("outside\n", encoding="utf-8")
    (repo / "valid.py").write_text("valid\n", encoding="utf-8")
    nodes = [
        {"id": "valid", "kind": "function", "label": "valid",
         "source_ref": "valid.py:L1"},
        {"id": "traversal", "kind": "function", "label": "traversal",
         "source_ref": "../outside.py:L1"},
        {"id": "absolute", "kind": "function", "label": "absolute",
         "source_ref": f"{outside}:L1"},
        {"id": "missing", "kind": "function", "label": "missing",
         "source_ref": "missing.py:L1"},
        {"id": "bad-line", "kind": "function", "label": "bad-line",
         "source_ref": "valid.py:not-a-line"},
        {"id": "no-location", "kind": "function", "label": "no-location",
         "source_ref": "valid.py"},
    ]
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": nodes,
        "edges": [],
    }

    excerpts = build_bundle(
        graph,
        hotspots=[{"id": node["id"]} for node in nodes],
        repo_dir=repo,
    )["excerpts"]

    assert excerpts == {"valid": "valid"}


def test_code_excerpts_honor_inclusive_source_ranges(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "range.py").write_text(
        "\n".join(f"line{index}" for index in range(1, 101)) + "\n",
        encoding="utf-8",
    )
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [{
            "id": "range", "kind": "function", "label": "range",
            "source_ref": "range.py:L10-L12",
        }],
        "edges": [],
    }

    excerpts = build_bundle(
        graph, hotspots=[{"id": "range"}], repo_dir=repo)["excerpts"]

    assert excerpts["range"] == "line10\nline11\nline12"


def test_python_code_listing_contains_preview_and_complete_symbol(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    body = "\n".join(f"    value_{i} = {i}" for i in range(1, 61))
    source = f"def long_helper():\n{body}\n    return value_60\n"
    (repo / "long.py").write_text(source, encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-08-05"},
        "nodes": [{
            "id": "long.py::long_helper", "kind": "function",
            "label": "long_helper", "source_ref": "long.py:L1",
        }],
        "edges": [],
    }

    bundle = build_bundle(
        graph,
        hotspots=[{"id": "long.py::long_helper"}],
        repo_dir=repo,
    )
    listing = bundle["codeListings"]["long.py::long_helper"]

    assert listing["path"] == "long.py"
    assert listing["symbolKind"] == "function"
    assert listing["startLine"] == 1
    assert listing["endLine"] == 62
    assert listing["previewEndLine"] == 40
    assert len(listing["preview"].splitlines()) == 40
    assert listing["full"].splitlines()[-1] == "    return value_60"
    assert listing["rangeResolved"] is True
    assert bundle["nodes"][0]["source_ref"] == "long.py:L1-L62"


def test_python_file_label_corrects_coarse_function_kind(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "sid.py").write_text("def helper():\n    return 1\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-08-05"},
        "nodes": [{
            "id": "sid", "kind": "function", "label": "sid.py",
            "source_ref": "sid.py:L1",
        }],
        "edges": [],
    }

    bundle = build_bundle(
        graph, hotspots=[{"id": "sid"}], repo_dir=repo,
    )
    listing = bundle["codeListings"]["sid"]

    assert listing["symbolKind"] == "file"
    assert listing["startLine"] == 1
    assert listing["endLine"] == 2
    assert listing["rangeResolved"] is True
    assert next(node for node in bundle["nodes"] if node["id"] == "sid")["kind"] == "file"


def test_python_ast_corrects_class_and_method_kinds(tmp_path):
    source = "@decorator\nclass SID:\n    def evaluate(self):\n        return 1\n"
    (tmp_path / "sid.py").write_text(source, encoding="utf-8")
    graph = {
        "meta": {"kind": "bridged", "generated": "2026-08-05"},
        "nodes": [
            {"id": "sid.py::SID", "kind": "function", "label": "SID",
             "source_ref": "sid.py:L2"},
            {"id": "sid.py::SID.evaluate", "kind": "function",
             "label": ".evaluate()", "source_ref": "sid.py:L3"},
        ],
        "edges": [],
    }

    bundle = build_bundle(graph, repo_dir=tmp_path)
    by_id = {node["id"]: node for node in bundle["nodes"]}

    assert by_id["sid.py::SID"]["kind"] == "class"
    assert by_id["sid.py::SID"]["source_ref"] == "sid.py:L1-L4"
    assert bundle["codeListings"]["sid.py::SID.evaluate"]["symbolKind"] == "method"


def test_code_listings_cover_every_code_node_and_mark_unresolved_ranges(tmp_path):
    (tmp_path / "module.py").write_text(
        "def first():\n    return 1\n\n\ndef second():\n    return 2\n",
        encoding="utf-8",
    )
    graph = {
        "meta": {"kind": "code"},
        "nodes": [
            {"id": "first", "kind": "function", "label": "first",
             "source_ref": "module.py:L1"},
            {"id": "second", "kind": "function", "label": "second",
             "source_ref": "module.py:L5"},
            {"id": "missing", "kind": "function", "label": "missing",
             "source_ref": "missing.py:L1"},
            {"id": "oversized", "kind": "function", "label": "oversized",
             "source_ref": "module.py:L1-L99"},
            {"id": "concept", "kind": "concept", "label": "Concept"},
        ],
        "edges": [],
    }

    listings = build_bundle(
        graph, hotspots=[{"id": "first"}], repo_dir=tmp_path,
    )["codeListings"]

    assert set(listings) == {"first", "second", "missing", "oversized"}
    assert listings["second"]["rangeResolved"] is True
    assert listings["missing"]["rangeResolved"] is False
    assert listings["oversized"]["rangeResolved"] is False


def test_python_ast_expands_a_truncated_explicit_source_range(tmp_path):
    (tmp_path / "module.py").write_text(
        "def expanded():\n    value = 1\n    value += 1\n    return value\n",
        encoding="utf-8",
    )
    graph = {
        "meta": {"kind": "code"},
        "nodes": [{"id": "expanded", "kind": "function", "label": "expanded",
                   "source_ref": "module.py:L1-L2"}],
        "edges": [],
    }

    bundle = build_bundle(graph, repo_dir=tmp_path)
    listing = bundle["codeListings"]["expanded"]

    assert listing["startLine"] == 1
    assert listing["endLine"] == 4
    assert listing["rangeResolved"] is True
    assert "return value" in listing["full"]
    assert bundle["nodes"][0]["source_ref"] == "module.py:L1-L4"


def test_code_listings_inspect_code_nodes_when_graph_meta_is_generic(tmp_path):
    (tmp_path / "module.py").write_text(
        "def helper():\n    return 1\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "concept"},
        "nodes": [{"id": "helper", "kind": "function", "label": "helper",
                   "source_ref": "module.py:L1"}],
        "edges": [],
    }

    listing = build_bundle(graph, repo_dir=tmp_path)["codeListings"]["helper"]

    assert listing["rangeResolved"] is True
    assert listing["endLine"] == 2


def test_code_excerpts_stream_the_bounded_range(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    source = repo / "stream.py"
    source.write_text(
        "\n".join(f"line{index}" for index in range(1, 101)) + "\n",
        encoding="utf-8",
    )
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [{
            "id": "stream", "kind": "function", "label": "stream",
            "source_ref": "stream.py:L10-L12",
        }],
        "edges": [],
    }
    original_read_text = Path.read_text

    def reject_whole_file_read(path, *args, **kwargs):
        if path == source:
            raise AssertionError("excerpt sources must be streamed")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", reject_whole_file_read)

    excerpts = _excerpts(
        graph, hotspots=[{"id": "stream"}], repo_dir=repo)

    assert excerpts["stream"] == "line10\nline11\nline12"


def test_code_excerpts_reject_reversed_source_ranges(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "range.py").write_text("line1\nline2\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [{
            "id": "reversed", "kind": "function", "label": "reversed",
            "source_ref": "range.py:L2-L1",
        }],
        "edges": [],
    }

    excerpts = build_bundle(
        graph, hotspots=[{"id": "reversed"}], repo_dir=repo)["excerpts"]

    assert excerpts == {}


def test_code_excerpts_skip_path_resolution_runtime_errors(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "loop.py").write_text("loop\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [{
            "id": "loop", "kind": "function", "label": "loop",
            "source_ref": "loop.py:L1",
        }],
        "edges": [],
    }
    original_resolve = Path.resolve

    def resolve_with_loop_error(path, *args, **kwargs):
        if path.name == "loop.py":
            raise RuntimeError("Symlink loop from 'loop.py'")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve_with_loop_error)

    excerpts = build_bundle(
        graph, hotspots=[{"id": "loop"}], repo_dir=repo)["excerpts"]

    assert excerpts == {}


def test_code_excerpts_skip_repo_resolution_runtime_errors(tmp_path, monkeypatch):
    repo = tmp_path / "repo-loop"
    repo.mkdir()
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [],
        "edges": [],
    }
    original_resolve = Path.resolve

    def resolve_with_loop_error(path, *args, **kwargs):
        if path == repo:
            raise RuntimeError("Symlink loop from repo_dir")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve_with_loop_error)

    assert build_bundle(graph, repo_dir=repo)["excerpts"] == {}


def test_code_excerpts_skip_oversized_numeric_locations(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "huge.py").write_text("line1\n", encoding="utf-8")
    graph = {
        "meta": {"kind": "code", "generated": "2026-07-09"},
        "nodes": [{
            "id": "huge", "kind": "function", "label": "huge",
            "source_ref": f"huge.py:L{'9' * 5000}",
        }],
        "edges": [],
    }

    excerpts = build_bundle(
        graph, hotspots=[{"id": "huge"}], repo_dir=repo)["excerpts"]

    assert excerpts == {}


def test_ts_output_is_wellformed_and_unicode_raw():
    b = build_bundle(FIXTURE, pack=PACK)
    ts = to_data_ts(b)
    assert ts.startswith("// generated by build_data.py")
    assert "export const KE_DATA" in ts
    assert "√dₖ" in ts
    json.loads(ts.split("=", 1)[1].rstrip().rstrip(";"))


def test_cli_writes_utf8_with_byte_stable_lf(tmp_path):
    out = tmp_path / "data.gen.ts"

    assert main(["--graph", str(FIXTURE_PATH), "--out", str(out)]) == 0

    data = out.read_bytes()
    assert data.startswith(b"// generated by build_data.py")
    assert b"\r\n" not in data
    assert data.endswith(b";\n")
    assert "√dₖ".encode() in data


def test_repo_fixture_regeneration_is_deterministic(tmp_path):
    out = tmp_path / "data.gen.ts"
    second = tmp_path / "data.second.gen.ts"

    args = [
        "--graph", str(FIXTURE_PATH),
        "--pack", str(TINY_PACK_PATH),
        "--pages-dir", str(PAGES_DIR),
        "--wiki-dir", str(WIKI_DIR),
    ]
    assert main([*args, "--out", str(out)]) == 0
    assert main([*args, "--out", str(second)]) == 0

    assert out.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")


def test_tour_descriptions_use_page_tldr():
    plan_graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "Alpha", "level": 0,
             "page": "01_a.md"},
            {"id": "b", "kind": "concept", "label": "Beta", "level": 1},
        ],
        "edges": [{"src": "a", "dst": "b", "kind": "prerequisite"}],
    }
    pages = {"a": "## TL;DR {#tldr}\nAlpha is the core idea. More.\n"}
    tour = _tour(plan_graph, [], pages)
    by_title = {t["title"]: t["description"] for t in tour}
    assert by_title["Alpha"] == "Alpha is the core idea."
    assert by_title["Beta"] == "Next stop on the dependency-ordered reading path."


def test_tour_descriptions_fall_back_when_page_lacks_tldr():
    plan_graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "c", "kind": "concept", "label": "Gamma", "level": 0,
             "page": "01_c.md"},
        ],
        "edges": [],
    }
    pages = {"c": "# Title\nSome intro text."}
    tour = _tour(plan_graph, [], pages)
    by_title = {t["title"]: t["description"] for t in tour}
    assert by_title["Gamma"] == "Next stop on the dependency-ordered reading path."


# --- code-bridge path (the AIAYN fixture has no implements edges / excerpts) ---
BRIDGE_DIR = ROOT / "fixtures" / "bridge_mini"
BRIDGE_GRAPH = json.loads((BRIDGE_DIR / "concept_graph.json").read_text(encoding="utf-8"))


def test_bridged_graph_yields_excerpt_and_implements_edge():
    b = build_bundle(BRIDGE_GRAPH, repo_dir=str(BRIDGE_DIR / "repo"))
    # the implements edge survives into the bundle
    assert any(e["kind"] == "implements"
               and e["src"] == "attention.py::attention"
               and e["dst"] == "scaled-dot-product-attention"
               for e in b["edges"])
    # the excerpt data path (empty for AIAYN) is populated for a real code node
    excerpt = b["excerpts"]["attention.py::attention"]
    assert "def attention" in excerpt and "softmax" in excerpt


def test_bridged_excerpt_is_embedded_in_generated_module():
    b = build_bundle(BRIDGE_GRAPH, repo_dir=str(BRIDGE_DIR / "repo"))
    ts = to_data_ts(b)
    assert "attention.py::attention" in ts
    assert "def attention" in ts


# On a bridged graph the `implements` edges run code -> concept, which makes the
# code nodes roots of the dependency order -- so reading_path handed the tour
# five pgmpy functions (._evaluate(), _compute_path_matrix(), ...). None of them
# has a page, so the guided tour walked the reader through empty panels and the
# article, whose chapters are built from those same steps, rendered nothing at
# all. The tour is about the paper; a step with no page has nothing to show.
BRIDGED = {
    "meta": {"kind": "bridged"},
    "nodes": [
        {"id": "fn_a", "kind": "function", "label": "_helper()", "level": 0},
        {"id": "fn_b", "kind": "function", "label": "_other()", "level": 0},
        {"id": "c1", "kind": "concept", "label": "First Concept", "level": 0,
         "page": "01_c1.md"},
        {"id": "c2", "kind": "concept", "label": "Second Concept", "level": 1,
         "page": "02_c2.md"},
    ],
    "edges": [
        {"src": "fn_a", "dst": "c1", "kind": "implements", "weight": 1.0},
        {"src": "fn_b", "dst": "c2", "kind": "implements", "weight": 1.0},
        {"src": "c1", "dst": "c2", "kind": "prerequisite", "weight": 1.0},
    ],
}
def _bridged_pages(tmp_path):
    d = tmp_path / "pages"
    d.mkdir()
    (d / "01_c1.md").write_text("## TL;DR {#tldr}\nFirst blurb.\n", encoding="utf-8")
    (d / "02_c2.md").write_text("## TL;DR {#tldr}\nSecond blurb.\n", encoding="utf-8")
    return d


def test_the_tour_skips_code_nodes(tmp_path):
    b = build_bundle(BRIDGED, pages_dir=_bridged_pages(tmp_path))
    picked = [s["nodeIds"][0] for s in b["tour"]]
    assert picked == ["c1", "c2"], picked


def test_the_tour_keeps_the_reading_order_of_what_is_left(tmp_path):
    b = build_bundle(BRIDGED, pages_dir=_bridged_pages(tmp_path))
    assert [s["title"] for s in b["tour"]] == ["First Concept", "Second Concept"]


def test_tour_steps_still_describe_themselves_from_the_page(tmp_path):
    b = build_bundle(BRIDGED, pages_dir=_bridged_pages(tmp_path))
    assert b["tour"][0]["description"] == "First blurb."


def test_a_graph_with_no_pages_at_all_still_gets_a_tour(tmp_path):
    """A code-only build has no pages; an empty tour would be worse than a
    generic one."""
    empty = tmp_path / "none"
    empty.mkdir()
    assert len(build_bundle(BRIDGED, pages_dir=empty)["tour"]) > 0


def test_a_graph_of_only_code_still_gets_a_tour(tmp_path):
    """Filtering to concepts must not empty the tour of a pure code graph."""
    code_only = {"meta": {"kind": "bridged"},
                 "nodes": [n for n in BRIDGED["nodes"] if n["kind"] == "function"],
                 "edges": []}
    empty = tmp_path / "none2"
    empty.mkdir()
    assert len(build_bundle(code_only, pages_dir=empty)["tour"]) > 0


# A code node has no page and no research note, so with no excerpt the drawer
# shows "no page or note for this node yet" and nothing else. Reported for
# _reachable_on_non_directed_path(): excerpts covered only hotspots and
# bridge-confirmed nodes, so 3 of the 6 pgmpy functions were blank panels.
def test_every_code_node_in_a_bridged_graph_carries_its_source(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def a():\n    return 1\n\n\ndef b():\n    return 2\n",
                   encoding="utf-8")
    graph = {
        "meta": {"kind": "bridged"},
        "nodes": [
            {"id": "c", "kind": "concept", "label": "Concept", "level": 0},
            {"id": "fn_a", "kind": "function", "label": "a()",
             "source_ref": "mod.py:L1"},
            {"id": "fn_b", "kind": "function", "label": "b()",
             "source_ref": "mod.py:L5"},
        ],
        # only fn_a is bridged; fn_b is the one that used to come back blank
        "edges": [{"src": "fn_a", "dst": "c", "kind": "implements"}],
    }

    excerpts = build_bundle(graph, repo_dir=tmp_path)["excerpts"]

    assert "fn_a" in excerpts
    assert "fn_b" in excerpts, "an unbridged code node still needs its source"
    assert "def b()" in excerpts["fn_b"]


def test_concept_nodes_do_not_get_excerpts(tmp_path):
    """They have pages; an excerpt would be duplicate weight in the bundle."""
    graph = {
        "meta": {"kind": "bridged"},
        "nodes": [{"id": "c", "kind": "concept", "label": "C",
                   "source_ref": "mod.py:L1"}],
        "edges": [],
    }
    (tmp_path / "mod.py").write_text("x = 1\n", encoding="utf-8")
    assert build_bundle(graph, repo_dir=tmp_path)["excerpts"] == {}


def _stable_generated_bundle(bundle):
    source_derived_or_audited = {
        "codeListings", "excerpts", "mtimes",
    }
    return {key: value for key, value in bundle.items()
            if key not in source_derived_or_audited}


def test_sid_production_regeneration_matches_checked_in_bundle():
    graph = json.loads(
        (SID_ARTIFACT / "bridged-graph.json").read_text(encoding="utf-8"))
    pack = json.loads(
        (SID_ARTIFACT / "pack.json").read_text(encoding="utf-8"))

    generated = build_bundle(
        graph,
        pack=pack,
        pages_dir=SID_ARTIFACT / "pages",
        wiki_dir=SID_ARTIFACT / "wiki",
        next_steps=SID_ARTIFACT / "ideas.yaml",
        quiz=SID_ARTIFACT / "quiz.json",
        learning_path=SID_ARTIFACT / "learning-path.json",
    )
    committed = parse_data_ts(COMMITTED_DATA.read_text(encoding="utf-8"))

    assert _stable_generated_bundle(generated) == _stable_generated_bundle(committed)


def test_sid_bundle_currently_fails_the_checkpoint_density_floor():
    """release=True used to pass here, on an artifact carrying one checkpoint
    per ~2,400 words with five of nine in a single chapter. The floor now says
    so out loud. This test is the ledger of that debt: when the quiz is written
    up to the floor it will fail, and the assertions below become release=True
    again on the test above.
    """
    graph = json.loads(
        (SID_ARTIFACT / "bridged-graph.json").read_text(encoding="utf-8"))
    pack = json.loads((SID_ARTIFACT / "pack.json").read_text(encoding="utf-8"))

    bundle = build_bundle(
        graph,
        pack=pack,
        pages_dir=SID_ARTIFACT / "pages",
        wiki_dir=SID_ARTIFACT / "wiki",
        quiz=SID_ARTIFACT / "quiz.json",
        learning_path=SID_ARTIFACT / "learning-path.json",
    )
    density = bundle["qualityReport"]["checkpointDensity"]

    assert density["items"] < density["expectedItems"], (
        "quiz now meets the density floor -- restore release=True above and "
        "delete this test")
    assert density["thinChapterIds"], "every chapter now has >=2 checkpoints"
    assert bundle["qualityReport"]["releasePass"] is False


def test_sid_pages_have_honest_worked_example_evidence_for_every_concept():
    graph = json.loads(
        (SID_ARTIFACT / "bridged-graph.json").read_text(encoding="utf-8"))
    pack = json.loads(
        (SID_ARTIFACT / "pack.json").read_text(encoding="utf-8"))

    report = build_bundle(
        graph,
        pack=pack,
        pages_dir=SID_ARTIFACT / "pages",
        quiz=SID_ARTIFACT / "quiz.json",
        learning_path=SID_ARTIFACT / "learning-path.json",
    )["qualityReport"]["workedExampleCoverage"]

    assert report["requiredConceptIds"] == report["coveredConceptIds"]
    assert report["missingConceptIds"] == []
    assert len(report["requiredConceptIds"]) == 24


def test_checked_in_sid_code_listings_match_the_production_source_contract():
    committed = parse_data_ts(COMMITTED_DATA.read_text(encoding="utf-8"))
    listings = committed["codeListings"]
    expected = {
        "sid": ("file", 1, 308, 40, 40, 308),
        "sid_compute_path_matrix": ("function", 10, 26, 26, 17, 17),
        "sid_reachable_on_non_directed_path": (
            "function", 29, 180, 68, 40, 152),
        "sid_sid": ("class", 256, 308, 295, 40, 53),
        "sid_sid_evaluate": ("method", 300, 308, 308, 9, 9),
        "sid_sid_matrix": ("function", 183, 253, 222, 40, 71),
    }

    assert set(listings) == set(expected)
    for listing_id, (kind, start, end, preview_end,
                     preview_lines, full_lines) in expected.items():
        listing = listings[listing_id]
        assert listing["symbolKind"] == kind, listing_id
        assert (listing["startLine"], listing["endLine"]) == (start, end), listing_id
        assert listing["rangeResolved"] is True, listing_id
        assert listing["previewEndLine"] == preview_end, listing_id
        assert len(listing["preview"].splitlines()) == preview_lines, listing_id
        assert len(listing["full"].splitlines()) == full_lines, listing_id
        assert full_lines == end - start + 1, listing_id
        assert preview_lines == preview_end - start + 1, listing_id

    reachable = listings["sid_reachable_on_non_directed_path"]
    assert reachable["full"].splitlines()[-1].strip() == (
        "return reachable_on_non_directed_path[:n_nodes] | "
        "reachable_on_non_directed_path[n_nodes:]"
    )

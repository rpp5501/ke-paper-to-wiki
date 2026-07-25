"""R16.C2 — provenance chips: sourceRef validated against emitted sections.

Every quiz item and every visual should be traceable to a paper span. A ref
that does not resolve is dropped with a warning rather than shipped as a chip
that goes nowhere — the build never breaks on provenance content.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))

PACK = {"sections": [{"id": "sec_3_2", "title": "SDPA", "level": 2,
                      "text": "t"}],
        "extraction": {}, "equations": []}


def _quiz_file(tmp_path, source_ref):
    path = tmp_path / "quiz.json"
    item = {"id": "q1", "nodeId": "attention", "prompt": "p", "correct": 0,
            "options": [{"text": "a", "explain": "e"},
                        {"text": "b", "explain": "e"}]}
    if source_ref is not None:
        item["source_ref"] = source_ref
    path.write_text(json.dumps({"items": [item]}), encoding="utf-8")
    return str(path)


def test_quiz_keeps_a_ref_that_resolves(tmp_path):
    bundle = build_bundle(FIXTURE, pack=PACK,
                          quiz=_quiz_file(tmp_path, "sec:3.2"))
    assert bundle["quiz"][0]["sectionRef"] == "sec:3.2"


def test_quiz_drops_an_unresolvable_ref_but_keeps_the_item(tmp_path, capsys):
    bundle = build_bundle(FIXTURE, pack=PACK,
                          quiz=_quiz_file(tmp_path, "sec:9.9"))

    assert len(bundle["quiz"]) == 1, "the item survives; only its ref is bad"
    assert bundle["quiz"][0]["sectionRef"] == ""
    assert "9.9" in capsys.readouterr().out


def test_quiz_ref_survives_when_the_build_has_no_sections(tmp_path):
    # Without --pack there is nothing to validate against; refs pass through
    # untouched rather than every item warning.
    bundle = build_bundle(FIXTURE, quiz=_quiz_file(tmp_path, "sec:3.2"))
    assert bundle["quiz"][0]["sectionRef"] == "sec:3.2"


def test_quiz_without_a_ref_is_unaffected(tmp_path):
    bundle = build_bundle(FIXTURE, pack=PACK,
                          quiz=_quiz_file(tmp_path, None))
    assert bundle["quiz"][0]["sectionRef"] == ""


def test_r15_page_anchor_is_a_different_field_and_survives(tmp_path, capsys):
    """R15.2's `sourceRef` is an in-page anchor like '#the-math', not a paper
    section. C2 must not validate it away — the shipped quiz fixture uses it."""
    path = tmp_path / "quiz.json"
    path.write_text(json.dumps({"items": [
        {"id": "q1", "nodeId": "attention", "prompt": "p", "correct": 0,
         "sourceRef": "#the-math",
         "options": [{"text": "a", "explain": "e"},
                     {"text": "b", "explain": "e"}]},
    ]}), encoding="utf-8")

    item = build_bundle(FIXTURE, pack=PACK, quiz=str(path))["quiz"][0]

    assert item["sourceRef"] == "#the-math"
    assert item["sectionRef"] == ""
    assert "the-math" not in capsys.readouterr().out


def _viz_dir(tmp_path, source_ref):
    viz = tmp_path / "viz"
    viz.mkdir()
    (viz / "a.html").write_text("<html>v</html>", encoding="utf-8")
    entry = {"src": "a.html", "title": "T", "caption": "c", "prompt": "p"}
    if source_ref is not None:
        entry["source_ref"] = source_ref
    (viz / "manifest.json").write_text(
        json.dumps({"attention": entry}), encoding="utf-8")
    return str(viz)


def test_viz_carries_a_ref_that_resolves(tmp_path):
    bundle = build_bundle(FIXTURE, pack=PACK,
                          viz_dir=_viz_dir(tmp_path, "sec:3.2"))
    assert bundle["viz"]["attention"]["sectionRef"] == "sec:3.2"


def test_viz_drops_an_unresolvable_ref_but_keeps_the_visual(tmp_path, capsys):
    bundle = build_bundle(FIXTURE, pack=PACK,
                          viz_dir=_viz_dir(tmp_path, "sec:9.9"))

    assert "attention" in bundle["viz"], "the visual survives; only its ref is bad"
    assert bundle["viz"]["attention"]["sectionRef"] == ""
    assert "9.9" in capsys.readouterr().out


def test_viz_without_a_ref_is_unaffected(tmp_path):
    bundle = build_bundle(FIXTURE, pack=PACK, viz_dir=_viz_dir(tmp_path, None))
    assert bundle["viz"]["attention"]["sectionRef"] == ""

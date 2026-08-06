"""R15.2 — build_data --quiz emission/validation + --update patch mode."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle, main, parse_data_ts, to_data_ts

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
QUIZ_JSON = ROOT / "fixtures" / "quiz" / "quiz.json"
IDEAS_YAML = ROOT / "fixtures" / "next_steps" / "ideas.yaml"


def test_no_flag_leaves_bundle_untouched():
    bundle = build_bundle(FIXTURE)
    assert "quiz" not in bundle
    assert "checkpoints" not in bundle
    assert '"quiz"' not in to_data_ts(bundle)


def test_quiz_emits_valid_items():
    bundle = build_bundle(FIXTURE, quiz=str(QUIZ_JSON))
    items = bundle["checkpoints"]
    assert bundle["quiz"] == items  # legacy alias for one compatibility cycle
    assert len(items) == 4
    first = items[0]
    assert first["id"] == "sdpa-why-sqrt-dk"
    assert first["nodeId"] == "scaled-dot-product-attention"
    assert 0 <= first["correct"] < len(first["options"])
    assert all(o["text"] and o["explain"] for o in first["options"])


def test_quiz_emits_inline_checkpoint_metadata(tmp_path):
    path = tmp_path / "quiz.json"
    path.write_text(json.dumps({"items": [{
        "id": "apply-a", "nodeId": "attention", "chapterId": "why",
        "kind": "application", "placement": "chapter-end",
        "prompt": "Apply it", "correct": 0, "sourceRef": "#mechanics",
        "options": [
            {"text": "A", "explain": "Grounded explanation"},
            {"text": "B", "explain": "Why this is wrong"},
        ],
    }]}), encoding="utf-8")

    item = build_bundle(FIXTURE, quiz=path)["quiz"][0]

    assert item["chapterId"] == "why"
    assert item["kind"] == "application"
    assert item["placement"] == "chapter-end"


def _reviewed_chapter(checkpoint_ids):
    return {
        "version": 1,
        "reviewed": True,
        "chapters": [{
            "id": "why", "title": "Why", "question": "Why?",
            "outcome": "Apply it.", "conceptIds": ["attention"],
            "foundationConceptIds": [], "advancedConceptIds": [],
            "checkpointIds": checkpoint_ids,
            "estimatedCoreMinutes": 1, "estimatedFullMinutes": 1,
        }],
    }


def _checkpoint_quiz(tmp_path, **changes):
    item = {
        "id": "apply-attention", "nodeId": "attention", "chapterId": "why",
        "kind": "application", "placement": "chapter-end",
        "prompt": "Apply it", "correct": 0,
        "options": [
            {"text": "A", "explain": "Grounded explanation"},
            {"text": "B", "explain": "Why this is wrong"},
        ],
    }
    item.update(changes)
    path = tmp_path / "quiz.json"
    path.write_text(json.dumps({"items": [item]}), encoding="utf-8")
    return path


def test_reviewed_checkpoint_requires_a_loaded_matching_application_item(tmp_path):
    quiz = _checkpoint_quiz(tmp_path)

    bundle = build_bundle(
        FIXTURE, quiz=quiz,
        learning_path=_reviewed_chapter(["apply-attention"]),
    )

    assert bundle["learningPath"]["chapters"][0]["checkpointIds"] == ["apply-attention"]


def test_reviewed_learning_path_rejects_duplicate_chapter_ids():
    learning = _reviewed_chapter([])
    learning["chapters"].append({
        **learning["chapters"][0],
        "conceptIds": ["scaled-dot-product-attention"],
    })

    with pytest.raises(ValueError, match="duplicate learning chapter id 'why'"):
        build_bundle(FIXTURE, learning_path=learning)


def test_reviewed_learning_path_rejects_duplicate_checkpoint_claims(tmp_path):
    quiz = _checkpoint_quiz(tmp_path)
    learning = _reviewed_chapter(["apply-attention"])
    learning["chapters"].append({
        **learning["chapters"][0],
        "id": "mechanics",
        "conceptIds": ["scaled-dot-product-attention"],
    })

    with pytest.raises(ValueError, match="duplicate checkpoint id 'apply-attention'"):
        build_bundle(FIXTURE, quiz=quiz, learning_path=learning)


def test_reviewed_chapter_must_list_each_quiz_item_that_names_it(tmp_path):
    quiz = _checkpoint_quiz(tmp_path)

    with pytest.raises(ValueError, match="quiz item 'apply-attention'.*not listed"):
        build_bundle(
            FIXTURE, quiz=quiz, learning_path=_reviewed_chapter([]),
        )


@pytest.mark.parametrize(("changes", "message"), [
    ({"id": "different-id"}, "missing loaded quiz item 'apply-attention'"),
    ({"chapterId": "elsewhere"}, "belongs to chapter 'elsewhere'"),
    ({"nodeId": "scaled-dot-product-attention"}, "is not a member"),
    ({"kind": "recall"}, "invalid kind 'recall'"),
    ({"placement": "between-chapters"}, "invalid placement 'between-chapters'"),
])
def test_reviewed_checkpoint_rejects_unshippable_quiz_contracts(
        tmp_path, changes, message):
    quiz = _checkpoint_quiz(tmp_path, **changes)

    with pytest.raises(ValueError, match=message):
        build_bundle(
            FIXTURE, quiz=quiz,
            learning_path=_reviewed_chapter(["apply-attention"]),
        )


def test_invalid_items_dropped(tmp_path):
    bad = tmp_path / "quiz.json"
    bad.write_text(json.dumps({"items": [
        {"id": "ok", "nodeId": "attention", "prompt": "p", "correct": 0,
         "options": [{"text": "a", "explain": "e"},
                     {"text": "b", "explain": "e"}]},
        {"id": "ghost-node", "nodeId": "nope", "prompt": "p", "correct": 0,
         "options": [{"text": "a", "explain": "e"},
                     {"text": "b", "explain": "e"}]},
        {"id": "bad-correct", "nodeId": "attention", "prompt": "p",
         "correct": 9,
         "options": [{"text": "a", "explain": "e"},
                     {"text": "b", "explain": "e"}]},
        {"id": "no-explain", "nodeId": "attention", "prompt": "p",
         "correct": 0,
         "options": [{"text": "a"}, {"text": "b", "explain": "e"}]},
    ]}), encoding="utf-8")
    items = build_bundle(FIXTURE, quiz=str(bad))["quiz"]
    assert [i["id"] for i in items] == ["ok"]


def test_parse_data_ts_roundtrip():
    bundle = build_bundle(FIXTURE)
    assert parse_data_ts(to_data_ts(bundle)) == bundle


def test_update_patches_existing_build(tmp_path):
    out = tmp_path / "data.gen.ts"
    graph = tmp_path / "graph.json"
    graph.write_text(json.dumps(FIXTURE), encoding="utf-8")
    # full build without any opt-in sections
    assert main(["--graph", str(graph), "--out", str(out)]) == 0
    before = parse_data_ts(out.read_text(encoding="utf-8"))
    assert "quiz" not in before and "nextSteps" not in before
    # patch quiz + next-steps in afterwards — no --graph needed
    assert main(["--update", "--quiz", str(QUIZ_JSON),
                 "--next-steps", str(IDEAS_YAML), "--out", str(out)]) == 0
    after = parse_data_ts(out.read_text(encoding="utf-8"))
    assert len(after["quiz"]) == 4
    assert after["checkpoints"] == after["quiz"]
    assert len(after["nextSteps"]) == 3
    # untouched sections identical
    for key in before:
        assert after[key] == before[key]


def test_update_requires_a_section(tmp_path):
    out = tmp_path / "data.gen.ts"
    out.write_text(to_data_ts(build_bundle(FIXTURE)), encoding="utf-8")
    try:
        main(["--update", "--out", str(out)])
    except SystemExit as e:
        assert e.code == 2
    else:
        raise AssertionError("expected argparse error")


def test_checkpoint_density_is_reported_and_gates_release():
    """9 items across 20k words, 5 of them in one chapter, used to ship with
    releasePass=true. Density now has to answer for itself."""
    from build_data import _checkpoint_density

    pages = {"a": " ".join(["word"] * 4000)}
    learning = {"chapters": [{"id": "one"}, {"id": "two"}]}
    thin = [{"id": "q1", "chapterId": "one"}, {"id": "q2", "chapterId": "one"}]

    report = _checkpoint_density(pages, thin, learning)
    assert report["expectedItems"] == 5          # 4000 words / 800
    assert report["items"] == 2
    assert report["thinChapterIds"] == ["two"]   # chapter with no checkpoint
    assert report["pass"] is False


def test_checkpoint_density_passes_when_spaced():
    from build_data import _checkpoint_density

    pages = {"a": " ".join(["word"] * 1600)}     # expects 2
    learning = {"chapters": [{"id": "one"}, {"id": "two"}]}
    spaced = [
        {"id": "q1", "chapterId": "one"}, {"id": "q2", "chapterId": "one"},
        {"id": "q3", "chapterId": "two"}, {"id": "q4", "chapterId": "two"},
    ]

    report = _checkpoint_density(pages, spaced, learning)
    assert report["thinChapterIds"] == []
    assert report["pass"] is True


def test_absent_quiz_does_not_fail_release():
    """--quiz is opt-in; a bundle built without it must not be gated on a
    density it was never asked to have."""
    from build_data import _content_quality_report

    report = _content_quality_report({"a": "short prose"}, checkpoints=None)
    assert report["checkpointDensity"] == {}
    assert report["releasePass"] is True

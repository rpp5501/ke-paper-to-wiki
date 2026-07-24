"""R15.2 — build_data --quiz emission/validation + --update patch mode."""
import json
import sys
from pathlib import Path

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
    assert '"quiz"' not in to_data_ts(bundle)


def test_quiz_emits_valid_items():
    items = build_bundle(FIXTURE, quiz=str(QUIZ_JSON))["quiz"]
    assert len(items) == 4
    first = items[0]
    assert first["id"] == "sdpa-why-sqrt-dk"
    assert first["nodeId"] == "scaled-dot-product-attention"
    assert 0 <= first["correct"] < len(first["options"])
    assert all(o["text"] and o["explain"] for o in first["options"])


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

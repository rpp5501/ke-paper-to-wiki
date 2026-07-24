"""R15.1 — build_data --next-steps: opt-in emission, anchor validation."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import build_bundle, to_data_ts

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads(
    (ROOT / "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
IDEAS_YAML = ROOT / "fixtures" / "next_steps" / "ideas.yaml"


def test_no_flag_leaves_bundle_untouched():
    bundle = build_bundle(FIXTURE)
    assert "nextSteps" not in bundle
    assert '"nextSteps"' not in to_data_ts(bundle)


def test_flag_emits_sorted_steps():
    bundle = build_bundle(FIXTURE, next_steps=str(IDEAS_YAML))
    steps = bundle["nextSteps"]
    assert len(steps) == 3
    assert steps[0]["confirmed"] is True  # confirmed first
    first = steps[0]
    assert first["title"]
    assert first["rationale"]
    assert first["kind"] == "paper-limitation"
    assert "scaled-dot-product-attention" in first["nodes"]
    assert first["sources"] == ["§sec:3.2"]


def test_unknown_anchor_nodes_dropped(tmp_path):
    ideas = tmp_path / "ideas.json"
    ideas.write_text(json.dumps({"ideas": [
        {"title": "mixed anchors", "rationale": "r", "kind": "k",
         "anchors": {"nodes": ["attention", "made-up-node"], "sources": []},
         "confirmed": False},
        {"title": "all unknown", "rationale": "r", "kind": "k",
         "anchors": {"nodes": ["ghost"], "sources": []}, "confirmed": True},
    ]}), encoding="utf-8")
    steps = build_bundle(FIXTURE, next_steps=str(ideas))["nextSteps"]
    assert len(steps) == 1
    assert steps[0]["nodes"] == ["attention"]  # ghost idea skipped entirely

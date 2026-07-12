from paper_skill.bridge import (propose_candidates, verify_candidates,
                                write_candidates_yaml, load_confirmed, merge_bridge)
import pytest
import yaml

# fixtures repeated verbatim (tasks may execute out of order — no cross-test imports)
CONCEPTS = {"nodes": [
    {"id": "multi-head-attention", "kind": "concept", "label": "Multi-Head Attention", "level": 2},
    {"id": "positional-encoding", "kind": "concept", "label": "Positional Encoding", "level": 2}],
    "edges": [], "meta": {}}
CODE = {"nodes": [
    {"id": "model.py::MultiHeadedAttention", "kind": "function",
     "label": "MultiHeadedAttention", "source_ref": "model.py:L120"},
    {"id": "model.py::subsequent_mask", "kind": "function",
     "label": "subsequent_mask", "source_ref": "model.py:L40"}],
    "edges": [], "meta": {}}


def test_verify_attaches_verdicts():
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE,
                          spawn=lambda p: "YES: class implements the mechanism")
    assert v[0]["verdict"] == "yes" and "implements" in v[0]["reason"]


def test_garbled_verdict_defaults_no():
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: "maybe??")
    assert all(row["verdict"] == "no" for row in v)


@pytest.mark.parametrize("raw", (
    "YESNO: malformed",
    "NOPE: malformed",
    "YES: ok\nextra",
    "YES",
))
def test_malformed_verdicts_are_not_parsed_as_affirmative(raw):
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: raw)
    assert all(row["verdict"] == "no" and
               row["reason"].startswith("unparseable verdict:") for row in v)


def test_string_confirmed_does_not_confirm(tmp_path):
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: "YES: ok")
    path = tmp_path / "bridge_candidates.yaml"
    write_candidates_yaml(v, path)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))

    doc["candidates"][0]["confirmed"] = "false"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    assert load_confirmed(path) == []


def test_string_include_unconfirmed_does_not_opt_in(tmp_path):
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: "YES: ok")
    path = tmp_path / "bridge_candidates.yaml"
    write_candidates_yaml(v, path)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    doc["candidates"][0]["confirmed"] = False
    doc["include_unconfirmed"] = "false"
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    assert load_confirmed(path) == []


def test_unconfirmed_yes_requires_literal_opt_in(tmp_path):
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: "YES: ok")
    path = tmp_path / "bridge_candidates.yaml"
    write_candidates_yaml(v, path)
    assert load_confirmed(path) == []

    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    doc["include_unconfirmed"] = True
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    selected = load_confirmed(path)
    assert len(selected) == 1
    merged = merge_bridge(CONCEPTS, CODE, selected)
    imp = [e for e in merged["edges"] if e["kind"] == "implements"]
    assert imp[0]["confidence"] == "inferred"
    assert imp[0]["confidence_score"] == 0.6


def test_confirm_roundtrip_and_merge(tmp_path):
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: "YES: ok")
    path = tmp_path / "bridge_candidates.yaml"
    write_candidates_yaml(v, path)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["include_unconfirmed"] is False
    doc["candidates"][0]["confirmed"] = True
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    confirmed = load_confirmed(path)
    assert len(confirmed) == 1
    merged = merge_bridge(CONCEPTS, CODE, confirmed)
    imp = [e for e in merged["edges"] if e["kind"] == "implements"]
    assert imp[0]["src"] == "model.py::MultiHeadedAttention"
    assert imp[0]["dst"] == "multi-head-attention"
    assert imp[0]["confidence"] == "extracted"
    assert imp[0]["confidence_score"] == 1.0
    assert merged["meta"]["kind"] == "bridged"

from paper_skill.bridge import (propose_candidates, verify_candidates,
                                write_candidates_yaml, load_confirmed, merge_bridge)
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
    assert merged["meta"]["kind"] == "bridged"

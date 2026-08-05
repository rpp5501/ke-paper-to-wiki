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
    "yes: lowercase",
    "Yes: mixed case",
    "no: lowercase",
    "No: mixed case",
))
def test_verdict_grammar_is_case_sensitive(raw):
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: raw)
    assert all(row["verdict"] == "no" and
               row["reason"].startswith("unparseable verdict:") for row in v)


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


def test_verifier_spawn_exception_fails_candidate_closed():
    cands = propose_candidates(CONCEPTS, CODE)

    def unavailable(_prompt):
        raise RuntimeError("worker unavailable")

    verified = verify_candidates(cands, CONCEPTS, CODE, spawn=unavailable)
    assert all(row["verdict"] == "no" for row in verified)
    assert all(row["reason"] == "verifier error: RuntimeError" for row in verified)
    assert not any(row.get("confirmed") is True for row in verified)


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


def test_merge_rejects_cross_graph_node_id_collision():
    code = {**CODE, "nodes": [
        {**CODE["nodes"][0], "id": CONCEPTS["nodes"][0]["id"]},
    ]}
    with pytest.raises(ValueError, match="node id collision across graphs: multi-head-attention"):
        merge_bridge(CONCEPTS, code, [])


@pytest.mark.parametrize(("candidate", "message"), (
    ({"concept": "multi-head-attention", "code": "missing-code"},
     "unknown code candidate endpoint: missing-code"),
    ({"concept": "missing-concept", "code": "model.py::MultiHeadedAttention"},
     "unknown concept candidate endpoint: missing-concept"),
))
def test_merge_rejects_unknown_candidate_endpoints(candidate, message):
    with pytest.raises(ValueError, match=message):
        merge_bridge(CONCEPTS, CODE, [candidate])


def test_merge_deduplicates_implements_pair_and_human_confirmation_wins():
    pair = {"concept": "multi-head-attention",
            "code": "model.py::MultiHeadedAttention", "verdict": "yes"}
    merged = merge_bridge(CONCEPTS, CODE, [pair, {**pair, "confirmed": True}])
    implements = [edge for edge in merged["edges"]
                  if edge["kind"] == "implements"]
    assert implements == [{
        "src": "model.py::MultiHeadedAttention",
        "dst": "multi-head-attention",
        "kind": "implements",
        "weight": 1.0,
        "confidence": "extracted",
        "confidence_score": 1.0,
    }]


# The prompt named a file and did not show it. `claude -p` has file tools, so
# it read that as an instruction to go and open sid.py -- from paper-skill's
# cwd, where a path recorded against another repo does not resolve. Every
# parseable verdict in the real run was a variation on "No file named `sid.py`
# exists anywhere in this repository", which is not an answer to the question
# asked. The verifier must judge from evidence carried in the prompt.
def test_prompt_carries_the_source_not_just_its_path(tmp_path):
    (tmp_path / "model.py").write_text(
        "\n" * 119 + "class MultiHeadedAttention:\n    'parallel heads'\n",
        encoding="utf-8")
    seen = []

    verify_candidates(
        [{"concept": "multi-head-attention",
          "code": "model.py::MultiHeadedAttention", "score": 1.0,
          "evidence": "x"}],
        CONCEPTS, CODE, spawn=lambda p: (seen.append(p), "YES: yes")[1],
        repo_dir=tmp_path)

    assert "class MultiHeadedAttention" in seen[0]


def test_prompt_tells_the_verifier_not_to_go_looking():
    seen = []

    verify_candidates(
        [{"concept": "multi-head-attention",
          "code": "model.py::MultiHeadedAttention", "score": 1.0,
          "evidence": "x"}],
        CONCEPTS, CODE, spawn=lambda p: (seen.append(p), "YES: yes")[1])

    assert "do not open" in seen[0].lower() or "do not read" in seen[0].lower()


def test_unreadable_source_still_gets_a_verdict(tmp_path):
    """A stale path must not turn into a filesystem question."""
    out = verify_candidates(
        [{"concept": "multi-head-attention",
          "code": "model.py::MultiHeadedAttention", "score": 1.0,
          "evidence": "x"}],
        CONCEPTS, CODE, spawn=lambda p: "NO: unrelated", repo_dir=tmp_path)

    assert out[0]["verdict"] == "no"

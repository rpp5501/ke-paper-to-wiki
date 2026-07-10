import json
from paper_skill.concepts import extract_concepts, CONCEPT_PROMPT

PACK = {"meta": {"source": "arXiv:1706.03762", "title": "Attention Is All You Need",
                 "generated": "2026-07-09"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_1", "title": "Introduction", "level": 1,
                      "text": "We propose the Transformer."}],
        "equations": [], "references": [], "figures": []}

GOOD = json.dumps({
    "nodes": [{"id": "transformer", "kind": "concept", "label": "The Transformer",
               "level": 0, "source_ref": "sec_1",
               "definition": "Sequence model built on attention.",
               "sub_questions": ["What replaces recurrence?"], "research": True}],
    "edges": []})


def test_good_spawn_yields_graph_and_toc():
    r = extract_concepts(PACK, spawn=lambda p: GOOD)
    assert r["status"] == "ok"
    assert r["graph"]["meta"]["kind"] == "concept"
    assert r["graph"]["nodes"][0]["id"] == "transformer"
    assert r["toc"][0]["research"] is True
    assert r["toc"][0]["sub_questions"] == ["What replaces recurrence?"]


def test_invalid_json_retries_once_then_stub():
    calls = []
    def bad(prompt):
        calls.append(prompt)
        return "sorry, here's some prose"
    r = extract_concepts(PACK, spawn=bad)
    assert r["status"] == "failed-orchestration"
    assert len(calls) == 2                       # one retry, then stop


SCHEMA_INVALID = json.dumps({
    "nodes": [{"id": "transformer", "kind": "concept", "label": "The Transformer",
               "level": 0, "source_ref": "sec_1"},
              {"id": "attention", "kind": "concept", "label": "Attention Mechanism",
               "level": 0, "source_ref": "sec_1"}],
    "edges": []})


def test_valid_json_but_schema_invalid_retries_then_fails():
    calls = []
    def spawn(prompt):
        calls.append(prompt)
        return SCHEMA_INVALID
    r = extract_concepts(PACK, spawn=spawn)
    assert r["status"] == "failed-orchestration"
    assert len(calls) == 2                       # one retry, then stop
    assert r["problems"]
    assert any("level-0" in p for p in r["problems"])


def test_prompt_carries_sections_and_json_contract():
    assert "{sections_digest}" in CONCEPT_PROMPT and "JSON" in CONCEPT_PROMPT

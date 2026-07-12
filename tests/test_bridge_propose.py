from paper_skill.bridge import propose_candidates, _tokens

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


def test_identifier_splitting():
    assert _tokens("MultiHeadedAttention") == {"multi", "headed", "attention"}
    assert _tokens("subsequent_mask") == {"subsequent", "mask"}


def test_mha_pairs_with_its_class():
    cands = propose_candidates(CONCEPTS, CODE)
    top = cands[0]
    assert top["concept"] == "multi-head-attention"
    assert top["code"] == "model.py::MultiHeadedAttention"
    assert top["score"] > 0.4


def test_no_pair_for_unrelated():
    cands = propose_candidates(CONCEPTS, CODE)
    assert not any(c["code"].endswith("subsequent_mask")
                   and c["concept"] == "positional-encoding" for c in cands)

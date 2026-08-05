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


def test_tie_order_is_independent_of_input_node_order():
    concepts = {"nodes": [
        {"id": "concept-z", "kind": "concept", "label": "Shared"},
        {"id": "concept-a", "kind": "concept", "label": "Shared"},
    ], "edges": [], "meta": {}}
    code = {"nodes": [
        {"id": "code-z", "kind": "function", "label": "Shared"},
        {"id": "code-a", "kind": "function", "label": "Shared"},
    ], "edges": [], "meta": {}}

    pairs = [(row["concept"], row["code"])
             for row in propose_candidates(concepts, code)]
    assert pairs == [
        ("concept-a", "code-a"),
        ("concept-a", "code-z"),
        ("concept-z", "code-a"),
        ("concept-z", "code-z"),
    ]
def test_structural_bonus_uses_filename_only():
    concepts = {"nodes": [{
        "id": "attention-route",
        "kind": "concept",
        "label": "Attention Query Key Value Output",
    }], "edges": [], "meta": {}}
    code = {"nodes": [{
        "id": "attention-code",
        "kind": "function",
        "label": "Attention",
        "source_ref": "attention_helpers/model.py:L10",
    }], "edges": [], "meta": {}}

    assert propose_candidates(concepts, code) == []

    code["nodes"][0]["source_ref"] = "helpers/attention.py:L10"
    assert propose_candidates(concepts, code)[0]["score"] == 0.4


# Concept labels are prose ("Equivalent Graphical Formulation"); code labels are
# identifiers (_compute_path_matrix). Jaccard over the two is near zero unless
# the names happen to coincide, so on pgmpy's sid.py every one of 30 candidates
# matched the single token "sid" while the two functions that actually
# implement the algorithms drew none. The paper's own one-line definition is the
# text that bridges the vocabularies, and P2 already wrote it -- into the TOC
# rows, not the graph nodes, which is why nothing downstream had it.
DEFS = {"multi-head-attention":
        "Runs several attention heads in parallel and concatenates them.",
        "positional-encoding":
        "Injects order information using sinusoids of varying frequency."}


def test_definition_text_widens_recall():
    code = {"nodes": [{"id": "m.py::parallel_heads", "kind": "function",
                       "label": "parallel_heads", "source_ref": "m.py:L1"}],
            "edges": [], "meta": {}}

    without = propose_candidates(CONCEPTS, code)
    with_defs = propose_candidates(CONCEPTS, code, definitions=DEFS)

    assert not any(c["code"] == "m.py::parallel_heads" for c in without)
    assert any(c["code"] == "m.py::parallel_heads" for c in with_defs)


def test_label_matches_still_outrank_definition_matches():
    """A name that matches is stronger evidence than a word in a sentence."""
    cands = propose_candidates(CONCEPTS, CODE, definitions=DEFS)

    assert cands[0]["concept"] == "multi-head-attention"
    assert cands[0]["code"] == "model.py::MultiHeadedAttention"


def test_definitions_are_optional():
    assert propose_candidates(CONCEPTS, CODE) == propose_candidates(
        CONCEPTS, CODE, definitions=None)


def test_function_words_are_not_evidence():
    """"on" matched _reachable_on_non_directed_path to an unrelated concept.
    A shared preposition is not evidence that code implements a concept."""
    assert _tokens("reachable on the non directed path") == {
        "reachable", "non", "directed", "path"}


def test_one_loud_concept_cannot_crowd_out_coverage():
    """The global cap sorts by score, so a handful of high-scoring pairs
    sharing one token ("sid") filled all 30 slots and three of six code
    entities drew no candidate at all. Capping per concept keeps breadth."""
    concepts = {"nodes": [
        {"id": f"sid-{i}", "kind": "concept", "label": f"SID Aspect {i}",
         "level": 1} for i in range(8)], "edges": [], "meta": {}}
    code = {"nodes": [
        {"id": "sid.py::SID", "kind": "function", "label": "SID",
         "source_ref": "sid.py:L1"},
        {"id": "sid.py::sid_matrix", "kind": "function", "label": "sid_matrix",
         "source_ref": "sid.py:L2"},
        {"id": "sid.py::sid_helper", "kind": "function", "label": "sid_helper",
         "source_ref": "sid.py:L3"}], "edges": [], "meta": {}}

    cands = propose_candidates(concepts, code, top=6)

    assert len({c["code"] for c in cands}) == 3

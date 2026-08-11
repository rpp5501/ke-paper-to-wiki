"""P3 asks the model to recall resources. Search hands it real ones instead."""
from paper_skill.candidates import (candidate_block, find_candidates, paper_topic,
                                 relevant, research_query)

BRIEF = {"concept": "ba-mitigation-algorithm",
         "definition": "Removing a planted backdoor from a trained classifier",
         "sub_questions": ["how is the trigger estimated?"]}


def test_query_uses_the_concept_and_its_definition():
    query = research_query(BRIEF)

    assert "ba mitigation algorithm" in query
    assert "planted backdoor" in query


RECORDS = [
    {"title": "Neural Cleanse: Identifying and Mitigating Backdoor Attacks",
     "url": "https://arxiv.org/abs/1902.06531x", "year": "2019", "citations": 900},
    {"title": "STRIP: A Defence Against Trojan Attacks",
     "url": "https://arxiv.org/abs/1902.06531", "year": "2019", "citations": 400},
]


def test_candidates_carry_the_title_and_url_together():
    """The pairing is the whole point: recall got the title and the id from
    different papers, and nothing downstream noticed."""
    block = candidate_block(RECORDS)

    assert "Neural Cleanse: Identifying and Mitigating Backdoor Attacks" in block
    assert "https://arxiv.org/abs/1902.06531x" in block
    assert "STRIP: A Defence Against Trojan Attacks" in block


def test_no_results_render_as_nothing():
    """An empty heading would read as "search ran and found nothing worth
    citing", which is a different claim from "search did not run"."""
    assert candidate_block([]) == ""


def test_search_is_asked_for_the_briefs_query():
    seen = {}

    def search(query, limit=5, **_kw):
        seen["query"] = query
        return {"status": "ok", "results": RECORDS}

    find_candidates(BRIEF, search=search)

    assert "ba mitigation algorithm" in seen["query"]
    assert "planted backdoor" in seen["query"]


def test_a_search_that_raises_does_not_break_the_run():
    """Search is an opportunistic improvement. If the providers are down the
    note should still be written -- verify_resources remains the backstop."""
    def search(*_a, **_kw):
        raise ConnectionError("all four providers down")

    assert find_candidates(BRIEF, search=search) == []


def test_disabled_apis_yield_no_candidates():
    def search(*_a, **_kw):
        return {"status": "apis_disabled", "records": [], "hint": "off"}

    assert find_candidates(BRIEF, search=search) == []


# A concept slug carries paper-internal shorthand ("nc", "tabor", "ba") and no
# field. Searched bare, "lagrangian optimization" returns pure optimization
# theory and "baseline detectors nc tabor" returned 1950s biochemistry. The
# paper's own top-level concepts are its subject vocabulary.
BACKDOOR_GRAPH = {"nodes": [
    {"id": "ba", "label": "Backdoor Attack (BA)", "level": 1},
    {"id": "bd", "label": "Backdoor Defense", "level": 1},
    {"id": "ptd", "label": "Post-Training Detection Scenario", "level": 1},
    {"id": "mm", "label": "Maximum Margin (MM) Statistic", "level": 1},
    {"id": "deep", "label": "Backdoor pattern estimation", "level": 2},
], "edges": []}


def test_topic_is_the_word_recurring_across_top_level_concepts():
    topic = paper_topic(BACKDOOR_GRAPH)

    assert "backdoor" in topic
    # Level 2 is a leaf, not the paper's subject.
    assert "estimation" not in topic


def test_a_graph_with_no_repeated_theme_yields_no_topic():
    """Inventing a topic from one-off labels would poison every query."""
    graph = {"nodes": [{"id": "a", "label": "Alpha", "level": 1},
                       {"id": "b", "label": "Beta", "level": 1}], "edges": []}

    assert paper_topic(graph) == ""


def test_query_carries_the_paper_topic():
    query = research_query(BRIEF, topic="backdoor detection")

    assert "backdoor detection" in query
    assert "ba mitigation algorithm" in query


# Every title below came back from a live search for a backdoor-detection
# concept, ranked above the relevant work because academic_search sorts by raw
# citation count across every field Crossref and OpenAlex index.
BACKDOOR_QUERY = ("backdoor detection baseline detectors nc tabor "
                  "post-training backdoor detection methods neural cleanse")
NOISE = [
    {"title": "[54] Amine oxidases", "url": "https://doi.org/x1", "citations": 35},
    {"title": "[44] Putrescine aminopropyltransferase (Escherichia coli)",
     "url": "https://doi.org/x2", "citations": 5},
    {"title": "Table 2: Performance comparison of MDDeep-Ace with baseline methods",
     "url": "https://doi.org/x3", "citations": 0},
    {"title": "Figure 4: Detail for the find-the-performance step",
     "url": "https://doi.org/x4", "citations": 0},
]
SIGNAL = [
    {"title": "Neural Cleanse: Identifying and Mitigating Backdoor Attacks in "
              "Neural Networks", "url": "https://doi.org/nc", "citations": 900},
    {"title": "Defending Graph Neural Networks Against Backdoor Attacks",
     "url": "https://doi.org/gnn", "citations": 2},
]


def test_off_field_results_are_dropped():
    kept = [r["title"] for r in relevant(NOISE + SIGNAL, BACKDOOR_QUERY)]

    assert "Amine oxidases" not in " ".join(kept)
    assert "Putrescine" not in " ".join(kept)


def test_the_relevant_papers_survive():
    kept = [r["url"] for r in relevant(NOISE + SIGNAL, BACKDOOR_QUERY)]

    assert kept == ["https://doi.org/nc", "https://doi.org/gnn"]


def test_table_and_figure_dois_are_not_papers():
    """Crossref indexes a paper's tables and figures under their own DOIs.
    "Table 2: Performance comparison ... baseline methods" overlaps the query
    on wording alone, so the word filter cannot be what excludes it."""
    kept = [r["title"] for r in relevant(NOISE, BACKDOOR_QUERY)]

    assert not any(t.startswith(("Table", "Figure")) for t in kept)


def test_find_candidates_filters_what_search_returns():
    """The filter has to be inside find_candidates, or every caller has to
    remember to apply it."""
    def search(_query, **_kw):
        return {"status": "ok", "results": NOISE + SIGNAL}

    kept = find_candidates({"concept": "baseline-detectors-nc-tabor",
                            "definition": "post-training backdoor detection "
                                          "methods including Neural Cleanse"},
                           search=search, topic="backdoor detection")

    assert [r["url"] for r in kept] == ["https://doi.org/nc", "https://doi.org/gnn"]


def test_find_candidates_searches_with_the_topic_included():
    seen = {}

    def search(query, **_kw):
        seen["query"] = query
        return {"status": "ok", "results": []}

    find_candidates(BRIEF, search=search, topic="backdoor detection")

    assert seen["query"].startswith("backdoor detection")


def test_word_forms_count_as_the_same_term():
    """"Mitigating" and "mitigation", "detectors" and "detection" are the same
    subject. Exact matching dropped Neural Cleanse from a query about
    mitigation, which is the paper the reader most needed."""
    kept = relevant(
        [{"title": "Neural Cleanse: Identifying and Mitigating Backdoor Attacks",
          "url": "https://doi.org/nc"}],
        "removing a planted backdoor mitigation of a trained classifier")

    assert len(kept) == 1


def test_a_query_too_thin_to_judge_does_not_silently_drop_everything():
    """A one-word concept ("elbo", no definition) cannot meet a two-term floor,
    so filtering it would return nothing however good the results were --
    search appearing to run and find nothing is the failure mode this whole
    session has been about. Hand the results on and let verify_resources and
    the model judge."""
    kept = relevant(SIGNAL, "elbo")

    assert kept == SIGNAL


def test_supplementary_material_records_are_not_papers():
    """IEEE registers a paper's multimedia supplement under the paper's own DOI
    with an /mmN suffix. The title is the paper's, so only the url gives it
    away -- it came back twice in one live run."""
    kept = relevant(
        [{"title": "Reverse Backdoor Distillation: Towards Online Backdoor "
                   "Attack Detection", "url": "https://doi.org/10.1109/tdsc.2024.3369751/mm1"},
         {"title": "Reverse Backdoor Distillation: Towards Online Backdoor "
                   "Attack Detection", "url": "https://doi.org/10.1109/tdsc.2024.3369751"}],
        "backdoor attack detection online distillation")

    assert [r["url"] for r in kept] == ["https://doi.org/10.1109/tdsc.2024.3369751"]

import pytest
import yaml
from paper_skill.p3_research import run_research
from paper_skill.toc import write_toc
from research_mcp.wiki import wiki_get

# These tests exercise orchestration, not verification. Without an injected
# verifier they reach the real network for every resource url in NOTE.
def _no_verify(_note):
    return []


def _no_search(_query, **_kw):
    """Without this the orchestration tests query four live providers."""
    return {"status": "insufficient-sources", "results": []}

GRAPH = {"nodes": [], "edges": []}
ROWS = [{"id": "c1", "label": "C1", "level": 1, "include": True, "research": True,
         "definition": "d", "sub_questions": ["q"]},
        {"id": "c2", "label": "C2", "level": 1, "include": True, "research": True,
         "definition": "d", "sub_questions": ["q"]}]

NOTE = """concept: {cid}
status: complete
synthesis: "Answer [S1]."
resources:
  - url: https://x.test/a
    title: A
    type: lecture
    why: clear
unresolved: []
sources_consulted: {{S1: https://x.test/a}}
"""


def _approved_toc(tmp_path):
    p = tmp_path / "toc.yaml"
    write_toc(ROWS, p)
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    doc["approved"] = True
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return p


def test_refuses_unapproved_toc(tmp_path):
    p = tmp_path / "toc.yaml"; write_toc(ROWS, p)
    r = run_research(p, GRAPH, spawn=lambda x: "", home=tmp_path, workdir=tmp_path,
                     verify=_no_verify, search=_no_search)
    assert r["status"] == "not_approved"


def test_runs_all_and_persists_notes(tmp_path):
    p = _approved_toc(tmp_path)
    def spawn(prompt):
        cid = "c1" if "c1" in prompt else "c2"
        return NOTE.format(cid=cid)
    r = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path,
                     verify=_no_verify, search=_no_search)
    assert r["done"] == ["c1", "c2"]
    assert wiki_get("c1", home=tmp_path)["status"] == "ok"


def test_resume_skips_done_concepts(tmp_path):
    p = _approved_toc(tmp_path)
    calls = []
    def spawn(prompt):
        cid = "c1" if "c1" in prompt else "c2"
        calls.append(cid)
        if cid == "c2" and len(calls) < 3:
            raise RuntimeError("killed mid-run")      # simulate session death
        return NOTE.format(cid=cid)
    r1 = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path,
                     verify=_no_verify, search=_no_search)
    assert r1["done"] == ["c1"] and r1["failed"] == ["c2"]
    r2 = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path,
                     verify=_no_verify, search=_no_search)
    assert r2["skipped"] == ["c1"] and r2["done"] == ["c2"]


def test_invalid_note_goes_to_inbox(tmp_path):
    from research_mcp.inbox import inbox_list
    p = _approved_toc(tmp_path)
    r = run_research(p, GRAPH, spawn=lambda x: "not yaml at all: [",
                     home=tmp_path, workdir=tmp_path, verify=_no_verify, search=_no_search)
    assert set(r["failed"]) == {"c1", "c2"}
    kinds = {i["kind"] for i in inbox_list(home=tmp_path)}
    assert kinds == {"failed-orchestration"}


def test_accepts_yaml_wrapped_in_a_markdown_fence(tmp_path):
    p = _approved_toc(tmp_path)

    def spawn(prompt):
        cid = "c1" if "c1" in prompt else "c2"
        return f"```yaml\n{NOTE.format(cid=cid)}```"

    result = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path,
                     verify=_no_verify, search=_no_search)

    assert result["done"] == ["c1", "c2"]


def test_retry_tells_the_researcher_what_lint_rejected():
    """The one retry re-sent the identical prompt, so a note with a bad key was
    re-rolled rather than corrected -- the same defect the page writer had."""
    from paper_skill.p3_research import _render_research_prompt

    brief = {"concept": "sdpa", "questions": ["why scale?"]}
    first = _render_research_prompt(brief)
    retry = _render_research_prompt(brief, ["sources_consulted must be a map"])

    assert "REJECTED" not in first
    assert "sources_consulted must be a map" in retry
    assert retry.startswith(first)


def test_no_problems_leaves_the_research_prompt_alone():
    from paper_skill.p3_research import _render_research_prompt

    brief = {"concept": "sdpa"}

    assert _render_research_prompt(brief, []) == _render_research_prompt(brief)


def test_a_wrong_citation_is_rejected_and_fed_back(tmp_path):
    """The gate has to reach the retry, and the retry has to say what was wrong
    -- otherwise the second attempt re-rolls the same bad citation."""
    p = _approved_toc(tmp_path)
    prompts, calls = [], []

    def verify(_note):
        calls.append(1)
        return [] if len(calls) > 1 else ['arXiv:2005.12439 is "Personalized Fashion '
                                          'Recommendation", not "A Benchmark Study"']

    def spawn(prompt):
        prompts.append(prompt)
        return NOTE.format(cid="c1" if "c1" in prompt else "c2")

    result = run_research(p, GRAPH, spawn=spawn, home=tmp_path,
                          workdir=tmp_path, verify=verify, search=_no_search)

    assert result["done"] == ["c1", "c2"]
    assert "Personalized Fashion Recommendation" in prompts[1]
    assert "REJECTED" not in prompts[0]


def test_a_citation_that_stays_wrong_fails_the_note(tmp_path):
    from research_mcp.inbox import inbox_list
    p = _approved_toc(tmp_path)

    result = run_research(
        p, GRAPH, spawn=lambda prompt: NOTE.format(cid="c1" if "c1" in prompt else "c2"),
        home=tmp_path, workdir=tmp_path,
        verify=lambda _n: ["arXiv:2005.12439 does not resolve to a paper"],
        search=_no_search)

    assert set(result["failed"]) == {"c1", "c2"}
    assert wiki_get("c1", home=tmp_path)["status"] != "ok"
    assert any("does not resolve" in str(i) for i in inbox_list(home=tmp_path))


def test_search_results_reach_the_researchers_prompt(tmp_path):
    """The whole point of step 2: the model selects from real results instead
    of recalling urls."""
    p = _approved_toc(tmp_path)
    prompts = []

    def search(_query, **_kw):
        return {"status": "ok", "results": [
            {"title": "STRIP: A Defence Against Trojan Attacks",
             "url": "https://arxiv.org/abs/1902.06531", "year": "2019",
             "citations": 400}]}

    run_research(p, GRAPH, spawn=lambda pr: prompts.append(pr) or NOTE.format(
        cid="c1" if "c1" in pr else "c2"),
        home=tmp_path, workdir=tmp_path, verify=_no_verify, search=search)

    assert "STRIP: A Defence Against Trojan Attacks" in prompts[0]
    assert "https://arxiv.org/abs/1902.06531" in prompts[0]


def test_no_search_results_leave_the_prompt_as_it_was(tmp_path):
    """A candidate heading with nothing under it reads as "search found
    nothing worth citing" -- a claim search never made."""
    p = _approved_toc(tmp_path)
    prompts = []

    run_research(p, GRAPH, spawn=lambda pr: prompts.append(pr) or NOTE.format(
        cid="c1" if "c1" in pr else "c2"),
        home=tmp_path, workdir=tmp_path, verify=_no_verify,
        search=lambda *_a, **_kw: {"status": "insufficient-sources", "results": []})

    assert "VERIFIED CANDIDATES" not in prompts[0]




def test_both_queries_are_asked_when_the_graph_has_a_subject(tmp_path):
    """run_research is the only place that holds the graph, so it is the only
    place that can supply the topic for the second query."""
    p = _approved_toc(tmp_path)
    themed = {"nodes": [{"id": "a", "label": "Backdoor Attack (BA)", "level": 1},
                        {"id": "b", "label": "Backdoor Defense", "level": 1}],
              "edges": []}
    asked = []

    run_research(p, themed,
                 spawn=lambda pr: NOTE.format(cid="c1" if "c1" in pr else "c2"),
                 home=tmp_path, workdir=tmp_path, verify=_no_verify,
                 search=lambda q, **_kw: asked.append(q) or {"status": "ok",
                                                             "results": []})

    assert any(q.startswith("backdoor") for q in asked)
    assert any(not q.startswith("backdoor") for q in asked)


def test_a_citation_with_a_quoted_title_survives_parsing():
    """The one research concept in the chain-of-thought run failed both
    attempts with "not parseable YAML" on a citation the model had every
    reason to write:

      S1: "Emergent Abilities of Large Language Models," Wei et al., arXiv:...

    YAML reads the quoted title as a complete scalar and then chokes on the
    author that follows. A title in quotes followed by the author is simply how
    citations are written, and the prompt asks for "citation or URL string", so
    this recurs on any paper whose notes cite titled works.

    concepts and next_steps already ask for JSON and share one tolerant reader;
    p3 was the last stage on YAML and the only one with this failure mode.
    """
    from paper_skill.p3_research import _parse_note

    reply = ('{"concept": "emergent-abilities", "status": "complete",'
             ' "synthesis": "Gains appear past a scale threshold [S1].",'
             ' "resources": [], "unresolved": [],'
             ' "sources_consulted": {"S1": "\\"Emergent Abilities of Large '
             'Language Models,\\" Wei et al., arXiv:2206.07682 (2022)"}}')

    note = _parse_note(reply)

    assert note is not None, "quoted-title citation still unparseable"
    assert "Wei et al." in note["sources_consulted"]["S1"]


def test_a_fenced_json_note_still_parses():
    """Models fence structured output some fraction of the time; the shared
    reader already tolerates it, which is half the reason to reuse it."""
    from paper_skill.p3_research import _parse_note

    assert _parse_note('```json\n{"concept": "x", "status": "complete"}\n```'
                       )["concept"] == "x"


def test_the_prompt_asks_for_json_not_yaml():
    """The two tests above passed the moment they were written, because
    yaml.safe_load already accepts JSON -- so the parser was never the defect.
    What produced the unparseable note is the prompt asking for YAML, which
    cannot hold `S1: "Quoted Title," Author` without escaping the model has no
    reason to add.

    Asking for JSON while keeping yaml.safe_load is the tolerant combination:
    the requested format is unambiguous, and a model that answers in YAML
    anyway still parses.
    """
    from paper_skill.p3_research import RESEARCH_PROMPT

    assert "JSON" in RESEARCH_PROMPT
    assert "as YAML" not in RESEARCH_PROMPT


# --- educational composition floor -------------------------------------------
_NO_TEACHING = {
    "concept": "sdpa", "status": "complete",
    "synthesis": "Scaling keeps softmax gradients usable [S1].",
    "resources": [{"url": "https://arxiv.org/abs/1706.03762",
                   "title": "Attention Is All You Need",
                   "type": "follow-up-paper", "why": "the paper"}],
    "unresolved": [], "sources_consulted": {"S1": "arXiv:1706.03762"},
}


def _run(tmp_path, spawn, graph=GRAPH):
    from paper_skill.p3_research import run_research
    p = tmp_path / "toc.yaml"
    write_toc([{**ROWS[0], "research": True}], p)
    p.write_text(p.read_text(encoding="utf-8").replace(
        "approved: false", "approved: true"), encoding="utf-8")
    return run_research(p, graph, spawn=spawn, home=tmp_path, workdir=tmp_path,
                        verify=lambda _n: [], search=lambda *a, **k: {"results": []})


def test_a_note_with_no_explainer_is_kept_not_thrown_away(tmp_path):
    """The floor drives a retry; it must not disqualify the note. A P3 failure
    means the page gets written with no research context at all, so discarding
    a note of three good papers because it lacks a lecture makes the page
    worse, which is the opposite of the point."""
    import json
    from research_mcp.wiki import wiki_get

    cid = ROWS[0]["id"]
    result = _run(tmp_path, lambda _p: json.dumps(_NO_TEACHING))

    assert result["done"] == [cid] and result["failed"] == [], result
    assert wiki_get(cid, home=tmp_path)["status"] == "ok"


def test_the_retry_asks_for_the_missing_explainer(tmp_path):
    import json

    prompts = []

    def spawn(prompt):
        prompts.append(prompt)
        return json.dumps(_NO_TEACHING)

    _run(tmp_path, spawn)

    assert len(prompts) == 2, "a satisfiable gap should cost the retry"
    assert "visual" in prompts[1] and "REJECTED" in prompts[1]


def test_a_note_that_already_teaches_costs_no_retry(tmp_path):
    import json

    good = {**_NO_TEACHING,
            "resources": _NO_TEACHING["resources"]
            + [{"url": "https://distill.pub/x", "title": "Explainer",
                "type": "visual", "why": "shows it"}]}
    calls = []

    _run(tmp_path, lambda _p: calls.append(1) or json.dumps(good))

    assert len(calls) == 1


def test_the_prompt_asks_for_a_visual_or_lecture():
    from paper_skill.p3_research import RESEARCH_PROMPT

    assert "visual" in RESEARCH_PROMPT and "lecture" in RESEARCH_PROMPT
    assert "at least one" in RESEARCH_PROMPT.lower()


# --- enrichment scope --------------------------------------------------------
# P2 marks research:true "only where the paper's own text is insufficient", and
# a paper is nearly always sufficient to describe its own concepts -- so across
# ddim, chain-of-thought and resnet it flagged 2 of 65 concepts and P3 ran on
# 3% of the build. That criterion is about EVIDENCE SUFFICIENCY. A learner
# wanting a lecture on ddim's neural-ode-relevance is asking something else
# entirely, and that concept is not flagged because the paper covers it fine.

_ENRICH_ROWS = [
    {"id": "thesis", "label": "T", "level": 0, "include": True, "research": False,
     "definition": "d", "sub_questions": ["q"]},
    {"id": "core", "label": "C", "level": 1, "include": True, "research": False,
     "definition": "d", "sub_questions": ["q"]},
    {"id": "detail", "label": "D", "level": 3, "include": True, "research": False,
     "definition": "d", "sub_questions": ["q"]},
]


def _enrich_toc(tmp_path, rows=_ENRICH_ROWS):
    p = tmp_path / "toc.yaml"
    write_toc(rows, p)
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    doc["approved"] = True
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    return p


def test_core_concepts_are_researched_without_being_flagged(tmp_path):
    """Level 0 and 1 are the concepts a learner meets first and the ones worth
    an explainer, whether or not the paper's own text has a gap."""
    result = run_research(_enrich_toc(tmp_path), GRAPH,
                          spawn=lambda _p: NOTE.format(cid="x"),
                          home=tmp_path, workdir=tmp_path,
                          verify=_no_verify, search=_no_search)

    assert set(result["done"]) == {"thesis", "core"}


def test_deep_details_are_left_alone(tmp_path):
    """Enrichment has to stay bounded or it researches every concept in every
    paper. Level 3 is where the paper's own text is the right depth."""
    result = run_research(_enrich_toc(tmp_path), GRAPH,
                          spawn=lambda _p: NOTE.format(cid="x"),
                          home=tmp_path, workdir=tmp_path,
                          verify=_no_verify, search=_no_search)

    assert "detail" not in result["done"]


def test_an_explicitly_flagged_deep_concept_is_still_researched(tmp_path):
    """The insufficiency flag still means what it meant; enrichment widens the
    net rather than replacing it."""
    rows = [dict(_ENRICH_ROWS[2], research=True)]
    result = run_research(_enrich_toc(tmp_path, rows), GRAPH,
                          spawn=lambda _p: NOTE.format(cid="x"),
                          home=tmp_path, workdir=tmp_path,
                          verify=_no_verify, search=_no_search)

    assert result["done"] == ["detail"]


def test_enrichment_depth_is_tunable(tmp_path):
    result = run_research(_enrich_toc(tmp_path), GRAPH,
                          spawn=lambda _p: NOTE.format(cid="x"),
                          home=tmp_path, workdir=tmp_path,
                          verify=_no_verify, search=_no_search, enrich_level=-1)

    assert result["done"] == []


def test_the_prompt_asks_where_in_the_resource_to_look():
    """A 40-minute lecture or a long explainer is not actionable on its own --
    "watch this" is a chore, "watch 12:30-18:00, the part where he derives the
    mask" is a five-minute answer. The note schema has always had an optional
    `anchor` field for exactly this and nothing ever asked for it: zero
    producers, zero consumers.
    """
    from paper_skill.p3_research import RESEARCH_PROMPT

    assert "anchor" in RESEARCH_PROMPT
    lowered = RESEARCH_PROMPT.lower()
    assert "timestamp" in lowered or "section" in lowered


def test_the_prompt_asks_for_the_video_not_the_course_homepage():
    """The lottery-ticket run returned hanlab.mit.edu/courses/2023-fall-65940
    and efficientml.ai as `lecture` resources. Both are course indexes whose
    actual lectures live on YouTube, so they classify as `link` and render no
    video card -- the one category where a direct media url really is the
    better resource."""
    from paper_skill.p3_research import RESEARCH_PROMPT

    lowered = RESEARCH_PROMPT.lower()
    assert "watch?v=" in lowered or "watch url" in lowered
    assert "landing page" in lowered or "course index" in lowered


# --- a searching researcher narrates before it answers ----------------------
# Giving P3 WebSearch made 6 of the first 7 concepts fail with "not parseable
# JSON". The notes were fine; the reader was not. A model that has just run
# tool calls introduces its answer instead of opening with a brace, and
# _strip_fences only peels a fence sitting at position zero.
#
# llm_spawn.parse_json_reply already exists for exactly this -- its docstring
# records next_steps hitting the identical symptom with a strict json.loads.
# P3 simply never adopted it.

REAL_SHAPE = ('{"concept": "functional-symmetry", "status": "complete",'
              ' "synthesis": "A claim [S1].", "resources": [],'
              ' "unresolved": [], "sources_consulted": {"S1": "a citation"}}')


@pytest.mark.parametrize("reply", [
    f"I searched for the canonical sources. Here is the note:\n\n{REAL_SHAPE}",
    f"Let me look that up.\n\n```json\n{REAL_SHAPE}\n```",
    f"```json\n{REAL_SHAPE}\n```\n\nI verified each url resolves.",
    f"Based on 3 searches:\n\n{REAL_SHAPE}\n\nAll three are reachable.",
])
def test_a_note_wrapped_in_narration_is_still_read(reply):
    from paper_skill.p3_research import _parse_note

    note = _parse_note(reply)

    assert note is not None, "narration around the object must not lose the note"
    assert note["concept"] == "functional-symmetry"


def test_a_reply_that_really_has_no_note_is_still_rejected():
    from paper_skill.p3_research import _parse_note

    assert _parse_note("I could not find any reliable sources for this.") is None


def test_a_yaml_note_still_parses():
    """The prompt asks for JSON, but the parser has deliberately accepted YAML
    since the citation-quoting incident. Do not regress that."""
    from paper_skill.p3_research import _parse_note

    note = _parse_note("concept: x\nstatus: complete\nsynthesis: a claim\n")

    assert note["concept"] == "x"

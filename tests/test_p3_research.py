import yaml
from paper_skill.p3_research import run_research
from paper_skill.toc import write_toc
from research_mcp.wiki import wiki_get

# These tests exercise orchestration, not verification. Without an injected
# verifier they reach the real network for every resource url in NOTE.
def _no_verify(_note):
    return []

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
                     verify=_no_verify)
    assert r["status"] == "not_approved"


def test_runs_all_and_persists_notes(tmp_path):
    p = _approved_toc(tmp_path)
    def spawn(prompt):
        cid = "c1" if "c1" in prompt else "c2"
        return NOTE.format(cid=cid)
    r = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path,
                     verify=_no_verify)
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
                     verify=_no_verify)
    assert r1["done"] == ["c1"] and r1["failed"] == ["c2"]
    r2 = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path,
                     verify=_no_verify)
    assert r2["skipped"] == ["c1"] and r2["done"] == ["c2"]


def test_invalid_note_goes_to_inbox(tmp_path):
    from research_mcp.inbox import inbox_list
    p = _approved_toc(tmp_path)
    r = run_research(p, GRAPH, spawn=lambda x: "not yaml at all: [",
                     home=tmp_path, workdir=tmp_path, verify=_no_verify)
    assert set(r["failed"]) == {"c1", "c2"}
    kinds = {i["kind"] for i in inbox_list(home=tmp_path)}
    assert kinds == {"failed-orchestration"}


def test_accepts_yaml_wrapped_in_a_markdown_fence(tmp_path):
    p = _approved_toc(tmp_path)

    def spawn(prompt):
        cid = "c1" if "c1" in prompt else "c2"
        return f"```yaml\n{NOTE.format(cid=cid)}```"

    result = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path,
                     verify=_no_verify)

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
                          workdir=tmp_path, verify=verify)

    assert result["done"] == ["c1", "c2"]
    assert "Personalized Fashion Recommendation" in prompts[1]
    assert "REJECTED" not in prompts[0]


def test_a_citation_that_stays_wrong_fails_the_note(tmp_path):
    from research_mcp.inbox import inbox_list
    p = _approved_toc(tmp_path)

    result = run_research(
        p, GRAPH, spawn=lambda prompt: NOTE.format(cid="c1" if "c1" in prompt else "c2"),
        home=tmp_path, workdir=tmp_path,
        verify=lambda _n: ["arXiv:2005.12439 does not resolve to a paper"])

    assert set(result["failed"]) == {"c1", "c2"}
    assert wiki_get("c1", home=tmp_path)["status"] != "ok"
    assert any("does not resolve" in str(i) for i in inbox_list(home=tmp_path))

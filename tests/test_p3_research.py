import yaml
from paper_skill.p3_research import run_research
from paper_skill.toc import write_toc
from research_mcp.wiki import wiki_get

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
    r = run_research(p, GRAPH, spawn=lambda x: "", home=tmp_path, workdir=tmp_path)
    assert r["status"] == "not_approved"


def test_runs_all_and_persists_notes(tmp_path):
    p = _approved_toc(tmp_path)
    def spawn(prompt):
        cid = "c1" if "c1" in prompt else "c2"
        return NOTE.format(cid=cid)
    r = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path)
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
    r1 = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path)
    assert r1["done"] == ["c1"] and r1["failed"] == ["c2"]
    r2 = run_research(p, GRAPH, spawn=spawn, home=tmp_path, workdir=tmp_path)
    assert r2["skipped"] == ["c1"] and r2["done"] == ["c2"]


def test_invalid_note_goes_to_inbox(tmp_path):
    from research_mcp.inbox import inbox_list
    p = _approved_toc(tmp_path)
    r = run_research(p, GRAPH, spawn=lambda x: "not yaml at all: [",
                     home=tmp_path, workdir=tmp_path)
    assert set(r["failed"]) == {"c1", "c2"}
    kinds = {i["kind"] for i in inbox_list(home=tmp_path)}
    assert kinds == {"failed-orchestration"}

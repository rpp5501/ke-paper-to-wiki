# Slice 6 — Concept Extraction + Research Orchestration (M5-P2/P3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** P2: pack → `concept_graph.json` (§5.1) + `concept_toc.yaml` human checkpoint. P3: one leased researcher run per `research: true` concept, with per-concept disk checkpoints, kill-resume, and inbox stubs.

**Architecture:** LLM work goes through an injectable `spawn(prompt) -> str` (production: `claude -p <prompt> --max-turns N`; tests: lambdas). Everything around the spawn is deterministic and tested: prompt assembly, JSON parsing/validation, retries (1), checkpointing, brief building.

**Tech Stack:** Python ≥3.10, pyyaml, subprocess; consumes slice-5 `paper_pack.json`, slice-3 `wiki_put`/`inbox_add`, existing `validate.validate_graph`/`validate_brief`.

## Global Constraints

- One retry max on schema-invalid LLM output; second failure → inbox stub, never a crash (round-2 lease design).
- The plan is fixed upfront: P2 emits pre-decomposed `sub_questions` per concept so P3 briefs need zero improvisation (deep-searcher rule).
- Human checkpoint: P3 REFUSES to run if `concept_toc.yaml` lacks `approved: true` (P4 principle).
- Tests: `cd paper-skill && PYTHONPATH="src:../research-mcp/src" python -m pytest tests/ -q`.

---

### Task 1: P2 prompt + output validation

**Files:**
- Create: `paper-skill/src/paper_skill/concepts.py`
- Test: `paper-skill/tests/test_concepts.py`

**Interfaces:**
- Produces: `CONCEPT_PROMPT` (template with `{title}`, `{sections_digest}`), `extract_concepts(pack: dict, spawn, max_retries=1) -> dict` returning `{"status": "ok", "graph": <§5.1>, "toc": [...]}` or `{"status": "failed-orchestration", "problems": [...]}`. Each toc row: `{id, label, level, research: bool, sub_questions: [..], definition, include: true}`.

- [ ] **Step 1: Failing test**

```python
# tests/test_concepts.py
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


def test_prompt_carries_sections_and_json_contract():
    assert "{sections_digest}" in CONCEPT_PROMPT and "JSON" in CONCEPT_PROMPT
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/concepts.py
"""P2: pack -> §5.1 concept graph + toc rows. LLM via injectable spawn."""
import datetime, json, re

CONCEPT_PROMPT = """You are extracting a concept graph from a research paper.
Paper: {title}

Sections (id: title — first sentence):
{sections_digest}

Emit ONLY a JSON object — no prose, no markdown fences — shaped exactly:
{{"nodes": [{{"id": "kebab-slug", "kind": "concept|equation|figure",
  "label": "...", "level": 0-3, "source_ref": "sec_x",
  "definition": "paper's own one-line definition",
  "sub_questions": ["2-4 research questions"], "research": true|false}}],
 "edges": [{{"src": "...", "dst": "...",
  "kind": "part-of|prerequisite|builds-on|defined-in|contrasts-with"}}]}}

Rules: 15-25 nodes for a full paper; exactly one level-0 node (the thesis);
every node's source_ref must be a real section id from the list above;
mark research:true only where the paper's own text is insufficient."""

_TOC_KEYS = ("definition", "sub_questions", "research")


def _digest(pack: dict) -> str:
    return "\n".join(f'{s["id"]}: {s["title"]} — {s["text"][:120]}'
                     for s in pack["sections"])


def _parse(raw: str) -> dict | None:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _problems(doc: dict, pack: dict) -> list[str]:
    probs = []
    if not isinstance(doc, dict) or "nodes" not in doc or "edges" not in doc:
        return ["missing nodes/edges"]
    section_ids = {s["id"] for s in pack["sections"]}
    node_ids = set()
    for n in doc["nodes"]:
        for k in ("id", "kind", "label", "level", "source_ref"):
            if k not in n:
                probs.append(f"node missing {k}: {n.get('id', '?')}")
        if n.get("source_ref") not in section_ids:
            probs.append(f"unknown source_ref: {n.get('source_ref')}")
        node_ids.add(n.get("id"))
    for e in doc["edges"]:
        if e.get("src") not in node_ids or e.get("dst") not in node_ids:
            probs.append(f"dangling edge: {e}")
    if sum(1 for n in doc["nodes"] if n.get("level") == 0) != 1:
        probs.append("exactly one level-0 node required")
    return probs


def extract_concepts(pack: dict, spawn, max_retries: int = 1) -> dict:
    prompt = CONCEPT_PROMPT.format(title=pack["meta"]["title"],
                                   sections_digest=_digest(pack))
    problems = []
    for attempt in range(1 + max_retries):
        doc = _parse(spawn(prompt if attempt == 0 else
                           prompt + f"\n\nYour previous output was invalid: "
                                    f"{problems}. Emit ONLY the JSON object."))
        problems = _problems(doc, pack) if doc else ["not parseable JSON"]
        if not problems:
            break
    if problems:
        return {"status": "failed-orchestration", "problems": problems}
    toc, nodes = [], []
    for n in doc["nodes"]:
        toc.append({"id": n["id"], "label": n["label"], "level": n["level"],
                    "include": True,
                    **{k: n.get(k) for k in _TOC_KEYS}})
        nodes.append({k: v for k, v in n.items() if k not in _TOC_KEYS})
    for e in doc["edges"]:
        e.setdefault("weight", 1.0)
        e.setdefault("confidence", "inferred")
        e.setdefault("confidence_score", 0.7)
    graph = {"meta": {"kind": "concept", "source": pack["meta"]["source"],
                      "generated": datetime.date.today().isoformat(), "version": 1},
             "nodes": nodes, "edges": doc["edges"]}
    return {"status": "ok", "graph": graph, "toc": toc}
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat(paper-skill): P2 concept extraction with validation loop"`

### Task 2: toc checkpoint writer/loader

**Files:**
- Create: `paper-skill/src/paper_skill/toc.py`
- Test: `paper-skill/tests/test_toc.py`

**Interfaces:**
- Produces: `write_toc(toc: list, path) -> None` (yaml with `approved: false` header), `load_approved_toc(path) -> dict` returning `{"status": "ok", "rows": [...]}` only when `approved: true` and every row has `include` — else `{"status": "not_approved", "hint": ...}`. P3 runner gates on this.

- [ ] **Step 1: Failing test**

```python
# tests/test_toc.py
import yaml
from paper_skill.toc import write_toc, load_approved_toc

ROWS = [{"id": "transformer", "label": "The Transformer", "level": 0,
         "include": True, "research": True,
         "definition": "d", "sub_questions": ["q"]}]


def test_written_toc_defaults_unapproved(tmp_path):
    p = tmp_path / "concept_toc.yaml"
    write_toc(ROWS, p)
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert doc["approved"] is False
    assert load_approved_toc(p)["status"] == "not_approved"


def test_approved_toc_loads_included_rows(tmp_path):
    p = tmp_path / "concept_toc.yaml"
    write_toc(ROWS + [{**ROWS[0], "id": "skip-me", "include": False}], p)
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    doc["approved"] = True
    p.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    r = load_approved_toc(p)
    assert r["status"] == "ok"
    assert [row["id"] for row in r["rows"]] == ["transformer"]
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/toc.py
"""concept_toc.yaml: THE human checkpoint before token spend (P4)."""
from pathlib import Path
import yaml


def write_toc(rows: list, path) -> None:
    Path(path).write_text(yaml.safe_dump(
        {"approved": False,
         "note": "review: prune concepts, set research flags, then set approved: true",
         "concepts": rows}, allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_approved_toc(path) -> dict:
    p = Path(path)
    if not p.is_file():
        return {"status": "not_approved", "hint": f"{p} does not exist — run P2 first"}
    doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not doc.get("approved"):
        return {"status": "not_approved",
                "hint": "set approved: true in concept_toc.yaml after review"}
    return {"status": "ok",
            "rows": [r for r in doc.get("concepts", []) if r.get("include")]}
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): concept_toc human checkpoint"`

### Task 3: Brief builder (toc row → research brief)

**Files:**
- Create: `paper-skill/src/paper_skill/briefs.py`
- Test: `paper-skill/tests/test_brief_builder.py`

**Interfaces:**
- Consumes: toc rows; graph edges (for `do_not_research` = sibling concept ids sharing a parent).
- Produces: `build_brief(row: dict, graph: dict, content_type="background") -> dict` valid per `research_mcp.validate.validate_brief`. Budget fixed: `{"searches": 3, "fetches": 3, "api_calls": 2}` (PLAN §4.1).

- [ ] **Step 1: Failing test**

```python
# tests/test_brief_builder.py
from paper_skill.briefs import build_brief
from research_mcp.validate import validate_brief

GRAPH = {"nodes": [], "edges": [
    {"src": "sdpa", "dst": "attention", "kind": "part-of"},
    {"src": "mha", "dst": "attention", "kind": "part-of"}]}
ROW = {"id": "sdpa", "label": "Scaled Dot-Product Attention", "level": 2,
       "include": True, "research": True,
       "definition": "Attention with 1/sqrt(dk) scaling.",
       "sub_questions": ["Why sqrt(dk)?", "Gradient effect?"]}


def test_brief_validates_and_excludes_siblings():
    brief = build_brief(ROW, GRAPH, content_type="math")
    assert validate_brief(brief) == []
    assert brief["concept"] == "sdpa"
    assert "mha" in brief["do_not_research"]
    assert brief["budget"] == {"searches": 3, "fetches": 3, "api_calls": 2}
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/briefs.py
"""Toc row -> research brief (schema-valid input for the playbook loop)."""


def _siblings(concept_id: str, graph: dict) -> list[str]:
    parents = {e["dst"] for e in graph["edges"]
               if e["src"] == concept_id and e["kind"] == "part-of"}
    return sorted({e["src"] for e in graph["edges"]
                   if e["dst"] in parents and e["kind"] == "part-of"
                   and e["src"] != concept_id})


def build_brief(row: dict, graph: dict, content_type: str = "background") -> dict:
    return {"concept": row["id"],
            "definition": row.get("definition", row["label"]),
            "content_type": content_type,
            "sub_questions": row.get("sub_questions", [])[:4],
            "do_not_research": _siblings(row["id"], graph),
            "budget": {"searches": 3, "fetches": 3, "api_calls": 2}}
```

- [ ] **Step 4: GREEN** (needs `PYTHONPATH` to include research-mcp/src). **Step 5: Commit** — `git commit -am "feat(paper-skill): brief builder with sibling exclusion"`

### Task 4: P3 orchestrator with checkpoint/resume + inbox

**Files:**
- Create: `paper-skill/src/paper_skill/p3_research.py`
- Test: `paper-skill/tests/test_p3_research.py`

**Interfaces:**
- Produces: `run_research(toc_path, graph: dict, spawn, home=None, workdir=None) -> dict` — `{"status", "done": [...], "failed": [...], "skipped": [...]}`. Per concept: skip if `wiki_get` hit or `<workdir>/p3_done/<id>` exists; spawn playbook prompt; parse YAML note; `wiki_put`; on invalid-after-retry → `inbox_add("failed-orchestration", ...)`. Refuses to run without approved toc. CLI: `python -m paper_skill.p3_research concept_toc.yaml --graph concept_graph.json`. Production spawn: `subprocess.run(["claude", "-p", prompt, "--max-turns", "15"], ...)`.

- [ ] **Step 1: Failing test**

```python
# tests/test_p3_research.py
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
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/p3_research.py
"""P3: one leased researcher run per flagged concept. Deterministic shell;
LLM only inside spawn. Checkpoint per concept; resume free (round-4)."""
import argparse, json, subprocess, sys
from pathlib import Path
import yaml
from research_mcp.inbox import inbox_add
from research_mcp.validate import lint_note
from research_mcp.wiki import wiki_get, wiki_put
from .briefs import build_brief
from .toc import load_approved_toc

RESEARCH_PROMPT = """Follow the research playbook loop exactly for this brief.
Budgets are hard. Output ONLY the finished note as YAML (schema: concept,
status, synthesis, resources, unresolved, sources_consulted) — no prose.

BRIEF:
{brief_yaml}
"""


def _spawn_claude(prompt: str) -> str:
    return subprocess.run(["claude", "-p", prompt, "--max-turns", "15"],
                          capture_output=True, text=True, timeout=900).stdout


def _parse_note(raw: str) -> dict | None:
    try:
        doc = yaml.safe_load(raw)
        return doc if isinstance(doc, dict) else None
    except yaml.YAMLError:
        return None


def run_research(toc_path, graph: dict, spawn=_spawn_claude,
                 home=None, workdir=None) -> dict:
    toc = load_approved_toc(toc_path)
    if toc["status"] != "ok":
        return {"status": "not_approved", "hint": toc["hint"],
                "done": [], "failed": [], "skipped": []}
    done_dir = Path(workdir or ".") / "p3_done"
    done_dir.mkdir(parents=True, exist_ok=True)
    done, failed, skipped = [], [], []
    for row in toc["rows"]:
        if not row.get("research"):
            continue
        cid = row["id"]
        if (done_dir / cid).exists() or wiki_get(cid, home=home)["status"] == "ok":
            skipped.append(cid)
            continue
        brief = build_brief(row, graph)
        prompt = RESEARCH_PROMPT.format(
            brief_yaml=yaml.safe_dump(brief, allow_unicode=True, sort_keys=False))
        note, problems = None, ["spawn failed"]
        for attempt in range(2):                       # one retry max
            try:
                note = _parse_note(spawn(prompt))
            except Exception as exc:
                note, problems = None, [f"spawn error: {exc}"]
                continue
            problems = lint_note(note) if note else ["not parseable YAML"]
            if not problems:
                break
        if problems:
            inbox_add("failed-orchestration",
                      {"concept": cid, "problems": problems}, home=home)
            failed.append(cid)
            continue
        wiki_put(cid, note, home=home)
        (done_dir / cid).write_text("done", encoding="utf-8")
        done.append(cid)
    return {"status": "ok", "done": done, "failed": failed, "skipped": skipped}


def main(argv=None):
    p = argparse.ArgumentParser(prog="p3_research")
    p.add_argument("toc")
    p.add_argument("--graph", required=True)
    a = p.parse_args(argv)
    graph = json.loads(Path(a.graph).read_text(encoding="utf-8"))
    print(json.dumps(run_research(a.toc, graph), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: GREEN (4 tests) + both suites.** **Step 5: Commit** — `git commit -am "feat(paper-skill): P3 orchestrator (checkpoint/resume, inbox stubs)"`

### Review gate (slice 6)

- [ ] End-to-end dry run with a scripted spawn (no tokens): pack fixture → `extract_concepts` → `write_toc` → hand-approve → `run_research` with fake notes → wiki populated, `p3_done/` markers exist.
- [ ] Kill-resume test passes (test_resume_skips_done_concepts).
- [ ] Live run on AIAYN pack via `claude -p` (owner, subscription): toc has 15–25 concepts; owner prunes + approves; P3 completes or stubs; every stored note passes `python -m research_mcp.validate note`.
- [ ] Update INDEX. Commit.

# Slice 10 — Next-Steps Skill (M7) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deterministic gap harvest (N1) → leased synthesis into anchored directions (N2) → top-k novelty checks (N3) → `NEXT_STEPS.md` + `ideas.yaml` human checkpoint (N4). Consumes existing artifacts only — no new infrastructure (PLAN round-5).

**Architecture:** N1 is pure Python over pack + graphs + `_research_wiki` + repo. N2/N3 use the injectable-spawn pattern. The anchor lint is the hard gate: an idea without graph-node ids AND source refs does not pass (round-5: unanchored ideas = lint failure).

**Tech Stack:** Python ≥3.10; consumes slices 3 (citation_walk, wiki), 4 (hotspots, graph_query), 5 (pack), 9 (bridged graph, optional — degrade without it).

## Global Constraints

- Every idea carries `anchors: {nodes: [...], sources: [...]}` — both non-empty; lint rejects otherwise.
- N3 runs only on the top-k (default 3) ideas; each novelty check is one leased researcher run through slice-6's `run_research` machinery with a generated brief.
- Honesty rule (round-6): LLM findings are triage candidates, never verdicts — `ideas.yaml` requires owner confirmation.
- Tests: `cd paper-skill && PYTHONPATH="src:../research-mcp/src" python -m pytest tests/test_next_steps*.py -q`.

---

### Task 1: N1 deterministic harvest

**Files:**
- Create: `paper-skill/src/paper_skill/next_steps.py`
- Test: `paper-skill/tests/test_next_steps_harvest.py`

**Interfaces:**
- Produces: `harvest(pack, concept_graph, code_graph=None, wiki_home=None, repo_dir=None) -> list[dict]` — gap items `{"kind", "text", "anchors": {"nodes": [...], "sources": [...]}}`. Kinds implemented: `paper-limitation` (sections whose title matches limitation/future/discussion), `unresolved-note` (every `unresolved:` entry across `_research_wiki`), `no-implements-concept` (bridged graph present: concepts without an incoming implements edge), `todo-comment` (repo_dir: `# TODO|FIXME|HACK` scan with file:line anchors).

- [ ] **Step 1: Failing test**

```python
# tests/test_next_steps_harvest.py
from paper_skill.next_steps import harvest
from research_mcp.wiki import wiki_put

PACK = {"meta": {"source": "arXiv:1", "title": "T", "generated": "x"},
        "extraction": {}, "figures": [], "references": [], "equations": [],
        "sections": [
            {"id": "sec_7", "title": "Conclusion and Future Work", "level": 1,
             "text": "We plan to extend attention to images and audio."}]}
CONCEPTS = {"meta": {"kind": "concept", "source": "arXiv:1", "generated": "x",
                     "version": 1},
            "nodes": [{"id": "mha", "kind": "concept", "label": "MHA", "level": 2}],
            "edges": []}
NOTE = {"concept": "mha", "status": "partial",
        "synthesis": "Covered [S1].",
        "resources": [{"url": "https://x.test", "title": "t", "type": "lecture",
                        "why": "w"}],
        "unresolved": ["Why 8 heads exactly?"],
        "sources_consulted": {"S1": "https://x.test"}}


def test_harvests_future_work_section():
    gaps = harvest(PACK, CONCEPTS)
    fw = [g for g in gaps if g["kind"] == "paper-limitation"]
    assert fw and "sec_7" in fw[0]["anchors"]["sources"][0]


def test_harvests_unresolved_ledger(tmp_path):
    wiki_put("mha", NOTE, home=tmp_path)
    gaps = harvest(PACK, CONCEPTS, wiki_home=tmp_path)
    un = [g for g in gaps if g["kind"] == "unresolved-note"]
    assert un and un[0]["text"] == "Why 8 heads exactly?"
    assert "mha" in un[0]["anchors"]["nodes"]


def test_no_implements_needs_bridged_graph():
    bridged = {**CONCEPTS, "meta": {**CONCEPTS["meta"], "kind": "bridged"}}
    gaps = harvest(PACK, bridged)
    kinds = {g["kind"] for g in gaps}
    assert "no-implements-concept" in kinds


def test_todo_scan(tmp_path):
    (tmp_path / "m.py").write_text("x = 1  # TODO: cache this\n", encoding="utf-8")
    gaps = harvest(PACK, CONCEPTS, repo_dir=tmp_path)
    todos = [g for g in gaps if g["kind"] == "todo-comment"]
    assert todos and "m.py:1" in todos[0]["anchors"]["sources"][0]
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/next_steps.py
"""M7: N1 deterministic gap harvest -> N2 anchored synthesis -> N3 novelty."""
import re
from pathlib import Path
import yaml

_LIMIT_TITLES = re.compile(r"limitation|future|discussion|conclusion", re.I)
_TODO = re.compile(r"#\s*(TODO|FIXME|HACK)[:\s](.*)")


def harvest(pack: dict, concept_graph: dict, code_graph: dict | None = None,
            wiki_home=None, repo_dir=None) -> list[dict]:
    gaps: list[dict] = []
    for s in pack["sections"]:
        if _LIMIT_TITLES.search(s["title"]):
            gaps.append({"kind": "paper-limitation", "text": s["text"][:300],
                         "anchors": {"nodes": [], "sources": [f'§{s["id"]}']}})
    if wiki_home is not None:
        wiki = Path(wiki_home) / "_research_wiki"
        for f in sorted(wiki.glob("*.yaml")) if wiki.is_dir() else []:
            note = yaml.safe_load(f.read_text(encoding="utf-8"))
            for u in note.get("unresolved") or []:
                gaps.append({"kind": "unresolved-note", "text": u,
                             "anchors": {"nodes": [note["concept"]],
                                          "sources": [f.name]}})
    if concept_graph.get("meta", {}).get("kind") == "bridged":
        implemented = {e["dst"] for e in concept_graph["edges"]
                       if e["kind"] == "implements"}
        for n in concept_graph["nodes"]:
            if n["kind"] == "concept" and n["id"] not in implemented:
                gaps.append({"kind": "no-implements-concept",
                             "text": f'no implementation linked for {n["label"]}',
                             "anchors": {"nodes": [n["id"]], "sources": ["bridge"]}})
    if repo_dir is not None:
        for py in Path(repo_dir).rglob("*.py"):
            for i, line in enumerate(py.read_text(encoding="utf-8",
                                                  errors="replace").splitlines(), 1):
                m = _TODO.search(line)
                if m:
                    gaps.append({"kind": "todo-comment", "text": m.group(2).strip(),
                                 "anchors": {"nodes": [],
                                              "sources": [f"{py.name}:{i}"]}})
    return gaps
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): N1 deterministic gap harvest"`

### Task 2: Forward citation gap (what the field did next)

**Files:**
- Modify: `paper-skill/src/paper_skill/next_steps.py` (append)
- Test: `paper-skill/tests/test_next_steps_citations.py`

**Interfaces:**
- Produces: `forward_gaps(paper_id, walk=None) -> list[dict]` — wraps slice-3 `citation_walk(direction="in")`; each citing paper becomes `{"kind": "field-follow-up", "text": title, "anchors": {"nodes": [], "sources": [paper id]}}`. Soft-empty when APIs disabled.

- [ ] **Step 1: Failing test**

```python
# tests/test_next_steps_citations.py
from paper_skill.next_steps import forward_gaps


def test_forward_gaps_wrap_citation_walk():
    fake = lambda pid, direction, limit=15: {
        "status": "ok", "papers": [{"id": "W1", "title": "BERT", "year": 2019}]}
    gaps = forward_gaps("arXiv:1706.03762", walk=fake)
    assert gaps[0]["kind"] == "field-follow-up"
    assert gaps[0]["text"] == "BERT"
    assert gaps[0]["anchors"]["sources"] == ["W1"]


def test_disabled_apis_soft_empty():
    fake = lambda pid, direction, limit=15: {"status": "apis_disabled", "papers": []}
    assert forward_gaps("x", walk=fake) == []
```

- [ ] **Step 2: RED.** **Step 3: Implement** (append):

```python
def forward_gaps(paper_id: str, walk=None) -> list[dict]:
    if walk is None:
        from research_mcp.citation_walk import citation_walk as walk  # noqa: F811
    r = walk(paper_id, direction="in", limit=15)
    return [{"kind": "field-follow-up", "text": p["title"],
             "anchors": {"nodes": [], "sources": [p["id"]]}}
            for p in r.get("papers", [])]
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): forward-citation gap harvest"`

### Task 3: N2 synthesis + anchor lint + N4 outputs

**Files:**
- Modify: `paper-skill/src/paper_skill/next_steps.py` (append)
- Test: `paper-skill/tests/test_next_steps_synthesis.py`

**Interfaces:**
- Produces: `SYNTHESIS_PROMPT`; `synthesize_ideas(gaps, spawn, top=8) -> dict` (`{"status", "ideas": [...]}`, parsed from strict JSON, one retry); `lint_ideas(ideas) -> list[str]` (unanchored = failure); `write_outputs(ideas, out_dir) -> None` → `NEXT_STEPS.md` (prose, one section per idea with anchors listed) + `ideas.yaml` (`confirmed: false` per idea).

- [ ] **Step 1: Failing test**

```python
# tests/test_next_steps_synthesis.py
import json
from paper_skill.next_steps import synthesize_ideas, lint_ideas, write_outputs

GAPS = [{"kind": "unresolved-note", "text": "Why 8 heads?",
         "anchors": {"nodes": ["mha"], "sources": ["mha.yaml"]}}]
GOOD = json.dumps({"ideas": [{
    "title": "Head-count ablation study",
    "rationale": "The paper never justifies 8 heads.",
    "anchors": {"nodes": ["mha"], "sources": ["mha.yaml", "§sec_7"]}}]})


def test_synthesis_parses_and_lints_clean():
    r = synthesize_ideas(GAPS, spawn=lambda p: GOOD)
    assert r["status"] == "ok"
    assert lint_ideas(r["ideas"]) == []


def test_unanchored_idea_fails_lint():
    bad = [{"title": "Vague vibes", "rationale": "…", "anchors": {"nodes": [], "sources": []}}]
    probs = lint_ideas(bad)
    assert probs and "unanchored" in probs[0]


def test_outputs_written(tmp_path):
    r = synthesize_ideas(GAPS, spawn=lambda p: GOOD)
    write_outputs(r["ideas"], tmp_path)
    assert (tmp_path / "NEXT_STEPS.md").read_text(encoding="utf-8").count("Head-count") == 1
    import yaml
    doc = yaml.safe_load((tmp_path / "ideas.yaml").read_text(encoding="utf-8"))
    assert doc["ideas"][0]["confirmed"] is False
```

- [ ] **Step 2: RED.** **Step 3: Implement** (append):

```python
import datetime, json as _json

SYNTHESIS_PROMPT = """Synthesize research/engineering directions from these
verified gaps. Dedupe aggressively; rank by leverage. Emit ONLY JSON:
{{"ideas": [{{"title": "...", "rationale": "2 sentences max",
  "anchors": {{"nodes": ["graph node ids"], "sources": ["§sec_x / file:line / note file"]}}}}]}}
Every idea MUST reuse anchors from the gap list — inventing anchors is failure.

GAPS:
{gaps_json}
"""


def synthesize_ideas(gaps: list[dict], spawn, top: int = 8) -> dict:
    prompt = SYNTHESIS_PROMPT.format(
        gaps_json=_json.dumps(gaps, ensure_ascii=False, indent=1))
    problems = []
    for attempt in range(2):
        raw = spawn(prompt if attempt == 0 else
                    prompt + f"\nPrevious output invalid: {problems}. JSON only.")
        try:
            ideas = _json.loads(re.search(r"\{.*\}", raw, re.S).group(0))["ideas"]
        except (AttributeError, KeyError, _json.JSONDecodeError):
            problems = ["not parseable JSON with an ideas list"]
            continue
        problems = lint_ideas(ideas)
        if not problems:
            return {"status": "ok", "ideas": ideas[:top]}
    return {"status": "failed-orchestration", "problems": problems, "ideas": []}


def lint_ideas(ideas: list[dict]) -> list[str]:
    probs = []
    for i in ideas:
        a = i.get("anchors") or {}
        if not a.get("nodes") and not a.get("sources"):
            probs.append(f'unanchored idea: {i.get("title", "?")}')
        elif not a.get("sources"):
            probs.append(f'idea missing source anchors: {i.get("title", "?")}')
    return probs


def write_outputs(ideas: list[dict], out_dir) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    md = [f"# Next steps — generated {datetime.date.today().isoformat()}", ""]
    for i in ideas:
        md += [f"## {i['title']}", i["rationale"],
               f"anchors: nodes={i['anchors'].get('nodes', [])} "
               f"sources={i['anchors'].get('sources', [])}", ""]
    (out / "NEXT_STEPS.md").write_text("\n".join(md), encoding="utf-8")
    (out / "ideas.yaml").write_text(yaml.safe_dump(
        {"note": "confirm per idea; N3 novelty runs only on confirmed/top-k",
         "ideas": [{**i, "confirmed": False} for i in ideas]},
        allow_unicode=True, sort_keys=False), encoding="utf-8")
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): N2 synthesis + anchor lint + N4 outputs"`

### Task 4: N3 novelty checks (reuse P3 machinery)

**Files:**
- Modify: `paper-skill/src/paper_skill/next_steps.py` (append)
- Test: `paper-skill/tests/test_next_steps_novelty.py`

**Interfaces:**
- Produces: `novelty_briefs(ideas, top=3) -> list[dict]` — one valid research brief per top idea: concept `novelty--<slug>`, content_type `background`, sub_questions `["Has this been done? Find the closest prior work.", "What would differentiate this from existing work?"]`. Owner runs them through the standard P3/playbook loop; resulting notes land in the wiki like any other.

- [ ] **Step 1: Failing test**

```python
# tests/test_next_steps_novelty.py
from paper_skill.next_steps import novelty_briefs
from research_mcp.validate import validate_brief

IDEAS = [{"title": "Head-count ablation study", "rationale": "r",
          "anchors": {"nodes": ["mha"], "sources": ["x"]}},
         {"title": "Audio attention", "rationale": "r",
          "anchors": {"nodes": [], "sources": ["§sec_7"]}}]


def test_briefs_valid_and_capped():
    briefs = novelty_briefs(IDEAS, top=1)
    assert len(briefs) == 1
    assert briefs[0]["concept"] == "novelty--head-count-ablation-study"
    assert validate_brief(briefs[0]) == []
    assert "been done" in briefs[0]["sub_questions"][0]
```

- [ ] **Step 2: RED.** **Step 3: Implement** (append):

```python
def novelty_briefs(ideas: list[dict], top: int = 3) -> list[dict]:
    briefs = []
    for i in ideas[:top]:
        slug = re.sub(r"[^a-z0-9]+", "-", i["title"].lower()).strip("-")
        briefs.append({"concept": f"novelty--{slug}",
                       "definition": i["rationale"],
                       "content_type": "background",
                       "sub_questions": [
                           "Has this been done? Find the closest prior work.",
                           "What would differentiate this from existing work?"],
                       "do_not_research": [],
                       "budget": {"searches": 3, "fetches": 3, "api_calls": 2}})
    return briefs
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): N3 novelty briefs"`

### Review gate (slice 10) — M7 exit

- [ ] Full run on AIAYN + the annotated-transformer clone: `harvest` + `forward_gaps` → `synthesize_ideas` (live spawn) → ≥5 deduped, anchored directions in `NEXT_STEPS.md`.
- [ ] Deliberately inject one unanchored idea → `lint_ideas` rejects it (M7 exit: zero unanchored suggestions pass lint).
- [ ] Top-3 novelty briefs run through P3; each resulting note cites at least one real paper (owner spot-checks titles exist).
- [ ] Update INDEX — project complete through M7; M8 remains backlog. Commit.

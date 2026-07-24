# Slice 4 — Code Graph Engine, Adapter-First (M3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest graphify-NATIVE code graphs into schema §5.1, add the M3 own-effort pieces (hotspots, explore/staleness graph queries, Leiden-community → TOC suggestions), and dogfood on research-mcp itself.

**Architecture:** graphify's CLI is the extraction engine (its stable surface); our code touches only `graph.json` in/out. Deterministic everywhere — zero LLM calls in this slice.

**Tech Stack:** Python ≥3.10, networkx, existing `graphify/schema_adapter.py` (fork), `research_mcp/graph_query.py`, `research_mcp/validate.validate_graph`.

## Global Constraints

- Fork-drift rule: fork changes are new modules only.
- §5.1 stays canonical; every ingested graph must pass `validate_graph` with zero problems.
- All graph tools success-shaped + capped (≤20 items unless caller raises it).
- Run fork tests: `cd "Forked repos/graphify" && PYTHONPATH=. python -m pytest tests/test_schema_adapter.py tests/test_native_ingest.py -q`.

---

### Task 1: graphify-native → §5.1 ingestion (`to_plan_schema_native`)

**Files:**
- Modify: `Forked repos/graphify/graphify/schema_adapter.py` (append function; existing functions untouched)
- Test: `Forked repos/graphify/tests/test_native_ingest.py`

**Interfaces:**
- Consumes: graphify native shape `nodes: [{id, label, file_type, source_file, source_location}]`, `edges: [{source, target, relation, confidence, weight, source_file}]` (verified against `tests/fixtures/extraction.json`).
- Produces: `to_plan_schema_native(graphify_graph: dict, source: str) -> dict` — valid §5.1. Mapping: `kind = {"concept": "concept", "file": "file"}.get(file_type, "function")` (coarse v1, documented); `source_ref = f"{source_file}:{source_location}"`; edge `kind = relation`, `confidence = confidence.lower() if in (extracted, inferred, ambiguous) else "inferred"`, `confidence_score = 1.0 if extracted else 0.5`. Unknown relations pass through (schema allows via validate check — if `validate_graph` rejects a relation, map it to `calls`).

- [ ] **Step 1: Failing test**

```python
# tests/test_native_ingest.py
import json
from pathlib import Path
import pytest
from graphify.schema_adapter import to_plan_schema_native

NATIVE = json.loads((Path(__file__).parent / "fixtures" / "extraction.json")
                    .read_text(encoding="utf-8"))


def test_produces_plan_schema_shape():
    g = to_plan_schema_native(NATIVE, source="repo:research-mcp")
    assert g["meta"]["kind"] == "code"
    n = g["nodes"][0]
    assert {"id", "kind", "label", "source_ref"} <= set(n)
    e = g["edges"][0]
    assert {"src", "dst", "kind", "weight", "confidence"} <= set(e)


def test_confidence_lowercased_with_score():
    g = to_plan_schema_native(NATIVE, source="x")
    for e in g["edges"]:
        assert e["confidence"] in ("extracted", "inferred", "ambiguous")
        assert 0.0 < e["confidence_score"] <= 1.0


def test_validates_against_pinned_schema():
    sys_path_note = pytest.importorskip("research_mcp.validate",
        reason="research-mcp on PYTHONPATH for cross-repo validation")
    from research_mcp.validate import validate_graph
    g = to_plan_schema_native(NATIVE, source="x")
    assert validate_graph(g) == []
```

- [ ] **Step 2: RED** (function missing). Run with both repos on path:
  `PYTHONPATH=".:../../research-mcp/src" python -m pytest tests/test_native_ingest.py -q`
- [ ] **Step 3: Implement** (append to `schema_adapter.py`):

```python
_KIND_FROM_FILE_TYPE = {"concept": "concept", "file": "file"}
_VALID_CONF = {"extracted", "inferred", "ambiguous"}


def to_plan_schema_native(graphify_graph: dict, source: str) -> dict:
    """Graphify-NATIVE extraction output → §5.1 (M3 ingestion half).

    Coarse v1 (documented): every code entity maps to kind='function' unless
    file_type says otherwise — §5.1 consumers in M6/M7 key on edges + ids,
    not code-node kind granularity.
    """
    import datetime
    nodes = []
    for n in graphify_graph["nodes"]:
        node = {"id": n["id"],
                "kind": _KIND_FROM_FILE_TYPE.get(n.get("file_type", "code"),
                                                 "function"),
                "label": n["label"]}
        if n.get("source_file"):
            loc = n.get("source_location", "")
            node["source_ref"] = f"{n['source_file']}:{loc}" if loc else n["source_file"]
        nodes.append(node)
    edges = []
    for e in graphify_graph["edges"]:
        conf = str(e.get("confidence", "inferred")).lower()
        if conf not in _VALID_CONF:
            conf = "inferred"
        edges.append({"src": e["source"], "dst": e["target"],
                      "kind": e.get("relation", "calls"),
                      "weight": float(e.get("weight", 1.0)),
                      "confidence": conf,
                      "confidence_score": 1.0 if conf == "extracted" else 0.5})
    return {"meta": {"kind": "code", "source": source,
                     "generated": datetime.date.today().isoformat(),
                     "version": 1},
            "nodes": nodes, "edges": edges}
```

- [ ] **Step 4: GREEN** (3 tests; the validate test needs research-mcp on PYTHONPATH — if `validate_graph` reports unknown edge kinds from the fixture, extend the mapping in this function to coerce them to `calls` and note it in the docstring).
- [ ] **Step 5: Commit** — `git commit -am "feat(fork): graphify-native -> §5.1 ingestion (M3 adapter half)"`

### Task 2: Dogfood runner (extract research-mcp's own graph)

**Files:**
- Create: `research-mcp/scripts/dogfood_graph.py`
- Test: manual gate step (subprocess-driven; skipped in CI when graphify absent)

**Interfaces:**
- Produces: `research-mcp/graphify-out/graph.json` (native) and `research-mcp/code_graph.json` (§5.1). Consumed by Task 3/4 and the slice-9 bridge.

- [ ] **Step 1: Write the runner**

```python
# scripts/gate note: requires `pip install -e "../Forked repos/graphify"` once.
# scripts/dogfood_graph.py
"""Extract research-mcp's own code graph via the graphify fork (keyless AST
path — code-only corpora need no LLM backend), then convert to §5.1."""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]
                       / "Forked repos" / "graphify"))
from graphify.schema_adapter import to_plan_schema_native

ROOT = Path(__file__).resolve().parents[1]

subprocess.run(["graphify", "extract", "src/"], cwd=ROOT, check=True)
native = json.loads((ROOT / "graphify-out" / "graph.json").read_text(encoding="utf-8"))
plan = to_plan_schema_native(native, source="repo:research-mcp")
(ROOT / "code_graph.json").write_text(
    json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"nodes={len(plan['nodes'])} edges={len(plan['edges'])} -> code_graph.json")
```

- [ ] **Step 2:** Add `graph.json`, `graphify-out/`, `code_graph.json` to `research-mcp/.gitignore` AND `.claudeignore` (round-8 artifact hygiene + graphify's own prompt-cache warning).
- [ ] **Step 3:** Run it; expect a non-trivial graph (≥30 nodes). Commit script + ignore rules only.

### Task 3: Hotspot analysis

**Files:**
- Create: `research-mcp/src/research_mcp/hotspots.py`
- Test: `research-mcp/tests/test_hotspots.py`

**Interfaces:**
- Consumes: §5.1 code graph dict; injectable `churn: dict[file, int]` (from `git log`) for tests.
- Produces: `hotspots(plan_graph, churn=None, git_dir=None, top=10) -> dict` — `{"status": "ok", "hotspots": [{"id", "score", "churn", "in_degree", "reasons"}]}` sorted desc. Score = normalized `churn × (1 + in_degree)` (complexity/test-absence factors are M7 additions — YAGNI here). M7 (slice 10) consumes this list.

- [ ] **Step 1: Failing test**

```python
# tests/test_hotspots.py
from research_mcp.hotspots import hotspots

G = {"meta": {"kind": "code", "source": "x", "generated": "2026-07-09", "version": 1},
     "nodes": [{"id": "a.py::f", "kind": "function", "label": "f", "source_ref": "a.py:L1"},
               {"id": "b.py::g", "kind": "function", "label": "g", "source_ref": "b.py:L1"},
               {"id": "c.py::h", "kind": "function", "label": "h", "source_ref": "c.py:L1"}],
     "edges": [{"src": "b.py::g", "dst": "a.py::f", "kind": "calls",
                "weight": 1.0, "confidence": "extracted", "confidence_score": 1.0},
               {"src": "c.py::h", "dst": "a.py::f", "kind": "calls",
                "weight": 1.0, "confidence": "extracted", "confidence_score": 1.0}]}


def test_high_churn_high_indegree_wins():
    r = hotspots(G, churn={"a.py": 9, "b.py": 1, "c.py": 0})
    assert r["status"] == "ok"
    assert r["hotspots"][0]["id"] == "a.py::f"
    assert r["hotspots"][0]["in_degree"] == 2


def test_zero_churn_graph_success_shaped():
    r = hotspots(G, churn={})
    assert r["status"] == "ok" and "hint" in r
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/research_mcp/hotspots.py
"""Hotspots (M3/M7): churn × centrality over a §5.1 code graph. Deterministic."""
import subprocess
from collections import Counter


def _git_churn(git_dir) -> dict:
    out = subprocess.run(
        ["git", "log", "--since=1 year ago", "--name-only", "--pretty=format:"],
        cwd=git_dir, capture_output=True, text=True).stdout
    return dict(Counter(l.strip() for l in out.splitlines() if l.strip()))


def _file_of(node) -> str:
    ref = node.get("source_ref", "")
    return ref.split(":", 1)[0] if ref else ""


def hotspots(plan_graph: dict, churn: dict | None = None,
             git_dir=None, top: int = 10) -> dict:
    if churn is None:
        churn = _git_churn(git_dir or ".")
    indeg = Counter()
    for e in plan_graph["edges"]:
        indeg[e["dst"]] += 1
    rows = []
    for n in plan_graph["nodes"]:
        c = churn.get(_file_of(n), 0)
        d = indeg.get(n["id"], 0)
        score = c * (1 + d)
        if score > 0:
            rows.append({"id": n["id"], "score": score, "churn": c,
                         "in_degree": d,
                         "reasons": [f"churn={c}", f"in_degree={d}"]})
    rows.sort(key=lambda r: -r["score"])
    result = {"status": "ok", "hotspots": rows[:top]}
    if not rows:
        result["hint"] = "no churn recorded — quiet repo or missing git history"
    return result
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat: hotspot analysis (churn x in-degree)"`

### Task 4: `graph_query.explore` + staleness banner

**Files:**
- Modify: `research-mcp/src/research_mcp/graph_query.py` (append; `impact` untouched)
- Test: `research-mcp/tests/test_graph_query_explore.py`

**Interfaces:**
- Produces: `explore(plan_graph, node_id, repo_dir=None) -> dict` — one task-shaped card (codegraph's composite-explore adoption, round-9): `{"status", "node": {...}, "neighbors": {kind: [ids ≤10]}, "impact_count": int, "stale": bool, "banner"?: str}`. Staleness: if `repo_dir` given and any file mtime > `meta.generated` date → `banner: "⚠️ edited since graph sync — Read files directly for ground truth"`.

- [ ] **Step 1: Failing test**

```python
# tests/test_graph_query_explore.py
import json, os, time
from pathlib import Path
from research_mcp.graph_query import explore

FIXTURE = json.loads((Path(__file__).resolve().parents[2] / "paper-skill" /
                      "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))


def test_card_groups_neighbors_by_edge_kind():
    r = explore(FIXTURE, "attention")
    assert r["status"] == "ok"
    assert "scaled-dot-product-attention" in r["neighbors"]["part-of"]
    assert r["impact_count"] >= 2


def test_unknown_node_success_shaped():
    assert explore(FIXTURE, "zzz")["status"] == "not_found"


def test_staleness_banner_when_files_newer(tmp_path):
    f = tmp_path / "late.py"; f.write_text("x")
    os.utime(f, (time.time(), time.time()))
    old = dict(FIXTURE); old["meta"] = dict(FIXTURE["meta"], generated="2020-01-01")
    r = explore(old, "attention", repo_dir=tmp_path)
    assert r["stale"] is True and "⚠️" in r["banner"]
```

- [ ] **Step 2: RED.** **Step 3: Implement** (append to `graph_query.py`):

```python
def explore(plan_graph: dict, node_id: str, repo_dir=None) -> dict:
    """Composite node card (codegraph 'explore', round-9): node + neighbors
    grouped by edge kind + blast-radius count + staleness banner."""
    import datetime
    from pathlib import Path
    known = {n["id"]: n for n in plan_graph["nodes"]}
    if node_id not in known:
        return {"status": "not_found", "node": node_id,
                "hint": f"'{node_id}' not in graph — ids look like: "
                        f"{sorted(known)[:5]}"}
    neighbors: dict = {}
    for e in plan_graph["edges"]:
        if e["src"] == node_id:
            neighbors.setdefault(e["kind"], []).append(e["dst"])
        elif e["dst"] == node_id:
            neighbors.setdefault(e["kind"], []).append(e["src"])
    neighbors = {k: v[:10] for k, v in neighbors.items()}
    result = {"status": "ok", "node": known[node_id], "neighbors": neighbors,
              "impact_count": len(impact(plan_graph, node_id, depth=2)["dependents"]),
              "stale": False}
    if repo_dir:
        gen = plan_graph.get("meta", {}).get("generated", "")
        try:
            gen_ts = datetime.datetime.fromisoformat(gen).timestamp()
            newest = max((p.stat().st_mtime for p in Path(repo_dir).rglob("*.py")),
                         default=0)
            if newest > gen_ts:
                result["stale"] = True
                result["banner"] = ("⚠️ edited since graph sync — Read files "
                                    "directly for ground truth")
        except ValueError:
            pass  # unparsable date: stay non-stale, never error
    return result
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat: graph_query.explore with staleness banner"`

### Task 5: Leiden communities → TOC suggestion

**Files:**
- Create: `research-mcp/scripts/toc_from_communities.py`
- Test: `research-mcp/tests/test_toc_from_communities.py`

**Interfaces:**
- Consumes: graphify's `graphify-out/graph.json` after `graphify . --cluster-only --exclude-hubs 99` (their Leiden + hub exclusion — round-9 adoption; do NOT hand-implement Leiden, round-3 rule). Communities appear as a node attribute `community` (verify on real output in the gate; if absent, communities live in `graphify-out/communities.json` — adjust loader in one place, `load_communities`).
- Produces: `toc_suggestion(nodes_with_community: list[dict]) -> list[dict]` — `[{chapter, members}]` sorted by size; script writes `toc_suggestion.yaml` for the human checkpoint (P4 principle).

- [ ] **Step 1: Failing test**

```python
# tests/test_toc_from_communities.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from toc_from_communities import toc_suggestion

NODES = [{"id": "a", "label": "fetch", "community": 0},
         {"id": "b", "label": "fetch_clean", "community": 0},
         {"id": "c", "label": "wiki", "community": 1}]


def test_groups_by_community_sorted_by_size():
    toc = toc_suggestion(NODES)
    assert toc[0]["members"] == ["a", "b"]
    assert toc[1]["members"] == ["c"]
    assert all("chapter" in row for row in toc)
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# scripts/toc_from_communities.py
"""Leiden communities (graphify --cluster-only) -> toc_suggestion.yaml.
Communities ≈ chapters, hubs ≈ anchor pages (PLAN §4.2)."""
import json, sys
from collections import defaultdict
from pathlib import Path
import yaml


def toc_suggestion(nodes: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for n in nodes:
        if "community" in n:
            groups[n["community"]].append(n["id"])
    rows = [{"chapter": f"community-{c}", "members": sorted(ms)}
            for c, ms in groups.items()]
    rows.sort(key=lambda r: -len(r["members"]))
    return rows


def main():
    graph = json.loads(Path("graphify-out/graph.json").read_text(encoding="utf-8"))
    toc = toc_suggestion(graph["nodes"])
    Path("toc_suggestion.yaml").write_text(
        yaml.safe_dump(toc, allow_unicode=True), encoding="utf-8")
    print(f"{len(toc)} chapters -> toc_suggestion.yaml (human checkpoint)")


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat: community->TOC suggestion script"`

### Review gate (slice 4)

- [ ] `to_plan_schema_native(extraction.json)` → `validate_graph` returns `[]`.
- [ ] `pip install -e "Forked repos/graphify"` then `python scripts/dogfood_graph.py` on research-mcp → `code_graph.json` with ≥30 nodes.
- [ ] `python -c "from research_mcp.hotspots import hotspots; ..."` on the dogfood graph + real git churn prints a top-10 with `fetch_clean.py` entities present.
- [ ] `graphify . --cluster-only --exclude-hubs 99 && python scripts/toc_from_communities.py` → `toc_suggestion.yaml` chapters look module-shaped (eyeball).
- [ ] Update INDEX status. Commit.

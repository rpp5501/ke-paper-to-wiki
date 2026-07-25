# Slice 9 — Paper↔Code Bridge (M6) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Propose–verify–confirm `implements` edges between the AIAYN concept graph and a Transformer implementation's code graph; merge both graphs into one explorer.

**Architecture:** Three stages, strictly separated: (1) deterministic candidate proposer (lexical + structural scoring, zero tokens); (2) leased LLM verification (one YES/NO+reason per candidate, injectable spawn); (3) human confirmation via `bridge_candidates.yaml` (never auto-commit an edge — automatic equation→code matching without human confirm is explicitly de-scoped, §8). Merged graph = §5.1 with `implements` edges (already reserved in the schema).

**Tech Stack:** Python ≥3.10; consumes slice-4 `to_plan_schema_native` (code graph) + slice-6 concept graph + slice-8 exporter.

## Global Constraints

- `implements` edge direction: `src` = code node, `dst` = concept node (dependent side = src, consistent with `graph_query._DEFAULT_SIDE`).
- Confirmed edges get `confidence: extracted, confidence_score: 1.0` (human-confirmed); unconfirmed verified candidates may ship as `inferred, 0.6` ONLY if the owner sets `include_unconfirmed: true` in the yaml header.
- Tests: `cd paper-skill && PYTHONPATH="src:../research-mcp/src" python -m pytest tests/test_bridge*.py -q`.

---

### Task 1: Candidate proposer (deterministic)

**Files:**
- Create: `paper-skill/src/paper_skill/bridge.py`
- Test: `paper-skill/tests/test_bridge_propose.py`

**Interfaces:**
- Produces: `propose_candidates(concept_graph, code_graph, top=30) -> list[dict]` — `[{concept, code, score, evidence}]` sorted desc. Scoring: token overlap between concept label tokens and split code identifiers (camelCase/snake_case → lowercase token sets), Jaccard; +0.2 bonus when the code node's file name contains a concept token. Threshold: keep score ≥ 0.25.

- [ ] **Step 1: Failing test**

```python
# tests/test_bridge_propose.py
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
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/bridge.py
"""M6 bridge: propose (deterministic) -> verify (leased) -> confirm (human)."""
import re

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|[_\-\s.:]+")
_STOP = {"the", "a", "an", "of", "and"}


def _tokens(name: str) -> set:
    return {t.lower() for t in _CAMEL.split(name) if t and t.lower() not in _STOP}


def propose_candidates(concept_graph: dict, code_graph: dict,
                       top: int = 30) -> list[dict]:
    out = []
    for c in concept_graph["nodes"]:
        ct = _tokens(c["label"])
        if not ct:
            continue
        for k in code_graph["nodes"]:
            kt = _tokens(k["label"])
            if not kt:
                continue
            jac = len(ct & kt) / len(ct | kt)
            bonus = 0.2 if any(t in k.get("source_ref", "").lower() for t in ct) else 0.0
            score = round(jac + bonus, 3)
            if score >= 0.25:
                out.append({"concept": c["id"], "code": k["id"], "score": score,
                            "evidence": f"shared tokens: {sorted(ct & kt)}"})
    out.sort(key=lambda r: -r["score"])
    return out[:top]
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): bridge candidate proposer (lexical+structural)"`

### Task 2: Verify (leased) + confirm checkpoint

**Files:**
- Modify: `paper-skill/src/paper_skill/bridge.py` (append)
- Test: `paper-skill/tests/test_bridge_verify.py`

**Interfaces:**
- Produces: `verify_candidates(cands, concept_graph, code_graph, spawn) -> list[dict]` (adds `verdict: yes|no`, `reason`); `write_candidates_yaml(cands, path)` (header `include_unconfirmed: false`, every row `confirmed: false`); `load_confirmed(path) -> list[dict]`; `merge_bridge(concept_graph, code_graph, confirmed) -> dict` (one §5.1 graph, `implements` edges, `meta.kind: "bridged"`).
- Verify prompt (exact): asks for a single-token verdict line `YES: <reason>` / `NO: <reason>` given concept definition + code label + file ref.

- [ ] **Step 1: Failing test**

```python
# tests/test_bridge_verify.py
from paper_skill.bridge import (propose_candidates, verify_candidates,
                                write_candidates_yaml, load_confirmed, merge_bridge)
import yaml

# fixtures repeated verbatim (tasks may execute out of order — no cross-test imports)
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


def test_verify_attaches_verdicts():
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE,
                          spawn=lambda p: "YES: class implements the mechanism")
    assert v[0]["verdict"] == "yes" and "implements" in v[0]["reason"]


def test_garbled_verdict_defaults_no():
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: "maybe??")
    assert all(row["verdict"] == "no" for row in v)


def test_confirm_roundtrip_and_merge(tmp_path):
    cands = propose_candidates(CONCEPTS, CODE)
    v = verify_candidates(cands, CONCEPTS, CODE, spawn=lambda p: "YES: ok")
    path = tmp_path / "bridge_candidates.yaml"
    write_candidates_yaml(v, path)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert doc["include_unconfirmed"] is False
    doc["candidates"][0]["confirmed"] = True
    path.write_text(yaml.safe_dump(doc, allow_unicode=True), encoding="utf-8")
    confirmed = load_confirmed(path)
    assert len(confirmed) == 1
    merged = merge_bridge(CONCEPTS, CODE, confirmed)
    imp = [e for e in merged["edges"] if e["kind"] == "implements"]
    assert imp[0]["src"] == "model.py::MultiHeadedAttention"
    assert imp[0]["dst"] == "multi-head-attention"
    assert imp[0]["confidence"] == "extracted"
    assert merged["meta"]["kind"] == "bridged"
```

- [ ] **Step 2: RED.** **Step 3: Implement** (append to `bridge.py`):

```python
import datetime
from pathlib import Path
import yaml

VERIFY_PROMPT = """Does this code entity implement this paper concept?
Concept: {label} — {definition}
Code: {code_label} at {source_ref}
Answer with exactly one line: "YES: <reason>" or "NO: <reason>"."""


def verify_candidates(cands: list[dict], concept_graph: dict, code_graph: dict,
                      spawn) -> list[dict]:
    concepts = {n["id"]: n for n in concept_graph["nodes"]}
    code = {n["id"]: n for n in code_graph["nodes"]}
    out = []
    for c in cands:
        cn, kn = concepts[c["concept"]], code[c["code"]]
        raw = spawn(VERIFY_PROMPT.format(
            label=cn["label"], definition=cn.get("definition", cn["label"]),
            code_label=kn["label"], source_ref=kn.get("source_ref", "?"))).strip()
        if raw.upper().startswith("YES"):
            verdict, reason = "yes", raw[3:].lstrip(": ").strip()
        elif raw.upper().startswith("NO"):
            verdict, reason = "no", raw[2:].lstrip(": ").strip()
        else:
            verdict, reason = "no", f"unparseable verdict: {raw[:60]}"
        out.append({**c, "verdict": verdict, "reason": reason})
    return out


def write_candidates_yaml(cands: list[dict], path) -> None:
    Path(path).write_text(yaml.safe_dump(
        {"include_unconfirmed": False,
         "note": "set confirmed: true per row you accept, then rerun merge",
         "candidates": [{**c, "confirmed": False} for c in cands]},
        allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_confirmed(path) -> list[dict]:
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = [c for c in doc["candidates"] if c.get("confirmed")]
    if doc.get("include_unconfirmed"):
        rows += [c for c in doc["candidates"]
                 if not c.get("confirmed") and c.get("verdict") == "yes"]
    return rows


def merge_bridge(concept_graph: dict, code_graph: dict,
                 confirmed: list[dict]) -> dict:
    edges = concept_graph["edges"] + code_graph["edges"]
    for c in confirmed:
        strong = c.get("confirmed", False)
        edges.append({"src": c["code"], "dst": c["concept"], "kind": "implements",
                      "weight": 1.0,
                      "confidence": "extracted" if strong else "inferred",
                      "confidence_score": 1.0 if strong else 0.6})
    return {"meta": {"kind": "bridged",
                     "source": f'{concept_graph["meta"].get("source", "?")} + '
                               f'{code_graph["meta"].get("source", "?")}',
                     "generated": datetime.date.today().isoformat(), "version": 1},
            "nodes": concept_graph["nodes"] + code_graph["nodes"], "edges": edges}
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): bridge verify + confirm checkpoint + merge"`

### Task 3: Bridged explorer styling

**Files:**
- Modify: `Forked repos/graphify/graphify/exporters/explorer.py` (template only)
- Test: `Forked repos/graphify/tests/test_explorer_bridge_style.py`

**Interfaces:**
- `implements` edges render distinctly: green dashed. One style selector added to the template.

- [ ] **Step 1: Failing test**

```python
# tests/test_explorer_bridge_style.py
from graphify.exporters.explorer import to_explorer_html

G = {"meta": {"kind": "bridged", "source": "x", "generated": "x", "version": 1},
     "nodes": [{"id": "c", "kind": "concept", "label": "C", "level": 0},
               {"id": "k", "kind": "function", "label": "K", "level": 3}],
     "edges": [{"src": "k", "dst": "c", "kind": "implements", "weight": 1.0,
                "confidence": "extracted", "confidence_score": 1.0}]}


def test_implements_edges_styled():
    html = to_explorer_html(G)
    assert 'edge[kind = "implements"]' in html
```

- [ ] **Step 2: RED.** **Step 3:** add to the template's style array, after the dashed-edge selector:

```javascript
    { selector: 'edge[kind = "implements"]', style: {
        "line-style": "dashed", "line-color": "#4a9b5e",
        "target-arrow-color": "#4a9b5e", width: 2 } },
```

- [ ] **Step 4: GREEN (all explorer tests).** **Step 5: Commit** — `git commit -am "feat(fork): implements-edge styling"`

### Review gate (slice 9)

- [ ] Clone `https://github.com/harvardnlp/annotated-transformer` (read-only); slice-4 dogfood runner on it → code graph.
- [ ] `propose_candidates` → ≥10 candidates including MHA/positional-encoding pairs; live `verify_candidates` via `claude -p`; owner confirms in `bridge_candidates.yaml`.
- [ ] Hand-label the top 10 pairs (owner); precision of confirmed set ≥ 80% (M6 exit).
- [ ] Merged graph renders in the explorer with green `implements` edges; concept panel's "depended on by" now lists code nodes.
- [ ] Update INDEX. Commit.

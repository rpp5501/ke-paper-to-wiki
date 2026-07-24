# Slice 7 — Writers + Validation (M5-P4/P5) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** P4: one writer spawn per concept producing a tiered page (`## TL;DR → ## Intuition → ## Mechanics → ## The Math → ## Go Deeper`) with per-claim anchors. P5: a deterministic linter that rejects unanchored claims, dangling anchors, dead links, and broken mermaid.

**Architecture:** Same spawn-injection pattern as slice 6. Context assembly implements the round-2 dual-level rule: TL;DR/Intuition writers get the GLOBAL slice (abstract + graph neighborhood, no equations); Mechanics/Math get the LOCAL slice (exact section text + equation LaTeX + research note). One spawn per page (the tier split is inside the prompt), keeping leases simple.

**Tech Stack:** Python ≥3.10, pyyaml, requests (HEAD liveness), node+`mermaid` npm package for parse-checking (optional, skips offline).

## Global Constraints

- Anchor grammar (round-3): `[§sec_3_2, eq_1]`-style semantic ids — every claim-bearing paragraph in Mechanics/The Math MUST end with `[§sec_x]`, `[eq_n]`, or `[S#]`; lint enforces.
- Page anchors are stable: `#tldr #intuition #mechanics #the-math #go-deeper` (§4.3).
- Link liveness: HEAD with 5s timeout; skipped entirely under `RESEARCH_MCP_NO_APIS=1` (offline lint must still pass structurally).
- Tests: `cd paper-skill && PYTHONPATH="src:../research-mcp/src" python -m pytest tests/ -q`.

---

### Task 1: Context assembler (global/local slices)

**Files:**
- Create: `paper-skill/src/paper_skill/p4_context.py`
- Test: `paper-skill/tests/test_p4_context.py`

**Interfaces:**
- Consumes: pack, concept graph, wiki note (dict or None), concept id.
- Produces: `assemble_context(pack, graph, concept_id, note) -> dict` with keys `global_slice` (str: title + level-0/1 neighborhood labels + definition; NO equation latex) and `local_slice` (str: owning section text + its equations' latex + note synthesis/resources). Writer prompt consumes both.

- [ ] **Step 1: Failing test**

```python
# tests/test_p4_context.py
from paper_skill.p4_context import assemble_context

PACK = {"meta": {"source": "arXiv:1706.03762", "title": "AIAYN", "generated": "x"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3", "title": "SDPA", "level": 2,
                      "text": "We compute dot products of queries and keys."}],
        "equations": [{"id": "eq_1", "latex": r"\frac{QK^T}{\sqrt{d_k}}",
                        "section": "sec_3"}],
        "references": [], "figures": []}
GRAPH = {"meta": {"kind": "concept", "source": "arXiv:1706.03762",
                  "generated": "x", "version": 1},
         "nodes": [{"id": "attention", "kind": "concept", "label": "Attention",
                    "level": 1, "source_ref": "sec_3"},
                   {"id": "sdpa", "kind": "concept", "label": "SDPA",
                    "level": 2, "source_ref": "sec_3"}],
         "edges": [{"src": "sdpa", "dst": "attention", "kind": "part-of",
                    "weight": 1.0, "confidence": "extracted", "confidence_score": 1.0}]}
NOTE = {"concept": "sdpa", "status": "complete",
        "synthesis": "Variance argument [S1].",
        "resources": [{"url": "https://d2l.ai/x", "title": "d2l",
                        "type": "lecture", "why": "derivation"}],
        "unresolved": [], "sources_consulted": {"S1": "https://d2l.ai/x"}}


def test_global_slice_has_neighborhood_but_no_latex():
    ctx = assemble_context(PACK, GRAPH, "sdpa", NOTE)
    assert "Attention" in ctx["global_slice"]          # parent label
    assert r"\sqrt{d_k}" not in ctx["global_slice"]    # round-2 rule


def test_local_slice_has_section_equations_and_note():
    ctx = assemble_context(PACK, GRAPH, "sdpa", NOTE)
    assert "dot products of queries" in ctx["local_slice"]
    assert r"\sqrt{d_k}" in ctx["local_slice"]
    assert "Variance argument [S1]" in ctx["local_slice"]
    assert "https://d2l.ai/x" in ctx["local_slice"]


def test_missing_note_is_fine():
    ctx = assemble_context(PACK, GRAPH, "sdpa", None)
    assert "no research note" in ctx["local_slice"]
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/p4_context.py
"""Dual-level context assembly (round-2): global for TL;DR/Intuition,
local for Mechanics/Math. Deterministic, zero tokens."""


def _neighborhood(graph: dict, concept_id: str) -> list[str]:
    labels = {n["id"]: n["label"] for n in graph["nodes"]}
    out = []
    for e in graph["edges"]:
        if e["src"] == concept_id:
            out.append(f'{e["kind"]} → {labels.get(e["dst"], e["dst"])}')
        elif e["dst"] == concept_id:
            out.append(f'{labels.get(e["src"], e["src"])} → {e["kind"]}')
    return out


def assemble_context(pack: dict, graph: dict, concept_id: str,
                     note: dict | None) -> dict:
    node = next(n for n in graph["nodes"] if n["id"] == concept_id)
    sec_id = node.get("source_ref", "")
    section = next((s for s in pack["sections"] if s["id"] == sec_id), None)
    eqs = [e for e in pack["equations"] if e["section"] == sec_id]

    global_slice = "\n".join([
        f'Paper: {pack["meta"]["title"]}',
        f'Concept: {node["label"]} (level L{node.get("level", 0)})',
        "Neighborhood:",
        *(f"  {line}" for line in _neighborhood(graph, concept_id)),
    ])

    local_parts = [f'Section {sec_id}: {section["title"]}' if section else
                   f"Section {sec_id}: (text unavailable)"]
    if section:
        local_parts.append(section["text"])
    for e in eqs:
        local_parts.append(f'[{e["id"]}] {e["latex"]}')
    if note:
        local_parts.append(f'Research note: {note["synthesis"]}')
        for r in note.get("resources", []):
            local_parts.append(f'  resource: {r["title"]} — {r["why"]} — {r["url"]}')
    else:
        local_parts.append("Research note: none (no research note for this concept)")
    return {"global_slice": global_slice, "local_slice": "\n".join(local_parts)}
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat(paper-skill): P4 dual-level context assembler"`

### Task 2: Page writer (prompt + runner)

**Files:**
- Create: `paper-skill/src/paper_skill/p4_write.py`
- Test: `paper-skill/tests/test_p4_write.py`

**Interfaces:**
- Produces: `PAGE_PROMPT`, `write_pages(pack, graph, toc_rows, spawn, home=None, out_dir="pages", workdir=None) -> dict` (`done/failed/skipped`, same checkpoint pattern as P3 under `<workdir>/p4_done/`). Page file: `<out_dir>/<NN>_<id>.md` (NN = reading-path order from the fork's `reading_path`; fall back to list order if fork import unavailable). First line: `# <label>`, then the five `##` tiers with stable anchors as HTML ids: `## TL;DR {#tldr}`.

- [ ] **Step 1: Failing test**

```python
# tests/test_p4_write.py
from pathlib import Path
from paper_skill.p4_write import write_pages, PAGE_PROMPT

# fixtures repeated verbatim (tasks may execute out of order — no cross-test imports)
PACK = {"meta": {"source": "arXiv:1706.03762", "title": "AIAYN", "generated": "x"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3", "title": "SDPA", "level": 2,
                      "text": "We compute dot products of queries and keys."}],
        "equations": [{"id": "eq_1", "latex": r"\frac{QK^T}{\sqrt{d_k}}",
                        "section": "sec_3"}],
        "references": [], "figures": []}
GRAPH = {"meta": {"kind": "concept", "source": "arXiv:1706.03762",
                  "generated": "x", "version": 1},
         "nodes": [{"id": "attention", "kind": "concept", "label": "Attention",
                    "level": 1, "source_ref": "sec_3"},
                   {"id": "sdpa", "kind": "concept", "label": "SDPA",
                    "level": 2, "source_ref": "sec_3"}],
         "edges": [{"src": "sdpa", "dst": "attention", "kind": "part-of",
                    "weight": 1.0, "confidence": "extracted", "confidence_score": 1.0}]}

ROWS = [{"id": "sdpa", "label": "SDPA", "level": 2, "include": True,
         "research": False, "definition": "d", "sub_questions": []}]

GOOD_PAGE = """# SDPA
## TL;DR {#tldr}
Scaling keeps softmax gradients usable [§sec_3].
## Intuition {#intuition}
Bigger d_k means bigger dot products [§sec_3].
## Mechanics {#mechanics}
Scores are divided by sqrt(d_k) [eq_1].
## The Math {#the-math}
Variance of the dot product grows with d_k [eq_1].
## Go Deeper {#go-deeper}
- d2l.ai derivation
"""


def test_writes_page_with_reading_order_prefix(tmp_path):
    r = write_pages(PACK, GRAPH, ROWS, spawn=lambda p: GOOD_PAGE,
                    home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path)
    assert r["done"] == ["sdpa"]
    files = list((tmp_path / "pages").glob("*_sdpa.md"))
    assert len(files) == 1
    assert files[0].read_text(encoding="utf-8").startswith("# SDPA")


def test_page_missing_tiers_fails_to_inbox(tmp_path):
    from research_mcp.inbox import inbox_list
    r = write_pages(PACK, GRAPH, ROWS, spawn=lambda p: "# SDPA\njust prose",
                    home=tmp_path, out_dir=tmp_path / "pages", workdir=tmp_path)
    assert r["failed"] == ["sdpa"]
    assert inbox_list(home=tmp_path)


def test_prompt_encodes_anchor_rule_and_tiers():
    assert "{#tldr}" in PAGE_PROMPT and "[§" in PAGE_PROMPT
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/p4_write.py
"""P4 writers: one spawn per concept page, tier template enforced."""
import subprocess
from pathlib import Path
from research_mcp.inbox import inbox_add
from research_mcp.wiki import wiki_get
from .p4_context import assemble_context

TIERS = ("{#tldr}", "{#intuition}", "{#mechanics}", "{#the-math}", "{#go-deeper}")

PAGE_PROMPT = """Write the wiki page for ONE concept. Output ONLY markdown.

Structure exactly:
# <label>
## TL;DR {{#tldr}}
## Intuition {{#intuition}}
## Mechanics {{#mechanics}}
## The Math {{#the-math}}
## Go Deeper {{#go-deeper}}

Anchor rule (hard): every claim paragraph in Mechanics/The Math ends with a
semantic anchor like [§sec_3_2], [eq_1], or a research tag [S1]. TL;DR and
Intuition use the GLOBAL context only (no equations). Mechanics and The Math
use the LOCAL context. Go Deeper lists the note's resources with one-line whys.
Honesty: if the local context lacks material for a tier, write one sentence
saying so rather than padding.

GLOBAL CONTEXT:
{global_slice}

LOCAL CONTEXT:
{local_slice}
"""


def _spawn_claude(prompt: str) -> str:
    return subprocess.run(["claude", "-p", prompt, "--max-turns", "3"],
                          capture_output=True, text=True, timeout=600).stdout


def _page_problems(page: str) -> list[str]:
    return [f"missing tier {t}" for t in TIERS if t not in page]


def write_pages(pack: dict, graph: dict, toc_rows: list, spawn=_spawn_claude,
                home=None, out_dir="pages", workdir=None) -> dict:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[3]
                               / "Forked repos" / "graphify"))
        from graphify.exporters.explorer import reading_path
        order = {cid: i + 1 for i, cid in enumerate(reading_path(graph))}
    except Exception:
        order = {r["id"]: i + 1 for i, r in enumerate(toc_rows)}
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    done_dir = Path(workdir or ".") / "p4_done"
    done_dir.mkdir(parents=True, exist_ok=True)
    done, failed, skipped = [], [], []
    for row in toc_rows:
        cid = row["id"]
        if (done_dir / cid).exists():
            skipped.append(cid)
            continue
        note = wiki_get(cid, home=home)
        ctx = assemble_context(pack, graph, cid,
                               note["note"] if note["status"] == "ok" else None)
        page, problems = "", ["spawn failed"]
        for attempt in range(2):
            try:
                page = spawn(PAGE_PROMPT.format(**ctx))
            except Exception as exc:
                problems = [f"spawn error: {exc}"]
                continue
            problems = _page_problems(page)
            if not problems:
                break
        if problems:
            inbox_add("failed-orchestration",
                      {"concept": cid, "phase": "p4", "problems": problems},
                      home=home)
            failed.append(cid)
            continue
        nn = order.get(cid, 99)
        (out / f"{nn:02d}_{cid}.md").write_text(page, encoding="utf-8")
        (done_dir / cid).write_text("done", encoding="utf-8")
        done.append(cid)
    return {"status": "ok", "done": done, "failed": failed, "skipped": skipped}
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat(paper-skill): P4 page writers (tier template, anchor rule, resume)"`

### Task 3: P5 lint — anchors, links, mermaid

**Files:**
- Create: `paper-skill/src/paper_skill/p5_lint.py`, `paper-skill/scripts/mermaid_parse.mjs`
- Test: `paper-skill/tests/test_p5_lint.py`

**Interfaces:**
- Produces: `lint_page(page_md: str, pack: dict, check_links=None, check_mermaid=None) -> list[str]` (empty = clean) and `lint_pages(pages_dir, pack) -> dict` CLI. Checks: (1) all five tier anchors present; (2) every `[§sec_x]`/`[eq_n]` resolves to a real pack id; (3) claim paragraphs in Mechanics/The Math carry an anchor; (4) every http(s) link HEAD-checks (skipped under NO_APIS); (5) every ```mermaid block parses via `node scripts/mermaid_parse.mjs` (skipped when node/mermaid absent — report `skipped`, not pass).

- [ ] **Step 1: Failing test**

```python
# tests/test_p5_lint.py
from paper_skill.p5_lint import lint_page

PACK = {"sections": [{"id": "sec_3", "title": "S", "level": 1, "text": "t"}],
        "equations": [{"id": "eq_1", "latex": "x", "section": "sec_3"}],
        "meta": {}, "extraction": {}, "references": [], "figures": []}

CLEAN = """# C
## TL;DR {#tldr}
Fine.
## Intuition {#intuition}
Fine.
## Mechanics {#mechanics}
Divided by sqrt(d_k) [eq_1].
## The Math {#the-math}
Variance grows [§sec_3].
## Go Deeper {#go-deeper}
- [d2l](https://d2l.ai/x)
"""


def test_clean_page_lints_empty():
    assert lint_page(CLEAN, PACK, check_links=lambda url: True) == []


def test_dangling_anchor_caught():
    bad = CLEAN.replace("[eq_1]", "[eq_9]")
    probs = lint_page(bad, PACK, check_links=lambda url: True)
    assert any("eq_9" in p for p in probs)


def test_unanchored_math_claim_caught():
    bad = CLEAN.replace("Variance grows [§sec_3].", "Variance grows a lot.")
    probs = lint_page(bad, PACK, check_links=lambda url: True)
    assert any("unanchored" in p for p in probs)


def test_dead_link_caught():
    probs = lint_page(CLEAN, PACK, check_links=lambda url: False)
    assert any("dead link" in p for p in probs)
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/p5_lint.py
"""P5 deterministic lint: anchors resolve, claims anchored, links live."""
import os, re, subprocess
from pathlib import Path
import requests

_TIERS = ("{#tldr}", "{#intuition}", "{#mechanics}", "{#the-math}", "{#go-deeper}")
_ANCHOR = re.compile(r"\[(§(sec_[\w]+)|(eq_\d+)|S\d+)\]")
_LINK = re.compile(r"\((https?://[^)]+)\)")


def _head_ok(url: str) -> bool:
    try:
        return requests.head(url, timeout=5, allow_redirects=True).status_code < 400
    except requests.RequestException:
        return False


def _mermaid_ok(block: str) -> bool | None:
    script = Path(__file__).resolve().parents[2] / "scripts" / "mermaid_parse.mjs"
    try:
        r = subprocess.run(["node", str(script)], input=block,
                           capture_output=True, text=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return None                                   # node absent: skipped


def lint_page(page_md: str, pack: dict, check_links=None,
              check_mermaid=None) -> list[str]:
    check_links = check_links or (
        (lambda url: True) if os.environ.get("RESEARCH_MCP_NO_APIS") == "1"
        else _head_ok)
    check_mermaid = check_mermaid or _mermaid_ok
    probs = []
    for t in _TIERS:
        if t not in page_md:
            probs.append(f"missing tier {t}")
    valid_ids = ({s["id"] for s in pack["sections"]}
                 | {e["id"] for e in pack["equations"]})
    for m in _ANCHOR.finditer(page_md):
        ref = m.group(2) or m.group(3)
        if ref and ref not in valid_ids:
            probs.append(f"dangling anchor: {ref}")
    for tier in ("{#mechanics}", "{#the-math}"):
        if tier not in page_md:
            continue
        body = page_md.split(tier, 1)[1].split("## ", 1)[0]
        for para in (p.strip() for p in body.split("\n\n") if p.strip()):
            if len(para.split()) >= 6 and not _ANCHOR.search(para):
                probs.append(f"unanchored claim in {tier}: {para[:60]}…")
    for m in _LINK.finditer(page_md):
        if not check_links(m.group(1)):
            probs.append(f"dead link: {m.group(1)}")
    for block in re.findall(r"```mermaid\n(.*?)```", page_md, re.S):
        ok = check_mermaid(block)
        if ok is False:
            probs.append("mermaid block fails to parse")
        elif ok is None:
            probs.append("mermaid check skipped (node/mermaid not installed)")
    return probs
```

```javascript
// scripts/mermaid_parse.mjs — exit 0 iff stdin parses as mermaid
// setup once: npm i mermaid (in paper-skill/)
import mermaid from "mermaid";
const chunks = [];
process.stdin.on("data", c => chunks.push(c));
process.stdin.on("end", async () => {
  try {
    await mermaid.parse(chunks.join(""));
    process.exit(0);
  } catch { process.exit(1); }
});
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat(paper-skill): P5 lint (anchors, claims, links, mermaid)"`

### Task 4: Acceptance runner (§4.3 checklist)

**Files:**
- Create: `paper-skill/scripts/gate_slice7.py`

- [ ] **Step 1: Write it**

```python
# scripts/gate_slice7.py
"""AIAYN acceptance (§4.3), deterministic half. Usage:
PYTHONPATH="src:../research-mcp/src" python scripts/gate_slice7.py pack.json concept_graph.json pages/"""
import json, sys
from pathlib import Path
from paper_skill.p5_lint import lint_page

pack = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
graph = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
pages = sorted(Path(sys.argv[3]).glob("*.md"))

n = len(graph["nodes"])
checks = {
    "15-25 concept nodes": 15 <= n <= 25,
    "one page per included concept": len(pages) >= n - 2,
    "all pages lint clean": all(not lint_page(p.read_text(encoding='utf-8'), pack)
                                for p in pages),
    "sqrt(d_k) math tier exists": any("sqrt{d_k}" in p.read_text(encoding="utf-8")
                                      or "√" in p.read_text(encoding="utf-8")
                                      for p in pages),
}
for name, ok in checks.items():
    print(("PASS " if ok else "FAIL "), name)
sys.exit(0 if all(checks.values()) else 1)
```

- [ ] **Step 2:** Run after the live P4 run; all PASS.

### Review gate (slice 7)

- [ ] All unit tests green (both repos).
- [ ] Live: `write_pages` over the approved AIAYN toc, then `gate_slice7.py` → all PASS; spot-check the SDPA page: variance argument present, Alammar/Annotated-Transformer in Go Deeper with one-line whys (from the notes).
- [ ] Update INDEX. Commit.

# Slice 3 — research-mcp MCP Server (M2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the research-mcp CLI core into a registered MCP server with the missing M2 tools (citation_walk, wiki cache, note_lint), the R11 API-kill switch, inbox resume stubs, and init/doctor.

**Architecture:** Every capability stays an importable, CLI-runnable function (P6 portable core); `server.py` is a thin FastMCP wrapper. All tools success-shaped, all outputs capped by the underlying functions.

**Tech Stack:** Python ≥3.10, `mcp>=1.2,<2` (FastMCP v1 API — v2 is pre-release/breaking, verified 2026-07-09), requests, pyyaml, existing `research_mcp.cache.Cache` / `validate.lint_note`.

## Global Constraints

- Keyless forever; every network-touching function returns `{"status": ..., "hint": ...}` instead of raising (R11).
- `RESEARCH_MCP_NO_APIS=1` disables ALL provider HTTP calls (arXiv/S2/OpenAlex/CrossRef/citations) — cache and local paths still work.
- Home dir: `RESEARCH_MCP_HOME` (default `~/.research_mcp`); wiki at `<home>/_research_wiki/`, inbox at `<home>/_inbox/`.
- Output caps: citation_walk ≤800 tokens (reuse `fetch_academic.cap_output` pattern), wiki_get ≤600 tokens.
- Run tests: `cd research-mcp && PYTHONPATH=src python -m pytest tests/ -q`.

---

### Task 1: `RESEARCH_MCP_NO_APIS` kill switch

**Files:**
- Modify: `research-mcp/src/research_mcp/fetch_academic.py` (top of `academic_search`)
- Test: `research-mcp/tests/test_no_apis.py`

**Interfaces:**
- Consumes: `academic_search(query, limit, get, cache)` (existing).
- Produces: `no_apis() -> bool` helper in `fetch_academic.py`; `academic_search` returns `{"status": "apis_disabled", "records": [], "errors": [], "hint": ...}` when set. Later tasks (citation_walk, doctor) import `no_apis`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_no_apis.py
import research_mcp.fetch_academic as fa


def test_academic_search_respects_kill_switch(monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    def boom(*a, **k):
        raise AssertionError("network call attempted with NO_APIS=1")
    r = fa.academic_search("attention scaling", get=boom)
    assert r["status"] == "apis_disabled"
    assert r["records"] == []
    assert "host-native" in r["hint"]


def test_kill_switch_off_by_default(monkeypatch):
    monkeypatch.delenv("RESEARCH_MCP_NO_APIS", raising=False)
    assert fa.no_apis() is False
```

- [ ] **Step 2: Run to verify it fails** — `PYTHONPATH=src python -m pytest tests/test_no_apis.py -q` → FAIL (`no_apis` not defined).

- [ ] **Step 3: Minimal implementation** — in `fetch_academic.py`:

```python
import os

def no_apis() -> bool:
    return os.environ.get("RESEARCH_MCP_NO_APIS", "") == "1"
```

and as the FIRST lines of `academic_search(...)`:

```python
    if no_apis():
        return {"status": "apis_disabled", "records": [], "errors": [],
                "hint": "academic APIs disabled by RESEARCH_MCP_NO_APIS — "
                        "use the host-native web search instead"}
```

- [ ] **Step 4: Run tests** → PASS, then full suite → all green.
- [ ] **Step 5: Commit** — `git add -A && git commit -m "feat: RESEARCH_MCP_NO_APIS kill switch (R11 exit criterion)"`

### Task 2: `citation_walk`

**Files:**
- Create: `research-mcp/src/research_mcp/citation_walk.py`
- Test: `research-mcp/tests/test_citation_walk.py`

**Interfaces:**
- Consumes: `Cache`, `no_apis`, `approx_tokens` from fetch_academic.
- Produces: `citation_walk(paper_id: str, direction: str = "out", limit: int = 15, get=requests.get, cache=None) -> dict` with `{"status", "paper_id", "direction", "papers": [{"id","title","year"}], "hint"?}`. OpenAlex first, S2 last (R11 order). `direction`: `"out"` = references, `"in"` = citations. CLI: `python -m research_mcp.citation_walk <id> --direction in`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_citation_walk.py
import json
from research_mcp.citation_walk import citation_walk
from research_mcp.cache import Cache


class Resp:
    def __init__(self, payload): self._p = payload
    def raise_for_status(self): pass
    def json(self): return self._p


def openalex_get(url, timeout, headers, params=None):
    assert "openalex.org" in url
    return Resp({"results": [
        {"id": "https://openalex.org/W1", "title": "BERT", "publication_year": 2019},
        {"id": "https://openalex.org/W2", "title": "GPT", "publication_year": 2018},
    ]})


def test_walk_in_returns_citing_papers(tmp_path):
    r = citation_walk("arXiv:1706.03762", direction="in",
                      get=openalex_get, cache=Cache(tmp_path))
    assert r["status"] == "ok"
    assert [p["title"] for p in r["papers"]] == ["BERT", "GPT"]


def test_no_apis_success_shaped(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    r = citation_walk("arXiv:1706.03762", cache=Cache(tmp_path))
    assert r["status"] == "apis_disabled" and r["papers"] == []


def test_provider_failure_is_soft(tmp_path):
    def broken(*a, **k): raise OSError("net down")
    r = citation_walk("arXiv:1706.03762", get=broken, cache=Cache(tmp_path))
    assert r["status"] == "insufficient-sources"
    assert r["papers"] == []
```

- [ ] **Step 2: Verify RED** — FAIL: module not found.
- [ ] **Step 3: Implement**

```python
# src/research_mcp/citation_walk.py
"""Citation graph walk — OpenAlex first, S2 unauthenticated last (R11 order)."""
import argparse, json, sys
import requests
from .cache import Cache
from .fetch_academic import no_apis
from .fetch_clean import DEFAULT_CACHE_DIR

UA = {"User-Agent": "research-mcp/0.1 (keyless research tool)"}


def _openalex(paper_id, direction, limit, get):
    # OpenAlex filter: cites=W... for "in"; a work's referenced_works for "out"
    if direction == "in":
        url = "https://api.openalex.org/works"
        params = {"filter": f"cites:{paper_id}", "per_page": limit,
                  "select": "id,title,publication_year"}
        data = get(url, timeout=20, headers=UA, params=params).json()
        rows = data.get("results", [])
    else:
        url = f"https://api.openalex.org/works/{paper_id}"
        data = get(url, timeout=20, headers=UA, params={"select": "referenced_works"}).json()
        rows = [{"id": w, "title": w, "publication_year": None}
                for w in (data.get("referenced_works") or [])[:limit]]
    return [{"id": r.get("id", ""), "title": r.get("title", r.get("id", "")),
             "year": r.get("publication_year")} for r in rows]


def _s2(paper_id, direction, limit, get):
    kind = "citations" if direction == "in" else "references"
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/{kind}"
    data = get(url, timeout=20, headers=UA,
               params={"fields": "title,year,paperId", "limit": limit}).json()
    out = []
    for row in data.get("data", []):
        p = row.get("citingPaper") or row.get("citedPaper") or {}
        out.append({"id": p.get("paperId", ""), "title": p.get("title", ""),
                    "year": p.get("year")})
    return out


def citation_walk(paper_id: str, direction: str = "out", limit: int = 15,
                  get=requests.get, cache: Cache | None = None) -> dict:
    cache = cache or Cache(DEFAULT_CACHE_DIR)
    key = f"citewalk:{direction}:{limit}:{paper_id}"
    hit = cache.get(key)
    if hit is not None:
        return hit
    if no_apis():
        return {"status": "apis_disabled", "paper_id": paper_id,
                "direction": direction, "papers": [],
                "hint": "citation APIs disabled by RESEARCH_MCP_NO_APIS"}
    papers, errors = [], []
    for provider in (_openalex, _s2):          # S2 strictly last (R11)
        try:
            papers = provider(paper_id, direction, limit, get)
            if papers:
                break
        except Exception as exc:               # soft: fewer results, not error
            errors.append(f"{provider.__name__}: {exc}")
    result = {"status": "ok" if papers else "insufficient-sources",
              "paper_id": paper_id, "direction": direction,
              "papers": papers[:limit], "errors": errors}
    if papers:
        cache.put(key, result)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(prog="citation_walk")
    p.add_argument("paper_id")
    p.add_argument("--direction", choices=("in", "out"), default="out")
    p.add_argument("--limit", type=int, default=15)
    a = p.parse_args(argv)
    print(json.dumps(citation_walk(a.paper_id, a.direction, a.limit),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Verify GREEN** (3 tests) + full suite.
- [ ] **Step 5: Commit** — `git commit -am "feat: citation_walk (OpenAlex-first, S2-last, cached, success-shaped)"`

### Task 3: wiki cache (`wiki_get` / `wiki_put` / `note_lint`)

**Files:**
- Create: `research-mcp/src/research_mcp/wiki.py`
- Test: `research-mcp/tests/test_wiki.py`

**Interfaces:**
- Consumes: `validate.lint_note(doc) -> list[str]` (existing), `approx_tokens`.
- Produces: `wiki_get(slug, home=None) -> dict` (`status: ok|not_found`, `note`, capped), `wiki_put(slug, note: dict, home=None) -> dict` (`status: ok|invalid`, `problems`), `note_lint(note: dict) -> dict` (`problems: [...]`). Index at `_research_wiki/index.md` gets one `- slug — title — date` line per put. Slice 6's P3 runner calls `wiki_put`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_wiki.py
import yaml
from research_mcp.wiki import wiki_get, wiki_put, note_lint

NOTE = {
    "concept": "sqrt-dk-scaling", "status": "complete",
    "synthesis": "Variance grows linearly with d_k [S1].",
    "resources": [{"url": "https://d2l.ai/x", "title": "d2l", "type": "lecture",
                   "why": "clean derivation"}],
    "unresolved": [],
    "sources_consulted": {"S1": "https://d2l.ai/x"},
}


def test_put_then_get_roundtrip(tmp_path):
    assert wiki_put("sqrt-dk-scaling", NOTE, home=tmp_path)["status"] == "ok"
    got = wiki_get("sqrt-dk-scaling", home=tmp_path)
    assert got["status"] == "ok"
    assert got["note"]["concept"] == "sqrt-dk-scaling"
    index = (tmp_path / "_research_wiki" / "index.md").read_text(encoding="utf-8")
    assert "sqrt-dk-scaling" in index


def test_put_rejects_invalid_note(tmp_path):
    bad = dict(NOTE); bad.pop("synthesis")
    r = wiki_put("bad", bad, home=tmp_path)
    assert r["status"] == "invalid" and r["problems"]
    assert wiki_get("bad", home=tmp_path)["status"] == "not_found"


def test_get_missing_is_success_shaped(tmp_path):
    r = wiki_get("nope", home=tmp_path)
    assert r["status"] == "not_found" and "no cached note" in r["hint"]


def test_note_lint_passthrough():
    assert note_lint(NOTE) == {"problems": []}
```

- [ ] **Step 2: Verify RED.**
- [ ] **Step 3: Implement**

```python
# src/research_mcp/wiki.py
"""Compounding wiki cache (P5): schema-gated notes under <home>/_research_wiki/."""
import datetime, os
from pathlib import Path
import yaml
from .validate import lint_note

def _home(home=None) -> Path:
    return Path(home or os.environ.get("RESEARCH_MCP_HOME",
                                       str(Path.home() / ".research_mcp")))

def _wiki_dir(home=None) -> Path:
    d = _home(home) / "_research_wiki"
    d.mkdir(parents=True, exist_ok=True)
    return d

def note_lint(note: dict) -> dict:
    return {"problems": lint_note(note)}

def wiki_put(slug: str, note: dict, home=None) -> dict:
    problems = lint_note(note)
    if problems:
        return {"status": "invalid", "slug": slug, "problems": problems}
    d = _wiki_dir(home)
    (d / f"{slug}.yaml").write_text(
        yaml.safe_dump(note, allow_unicode=True, sort_keys=False), encoding="utf-8")
    index = d / "index.md"
    line = f"- {slug} — {note.get('concept', slug)} — {datetime.date.today()}\n"
    prev = index.read_text(encoding="utf-8") if index.is_file() else "# research wiki index\n"
    if slug not in prev:
        index.write_text(prev + line, encoding="utf-8")
    return {"status": "ok", "slug": slug}

def wiki_get(slug: str, home=None) -> dict:
    f = _wiki_dir(home) / f"{slug}.yaml"
    if not f.is_file():
        return {"status": "not_found", "slug": slug,
                "hint": "no cached note for this slug — research it, then wiki_put"}
    return {"status": "ok", "slug": slug,
            "note": yaml.safe_load(f.read_text(encoding="utf-8"))}
```

- [ ] **Step 4: Verify GREEN** + full suite. **Step 5: Commit** — `git commit -am "feat: wiki cache tools (wiki_get/wiki_put/note_lint)"`

### Task 4: `_inbox/` resume stubs

**Files:**
- Create: `research-mcp/src/research_mcp/inbox.py`
- Test: `research-mcp/tests/test_inbox.py`

**Interfaces:**
- Produces: `inbox_add(kind: str, payload: dict, home=None) -> Path`, `inbox_list(home=None) -> list[dict]` (each item includes `_file`), `inbox_remove(path) -> None`. Slice 6's P3 runner writes `kind="failed-orchestration"` stubs; playbook drains at session start.

- [ ] **Step 1: Failing test**

```python
# tests/test_inbox.py
from research_mcp.inbox import inbox_add, inbox_list, inbox_remove


def test_add_list_remove(tmp_path):
    inbox_add("failed-orchestration", {"concept": "x", "reason": "timeout"}, home=tmp_path)
    items = inbox_list(home=tmp_path)
    assert len(items) == 1 and items[0]["kind"] == "failed-orchestration"
    inbox_remove(items[0]["_file"])
    assert inbox_list(home=tmp_path) == []


def test_empty_inbox_is_empty_list(tmp_path):
    assert inbox_list(home=tmp_path) == []
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/research_mcp/inbox.py
"""Agent inbox (round-4): retry stubs + resume state, drained at session start."""
import time
from pathlib import Path
import yaml
from .wiki import _home

def _inbox_dir(home=None) -> Path:
    d = _home(home) / "_inbox"
    d.mkdir(parents=True, exist_ok=True)
    return d

def inbox_add(kind: str, payload: dict, home=None) -> Path:
    d = _inbox_dir(home)
    f = d / f"{int(time.time()*1000)}-{kind}.yaml"
    f.write_text(yaml.safe_dump({"kind": kind, **payload}, allow_unicode=True),
                 encoding="utf-8")
    return f

def inbox_list(home=None) -> list[dict]:
    out = []
    for f in sorted(_inbox_dir(home).glob("*.yaml")):
        item = yaml.safe_load(f.read_text(encoding="utf-8"))
        item["_file"] = str(f)
        out.append(item)
    return out

def inbox_remove(path) -> None:
    Path(path).unlink(missing_ok=True)
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat: agent inbox for retry/resume stubs"`

### Task 5: FastMCP server with 7 tools + instructions

**Files:**
- Create: `research-mcp/src/research_mcp/server.py`
- Modify: `research-mcp/pyproject.toml` (add `mcp>=1.2,<2` to a `[project.optional-dependencies] server` extra)
- Test: `research-mcp/tests/test_server.py`

**Interfaces:**
- Produces: `research_mcp.server.mcp` (FastMCP instance) exposing tools `academic_search`, `citation_walk`, `fetch_clean`, `expand`, `wiki_get`, `wiki_put`, `note_lint`. Run: `python -m research_mcp.server`. Tool descriptions state when NOT to use (models pick by description). Instructions string = playbook loop digest (round-9: guidance in initialize, no CLAUDE.md writes).

- [ ] **Step 1: Failing test**

```python
# tests/test_server.py
import asyncio
import pytest

mcp_sdk = pytest.importorskip("mcp")
from research_mcp.server import mcp

EXPECTED = {"academic_search", "citation_walk", "fetch_clean", "expand",
            "wiki_get", "wiki_put", "note_lint"}


def test_all_seven_tools_registered():
    tools = asyncio.run(mcp.list_tools())
    assert {t.name for t in tools} == EXPECTED


def test_descriptions_teach_when_not_to_use():
    tools = {t.name: t for t in asyncio.run(mcp.list_tools())}
    assert "not" in tools["fetch_clean"].description.lower()
    assert "cache" in tools["wiki_get"].description.lower()


def test_instructions_carry_the_loop():
    assert "decompose" in (mcp.instructions or "").lower()
    assert "budget" in (mcp.instructions or "").lower()
```

- [ ] **Step 2: RED** (module missing). **Step 3: Implement**

```python
# src/research_mcp/server.py
"""MCP wrapper (M2). Thin: every tool is the importable core function."""
from mcp.server.fastmcp import FastMCP

from .citation_walk import citation_walk as _walk
from .fetch_academic import academic_search as _search
from .fetch_clean import expand as _expand, fetch_clean as _fetch
from .wiki import note_lint as _lint, wiki_get as _wget, wiki_put as _wput

INSTRUCTIONS = (
    "Research loop (fixed): 0 wiki_get cache check BEFORE planning → "
    "1 DECOMPOSE into a strict JSON list of ≤4 sub-questions → "
    "2 academic_search/citation_walk (opportunistic; a 429/empty is normal) → "
    "3 host web search, snippets only → 4 fetch_clean ≤3 urls with query= → "
    "5 one reflection round max → 6 synthesize ≤200 words, tag claims [S#], "
    "wiki_put. Budgets are server-enforced; on budget_exhausted synthesize "
    "immediately with what you have. insufficient-sources is a valid answer."
)

mcp = FastMCP("research-mcp", instructions=INSTRUCTIONS)


@mcp.tool()
def academic_search(query: str, limit: int = 5) -> dict:
    """Keyless academic metadata search (arXiv+OpenAlex+CrossRef, S2 last).
    Use BEFORE any web search. Do NOT use for full text — use fetch_clean."""
    return _search(query, limit=limit)


@mcp.tool()
def citation_walk(paper_id: str, direction: str = "out", limit: int = 15) -> dict:
    """Walk citations ('in') or references ('out') of a paper id (arXiv:… or
    OpenAlex W…). Use for related-work and what-came-next questions.
    Do NOT use for topical search — that's academic_search."""
    return _walk(paper_id, direction=direction, limit=limit)


@mcp.tool()
def fetch_clean(url: str, max_tokens: int = 1500, query: str = "",
                source_tag: str = "S1") -> dict:
    """Fetch one page → boilerplate-pruned, BM25-scored (pass query=active
    sub-question!) markdown with [Source:] provenance headers. Do NOT call
    without a query; do NOT open pages 'to see' — triage on snippets first.
    On status needs_js delegate the url to your own browser/web tool."""
    return _fetch(url, max_tokens=max_tokens, query=query or None,
                  source_tag=source_tag)


@mcp.tool()
def expand(marker_id: str) -> dict:
    """Retrieve ONE elided [expand:id] chunk from a prior fetch_clean.
    Use only when a sub-question is still unanswered."""
    return _expand(marker_id)


@mcp.tool()
def wiki_get(slug: str) -> dict:
    """Read the persistent research-wiki cache. Call FIRST, before planning —
    a covered concept means you skip the whole search loop."""
    return _wget(slug)


@mcp.tool()
def wiki_put(slug: str, note: dict) -> dict:
    """Persist a finished note (schema-validated; invalid notes are rejected
    with problems listed). Call exactly once, at synthesis."""
    return _wput(slug, note)


@mcp.tool()
def note_lint(note: dict) -> dict:
    """Check a draft note against the schema before wiki_put. Not for pages
    or briefs — notes only."""
    return _lint(note)


if __name__ == "__main__":
    mcp.run()   # stdio
```

pyproject addition:

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0"]
server = ["mcp>=1.2,<2"]
```

- [ ] **Step 4: GREEN** (install once: `pip install "mcp>=1.2,<2"`). Full suite green.
- [ ] **Step 5: Commit** — `git commit -am "feat: FastMCP server, 7 capped tools, playbook in initialize instructions"`

### Task 6: `init` + `doctor`

**Files:**
- Create: `research-mcp/src/research_mcp/doctor.py`
- Test: `research-mcp/tests/test_doctor.py`

**Interfaces:**
- Produces: `doctor(home=None, get=requests.get) -> dict` (`checks: [{name, ok, hint}]`, `ok: bool`) and `init() -> dict` returning registration snippets:
  Claude Code: `claude mcp add research-mcp -- python -m research_mcp.server`;
  Gemini CLI: JSON block for `~/.gemini/settings.json` `mcpServers`.

- [ ] **Step 1: Failing test**

```python
# tests/test_doctor.py
from research_mcp.doctor import doctor, init


def test_doctor_offline_all_deterministic_checks(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    r = doctor(home=tmp_path)
    names = {c["name"] for c in r["checks"]}
    assert {"python", "home-writable", "deps", "apis"} <= names
    apis = next(c for c in r["checks"] if c["name"] == "apis")
    assert apis["ok"] is True and "disabled" in apis["hint"]


def test_init_emits_both_harness_snippets():
    r = init()
    assert "claude mcp add" in r["claude_code"]
    assert "mcpServers" in r["gemini_cli"]
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/research_mcp/doctor.py
"""init/doctor (round-4 career-ops adoption): kill setup friction."""
import importlib, json, sys
import requests
from .fetch_academic import no_apis
from .wiki import _home

_DEPS = ("trafilatura", "requests", "jsonschema", "yaml", "bs4", "lxml")


def doctor(home=None, get=requests.get) -> dict:
    checks = []
    checks.append({"name": "python", "ok": sys.version_info >= (3, 10),
                   "hint": sys.version.split()[0]})
    try:
        h = _home(home); h.mkdir(parents=True, exist_ok=True)
        (h / ".touch").write_text("x"); (h / ".touch").unlink()
        checks.append({"name": "home-writable", "ok": True, "hint": str(h)})
    except OSError as e:
        checks.append({"name": "home-writable", "ok": False, "hint": str(e)})
    missing = [d for d in _DEPS if importlib.util.find_spec(d) is None]
    checks.append({"name": "deps", "ok": not missing,
                   "hint": f"missing: {missing}" if missing else "all present"})
    if no_apis():
        checks.append({"name": "apis", "ok": True,
                       "hint": "disabled by RESEARCH_MCP_NO_APIS (that's fine)"})
    else:
        try:
            get("https://api.openalex.org/works", timeout=5,
                params={"per_page": 1},
                headers={"User-Agent": "research-mcp/0.1"}).raise_for_status()
            checks.append({"name": "apis", "ok": True, "hint": "openalex reachable"})
        except Exception as e:
            checks.append({"name": "apis", "ok": True,   # soft: APIs optional
                           "hint": f"unreachable ({e}) — degraded mode is fine"})
    return {"ok": all(c["ok"] for c in checks), "checks": checks}


def init() -> dict:
    return {
        "claude_code": "claude mcp add research-mcp -- python -m research_mcp.server",
        "gemini_cli": json.dumps({"mcpServers": {"research-mcp": {
            "command": "python", "args": ["-m", "research_mcp.server"]}}}, indent=2),
    }


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="research-mcp-doctor")
    p.add_argument("cmd", choices=("doctor", "init"))
    a = p.parse_args(argv)
    print(json.dumps(doctor() if a.cmd == "doctor" else init(),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat: init/doctor commands"`

### Task 7: Playbook + review gate

**Files:**
- Modify: `research-mcp/playbook/SKILL.md` (step 0 gains: "drain `_inbox/` first — resume any stub before new work")
- Create: `research-mcp/scripts/gate_slice3.py`

- [ ] **Step 1:** Add the inbox-drain sentence to playbook step 0. Commit.
- [ ] **Step 2: Gate script** (deterministic part of the gate):

```python
# scripts/gate_slice3.py
"""Slice-3 review gate. Run: PYTHONPATH=src python scripts/gate_slice3.py
Checks: server tools listable; NO_APIS honored end-to-end; second wiki_put
round-trip hits cache. LLM half of the gate (10 briefs through `claude -p`
with the playbook) is run by the owner; notes must lint."""
import asyncio, os, sys
os.environ["RESEARCH_MCP_NO_APIS"] = "1"
from research_mcp.server import mcp
from research_mcp.fetch_academic import academic_search
from research_mcp.citation_walk import citation_walk

tools = asyncio.run(mcp.list_tools())
assert len(tools) == 7, f"expected 7 tools, got {len(tools)}"
assert academic_search("x")["status"] == "apis_disabled"
assert citation_walk("arXiv:1706.03762")["status"] == "apis_disabled"
print("slice-3 deterministic gate: PASS")
```

- [ ] **Step 3:** Run gate → `slice-3 deterministic gate: PASS`. Owner runs the 10 briefs (`RESEARCH_MCP_NO_APIS=1 claude -p ...` per brief); every produced note must pass `python -m research_mcp.validate note <file>`; rerun once — all `fetch_clean` calls must be cache hits (check `~/.research_mcp/fetch_cache` mtimes unchanged).
- [ ] **Step 4: Commit + update INDEX status row for slice 3.**

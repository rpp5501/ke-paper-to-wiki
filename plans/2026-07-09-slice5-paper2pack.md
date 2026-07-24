# Slice 5 — paper2pack, Fidelity-Laddered Ingestion (M5-P1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `paper2pack`: arXiv id / .tex / PDF → `paper_pack.json` with exact-LaTeX equations when possible and a mandatory provenance block (PLAN §15 fidelity ladder, rungs 1, 2 and 4).

**Architecture:** Deterministic router: rung 1 = arXiv e-print LaTeX (pylatexenc walk — never regex, round-6); rung 2 = ar5iv HTML (LaTeXML); rung 4 = born-digital PDF via pypdf with `equation_extraction: degraded`. Rung 3 (DOCX) and rung 5 (OCR) are follow-ups — the router returns `status: unsupported_input` for them, honestly. Source-upgrading: one OpenAlex call can climb PDF→LaTeX (§15).

**Tech Stack:** Python ≥3.10, `pylatexenc>=2.10`, `selectolax>=0.3`, pypdf (present), requests, existing `Cache`.

## Global Constraints

- New package: `paper-skill/src/paper_skill/` with its own pyproject (mirrors research-mcp layout). Tests: `cd paper-skill && PYTHONPATH=src python -m pytest tests/ -q`.
- Mandatory `extraction` block in every pack: `{"path": "latex|ar5iv|pdf", "equation_fidelity": "exact|converted-mathml|absent"}` (§15 provenance-driven degradation).
- Token hygiene (§15): strip running headers/footers/page numbers on the PDF path; references parsed to a structured list, never raw text.
- `RESEARCH_MCP_NO_APIS=1` disables the arXiv/ar5iv/OpenAlex downloads → `status: apis_disabled` (local .tex/.pdf inputs still work).

---

### Task 1: Package scaffold + pack schema

**Files:**
- Create: `paper-skill/pyproject.toml`, `paper-skill/src/paper_skill/__init__.py`, `paper-skill/src/paper_skill/schemas/paper_pack.schema.json`
- Test: `paper-skill/tests/test_pack_schema.py`

**Interfaces:**
- Produces: `paper_pack.json` contract all later slices consume:

```jsonc
{
  "meta": {"source": "arXiv:1706.03762", "title": "...", "generated": "ISO"},
  "extraction": {"path": "latex", "equation_fidelity": "exact"},
  "sections": [{"id": "sec_3_2_1", "title": "Scaled Dot-Product Attention",
                 "level": 2, "text": "..."}],
  "equations": [{"id": "eq_1", "latex": "...", "section": "sec_3_2_1"}],
  "references": [{"key": "bib1", "text": "Bahdanau et al. ...", "arxiv_id": null}],
  "figures": []
}
```

- [ ] **Step 1: Failing test**

```python
# tests/test_pack_schema.py
import json
from pathlib import Path
import jsonschema

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "src" / "paper_skill" /
                     "schemas" / "paper_pack.schema.json").read_text(encoding="utf-8"))

MINIMAL = {"meta": {"source": "arXiv:1706.03762", "title": "t", "generated": "2026-07-09"},
           "extraction": {"path": "latex", "equation_fidelity": "exact"},
           "sections": [], "equations": [], "references": [], "figures": []}


def test_minimal_pack_validates():
    jsonschema.validate(MINIMAL, SCHEMA)


def test_extraction_block_is_mandatory():
    import pytest
    bad = {k: v for k, v in MINIMAL.items() if k != "extraction"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, SCHEMA)
```

- [ ] **Step 2: RED.** **Step 3: Write the schema**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["meta", "extraction", "sections", "equations", "references"],
  "properties": {
    "meta": {"type": "object", "required": ["source", "title", "generated"]},
    "extraction": {"type": "object",
      "required": ["path", "equation_fidelity"],
      "properties": {
        "path": {"enum": ["latex", "ar5iv", "docx", "pdf", "ocr"]},
        "equation_fidelity": {"enum": ["exact", "converted-mathml",
                                        "converted-omml", "vlm", "ocr", "absent"]}}},
    "sections": {"type": "array", "items": {"type": "object",
      "required": ["id", "title", "level", "text"]}},
    "equations": {"type": "array", "items": {"type": "object",
      "required": ["id", "latex", "section"]}},
    "references": {"type": "array", "items": {"type": "object",
      "required": ["key", "text"]}},
    "figures": {"type": "array"}
  }
}
```

pyproject (paper-skill):

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "paper-skill"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["pylatexenc>=2.10", "selectolax>=0.3", "pypdf>=4.0",
                "requests>=2.31", "jsonschema>=4.21", "pyyaml>=6.0"]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[tool.hatch.build.targets.wheel]
packages = ["src/paper_skill"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): package scaffold + paper_pack schema"`

### Task 2: LaTeX pack builder (rung 1 core)

**Files:**
- Create: `paper-skill/src/paper_skill/latex_pack.py`
- Test: `paper-skill/tests/test_latex_pack.py`

**Interfaces:**
- Produces: `latex_to_pack(main_tex: str, resolve_input=None, source="", title="") -> dict` (a valid pack). `resolve_input(name) -> str` supplies `\input{...}` bodies (tests inject; the fetcher wires the tarball). Section ids: `sec_` + number path (`sec_3_2_1`); equation ids `eq_1..` in document order, latex verbatim.

- [ ] **Step 1: Failing test**

```python
# tests/test_latex_pack.py
from paper_skill.latex_pack import latex_to_pack

TEX = r"""
\section{Model Architecture}
Intro text here.
\subsection{Attention}
An attention function.
\begin{equation}
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
\end{equation}
\input{extra}
"""


def test_sections_form_numbered_tree():
    pack = latex_to_pack(TEX, resolve_input=lambda n: r"\section{Extra}Tail.")
    ids = [s["id"] for s in pack["sections"]]
    assert ids == ["sec_1", "sec_1_1", "sec_2"]
    assert pack["sections"][1]["title"] == "Attention"
    assert pack["sections"][1]["level"] == 2


def test_equation_latex_is_verbatim_and_anchored():
    pack = latex_to_pack(TEX, resolve_input=lambda n: "")
    eq = pack["equations"][0]
    assert eq["id"] == "eq_1"
    assert r"\sqrt{d_k}" in eq["latex"]
    assert eq["section"] == "sec_1_1"


def test_extraction_block_says_exact():
    pack = latex_to_pack(TEX, resolve_input=lambda n: "")
    assert pack["extraction"] == {"path": "latex", "equation_fidelity": "exact"}
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/latex_pack.py
"""Rung-1 pack builder: pylatexenc walk (never regex over TeX, round-6)."""
import datetime
import re
from pylatexenc.latexwalker import (LatexWalker, LatexEnvironmentNode,
                                    LatexMacroNode, LatexCharsNode,
                                    LatexGroupNode)

_SECTION_MACROS = {"section": 1, "subsection": 2, "subsubsection": 3}
_EQ_ENVS = {"equation", "equation*", "align", "align*", "eqnarray", "displaymath"}


def _flatten_inputs(tex: str, resolve_input, depth=0) -> str:
    if resolve_input is None or depth > 5:
        return tex
    def sub(m):
        return _flatten_inputs(resolve_input(m.group(1)) or "", resolve_input, depth + 1)
    return re.sub(r"\\input\{([^}]+)\}", sub, tex)


def _strip_comments(tex: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", tex)


def _group_text(node) -> str:
    if isinstance(node, LatexGroupNode):
        return "".join(_group_text(n) for n in node.nodelist)
    if isinstance(node, LatexCharsNode):
        return node.chars
    return ""


def latex_to_pack(main_tex: str, resolve_input=None, source: str = "",
                  title: str = "") -> dict:
    tex = _strip_comments(_flatten_inputs(main_tex, resolve_input))
    nodes, _, _ = LatexWalker(tex).get_latex_nodes()
    sections, equations = [], []
    counters = [0, 0, 0]
    cur_id, buf = None, []

    def flush():
        if cur_id is not None and sections:
            sections[-1]["text"] = " ".join("".join(buf).split())
        buf.clear()

    def walk(nodelist):
        nonlocal cur_id
        for n in nodelist or []:
            if isinstance(n, LatexMacroNode) and n.macroname in _SECTION_MACROS:
                flush()
                lvl = _SECTION_MACROS[n.macroname]
                counters[lvl - 1] += 1
                for i in range(lvl, 3):
                    counters[i] = 0
                cur_id = "sec_" + "_".join(str(c) for c in counters[:lvl])
                stitle = ""
                if n.nodeargd and n.nodeargd.argnlist:
                    stitle = _group_text(n.nodeargd.argnlist[-1]).strip()
                sections.append({"id": cur_id, "title": stitle,
                                 "level": lvl, "text": ""})
            elif isinstance(n, LatexEnvironmentNode) and n.environmentname in _EQ_ENVS:
                latex = tex[n.nodelist[0].pos:n.nodelist[-1].pos
                            + n.nodelist[-1].len] if n.nodelist else ""
                equations.append({"id": f"eq_{len(equations) + 1}",
                                  "latex": latex.strip(),
                                  "section": cur_id or "sec_0"})
            elif isinstance(n, LatexCharsNode):
                buf.append(n.chars)
            elif isinstance(n, (LatexEnvironmentNode, LatexGroupNode)):
                walk(n.nodelist)

    walk(nodes)
    flush()
    return {"meta": {"source": source, "title": title,
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "latex", "equation_fidelity": "exact"},
            "sections": sections, "equations": equations,
            "references": [], "figures": []}
```

- [ ] **Step 4: GREEN** (if pylatexenc's node offsets differ for the env-body slice, take `tex[n.pos:n.pos+n.len]` and cut the `\begin{...}`/`\end{...}` wrappers by string index — assert the test's `\sqrt{d_k}` still verbatim). Full suite.
- [ ] **Step 5: Commit** — `git commit -am "feat(paper-skill): rung-1 LaTeX pack builder (pylatexenc walk)"`

### Task 3: `.bbl` references parser

**Files:**
- Create: `paper-skill/src/paper_skill/references.py`
- Test: `paper-skill/tests/test_references.py`

**Interfaces:**
- Produces: `parse_bbl(bbl_text: str) -> list[dict]` — `[{key, text, arxiv_id|None}]`; wired into pack["references"] by the router.

- [ ] **Step 1: Failing test**

```python
# tests/test_references.py
from paper_skill.references import parse_bbl

BBL = r"""
\begin{thebibliography}{10}
\bibitem{bahdanau2014} Dzmitry Bahdanau, et al. Neural machine translation.
arXiv:1409.0473, 2014.
\bibitem{he2016} Kaiming He, et al. Deep residual learning. CVPR 2016.
\end{thebibliography}
"""


def test_two_items_with_keys_and_arxiv_id():
    refs = parse_bbl(BBL)
    assert len(refs) == 2
    assert refs[0]["key"] == "bahdanau2014"
    assert refs[0]["arxiv_id"] == "1409.0473"
    assert refs[1]["arxiv_id"] is None
    assert "residual" in refs[1]["text"]
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/references.py
"""Structured .bbl parse (§15 token hygiene: never haul raw citation text)."""
import re

_ARXIV = re.compile(r"arXiv[:\s]*(\d{4}\.\d{4,5})", re.I)


def parse_bbl(bbl_text: str) -> list[dict]:
    refs = []
    for m in re.finditer(r"\\bibitem\{([^}]+)\}(.*?)(?=\\bibitem\{|\\end\{thebibliography\})",
                         bbl_text, re.S):
        text = " ".join(m.group(2).split())
        ax = _ARXIV.search(text)
        refs.append({"key": m.group(1), "text": text,
                     "arxiv_id": ax.group(1) if ax else None})
    return refs
```

- [ ] **Step 4: GREEN.** **Step 5: Commit** — `git commit -am "feat(paper-skill): bbl references parser"`

### Task 4: Fetcher + router + PDF rung + ar5iv rung

**Files:**
- Create: `paper-skill/src/paper_skill/paper2pack.py`
- Test: `paper-skill/tests/test_router.py`

**Interfaces:**
- Produces: `build_pack(target: str, get=requests.get, cache_dir=None) -> dict` and CLI `python -m paper_skill.paper2pack <arxiv-id|file.tex|file.pdf> -o pack.json`. Detection is deterministic (§15): arXiv-id regex → rung 1 (e-print tarball, main .tex = the one containing `\documentclass`; `.bbl` alongside feeds references); `.tex` file → rung 1 local; `.pdf` → rung 4 (pypdf text, de-hyphenated, running headers stripped, `equation_fidelity: absent`); ar5iv rung 2 used when the e-print download fails but `https://ar5iv.labs.arxiv.org/html/<id>` succeeds — selectolax pulls `<h2>/<h3>` sections and `<math alttext=...>` as `converted-mathml` equations.

- [ ] **Step 1: Failing test**

```python
# tests/test_router.py
import io, tarfile
from paper_skill.paper2pack import build_pack, detect

class Resp:
    def __init__(self, content): self.content = content
    def raise_for_status(self): pass


def _tarball():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        tex = (r"\documentclass{article}\begin{document}\section{Intro}"
               r"\begin{equation}E=mc^2\end{equation}\end{document}").encode()
        info = tarfile.TarInfo("main.tex"); info.size = len(tex)
        t.addfile(info, io.BytesIO(tex))
        bbl = (r"\begin{thebibliography}{1}\bibitem{x} Y. arXiv:1409.0473."
               r"\end{thebibliography}").encode()
        info2 = tarfile.TarInfo("main.bbl"); info2.size = len(bbl)
        t.addfile(info2, io.BytesIO(bbl))
    return buf.getvalue()


def test_detect_is_deterministic(tmp_path):
    assert detect("1706.03762") == "arxiv"
    assert detect("arXiv:1706.03762") == "arxiv"
    p = tmp_path / "x.tex"; p.write_text("x")
    assert detect(str(p)) == "tex"
    q = tmp_path / "x.pdf"; q.write_bytes(b"%PDF-1.4")
    assert detect(str(q)) == "pdf"


def test_arxiv_rung1_builds_exact_pack(tmp_path):
    pack = build_pack("1706.03762", get=lambda url, timeout, headers: Resp(_tarball()),
                      cache_dir=tmp_path)
    assert pack["extraction"]["path"] == "latex"
    assert pack["equations"][0]["latex"] == "E=mc^2"
    assert pack["references"][0]["arxiv_id"] == "1409.0473"


def test_no_apis_blocks_download_not_local(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    pack = build_pack("1706.03762", get=None, cache_dir=tmp_path)
    assert pack["status"] == "apis_disabled"
    tex = tmp_path / "local.tex"
    tex.write_text(r"\section{A}\begin{equation}x=1\end{equation}")
    local = build_pack(str(tex), get=None, cache_dir=tmp_path)
    assert local["extraction"]["equation_fidelity"] == "exact"
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/paper2pack.py
"""Fidelity-laddered router (§15). Rungs implemented: 1 latex, 2 ar5iv, 4 pdf."""
import argparse, io, json, os, re, sys, tarfile
from pathlib import Path
import requests
from .latex_pack import latex_to_pack
from .references import parse_bbl

UA = {"User-Agent": "paper-skill/0.1 (keyless research tool)"}
_ARXIV_ID = re.compile(r"^(arXiv:)?(\d{4}\.\d{4,5})(v\d+)?$")


def _no_apis() -> bool:
    return os.environ.get("RESEARCH_MCP_NO_APIS", "") == "1"


def detect(target: str) -> str:
    if _ARXIV_ID.match(target.strip()):
        return "arxiv"
    p = Path(target)
    if p.suffix == ".tex":
        return "tex"
    if p.suffix == ".pdf":
        return "pdf"
    return "unknown"


def _pack_from_tarball(blob: bytes, source: str) -> dict:
    tf = tarfile.open(fileobj=io.BytesIO(blob), mode="r:*")
    files = {m.name: tf.extractfile(m).read().decode("utf-8", "replace")
             for m in tf.getmembers() if m.isfile()}
    main = next((t for t in files.values() if "\\documentclass" in t),
                next(iter(files.values()), ""))
    def resolve(name):
        return files.get(name) or files.get(name + ".tex") or ""
    pack = latex_to_pack(main, resolve_input=resolve, source=source)
    bbl = next((t for n, t in files.items() if n.endswith(".bbl")), "")
    if bbl:
        pack["references"] = parse_bbl(bbl)
    return pack


def _pack_from_ar5iv(html: bytes, source: str) -> dict:
    import datetime
    from selectolax.parser import HTMLParser
    doc = HTMLParser(html)
    sections, equations = [], []
    for i, h in enumerate(doc.css("h2, h3"), 1):
        sections.append({"id": f"sec_{i}", "title": h.text(strip=True),
                         "level": 2 if h.tag == "h2" else 3, "text": ""})
    for i, m in enumerate(doc.css("math[alttext]"), 1):
        equations.append({"id": f"eq_{i}", "latex": m.attributes["alttext"],
                          "section": sections[-1]["id"] if sections else "sec_0"})
    return {"meta": {"source": source, "title": doc.css_first("title").text()
                     if doc.css_first("title") else "",
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "ar5iv", "equation_fidelity": "converted-mathml"},
            "sections": sections, "equations": equations,
            "references": [], "figures": []}


def _pack_from_pdf(path: str, source: str) -> dict:
    import datetime
    from pypdf import PdfReader
    pages = [p.extract_text() or "" for p in PdfReader(path).pages]
    body = "\n".join(pages)
    body = re.sub(r"-\n(?=[a-z])", "", body)             # de-hyphenate
    body = re.sub(r"^\s*\d+\s*$", "", body, flags=re.M)  # bare page numbers
    return {"meta": {"source": source, "title": Path(path).stem,
                     "generated": datetime.date.today().isoformat()},
            "extraction": {"path": "pdf", "equation_fidelity": "absent"},
            "sections": [{"id": "sec_1", "title": "full-text", "level": 1,
                          "text": " ".join(body.split())}],
            "equations": [], "references": [], "figures": []}


def build_pack(target: str, get=requests.get, cache_dir=None) -> dict:
    kind = detect(target)
    if kind == "tex":
        return latex_to_pack(Path(target).read_text(encoding="utf-8"),
                             source=f"file:{target}")
    if kind == "pdf":
        return _pack_from_pdf(target, source=f"file:{target}")
    if kind == "arxiv":
        if _no_apis():
            return {"status": "apis_disabled",
                    "hint": "arXiv download blocked by RESEARCH_MCP_NO_APIS — "
                            "pass a local .tex or .pdf instead"}
        arxiv_id = _ARXIV_ID.match(target.strip()).group(2)
        source = f"arXiv:{arxiv_id}"
        try:
            blob = get(f"https://arxiv.org/e-print/{arxiv_id}",
                       timeout=60, headers=UA).content
            return _pack_from_tarball(blob, source)
        except Exception:
            html = get(f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}",
                       timeout=60, headers=UA).content
            return _pack_from_ar5iv(html, source)
    return {"status": "unsupported_input",
            "hint": f"cannot route '{target}' — supported: arXiv id, .tex, .pdf "
                    "(docx/ocr rungs are backlog)"}


def main(argv=None):
    p = argparse.ArgumentParser(prog="paper2pack")
    p.add_argument("target")
    p.add_argument("-o", "--output", default="paper_pack.json")
    a = p.parse_args(argv)
    pack = build_pack(a.target)
    Path(a.output).write_text(json.dumps(pack, ensure_ascii=False, indent=1),
                              encoding="utf-8")
    print(f"{a.output}: path={pack.get('extraction', {}).get('path', pack.get('status'))}")
    return 0 if "status" not in pack else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat(paper-skill): paper2pack router (rungs 1/2/4, provenance block)"`

### Task 5: Source upgrading (PDF/DOI → arXiv sibling)

**Files:**
- Create: `paper-skill/src/paper_skill/upgrade.py`
- Test: `paper-skill/tests/test_upgrade.py`

**Interfaces:**
- Produces: `find_arxiv_sibling(title: str, get=requests.get) -> str | None` (OpenAlex title search → `ids.arxiv` / locations with arxiv.org URL). Router callers try it before settling for rung 4.

- [ ] **Step 1: Failing test**

```python
# tests/test_upgrade.py
from paper_skill.upgrade import find_arxiv_sibling

class Resp:
    def __init__(self, p): self._p = p
    def raise_for_status(self): pass
    def json(self): return self._p


def test_finds_arxiv_id_from_openalex():
    payload = {"results": [{"ids": {"arxiv": "https://arxiv.org/abs/1706.03762"}}]}
    ax = find_arxiv_sibling("Attention Is All You Need",
                            get=lambda *a, **k: Resp(payload))
    assert ax == "1706.03762"


def test_no_match_returns_none():
    assert find_arxiv_sibling("x", get=lambda *a, **k: Resp({"results": []})) is None


def test_no_apis_returns_none(monkeypatch):
    monkeypatch.setenv("RESEARCH_MCP_NO_APIS", "1")
    assert find_arxiv_sibling("x") is None
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/upgrade.py
"""Source upgrading (§15): one free OpenAlex call climbs rung 4 -> rung 1."""
import re
import requests
from .paper2pack import UA, _no_apis


def find_arxiv_sibling(title: str, get=requests.get) -> str | None:
    if _no_apis():
        return None
    try:
        data = get("https://api.openalex.org/works", timeout=20, headers=UA,
                   params={"search": title, "per_page": 1,
                           "select": "ids"}).json()
        ids = (data.get("results") or [{}])[0].get("ids") or {}
        m = re.search(r"(\d{4}\.\d{4,5})", ids.get("arxiv") or "")
        return m.group(1) if m else None
    except Exception:
        return None
```

- [ ] **Step 4: GREEN + suite.** **Step 5: Commit** — `git commit -am "feat(paper-skill): OpenAlex source upgrading"`

### Review gate (slice 5)

- [ ] `python -m paper_skill.paper2pack 1706.03762 -o /tmp/aiayn_pack.json` (network on) →
  `extraction.path == "latex"`, `equation_fidelity == "exact"`; grep the pack for `\sqrt{d_k` — present verbatim; a section titled "Scaled Dot-Product Attention" exists; `references` list non-empty with ≥5 `arxiv_id`s.
- [ ] Same command with `RESEARCH_MCP_NO_APIS=1` → clean `apis_disabled` message, exit 1.
- [ ] All paper-skill tests green. Update INDEX. Commit.

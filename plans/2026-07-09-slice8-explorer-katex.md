# Slice 8 — Explorer Integration + KaTeX (M5-P6, closes M4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge pack + concept graph + pages into the offline Cytoscape explorer with tiered accordion panels; render The-Math LaTeX via inlined KaTeX. Output: ONE self-contained HTML file per paper.

**Architecture:** Extend the fork's `exporters/explorer.py` (our module — extending it is not upstream drift) with an optional `pages` payload: per-node pre-rendered HTML per tier. KaTeX (js+css) vendored via npm-pack like cytoscape, inlined only when any node has math. **Fonts (owner refinement):** the two core faces — `KaTeX_Main-Regular.woff2` and `KaTeX_Math-Italic.woff2` (~30KB each) — are base64-embedded as `data:` URIs directly in the CSS, and every other `url(fonts/...)` reference is stripped from the inlined css (a dangling relative url would silently 404 offline). Single-file rule holds AND √dₖ renders with real KaTeX glyphs.

**Tech Stack:** Python ≥3.10, `markdown>=3.5` (md→html), npm (`npm pack katex`), existing exporter + adapter.

## Global Constraints

- Output must stay single-file and zero-network (extend the existing offline test).
- `ensure_ascii=False` everywhere; `</script>` guard via existing `_embed_json`.
- Fork tests: `cd "Forked repos/graphify" && PYTHONPATH=. python -m pytest tests/ -q` (adapter + explorer + new).

---

### Task 1: Vendor KaTeX

**Files:**
- Create: `Forked repos/graphify/graphify/exporters/vendor/katex.min.js`, `.../vendor/katex.min.css`

- [ ] **Step 1:** `cd /tmp && npm pack katex && tar xzf katex-*.tgz` → copy `package/dist/katex.min.js` and `package/dist/katex.min.css` into `Forked repos/graphify/graphify/exporters/vendor/`, plus `package/dist/fonts/KaTeX_Main-Regular.woff2` and `package/dist/fonts/KaTeX_Math-Italic.woff2`.
- [ ] **Step 2:** Verify: all four files exist; `grep -c "KaTeX" vendor/katex.min.js` ≥ 1; js ~250–300KB, css ~20–30KB, each woff2 ≤ 40KB.
- [ ] **Step 3: Commit** — `git commit -am "chore(fork): vendor katex js+css+core woff2 fonts (offline math tier)"`

### Task 2: Pages payload + accordion + KaTeX hook in the exporter

**Files:**
- Modify: `Forked repos/graphify/graphify/exporters/explorer.py`
- Test: `Forked repos/graphify/tests/test_explorer_pages.py`

**Interfaces:**
- Produces: `to_explorer_html(plan_graph, title=None, cytoscape_js=None, pages=None, katex=None)` — `pages: dict[node_id, dict[tier_anchor, html]]` where tier anchors are `tldr|intuition|mechanics|the-math|go-deeper`. When `pages` is truthy: panel shows an accordion (`<details>` per tier) instead of the plain detail block, and KaTeX js+css are inlined (auto-loaded from vendor when `katex=None`). Math delimiters in page HTML: `\(...\)` inline and `$$...$$` display; a small script calls `katex.render` on `.math` spans after panel open. Backwards compatible: `pages=None` → current behavior byte-identical.

- [ ] **Step 1: Failing test**

```python
# tests/test_explorer_pages.py
import json
from pathlib import Path
import pytest
from graphify.exporters.explorer import to_explorer_html

FIXTURE = json.loads((Path(__file__).resolve().parents[3] / "paper-skill" /
                      "fixtures" / "aiayn_concept_graph.json").read_text(encoding="utf-8"))
PAGES = {"scaled-dot-product-attention": {
    "tldr": "<p>Scaling keeps softmax sane.</p>",
    "intuition": "<p>Bigger d_k, bigger dots.</p>",
    "mechanics": "<p>Divide by sqrt(d_k).</p>",
    "the-math": '<p><span class="math">\\sqrt{d_k}</span></p>',
    "go-deeper": "<ul><li>d2l</li></ul>"}}


def test_pages_payload_embedded_with_accordion():
    html = to_explorer_html(FIXTURE, pages=PAGES)
    assert "PAGES" in html and "<details" in html
    assert "Scaling keeps softmax sane." in html


def test_katex_inlined_only_with_pages():
    with_pages = to_explorer_html(FIXTURE, pages=PAGES)
    without = to_explorer_html(FIXTURE)
    assert "KaTeX" in with_pages
    assert "KaTeX" not in without


def test_still_offline_with_pages():
    html = to_explorer_html(FIXTURE, pages=PAGES)
    assert "unpkg.com" not in html and 'src="http' not in html
    assert "<link" not in html                       # css inlined in <style>


def test_backwards_compatible_without_pages():
    html = to_explorer_html(FIXTURE)
    assert "collapseSubtree" in html and "READING_PATH" in html
```

- [ ] **Step 2: RED** (new kwargs unknown).
- [ ] **Step 3: Implement.** In `explorer.py`:

1. Add module constant `_VENDOR_KATEX_JS = _VENDOR_JS.parent / "katex.min.js"`, `_VENDOR_KATEX_CSS = _VENDOR_JS.parent / "katex.min.css"`.
2. Extend signature: `def to_explorer_html(plan_graph, title=None, cytoscape_js=None, pages=None, katex=None):` — build `pages_json = _embed_json(pages or {})`; when `pages`: `katex_js = (katex or {}).get("js") or _VENDOR_KATEX_JS.read_text(encoding="utf-8")`, same for css; else empty strings.
   The css is passed through `_inline_fonts(css)` (new module function): base64-embed `KaTeX_Main-Regular.woff2` + `KaTeX_Math-Italic.woff2` from vendor as `data:font/woff2;base64,...` URIs replacing their `url(fonts/KaTeX_Main-Regular.woff2)` / `url(fonts/KaTeX_Math-Italic.woff2)` refs (match any `format(...)` suffix), then strip every remaining `src:` alternative that still references `url(fonts/` so no dangling relative fetch survives. Add two test assertions to Task 2's test: `"data:font/woff2;base64," in with_pages` and `"url(fonts/" not in with_pages`.
3. Template replacements gain: `__PAGES_JSON__`, `__KATEX_JS__`, `__KATEX_CSS__` (css injected inside the existing `<style>` block; js in its own `<script>` before the main script, both empty-string when no pages).
4. In the template's `<script>`, add after `showDetail` definition:

```javascript
const PAGES = __PAGES_JSON__;
const TIER_ORDER = ["tldr", "intuition", "mechanics", "the-math", "go-deeper"];
const TIER_LABEL = {"tldr": "TL;DR", "intuition": "Intuition",
                    "mechanics": "Mechanics", "the-math": "The Math",
                    "go-deeper": "Go Deeper"};

function renderTiers(id) {
  const tiers = PAGES[id];
  if (!tiers) return "";
  let html = "";
  TIER_ORDER.forEach(t => {
    if (tiers[t]) html += `<details ${t === "tldr" ? "open" : ""}>` +
      `<summary>${TIER_LABEL[t]}</summary><div class="tier">${tiers[t]}</div></details>`;
  });
  return html;
}

function typeset(container) {
  if (typeof katex === "undefined") return;
  container.querySelectorAll(".math").forEach(el => {
    try { katex.render(el.textContent, el, {throwOnError: false}); }
    catch (e) { /* leave source text visible */ }
  });
}
```

5. Change `showDetail` to append `renderTiers(id)` to the detail HTML and call `typeset(document.getElementById("detail"))` at the end.
6. Keep the `__CYTOSCAPE_JS__` replace LAST; do `__KATEX_JS__` second-to-last (both are large).

- [ ] **Step 4: GREEN (4 new + 10 existing explorer tests).**
- [ ] **Step 5: Commit** — `git commit -am "feat(fork): tiered accordion pages + inlined KaTeX in explorer"`

### Task 3: `build_explorer` pipeline script (P6)

**Files:**
- Create: `paper-skill/src/paper_skill/p6_explorer.py`
- Test: `paper-skill/tests/test_p6_explorer.py`

**Interfaces:**
- Consumes: pack, concept graph, pages dir (slice-7 output).
- Produces: `build_explorer(pack, graph, pages_dir, out_path) -> dict` — parses each page md, splits on the five `## X {#anchor}` headings, converts each tier to HTML via `markdown.markdown`, converts `$$...$$`/`\(...\)` spans to `<span class="math">`, back-fills `page`/`anchor` onto graph nodes, calls the fork exporter with `pages=`. CLI: `python -m paper_skill.p6_explorer pack.json concept_graph.json pages/ -o explorer.html`.

- [ ] **Step 1: Failing test**

```python
# tests/test_p6_explorer.py
import json
from pathlib import Path
from paper_skill.p6_explorer import split_tiers, build_explorer

PAGE = """# SDPA
## TL;DR {#tldr}
Short.
## Intuition {#intuition}
Feel.
## Mechanics {#mechanics}
Divide [eq_1].
## The Math {#the-math}
$$\\sqrt{d_k}$$
## Go Deeper {#go-deeper}
- link
"""


def test_split_tiers_five_keys():
    tiers = split_tiers(PAGE)
    assert set(tiers) == {"tldr", "intuition", "mechanics", "the-math", "go-deeper"}
    assert "Short." in tiers["tldr"]


def test_math_becomes_math_span():
    tiers = split_tiers(PAGE)
    assert '<span class="math">' in tiers["the-math"]
    assert "\\sqrt{d_k}" in tiers["the-math"]


def test_build_explorer_end_to_end(tmp_path):
    graph = json.loads((Path(__file__).resolve().parents[2] / "fixtures" /
                        "aiayn_concept_graph.json").read_text(encoding="utf-8"))
    pages = tmp_path / "pages"; pages.mkdir()
    (pages / "01_scaled-dot-product-attention.md").write_text(PAGE, encoding="utf-8")
    pack = {"meta": {"source": "arXiv:1706.03762", "title": "AIAYN",
                     "generated": "x"}, "extraction": {}, "sections": [],
            "equations": [], "references": [], "figures": []}
    out = tmp_path / "explorer.html"
    r = build_explorer(pack, graph, pages, out)
    assert r["status"] == "ok"
    html = out.read_text(encoding="utf-8")
    assert "\\sqrt{d_k}" in html and "KaTeX" in html
    assert "unpkg.com" not in html
```

- [ ] **Step 2: RED.** **Step 3: Implement**

```python
# src/paper_skill/p6_explorer.py
"""P6: pack + graph + pages -> one offline explorer.html via the fork exporter."""
import argparse, json, re, sys
from pathlib import Path
import markdown

sys.path.insert(0, str(Path(__file__).resolve().parents[3]
                       / "Forked repos" / "graphify"))

_TIER_RE = re.compile(r"^## .+?\{#([\w-]+)\}\s*$", re.M)
_DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
_INLINE = re.compile(r"\\\((.+?)\\\)", re.S)


def _mathify(md_text: str) -> str:
    md_text = _DISPLAY.sub(lambda m: f'<span class="math">{m.group(1).strip()}</span>',
                           md_text)
    return _INLINE.sub(lambda m: f'<span class="math">{m.group(1).strip()}</span>',
                       md_text)


def split_tiers(page_md: str) -> dict:
    marks = list(_TIER_RE.finditer(page_md))
    tiers = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(page_md)
        body = page_md[m.end():end].strip()
        tiers[m.group(1)] = markdown.markdown(_mathify(body))
    return tiers


def build_explorer(pack: dict, graph: dict, pages_dir, out_path) -> dict:
    from graphify.exporters.explorer import to_explorer_html
    pages = {}
    for f in sorted(Path(pages_dir).glob("*.md")):
        cid = f.stem.split("_", 1)[1] if "_" in f.stem else f.stem
        pages[cid] = split_tiers(f.read_text(encoding="utf-8"))
    for n in graph["nodes"]:
        if n["id"] in pages:
            n["page"] = f'{n["id"]}.md'
            n.setdefault("anchor", "#tldr")
    html = to_explorer_html(graph, title=pack["meta"]["title"], pages=pages)
    Path(out_path).write_text(html, encoding="utf-8")
    return {"status": "ok", "pages": len(pages), "bytes": len(html)}


def main(argv=None):
    p = argparse.ArgumentParser(prog="p6_explorer")
    p.add_argument("pack"); p.add_argument("graph"); p.add_argument("pages")
    p.add_argument("-o", "--output", default="explorer.html")
    a = p.parse_args(argv)
    r = build_explorer(json.loads(Path(a.pack).read_text(encoding="utf-8")),
                       json.loads(Path(a.graph).read_text(encoding="utf-8")),
                       a.pages, a.output)
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: GREEN + all suites.** **Step 5: Commit** — `git commit -am "feat(paper-skill): P6 explorer builder"`

### Review gate (slice 8) — THE M5 acceptance demo

- [ ] `python -m paper_skill.p6_explorer aiayn_pack.json concept_graph.json pages/ -o aiayn_full_explorer.html` (live artifacts from slices 5–7).
- [ ] Open with network disabled: click Transformer → Attention → Scaled Dot-Product Attention; The-Math tier renders the attention equation via KaTeX; Go Deeper shows Illustrated Transformer + Annotated Transformer with whys; reading path clickable; zero console network errors.
- [ ] `grep -c unpkg aiayn_full_explorer.html` → 0.
- [ ] Update INDEX (M4 + M5 close). Commit.

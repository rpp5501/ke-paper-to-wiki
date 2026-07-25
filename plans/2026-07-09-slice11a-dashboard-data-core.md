# Slice 11a — Dashboard Data Layer + Core Logic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Vite+React scaffold for an internet-disconnected localhost app, the `build_data.py` bundler (fixture → `data.gen.ts`), fully vitest-covered pure logic (insights, blast radius, LOD), and worker-backed ELK layout — everything Slice 11b's UI consumes.

**Architecture:** Per the approved design doc (`2026-07-09-slice11-dashboard-design.md`). Data remains bundled at build time into `src/data.gen.ts`; the localhost pivot does not add runtime data fetching. elkjs topology calculation runs in a Vite-bundled Web Worker so large graphs cannot block the interaction thread. All non-layout graph math remains pure TS, testable without DOM.

**Tech Stack:** Vite 5+, React 19, TypeScript, `@xyflow/react@^12` (NOT legacy `reactflow`), zustand, elkjs, katex, react-markdown+remark-gfm, prism-react-renderer, vitest; Python ≥3.10 + networkx + pytest for the bundler.

## Global Constraints

- **Offline means internet-disconnected:** no external CDNs, telemetry, external APIs, remote fonts, or remote assets. Runtime execution is over `http://localhost`; localhost asset requests are allowed.
- Standard Vite asset handling is used. Do not require `base: './'`; relative and root-absolute local asset paths such as `url(/assets/...)` are valid when served from localhost.
- elkjs layout must execute in a Web Worker. Do not replace it with synchronous main-thread layout in production.
- `@xyflow/react` v12 import paths; never `reactflow`.
- Unicode raw everywhere (`ensure_ascii=False`; assert `√dₖ` survives to dist).
- Markdown images stripped at bundle time (logged count); code excerpts only for (top-20 hotspots ∪ implements-edge nodes), ≤80 lines.
- Edge dependent-side map (single source of truth, both languages): `part-of→dst, prerequisite→dst, builds-on→src`, default `src`.
- Run JS tests: `cd dashboard && npm test` (vitest run). Python: `cd dashboard && python -m pytest tests/ -q`.
- Run development: `cd dashboard && npm run dev`. Run the production build locally: `cd dashboard && npm run build`, then `python -m http.server -d dist 8000`; open `http://localhost:8000/`.
- Commit after every task; OneDrive caveat applies (canonical = file-tool view).

---

### Task 1: Scaffold + localhost execution

**Files:**
- Create: `dashboard/package.json`, `dashboard/vite.config.ts`, `dashboard/vitest.config.ts`, `dashboard/tsconfig.json`, `dashboard/index.html`, `dashboard/src/main.tsx`, `dashboard/src/App.tsx` (placeholder), `dashboard/src/styles.css` (empty ok), `dashboard/.gitignore`

**Interfaces:**
- Produces: `npm run dev` → Vite localhost development server; `npm run build` → `dist/`; `python -m http.server -d dist 8000` → production build at `http://localhost:8000/`. 11b replaces App.tsx.

- [ ] **Step 1:** Scaffold by hand (no `npm create` wizard — deterministic files):

`dashboard/package.json`:
```json
{
  "name": "knowledge-dashboard",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "test": "vitest run"
  },
  "dependencies": {
    "@xyflow/react": "^12.0.0",
    "elkjs": "^0.9.3",
    "katex": "^0.16.0",
    "prism-react-renderer": "^2.4.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-markdown": "^10.0.0",
    "remark-gfm": "^4.0.0",
    "zustand": "^5.0.0"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "vitest": "^2.0.0"
  }
}
```

`dashboard/vite.config.ts`:
```ts
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  build: { chunkSizeWarningLimit: 1500 },
});
```

`dashboard/vitest.config.ts`:
```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: { include: ["src/**/*.test.ts"], environment: "node" },
});
```

`dashboard/tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true,
    "types": ["vite/client"]
  },
  "include": ["src"]
}
```

`dashboard/index.html`:
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Knowledge Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="./src/main.tsx"></script>
  </body>
</html>
```

`dashboard/src/main.tsx`:
```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

`dashboard/src/App.tsx` (placeholder, replaced in 11b Task 1):
```tsx
export default function App() {
  return <div>knowledge dashboard — scaffold ok</div>;
}
```

`dashboard/.gitignore`:
```
node_modules/
dist/
src/data.gen.ts
```

- [ ] **Step 2:** `cd dashboard && npm install && npm run build` → `dist/` produced (tsc + Vite succeed). Confirm the generated HTML references only local build assets; root-absolute localhost paths are allowed.
- [ ] **Step 3:** Run `npm run dev`, open the printed localhost URL, and confirm the scaffold renders with browser networking disabled. Requests to the Vite localhost origin are expected; requests to non-local origins are forbidden.
- [ ] **Step 4:** Stop the development server, run `python -m http.server -d dist 8000`, open `http://localhost:8000/`, and confirm the production scaffold renders without external requests.
- [ ] **Step 5: Commit** — `git add dashboard && git commit -m "feat(dashboard): vite scaffold + localhost runtime"`

### Task 2: `build_data.py` bundler (pytest, TDD)

**Files:**
- Create: `dashboard/build_data.py`, `dashboard/tests/test_build_data.py`, `dashboard/tests/__init__.py` (empty)
- Create (generated, committed as dev fixture): `dashboard/src/data.gen.ts`

**Interfaces:**
- Produces: CLI `python build_data.py --graph G.json [--pack P.json] [--pages-dir D] [--wiki-dir W] [--hotspots H.json] [--repo-dir R] --out src/data.gen.ts` and importable `build_bundle(...) -> dict`. Bundle keys (design §4): `meta, nodes, edges, pages, notes, hotspots, clusters, tour, provenance, centrality, eqIndex, trace, glossary`. 11b imports `KE_DATA` from `./data.gen`.

- [ ] **Step 1: Write the failing tests**

`dashboard/tests/test_build_data.py`:
```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_data import (build_bundle, reading_path, strip_images,
                        to_data_ts)

FIXTURE = json.loads((Path(__file__).resolve().parents[2] / "paper-skill" /
                      "fixtures" / "aiayn_concept_graph.json")
                     .read_text(encoding="utf-8"))
PACK = {"meta": {"source": "arXiv:1706.03762", "title": "AIAYN",
                 "generated": "2026-07-09"},
        "extraction": {"path": "latex", "equation_fidelity": "exact"},
        "sections": [{"id": "sec_3_2", "title": "SDPA", "level": 2, "text": "t"}],
        "equations": [{"id": "eq_1", "latex": "x", "section": "sec_3_2"}],
        "references": [], "figures": []}


def test_bundle_has_all_contract_keys():
    b = build_bundle(FIXTURE, pack=PACK)
    for k in ("meta", "nodes", "edges", "pages", "notes", "hotspots",
              "clusters", "tour", "provenance", "centrality", "eqIndex",
              "trace", "glossary"):
        assert k in b, k


def test_tour_is_deterministic_reading_path_head():
    b = build_bundle(FIXTURE, pack=PACK)
    order = reading_path(FIXTURE)
    assert [s["nodeIds"][0] for s in b["tour"]] == order[:5]
    assert all(s["title"] and s["description"] for s in b["tour"])


def test_clusters_fall_back_to_level1_grouping():
    b = build_bundle(FIXTURE, pack=PACK)
    ids = {c["id"] for c in b["clusters"]}
    assert "attention" in ids            # L1 node with part-of children
    members = next(c for c in b["clusters"] if c["id"] == "attention")["nodeIds"]
    assert "scaled-dot-product-attention" in members


def test_centrality_present_for_every_node():
    b = build_bundle(FIXTURE, pack=PACK)
    assert set(b["centrality"]) == {n["id"] for n in FIXTURE["nodes"]}


def test_eq_index_maps_equation_to_anchored_concepts():
    g = json.loads(json.dumps(FIXTURE))
    g["nodes"][0]["source_ref"] = "sec_3_2"     # anchor one node to the section
    b = build_bundle(g, pack=PACK)
    assert g["nodes"][0]["id"] in b["eqIndex"]["eq_1"]


def test_strip_images_removes_and_counts():
    md = "before ![diagram](../assets/x.png) after"
    out, n = strip_images(md)
    assert "![" not in out and "x.png" not in out and n == 1


def test_ts_output_is_wellformed_and_unicode_raw(tmp_path):
    b = build_bundle(FIXTURE, pack=PACK)
    ts = to_data_ts(b)
    assert ts.startswith("// generated by build_data.py")
    assert "export const KE_DATA" in ts
    assert "√dₖ" in ts                          # never \u-escaped
    json.loads(ts.split("=", 1)[1].rstrip().rstrip(";"))  # payload is valid JSON
```

- [ ] **Step 2: Verify RED** — `cd dashboard && python -m pytest tests/ -q` → FAIL: `build_data` not found.
- [ ] **Step 3: Implement**

`dashboard/build_data.py`:
```python
"""Bundle pipeline artifacts into src/data.gen.ts (design doc §3-§4).

Everything deterministic; runs without internet access. No runtime fetch exists in the
dashboard, so this file IS the data path.
"""
import argparse
import datetime
import json
import re
from collections import defaultdict
from pathlib import Path

import networkx as nx
import yaml

_IMG = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_DEPENDENT_SIDE = {"part-of": "dst", "prerequisite": "dst", "builds-on": "src"}


def reading_path(plan_graph):
    """Kahn topo over prerequisite/builds-on (mirror of fork exporter;
    duplicated deliberately — 30 lines beats a cross-repo import)."""
    nodes = {n["id"]: n for n in plan_graph["nodes"]}
    after = {i: set() for i in nodes}
    indeg = {i: 0 for i in nodes}
    for e in plan_graph["edges"]:
        if e["kind"] == "prerequisite":
            first, later = e["src"], e["dst"]
        elif e["kind"] == "builds-on":
            first, later = e["dst"], e["src"]
        else:
            continue
        if later not in after[first]:
            after[first].add(later)
            indeg[later] += 1
    key = lambda i: (nodes[i].get("level", 0), nodes[i].get("label", ""))
    ready = sorted((i for i in nodes if indeg[i] == 0), key=key)
    order = []
    while ready:
        cur = ready.pop(0)
        order.append(cur)
        for nxt in sorted(after[cur], key=key):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                ready.append(nxt)
        ready.sort(key=key)
    order += [i for i in sorted(nodes, key=key) if i not in order]
    return order


def strip_images(md: str):
    n = len(_IMG.findall(md))
    return _IMG.sub("", md), n


def _clusters(plan_graph):
    nodes = {n["id"]: n for n in plan_graph["nodes"]}
    if any("community" in n for n in plan_graph["nodes"]):
        groups = defaultdict(list)
        for n in plan_graph["nodes"]:
            groups[n.get("community", -1)].append(n["id"])
        return [{"id": f"community-{c}", "label": f"Community {c}",
                 "nodeIds": sorted(ms)} for c, ms in sorted(groups.items())]
    # fallback: every L1 node + its transitive part-of descendants
    children = defaultdict(list)
    for e in plan_graph["edges"]:
        if e["kind"] == "part-of":
            children[e["dst"]].append(e["src"])

    def desc(i):
        out = []
        for k in children.get(i, []):
            out += [k] + desc(k)
        return out
    return [{"id": n["id"], "label": n["label"],
             "nodeIds": sorted(set([n["id"]] + desc(n["id"])))}
            for n in plan_graph["nodes"] if n.get("level", 0) == 1]


def _centrality(plan_graph):
    g = nx.DiGraph()
    g.add_nodes_from(n["id"] for n in plan_graph["nodes"])
    g.add_edges_from((e["src"], e["dst"]) for e in plan_graph["edges"])
    return {k: round(v, 4) for k, v in nx.betweenness_centrality(g).items()}


def _tour(plan_graph, hotspots):
    labels = {n["id"]: n["label"] for n in plan_graph["nodes"]}
    if plan_graph["meta"].get("kind") == "code" and hotspots:
        picks = [h["id"] for h in hotspots[:5]]
        blurb = "High-churn, high-dependency hotspot — start here."
    else:
        picks = reading_path(plan_graph)[:5]
        blurb = "Next stop on the dependency-ordered reading path."
    return [{"order": i + 1, "title": labels.get(p, p), "description": blurb,
             "nodeIds": [p]} for i, p in enumerate(picks)]


def _eq_index(plan_graph, pack):
    if not pack:
        return {}
    sec_of_eq = {e["id"]: e["section"] for e in pack.get("equations", [])}
    by_sec = defaultdict(list)
    for n in plan_graph["nodes"]:
        ref = (n.get("source_ref") or "").replace("§", "")
        by_sec[ref].append(n["id"])
    return {eq: sorted(by_sec.get(sec, [])) for eq, sec in sec_of_eq.items()}


def _load_pages(pages_dir):
    pages = {}
    if not pages_dir:
        return pages, 0
    stripped = 0
    for f in sorted(Path(pages_dir).glob("*.md")):
        cid = f.stem.split("_", 1)[1] if "_" in f.stem else f.stem
        text, n = strip_images(f.read_text(encoding="utf-8"))
        stripped += n
        pages[cid] = text
    return pages, stripped


def _load_notes(wiki_dir):
    notes, glossary, trace = {}, {}, []
    if not wiki_dir:
        return notes, glossary, trace
    for f in sorted(Path(wiki_dir).glob("*.yaml")):
        note = yaml.safe_load(f.read_text(encoding="utf-8"))
        cid = note.get("concept", f.stem)
        text, _ = strip_images(note.get("synthesis", ""))
        note["synthesis"] = text
        notes[cid] = note
        if note.get("glossary"):
            glossary[cid] = note["glossary"]
        trace.append({"nodeId": cid, "phase": "researched",
                      "status": note.get("status", "unknown"),
                      "date": datetime.date.fromtimestamp(
                          f.stat().st_mtime).isoformat()})
    return notes, glossary, trace


def build_bundle(plan_graph, pack=None, pages_dir=None, wiki_dir=None,
                 hotspots=None, repo_dir=None):
    hotspots = hotspots or []
    pages, stripped = _load_pages(pages_dir)
    notes, glossary, trace = _load_notes(wiki_dir)
    for cid in pages:
        trace.append({"nodeId": cid, "phase": "written", "status": "ok",
                      "date": plan_graph["meta"].get("generated", "")})
    if stripped:
        print(f"stripped {stripped} image block(s) (rich media is v2)")
    return {"meta": plan_graph["meta"], "nodes": plan_graph["nodes"],
            "edges": plan_graph["edges"], "pages": pages, "notes": notes,
            "hotspots": hotspots, "clusters": _clusters(plan_graph),
            "tour": _tour(plan_graph, hotspots),
            "provenance": (pack or {}).get("extraction", {}),
            "centrality": _centrality(plan_graph),
            "eqIndex": _eq_index(plan_graph, pack),
            "trace": sorted(trace, key=lambda t: (t["nodeId"], t["phase"])),
            "glossary": glossary,
            "dependentSide": _DEPENDENT_SIDE}


def to_data_ts(bundle) -> str:
    payload = json.dumps(bundle, ensure_ascii=False, indent=1)
    return ("// generated by build_data.py — do not edit\n"
            "export const KE_DATA = " + payload + ";\n")


def main(argv=None):
    p = argparse.ArgumentParser(prog="build_data")
    p.add_argument("--graph", required=True)
    p.add_argument("--pack")
    p.add_argument("--pages-dir")
    p.add_argument("--wiki-dir")
    p.add_argument("--hotspots")
    p.add_argument("--repo-dir")
    p.add_argument("--out", default="src/data.gen.ts")
    a = p.parse_args(argv)
    load = lambda x: json.loads(Path(x).read_text(encoding="utf-8")) if x else None
    bundle = build_bundle(load(a.graph), pack=load(a.pack),
                          pages_dir=a.pages_dir, wiki_dir=a.wiki_dir,
                          hotspots=(load(a.hotspots) or {}).get("hotspots")
                          if a.hotspots else None,
                          repo_dir=a.repo_dir)
    Path(a.out).write_text(to_data_ts(bundle), encoding="utf-8")
    print(f"{a.out}: {len(bundle['nodes'])} nodes, {len(bundle['tour'])} tour steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Note: `pip install networkx pyyaml` if missing. Code-excerpt embedding (hotspot∪implements, ≤80 lines) activates only for code graphs with `--repo-dir`; the AIAYN fixture has neither, and the excerpt loader is added in 11b Task 4 alongside its consumer (`CodeViewer`) — one task owns both sides.

- [ ] **Step 4: Verify GREEN** — 7/7 pass.
- [ ] **Step 5:** Generate + force-commit the dev fixture bundle:
  `python build_data.py --graph ../paper-skill/fixtures/aiayn_concept_graph.json --out src/data.gen.ts`
  then `git add -f src/data.gen.ts` (gitignored otherwise) — committed so `npm run dev` works from a fresh clone.
- [ ] **Step 6:** Wire it: in `src/App.tsx` placeholder add `import { KE_DATA } from "./data.gen";` and render `<div>{KE_DATA.nodes.length} nodes loaded</div>`. Run `npm test && npm run build`, then serve `dist/` with `python -m http.server -d dist 8000`; confirm the fixture loads and raw Unicode renders at `http://localhost:8000/` with internet access disabled.
- [ ] **Step 7: Commit** — `git commit -am "feat(dashboard): build_data bundler + fixture data.gen"`

### Task 3: Pure logic modules + worker layout integration

**Files:**
- Create: `dashboard/src/types.ts`, `dashboard/src/lib/deps.ts`, `dashboard/src/lib/insights.ts`, `dashboard/src/lib/blastRadius.ts`, `dashboard/src/lib/lod.ts`, `dashboard/src/lib/layout.ts`
- Test: `dashboard/src/lib/deps.test.ts`, `dashboard/src/lib/insights.test.ts`, `dashboard/src/lib/blastRadius.test.ts`, `dashboard/src/lib/lod.test.ts`

**Interfaces (consumed by every 11b component):**
```ts
// types.ts
export type KENode = { id: string; kind: string; label: string; level?: number;
  source_ref?: string; community?: number };
export type KEEdge = { src: string; dst: string; kind: string; weight?: number;
  confidence?: string };
export type Insight = { severity: "HIGH" | "MED" | "LOW"; rule: string;
  nodeId: string; text: string };
// deps.ts
export function dependentsOf(id: string, edges: KEEdge[]): string[];
export function dependencyRings(id: string, edges: KEEdge[], maxDepth?: number): Map<string, number>;
// insights.ts
export function computeInsights(data: {nodes; edges; notes; provenance; centrality; meta}): Insight[];
// blastRadius.ts
export function ghostStyles(rings: Map<string, number>, allIds: string[], selected?: string): Map<string, {opacity: number; ring: number}>;
// lod.ts
export function visibleAtZoom(zoom: number, threshold: number, clusters, nodeIds: string[]): {showClusters: boolean; hiddenNodes: Set<string>};
// layout.ts
export async function layoutGraph(nodes: KENode[], edges: KEEdge[]): Promise<Map<string, {x: number; y: number}>>;  // elkjs Web Worker
```

- [ ] **Step 1: Write failing tests**

`dashboard/src/lib/deps.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { dependencyRings, dependentsOf } from "./deps";

const EDGES = [
  { src: "sdpa", dst: "attention", kind: "part-of" },
  { src: "mha", dst: "sdpa", kind: "builds-on" },
  { src: "attention", dst: "transformer", kind: "part-of" },
];

describe("dependentsOf", () => {
  it("mirrors the python dependent-side map", () => {
    expect(new Set(dependentsOf("sdpa", EDGES)))
      .toEqual(new Set(["attention", "mha"]));
  });
});

describe("dependencyRings", () => {
  it("assigns hop depth per dependent", () => {
    const rings = dependencyRings("sdpa", EDGES, 3);
    expect(rings.get("attention")).toBe(1);
    expect(rings.get("mha")).toBe(1);
    expect(rings.get("transformer")).toBe(2);
    expect(rings.has("sdpa")).toBe(false);
  });
});
```

`dashboard/src/lib/insights.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { computeInsights } from "./insights";

const base = {
  meta: { kind: "code" },
  nodes: [
    { id: "a", kind: "function", label: "a" },
    { id: "b", kind: "function", label: "b" },
  ],
  edges: [{ src: "a", dst: "b", kind: "calls" }],
  notes: { a: { status: "partial", unresolved: ["why?"] } },
  provenance: { equation_fidelity: "absent" },
  centrality: { a: 0.9, b: 0.0 },
};

describe("computeInsights", () => {
  it("flags dead code (in-degree 0, code kind)", () => {
    const r = computeInsights(base as never);
    expect(r.some((i) => i.rule === "dead-code" && i.nodeId === "a")).toBe(true);
  });
  it("flags cycles", () => {
    const cyc = { ...base, edges: [...base.edges, { src: "b", dst: "a", kind: "calls" }] };
    expect(computeInsights(cyc as never).some((i) => i.rule === "cycle")).toBe(true);
  });
  it("flags degraded math + unresolved notes as LOW", () => {
    const r = computeInsights(base as never);
    expect(r.some((i) => i.rule === "degraded-math" && i.severity === "LOW")).toBe(true);
    expect(r.some((i) => i.rule === "unresolved-note" && i.nodeId === "a")).toBe(true);
  });
  it("flags bottleneck via centrality p90", () => {
    const r = computeInsights(base as never);
    expect(r.some((i) => i.rule === "bottleneck" && i.nodeId === "a")).toBe(true);
  });
});
```

`dashboard/src/lib/blastRadius.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { ghostStyles } from "./blastRadius";

describe("ghostStyles", () => {
  it("selected=0, ring1, ring2, others ghosted", () => {
    const rings = new Map([["x", 1], ["y", 2]]);
    const s = ghostStyles(rings, ["sel", "x", "y", "z"], "sel");
    expect(s.get("sel")).toEqual({ opacity: 1, ring: 0 });
    expect(s.get("x")!.ring).toBe(1);
    expect(s.get("y")!.ring).toBe(2);
    expect(s.get("z")!.opacity).toBeLessThanOrEqual(0.15);
  });
});
```

`dashboard/src/lib/lod.test.ts`:
```ts
import { describe, expect, it } from "vitest";
import { visibleAtZoom } from "./lod";

const clusters = [{ id: "c1", label: "C1", nodeIds: ["a", "b"] }];

describe("visibleAtZoom", () => {
  it("zoomed out shows clusters, hides members", () => {
    const v = visibleAtZoom(0.3, 0.5, clusters, ["a", "b", "solo"]);
    expect(v.showClusters).toBe(true);
    expect(v.hiddenNodes.has("a")).toBe(true);
    expect(v.hiddenNodes.has("solo")).toBe(false);  // unclustered stays visible
  });
  it("zoomed in shows members", () => {
    const v = visibleAtZoom(0.8, 0.5, clusters, ["a", "b"]);
    expect(v.showClusters).toBe(false);
    expect(v.hiddenNodes.size).toBe(0);
  });
});
```

- [ ] **Step 2: RED** — `npm test` → module-not-found failures.
- [ ] **Step 3: Implement**

`dashboard/src/lib/deps.ts`:
```ts
import type { KEEdge } from "../types";

// Single source of truth mirrored from research_mcp.graph_query (python):
//   part-of→dst, prerequisite→dst, builds-on→src, everything else→src.
const DEPENDENT_SIDE: Record<string, "src" | "dst"> = {
  "part-of": "dst",
  prerequisite: "dst",
  "builds-on": "src",
};

function split(e: KEEdge): { dependent: string; dependency: string } {
  const side = DEPENDENT_SIDE[e.kind] ?? "src";
  return side === "src"
    ? { dependent: e.src, dependency: e.dst }
    : { dependent: e.dst, dependency: e.src };
}

export function dependentsOf(id: string, edges: KEEdge[]): string[] {
  const out = new Set<string>();
  for (const e of edges) {
    const { dependent, dependency } = split(e);
    if (dependency === id) out.add(dependent);
  }
  return [...out];
}

export function dependencyRings(
  id: string, edges: KEEdge[], maxDepth = 2,
): Map<string, number> {
  const rings = new Map<string, number>();
  let frontier = [id];
  const seen = new Set([id]);
  for (let depth = 1; depth <= maxDepth; depth++) {
    const next: string[] = [];
    for (const cur of frontier)
      for (const dep of dependentsOf(cur, edges))
        if (!seen.has(dep)) {
          seen.add(dep);
          rings.set(dep, depth);
          next.push(dep);
        }
    frontier = next;
  }
  return rings;
}
```

`dashboard/src/lib/insights.ts`:
```ts
import type { Insight, KEEdge, KENode } from "../types";
import { dependentsOf } from "./deps";

const CODE_KINDS = new Set(["function", "class", "file", "route"]);

function findCycle(nodes: KENode[], edges: KEEdge[]): string[] | null {
  const adj = new Map<string, string[]>();
  for (const e of edges) (adj.get(e.src) ?? adj.set(e.src, []).get(e.src)!)?.push(e.dst);
  const state = new Map<string, 1 | 2>(); // 1 visiting, 2 done
  const stack: string[] = [];
  const visit = (v: string): string[] | null => {
    state.set(v, 1);
    stack.push(v);
    for (const w of adj.get(v) ?? []) {
      if (state.get(w) === 1) return stack.slice(stack.indexOf(w));
      if (!state.has(w)) {
        const c = visit(w);
        if (c) return c;
      }
    }
    stack.pop();
    state.set(v, 2);
    return null;
  };
  for (const n of nodes) if (!state.has(n.id)) {
    const c = visit(n.id);
    if (c) return c;
  }
  return null;
}

export function computeInsights(data: {
  nodes: KENode[]; edges: KEEdge[];
  notes: Record<string, { status?: string; unresolved?: string[] }>;
  provenance: { equation_fidelity?: string };
  centrality: Record<string, number>;
  meta: { kind?: string };
}): Insight[] {
  const out: Insight[] = [];
  const indeg = new Map<string, number>();
  for (const e of data.edges) indeg.set(e.dst, (indeg.get(e.dst) ?? 0) + 1);

  for (const n of data.nodes)
    if (CODE_KINDS.has(n.kind) && !(indeg.get(n.id) ?? 0) &&
        dependentsOf(n.id, data.edges).length === 0)
      out.push({ severity: "MED", rule: "dead-code", nodeId: n.id,
                 text: `${n.label}: nothing depends on it — potentially dead` });

  const cycle = findCycle(data.nodes, data.edges);
  if (cycle)
    out.push({ severity: "MED", rule: "cycle", nodeId: cycle[0],
               text: `dependency cycle: ${cycle.join(" → ")}` });

  if (data.provenance.equation_fidelity &&
      data.provenance.equation_fidelity !== "exact")
    out.push({ severity: "LOW", rule: "degraded-math",
               nodeId: data.nodes[0]?.id ?? "",
               text: `equations extracted via ${data.provenance.equation_fidelity} — distrust exact forms` });

  for (const [id, note] of Object.entries(data.notes))
    if (note.unresolved?.length)
      out.push({ severity: "LOW", rule: "unresolved-note", nodeId: id,
                 text: `open questions: ${note.unresolved.join("; ")}` });

  const vals = Object.values(data.centrality).sort((a, b) => a - b);
  const p90 = vals[Math.floor(vals.length * 0.9)] ?? Infinity;
  for (const [id, c] of Object.entries(data.centrality))
    if (vals.length > 1 && c >= p90 && c > 0)
      out.push({ severity: "MED", rule: "bottleneck", nodeId: id,
                 text: `bridge node (betweenness ${c}) — many paths run through it` });

  const order = { HIGH: 0, MED: 1, LOW: 2 };
  return out.sort((a, b) => order[a.severity] - order[b.severity]);
}
```

`dashboard/src/lib/blastRadius.ts`:
```ts
export function ghostStyles(
  rings: Map<string, number>, allIds: string[], selected?: string,
): Map<string, { opacity: number; ring: number }> {
  const out = new Map<string, { opacity: number; ring: number }>();
  for (const id of allIds) {
    if (id === selected) out.set(id, { opacity: 1, ring: 0 });
    else if (rings.has(id)) out.set(id, { opacity: 1, ring: rings.get(id)! });
    else out.set(id, { opacity: 0.1, ring: -1 });
  }
  return out;
}
```

`dashboard/src/lib/lod.ts`:
```ts
export function visibleAtZoom(
  zoom: number, threshold: number,
  clusters: { id: string; nodeIds: string[] }[], nodeIds: string[],
): { showClusters: boolean; hiddenNodes: Set<string> } {
  const showClusters = zoom < threshold && clusters.length > 0;
  if (!showClusters) return { showClusters, hiddenNodes: new Set() };
  const clustered = new Set(clusters.flatMap((c) => c.nodeIds));
  return { showClusters,
           hiddenNodes: new Set(nodeIds.filter((i) => clustered.has(i))) };
}
```

`dashboard/src/lib/layout.ts`:
```ts
import ELK from "elkjs/lib/elk-api";
import elkWorkerUrl from "elkjs/lib/elk-worker.min.js?url";
import type { KEEdge, KENode } from "../types";

// Vite emits the worker as a local build asset. localhost supplies the normal
// origin required to start it; all topology calculation stays off-thread.
const elk = new ELK({ workerUrl: elkWorkerUrl });

export async function layoutGraph(
  nodes: KENode[], edges: KEEdge[],
): Promise<Map<string, { x: number; y: number }>> {
  const res = await elk.layout({
    id: "root",
    layoutOptions: { "elk.algorithm": "layered",
                     "elk.direction": "DOWN",
                     "elk.spacing.nodeNode": "40" },
    children: nodes.map((n) => ({ id: n.id, width: 180, height: 64 })),
    edges: edges.map((e, i) => ({ id: `e${i}`, sources: [e.src], targets: [e.dst] })),
  });
  return new Map((res.children ?? []).map((c) => [c.id, { x: c.x ?? 0, y: c.y ?? 0 }]));
}
```

`dashboard/src/types.ts`: exactly the block from **Interfaces** above.

- [ ] **Step 4: GREEN** — `npm test` → all suites pass; `npm run build` succeeds and emits a local ELK worker asset. Run `npm run dev` and confirm browser DevTools shows layout work in a Worker rather than on the main thread.
- [ ] **Step 5 (stale-doc rule, HIGH — design §5.1):** RED test appended to `insights.test.ts`:

```ts
it("flags stale docs when code mtime is newer than its note date", () => {
  const stale = { ...base,
    mtimes: { a: "2026-07-08" },
    notes: { a: { status: "complete", unresolved: [], date: "2026-07-01" } } };
  const r = computeInsights(stale as never);
  expect(r.some((i) => i.rule === "stale-doc" && i.severity === "HIGH"
                       && i.nodeId === "a")).toBe(true);
});
```

Implementation: `computeInsights` gains optional `mtimes?: Record<string,string>` on its input; rule (after dead-code):

```ts
  for (const [id, m] of Object.entries(data.mtimes ?? {})) {
    const noteDate = (data.notes[id] as { date?: string } | undefined)?.date;
    if (noteDate && m > noteDate)
      out.push({ severity: "HIGH", rule: "stale-doc", nodeId: id,
                 text: `code edited ${m}, doc last updated ${noteDate} — drift` });
  }
```

Data side: in `build_data.py`'s `build_bundle`, when `repo_dir` is given, bake
`"mtimes": {n["id"]: iso-mtime-of-source-file}` for code nodes (reuse the
`source_ref.rsplit(":", 1)` file resolution from the excerpts block); `_load_notes`
already stamps each note dict with its file date — add `note["date"] = <same iso>`
there. pytest: assert `mtimes` present for a repo-dir bundle and absent otherwise.
- [ ] **Step 6: GREEN + Commit** — `git commit -am "feat(dashboard): pure logic core (deps/insights/blast/lod/layout) + vitest"`

### Review gate (slice 11a)

- [ ] `python -m pytest tests/ -q` → 7 pass. `npm test` → 4 suites pass. `npm run build` → PASS and `dist/assets/` includes the bundled ELK worker.
- [ ] With internet access disabled, run `python -m http.server -d dist 8000`, open `http://localhost:8000/`, confirm the fixture renders with zero external requests, and verify a large code-graph layout runs in a Worker while the UI remains responsive.
- [ ] `src/data.gen.ts` committed, contains raw `√dₖ`.
- [ ] Update `plans/2026-07-09-INDEX.md` status table. Commit.

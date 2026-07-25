# Slice 11 — Knowledge Dashboard Design (approved forks inline)

**Status:** DESIGN — approved by owner (2026-07-09), runtime constraint amended 2026-07-12: keep single-file lite export **and** dashboard; build **dashboard first** against the AIAYN fixture; tours deterministic with optional LLM narration; serve the dashboard from localhost rather than `file://`.
**Supersedes nothing:** slices 8.3 (p6 builder) and 9 (bridge) remain as planned and later feed real data into this dashboard.

## 1. Goal

A beautiful, interactive, **100% internet-disconnected** knowledge dashboard for BOTH research-paper concept graphs and code graphs (and their slice-9 bridged merge) — UA-grade visual exploration + TrueCourse-grade insight surfacing, for efficient learning and quick concept digestion. "Offline" means no internet traffic, external CDNs, telemetry, external APIs, remote fonts, or remote assets; the app itself is served locally over `http://localhost`.

## 2. Verified research inputs (2026-07-09)

- **Understand-Anything (MIT):** dashboard = React 19 + `@xyflow/react` ^12 + Vite + zustand + elkjs/dagre + graphology(+louvain) + react-markdown + prism-react-renderer. Liftable components: `OnboardingOverlay` (tour), `FilterPanel`, `LayerLegend`, `DiffToggle`, `CodeViewer`, `LearnPanel`, `CustomNode/ContainerNode`, `Breadcrumb`. Their graph JSON carries first-class `tour[]` `{order,title,description,nodeIds[]}` and `layers[]` — we mirror both. Explain skill: `skills/understand-explain/SKILL.md` (58 lines, grep-graph-before-reading discipline).
- **TrueCourse (MIT):** UI paradigms lifted — severity-tagged Insights sidebar, diff/staleness mode, top context switcher, bottom trace player. Their dashboard uses an application server (`:3001`); ours uses only a static localhost server and adds no backend/API service.
- **Package fact:** React Flow v12 = `@xyflow/react` (12.11.x); `reactflow` is legacy v11. All plans use `@xyflow/react`.

## 3. Architecture

- New top-level app: `Deepwiki/dashboard/` — Vite + React 19 + TypeScript + `@xyflow/react` 12 + zustand + react-markdown + remark-gfm + KaTeX + prism-react-renderer. Layout: elkjs runs in a Vite-bundled **Web Worker** so topology calculation stays off the main thread and massive code graphs do not freeze interaction. Localhost provides a normal origin, so a script-file worker is supported; synchronous main-thread ELK is not an acceptable production fallback.
- `vite.config.ts` uses standard Vite asset handling; `base: './'` is neither required nor prescribed. Production output is served from `dist/` over localhost, so standard absolute local asset paths such as `url(/assets/...)` resolve correctly.
- **No runtime data fetch:** keep the deterministic Python bundler `dashboard/build_data.py` (pytest-covered). It globs pack + §5.1 graphs + pages + `_research_wiki` notes + hotspots output into ONE generated `src/data.gen.ts` (`export const KE_DATA = {...}`), `ensure_ascii=False`-equivalent (raw unicode). The localhost pivot changes browser execution and worker support, not the data contract. A committed AIAYN fixture bundle keeps `npm run dev` usable from a fresh clone.
- Offline constraint is hard: no external CDN refs, telemetry, external API calls, remote web fonts, or remote assets. KaTeX CSS and woff2 fonts remain local build assets; relative and root-absolute localhost asset URLs are both allowed.
- Run development with `cd dashboard && npm run dev`. For production viewing, run `cd dashboard && npm run build`, then `python -m http.server -d dist 8000` and open `http://localhost:8000/`.
- The existing single-file Cytoscape exporter stays untouched as the **lite export** (portable share artifact).

## 4. Data contract (KE_DATA)

```ts
{
  meta: {kind: "concept"|"code"|"bridged", source, generated},
  nodes: [...§5.1 node + {community?: int}], edges: [...§5.1 edge],
  pages: {node_id: {tldr, intuition, mechanics, "the-math", "go-deeper"}},  // html
  notes: {node_id: NoteYaml},               // research wiki
  hotspots: [{id, score, churn, in_degree}],// slice-4 output, [] for papers
  clusters: [{id, label, nodeIds}],         // Leiden communities or level-1 grouping
  tour: [{order, title, description, nodeIds}],   // UA shape
  provenance: {equation_fidelity, path},    // pack extraction block
  centrality: {node_id: float},             // networkx betweenness, build-time
  eqIndex: {eq_id: [node_ids]},             // equation -> concepts anchored to it
  trace: [{nodeId, phase, status, date}],   // real pipeline provenance (P3/P4/P5)
  glossary: {node_id: {symbol: definition}} // from NoteYaml.glossary (optional)
}
```

`build_data.py` computes deterministically: `clusters` (from graphify communities if present, else level-1 part-of grouping), `tour` (papers: first 5 reading-path nodes; code: top-5 hotspots; template text), `insights` are computed **client-side** in JS (below) so they stay live with filters.

**Bundle hygiene (internet-disconnected runtime):**
- **Markdown images:** rich media is OUT of scope for v1. `build_data.py` strips `![...](...)` image blocks from every page/note string at bundle time and logs the stripped count, preventing bundled content from introducing remote requests or unresolved media dependencies.
- **Payload cap:** code-node source excerpts are included ONLY for (top-20 hotspot nodes ∪ nodes with an `implements` edge), clipped to the node's own function boundaries with a hard 80-line ceiling. All other code nodes get explore-card facts only (label, source_ref, neighbors, impact count). Keeps `data.gen.ts` in the hundreds-of-KB range even for 380-node graphs.

## 5. Feature set (each works for paper AND code)

1. **Insights & Health panel** (left, TrueCourse): severity-tagged cards, click centers canvas. Rules (pure JS over KE_DATA): HIGH `stale-doc` (code node file mtime baked at bundle-time newer than linked note/page date), MED `dead-code` (in-degree 0, code kinds, minus entry heuristics) / `cycle` (DFS cycle detection), LOW `degraded-math` (provenance ≠ exact), `no-implements` (bridged only), `unresolved-note` (note.unresolved non-empty).
2. **Context switcher** (top, TrueCourse): Concepts / Clusters / Code / Bridged — DataView-style visibility toggles; pills also per edge-kind (`implements` on/off).
3. **Explain drawer** (right, UA): a 380px flex rail at viewport widths ≥1280px and a right-side canvas overlay below 1280px; concepts → tiered accordion (KaTeX-rendered math), code → prism source excerpt + explore-card facts (neighbors by kind, impact count); empty-canvas click dismisses.
4. **Player bar** (bottom, TrueCourse trace-player UI): paper/concept graphs expose only the reading path; code/bridged graphs expose only the blast-radius trace from the selected node (topological depth order). Prev/Next/Play(auto-advance); camera `fitView`/`setCenter` animations.
5. **Blast-radius ghosting** (UA `/understand-diff`): toggle; selected node accent, depth-1/2 rings warm colors, rest at 0.1 opacity — uses `graph_query.impact` semantics re-implemented in JS (same dependent-side map).
6. **Guided tour overlay** (UA OnboardingOverlay): floating card, prev/next, drives camera + drawer from `tour[]`. Deterministic text; optional `--narrate` flag in build_data.py runs one leased spawn to rewrite descriptions (P2-compliant: optional, never required).
7. **Semantic zoom LOD**: zoom < threshold → cluster container-nodes only; ≥ threshold → member nodes (React Flow zoom hook + hidden flags).
8. **Legend + filter pills + search** (ports of LayerLegend/FilterPanel + our existing search semantics: reveal ancestors, center, select).
9. **Formula→graph bridge** (round-12 adoption, equation-level v1): hovering a rendered equation block in the drawer highlights every node in `eqIndex[eq_id]` on the canvas (zustand hover state). Per-VARIABLE hover needs variable→node data we don't extract — v2.
10. **Build-trace tab** (Undermind-pattern, honest adaptation): a sidebar tab listing real pipeline provenance per node (`trace`: researched/written/validated + status + date, derived from wiki notes, `p3_done`/`p4_done`, lint results — NOT fabricated AI streams); clicking an entry centers the canvas on that node.
11. **Glossary tooltips** (Explainpaper pattern): drawer wraps symbols found in `glossary[node_id]` in hover tooltips with their 1-sentence plain definitions. Requires a small slice-7 amendment: the P4 writer prompt asks for a `glossary:` map (symbol → one sentence) appended to the note; field is optional everywhere.
12. **Bidirectional bridge tracing** (blueprint adoption): a concept's drawer lists code nodes implementing it; a code node's drawer lists the concepts it implements — straight from `implements` edges, both directions.
13. **Node badges from build-time math**: networkx betweenness `centrality` computed in `build_data.py` (offline, deterministic); high-centrality nodes get a "bridge" badge on the card and a MED `bottleneck` insight.

## 6. Explain skill (separate small deliverable)

Port UA's `understand-explain/SKILL.md` → `Deepwiki/skills/explain/SKILL.md`, adapted: §5.1 schema reference block, our id conventions, `python -m research_mcp.graph_query impact|explore` calls, wiki note lookup path, grep-before-read discipline verbatim. MIT attribution line.

## 7. Testing

- `build_data.py`: pytest — bundle shape, unicode intact, deterministic tour built from fixture, fixture-bundle golden test.
- Dashboard logic: vitest on pure functions (`insights.ts`, `blastRadius.ts`, `lod.ts`, `tourSteps.ts`) — no DOM tests in v1.
- Automated verification: `python -m pytest tests/ -q`, `npm test`, and `npm run build`. No custom offline gate script is created or run.
- Acceptance (AIAYN fixture, internet disabled): serve `dist/` with `python -m http.server -d dist 8000`, open `http://localhost:8000/`, and verify zero external network requests. Tour walks ≥3 steps with camera motion; insights panel lists ≥1 card; drawer renders √dₖ via locally bundled KaTeX; player walks the reading path; switcher toggles; blast radius ghosts correctly on `scaled-dot-product-attention`; ELK layout runs in a Worker and the UI remains responsive during large-graph layout.

## 8. Out of scope (v1)

UA mobile components, ExportMenu, FileExplorer; TrueCourse rule engine (we surface OUR data, not 1300 lint rules); backend/API services; editing. The Vite development server and static localhost production server are required execution infrastructure, not application backends. M8 unaffected.

Deferred with reasons (round-12 triage of owner's research batch):
- **Time-axis lineage view** — needs per-node publication dates; only meaningful for a citation-map graph (papers as nodes), which isn't bundled yet. Revisit with the citation-map view (PLAN §4.4) in v2.
- **Tensor-shape isometric cards** (BioRender pattern) — §5.1 carries no tensor-shape data; adopting would mean inventing fields nothing extracts. Revisit if P2 ever emits shapes.
- **Citation sentiment radar** (scite pattern) — needs per-reference S2 citation-intent calls, colliding with the standing no-API-babysitting rule (R11) and S2's throttling. Revisit as a cache-only opportunistic enhancement alongside the citation-map view.
- **Per-variable formula hover** — v2 of feature 9; requires variable→node mapping data.

## 9. Attribution

Dashboard README credits Understand-Anything (MIT) and TrueCourse (MIT) for derived components/paradigms; crawl4ai/deep-searcher attributions unchanged.

# Slice 11b — Dashboard UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The full dashboard UI on top of 11a's data + logic: canvas with card nodes, insights panel, context switcher, explain drawer (KaTeX + glossary + formula-link + bidirectional bridge), player bar, guided tour, semantic zoom — plus the ported explain skill and attribution.

**Architecture:** One zustand store drives everything; components are thin views over 11a's pure functions and worker-backed ELK layout. UI verification = `npm test`, `npm run build`, and localhost acceptance with internet access disabled (§Review gate). Component tests are NOT written in v1 (design §7) — logic already has vitest coverage in 11a.

**Tech Stack:** as 11a. All imports from `@xyflow/react` v12.

## Global Constraints

- Same as 11a: internet-disconnected localhost runtime, no external CDNs/APIs/telemetry/fonts/assets, bundled `KE_DATA` with no runtime data fetch, Unicode preserved, and worker-backed ELK layout. Do not require `base: './'`.
- Layout/styling: single `src/styles.css`, dark slate theme via CSS variables (`--bg:#0b1220; --surface:#111a2c; --border:#1e293b; --text:#e2e8f0; --muted:#94a3b8; --accent:#4a7ebb; --warn:#eab308; --bad:#ef4444`).
- Severity colors: HIGH `--bad`, MED `--warn`, LOW `--muted`. Rings: 0 red, 1 orange (#f97316), 2 yellow (#eab308).
- KaTeX: `import "katex/dist/katex.min.css"`; Vite copies woff2 into local build assets. Relative and root-absolute localhost asset URLs are both valid; remote font URLs are forbidden.
- Every task: `npm test && npm run build` must pass before commit. Use `npm run dev` for development checks; use `python -m http.server -d dist 8000` for production-build checks.

---

### Task 1: Store + app shell + canvas with card nodes

**Files:**
- Create: `dashboard/src/store.ts`, `dashboard/src/components/Canvas.tsx`, `dashboard/src/components/nodes.tsx`, `dashboard/src/components/Legend.tsx`
- Replace: `dashboard/src/App.tsx`, `dashboard/src/styles.css`

**Interfaces:**
- Produces `useApp` store consumed by every later task:

```ts
type View = "concepts" | "clusters" | "code" | "bridged";
type PlayerState = { steps: string[]; idx: number; label: string } | null;
interface AppState {
  selected: string | null;      setSelected(id: string | null): void;
  view: View;                   setView(v: View): void;
  hiddenKinds: Set<string>;     toggleKind(k: string): void;   // edge-kind pills
  blastOn: boolean;             setBlastOn(b: boolean): void;
  hoverEq: string | null;       setHoverEq(id: string | null): void;
  player: PlayerState;          setPlayer(p: PlayerState): void; step(d: 1 | -1): void;
  tourIdx: number | null;       setTourIdx(i: number | null): void;
  sidebarTab: "insights" | "trace"; setSidebarTab(t: "insights" | "trace"): void;
}
```

- `Canvas` renders `KE_DATA` through `layoutGraph` (positions computed once in a `useEffect`, stored in local state), node types `concept | code | cluster`, edge styling (`implements` = green #4a9b5e dashed width 2; `prerequisite/builds-on` dashed #cc8855; rest #475569). Node visibility = intersection of view filter, LOD (Task 5), blast ghosting (Task 4), hidden edge kinds.

- [ ] **Step 1:** `store.ts`:

```ts
import { create } from "zustand";

type View = "concepts" | "clusters" | "code" | "bridged";
type PlayerState = { steps: string[]; idx: number; label: string } | null;

interface AppState {
  selected: string | null; setSelected: (id: string | null) => void;
  view: View; setView: (v: View) => void;
  hiddenKinds: Set<string>; toggleKind: (k: string) => void;
  blastOn: boolean; setBlastOn: (b: boolean) => void;
  hoverEq: string | null; setHoverEq: (id: string | null) => void;
  player: PlayerState; setPlayer: (p: PlayerState) => void; step: (d: 1 | -1) => void;
  tourIdx: number | null; setTourIdx: (i: number | null) => void;
  sidebarTab: "insights" | "trace"; setSidebarTab: (t: "insights" | "trace") => void;
}

export const useApp = create<AppState>((set) => ({
  selected: null, setSelected: (selected) => set({ selected }),
  view: "concepts", setView: (view) => set({ view }),
  hiddenKinds: new Set(), toggleKind: (k) =>
    set((s) => {
      const next = new Set(s.hiddenKinds);
      next.has(k) ? next.delete(k) : next.add(k);
      return { hiddenKinds: next };
    }),
  blastOn: false, setBlastOn: (blastOn) => set({ blastOn }),
  hoverEq: null, setHoverEq: (hoverEq) => set({ hoverEq }),
  player: null, setPlayer: (player) => set({ player }),
  step: (d) => set((s) => s.player
    ? { player: { ...s.player,
        idx: Math.min(Math.max(s.player.idx + d, 0), s.player.steps.length - 1) } }
    : {}),
  tourIdx: null, setTourIdx: (tourIdx) => set({ tourIdx }),
  sidebarTab: "insights", setSidebarTab: (sidebarTab) => set({ sidebarTab }),
}));
```

- [ ] **Step 2:** `components/nodes.tsx` (card nodes; bridge/hotspot badges):

```tsx
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { KE_DATA } from "../data.gen";

const p90 = (() => {
  const v = Object.values(KE_DATA.centrality as Record<string, number>)
    .sort((a, b) => a - b);
  return v[Math.floor(v.length * 0.9)] ?? Infinity;
})();
const hotspotRank = new Map(
  (KE_DATA.hotspots as { id: string }[]).map((h, i) => [h.id, i + 1]));

function Card({ id, data, cls }: { id: string; data: { label: string; level?: number };
                cls: string }) {
  const bridge = (KE_DATA.centrality as Record<string, number>)[id] >= p90 &&
    Object.keys(KE_DATA.centrality).length > 1;
  const hot = hotspotRank.get(id);
  return (
    <div className={`node-card ${cls}`}>
      <Handle type="target" position={Position.Top} />
      <div className="node-label">{data.label}</div>
      <div className="node-badges">
        {data.level !== undefined && <span className="badge">L{data.level}</span>}
        {bridge && <span className="badge badge-bridge">bridge</span>}
        {hot && <span className="badge badge-hot">hotspot #{hot}</span>}
      </div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export const nodeTypes = {
  concept: (p: NodeProps) => <Card id={p.id} data={p.data as never} cls="node-concept" />,
  code: (p: NodeProps) => <Card id={p.id} data={p.data as never} cls="node-code" />,
  cluster: (p: NodeProps) => (
    <div className="node-card node-cluster">
      <Handle type="target" position={Position.Top} />
      <div className="node-label">{(p.data as { label: string }).label}</div>
      <div className="node-badges"><span className="badge">
        {(p.data as { count: number }).count} nodes</span></div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  ),
};
```

- [ ] **Step 3:** `components/Canvas.tsx`:

```tsx
import { Background, Controls, ReactFlow, useReactFlow,
         type Edge, type Node } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect, useMemo, useState } from "react";
import { KE_DATA } from "../data.gen";
import { ghostStyles } from "../lib/blastRadius";
import { dependencyRings } from "../lib/deps";
import { layoutGraph } from "../lib/layout";
import { useApp } from "../store";
import { nodeTypes } from "./nodes";
import type { KEEdge, KENode } from "../types";

const CODE_KINDS = new Set(["function", "class", "file", "route"]);
const RING_COLOR = ["#ef4444", "#f97316", "#eab308"];

function edgeStyle(kind: string) {
  if (kind === "implements")
    return { stroke: "#4a9b5e", strokeDasharray: "6 3", strokeWidth: 2 };
  if (kind === "prerequisite" || kind === "builds-on")
    return { stroke: "#cc8855", strokeDasharray: "4 3" };
  return { stroke: "#475569" };
}

export default function Canvas() {
  const { selected, setSelected, view, hiddenKinds, blastOn, hoverEq } = useApp();
  const [pos, setPos] = useState<Map<string, { x: number; y: number }>>(new Map());
  const flow = useReactFlow();

  const keNodes = KE_DATA.nodes as KENode[];
  const keEdges = KE_DATA.edges as KEEdge[];

  useEffect(() => {
    layoutGraph(keNodes, keEdges).then(setPos);
  }, []);

  const rings = useMemo(
    () => (blastOn && selected ? dependencyRings(selected, keEdges) : new Map()),
    [blastOn, selected]);
  const ghost = useMemo(
    () => ghostStyles(rings as Map<string, number>,
                      keNodes.map((n) => n.id), selected ?? undefined),
    [rings, selected]);
  const eqHits = useMemo(
    () => new Set(hoverEq ? (KE_DATA.eqIndex as Record<string, string[]>)[hoverEq] ?? [] : []),
    [hoverEq]);

  const nodes: Node[] = keNodes
    .filter((n) => view !== "concepts" || !CODE_KINDS.has(n.kind))
    .filter((n) => view !== "code" || CODE_KINDS.has(n.kind))
    .map((n) => {
      const g = blastOn && selected ? ghost.get(n.id) : undefined;
      return {
        id: n.id,
        type: CODE_KINDS.has(n.kind) ? "code" : "concept",
        position: pos.get(n.id) ?? { x: 0, y: 0 },
        data: { label: n.label, level: n.level },
        selected: n.id === selected,
        style: {
          opacity: g ? g.opacity : 1,
          outline: eqHits.has(n.id) ? "3px solid #4a7ebb"
            : g && g.ring >= 0 ? `3px solid ${RING_COLOR[g.ring]}` : undefined,
        },
      };
    });

  const shown = new Set(nodes.map((n) => n.id));
  const edges: Edge[] = keEdges
    .filter((e) => !hiddenKinds.has(e.kind) && shown.has(e.src) && shown.has(e.dst))
    .map((e, i) => ({ id: `e${i}`, source: e.src, target: e.dst,
                      style: edgeStyle(e.kind) }));

  return (
    <ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} fitView
      onNodeClick={(_, n) => setSelected(n.id)}
      onPaneClick={() => setSelected(null)}>
      <Background color="#1e293b" gap={24} />
      <Controls />
    </ReactFlow>
  );
}

export function useCenterOn() {
  const flow = useReactFlow();
  return (id: string) => {
    const n = flow.getNode(id);
    if (n) flow.setCenter(n.position.x + 90, n.position.y + 32,
                          { zoom: 1.2, duration: 600 });
  };
}
```

- [ ] **Step 4:** `components/Legend.tsx`:

```tsx
export default function Legend() {
  return (
    <div className="legend">
      <span className="chip chip-concept">concept</span>
      <span className="chip chip-code">code</span>
      <span className="chip chip-impl">implements</span>
      <span className="chip chip-prereq">prereq / builds-on</span>
    </div>
  );
}
```

- [ ] **Step 5:** `App.tsx` (three-pane shell; drawer/panel slots filled by later tasks render nothing yet):

```tsx
import { ReactFlowProvider } from "@xyflow/react";
import Canvas from "./components/Canvas";
import Legend from "./components/Legend";

export default function App() {
  return (
    <ReactFlowProvider>
      <div className="shell">
        <aside className="sidebar" id="left-panel" />
        <main className="main">
          <header className="topbar" id="topbar" />
          <div className="workspace">
            <div className="canvas-wrap">
              <Canvas />
              <Legend />
              <div id="playerbar" />
              <div id="tour-overlay" />
            </div>
            <aside className="drawer" id="drawer" />
          </div>
        </main>
      </div>
    </ReactFlowProvider>
  );
}
```

`styles.css` (complete):

```css
:root { --bg:#0b1220; --surface:#111a2c; --border:#1e293b; --text:#e2e8f0;
        --muted:#94a3b8; --accent:#4a7ebb; --warn:#eab308; --bad:#ef4444; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--text);
       font-family:system-ui,sans-serif; }
.shell { display:flex; height:100vh; }
.sidebar { width:300px; border-right:1px solid var(--border);
           background:var(--surface); overflow-y:auto; }
.main { flex:1; display:flex; flex-direction:column; position:relative; }
.topbar { height:52px; border-bottom:1px solid var(--border); display:flex;
          align-items:center; justify-content:center; gap:8px; }
.workspace { flex:1; min-height:0; position:relative; display:flex; }
.canvas-wrap { flex:1; min-width:0; position:relative; }
.drawer { width:380px; border-left:1px solid var(--border);
          background:var(--surface); overflow-y:auto; padding:16px;
          flex:0 0 380px; }
@media (max-width:1279px) {
  .drawer { position:absolute; top:0; right:0; bottom:0;
            width:min(380px, 90vw); z-index:25; flex:none; }
}
.node-card { background:var(--surface); border:1px solid var(--border);
             border-radius:8px; padding:8px 12px; width:180px; color:var(--text); }
.node-concept { border-left:4px solid var(--accent); }
.node-code { border-left:4px solid #64748b; }
.node-cluster { border:2px dashed var(--accent); background:#0e1626; }
.node-label { font-size:13px; font-weight:600; }
.node-badges { margin-top:4px; display:flex; gap:4px; flex-wrap:wrap; }
.badge { font-size:10px; padding:1px 6px; border-radius:8px;
         background:#1c2a44; color:var(--muted); }
.badge-bridge { background:#3b2f14; color:var(--warn); }
.badge-hot { background:#3a1420; color:var(--bad); }
.legend { position:absolute; bottom:14px; left:14px; display:flex; gap:6px; }
.chip { font-size:11px; padding:2px 8px; border-radius:10px;
        background:var(--surface); border:1px solid var(--border); }
.chip-concept { border-left:4px solid var(--accent); }
.chip-code { border-left:4px solid #64748b; }
.chip-impl { border-left:4px solid #4a9b5e; }
.chip-prereq { border-left:4px solid #cc8855; }
.pill { padding:4px 12px; border-radius:14px; border:1px solid var(--border);
        background:var(--surface); color:var(--muted); cursor:pointer; font-size:13px; }
.pill.active { background:var(--accent); color:#fff; }
.card { background:var(--bg); border:1px solid var(--border); border-radius:8px;
        padding:10px; margin:8px 12px; cursor:pointer; }
.card:hover { border-color:var(--accent); }
.sev { font-size:10px; font-weight:700; padding:1px 6px; border-radius:6px; }
.sev-HIGH { color:var(--bad); background:#3a1420; }
.sev-MED { color:var(--warn); background:#3b2f14; }
.sev-LOW { color:var(--muted); background:#1c2a44; }
.playerbar { position:absolute; bottom:18px; left:50%; transform:translateX(-50%);
             background:var(--surface); border:1px solid var(--border);
             border-radius:22px; padding:8px 18px; display:flex; gap:14px;
             align-items:center; z-index:20; }
.tour-overlay { position:absolute; bottom:26px; right:26px; width:300px; z-index:30;
                background:var(--surface); border:1px solid var(--accent);
                border-radius:10px; padding:16px; box-shadow:0 10px 25px #0008; }
.tier details { border-bottom:1px solid var(--border); padding:6px 0; }
.tier summary { cursor:pointer; font-weight:600; }
.tooltip { border-bottom:1px dotted var(--accent); cursor:help; position:relative; }
.tooltip:hover::after { content:attr(data-def); position:absolute; left:0; top:1.4em;
   background:var(--bg); border:1px solid var(--border); padding:6px 8px;
   border-radius:6px; font-size:12px; width:240px; z-index:40; }
```

- [ ] **Step 6:** `npm test && npm run build` → PASS; `npm run dev` shows the AIAYN graph as cards with edges and legend, with ELK topology calculation running in a Worker.
- [ ] **Step 7: Commit** — `git commit -am "feat(dashboard): shell, store, canvas with card nodes"`

### Task 2: Insights panel + trace tab + context switcher + filter pills

**Files:**
- Create: `dashboard/src/components/Sidebar.tsx`, `dashboard/src/components/TopBar.tsx`
- Modify: `dashboard/src/App.tsx` (fill `#left-panel` and `#topbar` slots)

**Interfaces:** consumes `computeInsights`, `KE_DATA.trace`, `useCenterOn`.

- [ ] **Step 1:** `components/Sidebar.tsx`:

```tsx
import { useMemo } from "react";
import { KE_DATA } from "../data.gen";
import { computeInsights } from "../lib/insights";
import { useApp } from "../store";
import { useCenterOn } from "./Canvas";

export default function Sidebar() {
  const { sidebarTab, setSidebarTab, setSelected } = useApp();
  const centerOn = useCenterOn();
  const insights = useMemo(() => computeInsights(KE_DATA as never), []);
  const go = (id: string) => { setSelected(id); centerOn(id); };
  return (
    <div>
      <div style={{ display: "flex", gap: 8, padding: 12 }}>
        <button className={`pill ${sidebarTab === "insights" ? "active" : ""}`}
          onClick={() => setSidebarTab("insights")}>Insights & Health</button>
        <button className={`pill ${sidebarTab === "trace" ? "active" : ""}`}
          onClick={() => setSidebarTab("trace")}>Build Trace</button>
      </div>
      {sidebarTab === "insights" && insights.map((i, k) => (
        <div key={k} className="card" onClick={() => go(i.nodeId)}>
          <span className={`sev sev-${i.severity}`}>{i.severity}</span>
          <div style={{ fontSize: 13, marginTop: 6 }}>{i.rule}</div>
          <div style={{ fontSize: 12, color: "var(--muted)" }}>{i.text}</div>
        </div>
      ))}
      {sidebarTab === "insights" && insights.length === 0 && (
        <div className="card">no findings — healthy graph</div>
      )}
      {sidebarTab === "trace" &&
        (KE_DATA.trace as { nodeId: string; phase: string; status: string;
                            date: string }[]).map((t, k) => (
          <div key={k} className="card" onClick={() => go(t.nodeId)}>
            <div style={{ fontSize: 12 }}>
              <b>{t.nodeId}</b> — {t.phase} [{t.status}] {t.date}
            </div>
          </div>
        ))}
    </div>
  );
}
```

- [ ] **Step 2:** `components/TopBar.tsx`:

```tsx
import { useApp } from "../store";

const VIEWS = ["concepts", "clusters", "code", "bridged"] as const;
const EDGE_KINDS = ["implements", "prerequisite", "builds-on"];

export default function TopBar() {
  const { view, setView, hiddenKinds, toggleKind, blastOn, setBlastOn } = useApp();
  return (
    <>
      {VIEWS.map((v) => (
        <button key={v} className={`pill ${view === v ? "active" : ""}`}
          onClick={() => setView(v)}>{v}</button>
      ))}
      <span style={{ width: 18 }} />
      {EDGE_KINDS.map((k) => (
        <button key={k} className={`pill ${hiddenKinds.has(k) ? "" : "active"}`}
          onClick={() => toggleKind(k)}>{k}</button>
      ))}
      <button className={`pill ${blastOn ? "active" : ""}`}
        onClick={() => setBlastOn(!blastOn)}>blast radius</button>
      <SearchBox />
    </>
  );
}

function SearchBox() {
  const { setSelected } = useApp();
  const centerOn = useCenterOn();
  return (
    <input
      placeholder="search… (Enter)"
      style={{ marginLeft: 12, padding: "5px 10px", borderRadius: 14,
               border: "1px solid var(--border)", background: "var(--bg)",
               color: "var(--text)", fontSize: 13 }}
      onKeyDown={(e) => {
        if (e.key !== "Enter") return;
        const q = (e.target as HTMLInputElement).value.toLowerCase().trim();
        if (!q) return;
        const hit = (KE_DATA.nodes as { id: string; label: string }[])
          .find((n) => n.label.toLowerCase().includes(q));
        if (hit) { setSelected(hit.id); centerOn(hit.id); }
      }}
    />
  );
}
```

(SearchBox imports: add `import { KE_DATA } from "../data.gen";` and
`import { useCenterOn } from "./Canvas";` to TopBar.tsx.)

- [ ] **Step 3:** In `App.tsx` replace the two empty slots: `<aside className="sidebar"><Sidebar /></aside>` and `<header className="topbar"><TopBar /></header>` (imports added). Sidebar/TopBar must render INSIDE `ReactFlowProvider` (useCenterOn needs it) — they already are.
- [ ] **Step 4:** `npm test && npm run build` → PASS. Dev check via `npm run dev`: clicking an insight centers + selects its node; pills toggle views/edges; blast toggle ghosts.
- [ ] **Step 5: Commit** — `git commit -am "feat(dashboard): insights/trace sidebar + context switcher + pills"`

### Task 3: Explain drawer (tiers, KaTeX, glossary, formula-link, bridge, impact)

**Files:**
- Create: `dashboard/src/components/Drawer.tsx`, `dashboard/src/lib/mathHtml.ts`
- Modify: `dashboard/src/App.tsx` (drawer slot)

**Interfaces:**
- `renderTierHtml(md: string) -> string` in `mathHtml.ts`: markdown→HTML is NOT redone here — 11a bundles page markdown; drawer renders it with `react-markdown` + a KaTeX pass. Math delimiters `$$...$$` become `<span class="math">` pre-pass (mirror of the lite exporter).

- [ ] **Step 1:** `lib/mathHtml.ts`:

```ts
import katex from "katex";
import "katex/dist/katex.min.css";

// $$...$$ display math -> rendered KaTeX html; inline \( \) likewise.
export function renderMathHtml(text: string): string {
  const render = (tex: string, display: boolean) => {
    try { return katex.renderToString(tex, { displayMode: display,
                                             throwOnError: false }); }
    catch { return tex; }
  };
  return text
    .replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => render(tex, true))
    .replace(/\\\((.+?)\\\)/g, (_, tex) => render(tex, false));
}

export function wrapGlossary(html: string,
                             glossary: Record<string, string>): string {
  for (const [sym, def] of Object.entries(glossary)) {
    const safe = sym.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    html = html.replace(new RegExp(`(?<![\\w-])${safe}(?![\\w-])`, "g"),
      `<span class="tooltip" data-def="${def.replace(/"/g, "&quot;")}">${sym}</span>`);
  }
  return html;
}
```

- [ ] **Step 2:** `components/Drawer.tsx`:

```tsx
import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { KE_DATA } from "../data.gen";
import { dependencyRings, dependentsOf } from "../lib/deps";
import { renderMathHtml, wrapGlossary } from "../lib/mathHtml";
import { useApp } from "../store";
import { useCenterOn } from "./Canvas";
import type { KEEdge, KENode } from "../types";

const TIERS = ["tldr", "intuition", "mechanics", "the-math", "go-deeper"];
const TIER_LABEL: Record<string, string> = { tldr: "TL;DR", intuition: "Intuition",
  mechanics: "Mechanics", "the-math": "The Math", "go-deeper": "Go Deeper" };

function splitTiers(md: string): Record<string, string> {
  const out: Record<string, string> = {};
  const re = /^## .+?\{#([\w-]+)\}\s*$/gm;
  const marks = [...md.matchAll(re)];
  marks.forEach((m, i) => {
    const end = i + 1 < marks.length ? marks[i + 1].index! : md.length;
    out[m[1]] = md.slice(m.index! + m[0].length, end).trim();
  });
  return out;
}

export default function Drawer() {
  const { selected, setSelected, setHoverEq } = useApp();
  const centerOn = useCenterOn();
  if (!selected) return null;

  const node = (KE_DATA.nodes as KENode[]).find((n) => n.id === selected);
  if (!node) return null;
  const edges = KE_DATA.edges as KEEdge[];
  const pageMd = (KE_DATA.pages as Record<string, string>)[selected];
  const note = (KE_DATA.notes as Record<string, never>)[selected];
  const glossary =
    (KE_DATA.glossary as Record<string, Record<string, string>>)[selected] ?? {};
  const tiers = useMemo(() => (pageMd ? splitTiers(pageMd) : {}), [pageMd]);
  const rings = useMemo(() => dependencyRings(selected, edges), [selected]);
  const depth1 = [...rings.values()].filter((d) => d === 1).length;
  const depth2 = [...rings.values()].filter((d) => d === 2).length;
  const implementedBy = edges.filter(
    (e) => e.kind === "implements" && e.dst === selected).map((e) => e.src);
  const implementsWhat = edges.filter(
    (e) => e.kind === "implements" && e.src === selected).map((e) => e.dst);
  const myEqs = Object.entries(KE_DATA.eqIndex as Record<string, string[]>)
    .filter(([, ids]) => ids.includes(selected)).map(([eq]) => eq);

  const html = (body: string) =>
    wrapGlossary(renderMathHtml(body), glossary);

  return (
    <div>
      <h2>{node.label}</h2>
      <p style={{ color: "var(--muted)", fontSize: 13 }}>
        {node.kind} · {node.source_ref ?? "—"} · depends-on-this:
        immediate {depth1}, secondary {depth2}
      </p>
      {(implementedBy.length > 0 || implementsWhat.length > 0) && (
        <div className="card" style={{ margin: "8px 0" }}>
          {implementedBy.map((id) => (
            <div key={id} onClick={() => { setSelected(id); centerOn(id); }}
              style={{ cursor: "pointer", fontSize: 13 }}>⚙ implemented by {id}</div>
          ))}
          {implementsWhat.map((id) => (
            <div key={id} onClick={() => { setSelected(id); centerOn(id); }}
              style={{ cursor: "pointer", fontSize: 13 }}>📄 implements {id}</div>
          ))}
        </div>
      )}
      {myEqs.length > 0 && (
        <p style={{ fontSize: 12, color: "var(--muted)" }}
           onMouseLeave={() => setHoverEq(null)}>
          equations:{" "}
          {myEqs.map((eq) => (
            <span key={eq} className="pill" style={{ marginRight: 4 }}
              onMouseEnter={() => setHoverEq(eq)}>{eq}</span>
          ))}
        </p>
      )}
      {pageMd ? (
        <div className="tier">
          {TIERS.filter((t) => tiers[t]).map((t) => (
            <details key={t} open={t === "tldr"}>
              <summary>{TIER_LABEL[t]}</summary>
              <div dangerouslySetInnerHTML={{ __html: html(tiers[t]) }} />
            </details>
          ))}
        </div>
      ) : note ? (
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {(note as { synthesis: string }).synthesis}
        </ReactMarkdown>
      ) : (
        <p className="muted" style={{ color: "var(--muted)" }}>
          no page or note for this node yet
        </p>
      )}
    </div>
  );
}
```

Hover-eq behavior: `Canvas` already outlines nodes in `eqIndex[hoverEq]` (11b Task 1) — hovering the equation pill flashes every node anchored to that equation (design feature 9, equation-level).

- [ ] **Step 3:** App.tsx drawer slot — hide the drawer entirely when nothing is selected: add `const selected = useApp((s) => s.selected);` in `App` and render `{selected && <aside className="drawer"><Drawer /></aside>}` inside `.workspace`, after `.canvas-wrap`. The CSS above keeps it as a 380px flex rail at viewport widths ≥1280px and changes it below 1280px to a border-only right-side overlay positioned against `.workspace` with `top:0` and `bottom:0`; it has no drawer shadow and cannot overlap a wrapped top toolbar.
- [ ] **Step 4:** `npm test && npm run build` → PASS. With internet access disabled, use `npm run dev`; select an SDPA-like node and verify the drawer shows tiers, KaTeX math/fonts load only from localhost, glossary terms show hover tooltips, and implements rows jump-navigate.
- [ ] **Step 5: Commit** — `git commit -am "feat(dashboard): explain drawer (katex, glossary, formula-link, bridge, impact)"`

### Task 4: Player bar + guided tour + code excerpts

**Files:**
- Create: `dashboard/src/components/PlayerBar.tsx`, `dashboard/src/components/TourOverlay.tsx`, `dashboard/src/components/CodeViewer.tsx`
- Modify: `dashboard/src/components/Drawer.tsx` (mount CodeViewer for code nodes), `dashboard/src/App.tsx` (mount PlayerBar + TourOverlay), `dashboard/build_data.py` + `dashboard/tests/test_build_data.py` (code excerpts)

**Interfaces:**
- Player mode is graph-kind-exclusive: paper/concept graphs expose only the reading path using `KE_DATA.tour` node order; code/bridged graphs expose only blast trace using `dependencyRings` sorted by depth. `excerpts: {node_id: string}` joins the bundle (11a contract addendum).

- [ ] **Step 1 (TDD, python side): failing test for excerpts** — append to `tests/test_build_data.py`:

```python
def test_code_excerpts_only_for_hotspots_and_capped(tmp_path):
    repo = tmp_path / "repo"; repo.mkdir()
    (repo / "big.py").write_text("\n".join(f"line{i}" for i in range(200)),
                                 encoding="utf-8")
    graph = {"meta": {"kind": "code", "source": "x", "generated": "2026-07-09",
                      "version": 1},
             "nodes": [{"id": "big.py::f", "kind": "function", "label": "f",
                        "source_ref": "big.py:L1"},
                       {"id": "cold.py::g", "kind": "function", "label": "g",
                        "source_ref": "cold.py:L1"}],
             "edges": []}
    b = build_bundle(graph, hotspots=[{"id": "big.py::f"}], repo_dir=repo)
    assert "big.py::f" in b["excerpts"]
    assert len(b["excerpts"]["big.py::f"].splitlines()) <= 80
    assert "cold.py::g" not in b["excerpts"]     # not a hotspot, no implements
```

- [ ] **Step 2: RED**, then implement in `build_data.py` — add to `build_bundle` (before return) and `"excerpts": excerpts` to the dict:

```python
    excerpts = {}
    if repo_dir and plan_graph["meta"].get("kind") in ("code", "bridged"):
        keep = {h["id"] for h in hotspots[:20]}
        keep |= {e["src"] for e in plan_graph["edges"] if e["kind"] == "implements"}
        for n in plan_graph["nodes"]:
            if n["id"] not in keep or ":" not in (n.get("source_ref") or ""):
                continue
            fname, loc = n["source_ref"].rsplit(":", 1)
            f = Path(repo_dir) / fname
            if not f.is_file():
                continue
            start = max(int(re.sub(r"\D", "", loc) or 1) - 1, 0)
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            excerpts[n["id"]] = "\n".join(lines[start:start + 80])
```

GREEN, regenerate fixture bundle (no excerpts for AIAYN — key present, empty), commit.

- [ ] **Step 3:** `components/PlayerBar.tsx`:

```tsx
import { KE_DATA } from "../data.gen";
import { dependencyRings } from "../lib/deps";
import { useApp } from "../store";
import { useCenterOn } from "./Canvas";
import type { KEEdge } from "../types";

export default function PlayerBar() {
  const { player, setPlayer, step, selected, setSelected } = useApp();
  const centerOn = useCenterOn();
  const graphKind = (KE_DATA.meta as { kind: "concept" | "code" | "bridged" }).kind;
  const isConceptGraph = graphKind === "concept";

  const startReading = () => {
    if (!isConceptGraph) return;
    const steps = (KE_DATA.tour as { nodeIds: string[] }[]).map((s) => s.nodeIds[0]);
    setPlayer({ steps, idx: 0, label: "Reading path" });
    setSelected(steps[0]); centerOn(steps[0]);
  };
  const startTrace = () => {
    if (isConceptGraph || !selected) return;
    const rings = dependencyRings(selected, KE_DATA.edges as KEEdge[], 3);
    const steps = [selected,
      ...[...rings.entries()].sort((a, b) => a[1] - b[1]).map(([id]) => id)];
    setPlayer({ steps, idx: 0, label: `Blast radius of ${selected}` });
  };
  const move = (d: 1 | -1) => {
    if (!player) return;
    const idx = Math.min(Math.max(player.idx + d, 0), player.steps.length - 1);
    step(d); setSelected(player.steps[idx]); centerOn(player.steps[idx]);
  };

  if (!player)
    return (
      <div className="playerbar">
        {isConceptGraph ? (
          <button className="pill" onClick={startReading}>▶ reading path</button>
        ) : (
          <button className="pill" onClick={startTrace} disabled={!selected}>
            ▶ trace blast radius</button>
        )}
      </div>
    );
  return (
    <div className="playerbar">
      <button className="pill" onClick={() => move(-1)}>◀</button>
      <span style={{ fontSize: 13 }}>
        {player.label} — step {player.idx + 1} / {player.steps.length}</span>
      <button className="pill" onClick={() => move(1)}>▶</button>
      <button className="pill" onClick={() => setPlayer(null)}>✕</button>
    </div>
  );
}
```

- [ ] **Step 4:** `components/TourOverlay.tsx`:

```tsx
import { KE_DATA } from "../data.gen";
import { useApp } from "../store";
import { useCenterOn } from "./Canvas";

export default function TourOverlay() {
  const { tourIdx, setTourIdx, setSelected } = useApp();
  const centerOn = useCenterOn();
  const tour = KE_DATA.tour as { order: number; title: string;
                                 description: string; nodeIds: string[] }[];
  if (tour.length === 0) return null;
  if (tourIdx === null)
    return (
      <div className="tour-overlay">
        <h3 style={{ color: "var(--accent)", margin: 0 }}>Guided tour</h3>
        <p style={{ fontSize: 13 }}>Walk the {tour.length} key concepts.</p>
        <button className="pill active" onClick={() => {
          setTourIdx(0); setSelected(tour[0].nodeIds[0]); centerOn(tour[0].nodeIds[0]);
        }}>Start</button>
      </div>
    );
  const s = tour[tourIdx];
  const go = (i: number) => {
    setTourIdx(i); setSelected(tour[i].nodeIds[0]); centerOn(tour[i].nodeIds[0]);
  };
  return (
    <div className="tour-overlay">
      <h3 style={{ color: "var(--accent)", margin: 0 }}>{s.title}</h3>
      <p style={{ fontSize: 13 }}>{s.description}</p>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <button className="pill" disabled={tourIdx === 0}
          onClick={() => go(tourIdx - 1)}>Back</button>
        <span style={{ fontSize: 12, color: "var(--muted)" }}>
          {tourIdx + 1}/{tour.length}</span>
        {tourIdx < tour.length - 1
          ? <button className="pill active" onClick={() => go(tourIdx + 1)}>Next</button>
          : <button className="pill" onClick={() => setTourIdx(null)}>Finish</button>}
      </div>
    </div>
  );
}
```

- [ ] **Step 5:** `components/CodeViewer.tsx` + Drawer hookup:

```tsx
import { Highlight, themes } from "prism-react-renderer";
import { KE_DATA } from "../data.gen";

export default function CodeViewer({ nodeId }: { nodeId: string }) {
  const code = (KE_DATA.excerpts as Record<string, string>)?.[nodeId];
  if (!code) return null;
  return (
    <Highlight theme={themes.nightOwl} code={code} language="python">
      {({ style, tokens, getLineProps, getTokenProps }) => (
        <pre style={{ ...style, padding: 10, borderRadius: 8, fontSize: 12,
                      overflowX: "auto" }}>
          {tokens.map((line, i) => (
            <div key={i} {...getLineProps({ line })}>
              {line.map((tok, k) => <span key={k} {...getTokenProps({ token: tok })} />)}
            </div>
          ))}
        </pre>
      )}
    </Highlight>
  );
}
```

In `Drawer.tsx`, after the bridge card: `{["function","class","file","route"].includes(node.kind) && <CodeViewer nodeId={selected} />}`.

- [ ] **Step 6:** Mount both controls inside `.canvas-wrap`: replace its `<div id="playerbar" />` with `<PlayerBar />` and `<div id="tour-overlay" />` with `<TourOverlay />`. Their absolute positioning is therefore canvas-relative, so opening the 380px desktop drawer cannot shift the player or cover the tour. `npm test && npm run build` → PASS.
- [ ] **Step 7: Commit** — `git commit -am "feat(dashboard): player bar, guided tour, code excerpts"`

### Task 5: Semantic zoom (LOD)

**Files:**
- Modify: `dashboard/src/components/Canvas.tsx`

- [ ] **Step 1:** In Canvas, read zoom via `useStore` and merge LOD:

```tsx
import { useStore } from "@xyflow/react";
import { visibleAtZoom } from "../lib/lod";
// inside component:
const zoom = useStore((s) => s.transform[2]);
const lod = useMemo(
  () => visibleAtZoom(zoom, 0.5,
    KE_DATA.clusters as { id: string; label: string; nodeIds: string[] }[],
    keNodes.map((n) => n.id)),
  [zoom]);
```

Filter `nodes` additionally by `!lod.hiddenNodes.has(n.id)`; when `lod.showClusters || view === "clusters"`, append cluster container nodes:

```tsx
const clusterNodes: Node[] = (lod.showClusters || view === "clusters")
  ? (KE_DATA.clusters as { id: string; label: string; nodeIds: string[] }[])
      .map((c, i) => ({
        id: `cluster:${c.id}`, type: "cluster",
        position: pos.get(c.nodeIds[0]) ?? { x: i * 220, y: 0 },
        data: { label: c.label, count: c.nodeIds.length },
      }))
  : [];
```

and render `nodes={[...clusterNodes, ...nodes]}`. Cluster click zooms in: in `onNodeClick`, if `n.id.startsWith("cluster:")` call `flow.zoomTo(0.9, { duration: 500 })` instead of selecting.

- [ ] **Step 2:** `npm test && npm run build` → PASS. Dev check via `npm run dev`: zoom out < 0.5 → clusters replace members; zoom in → members return.
- [ ] **Step 3: Commit** — `git commit -am "feat(dashboard): semantic zoom LOD"`

### Task 6: Explain skill port + attribution + wrap-up

**Files:**
- Create: `Deepwiki/skills/explain/SKILL.md`, `dashboard/README.md`
- Modify: `plans/2026-07-09-INDEX.md` (status row)

- [ ] **Step 1:** `Deepwiki/skills/explain/SKILL.md` (UA port, our schema):

```markdown
---
name: explain
description: Use when you need a deep-dive explanation of a specific concept, file, function, or module in a Knowledge-Engine graph (concept_graph.json / code_graph.json / bridged graph)
argument-hint: "[node-id or file-path]"
---

# /explain

Provide a thorough, in-depth explanation of one graph node. Adapted from
Understand-Anything's understand-explain skill (MIT).

## Graph structure reference (§5.1)

- `meta` — {kind: code|concept|bridged, source, generated, version}
- `nodes[]` — {id, kind, label, level?, page?, anchor?, source_ref?}
  - kinds: file, class, function, route, concept, equation, figure
  - ids: concepts are kebab-slugs ("scaled-dot-product-attention");
    code ids are "path::Entity" ("src/fetch_clean.py::fetch_clean")
- `edges[]` — {src, dst, kind, weight, confidence, confidence_score}
  - kinds: part-of, imports, calls, inherits, prerequisite, builds-on,
    defined-in, contrasts-with, implements (src=code, dst=concept)

## How to read efficiently (kept verbatim from UA — it works)

1. Grep within the JSON for relevant entries BEFORE reading the full file
2. Only read sections you need — don't dump the entire graph into context
3. Node labels and source_refs are the most useful fields
4. Edges tell you how components connect — follow implements both ways

## Tools you already have

- `python -m research_mcp.graph_query explore <graph.json> <node-id>` —
  composite card: neighbors by kind, impact count, staleness banner
- `python -m research_mcp.graph_query impact <graph.json> <node-id>` —
  who depends on this (blast radius)
- Research notes live at `$RESEARCH_MCP_HOME/_research_wiki/<id>.yaml`;
  wiki pages next to the graph under `pages/NN_<id>.md`

## Output shape

1. One-paragraph role summary (what it is, why it exists)
2. Structure: neighbors grouped by edge kind (from explore)
3. Blast radius: what breaks/changes if this changes (from impact)
4. For concepts: the math intuition from the page's Mechanics/The Math tiers
   For code: key call paths + the concepts it implements
5. Honest gaps: unresolved note questions, ambiguous edges
```

- [ ] **Step 2:** `dashboard/README.md`:

```markdown
# Knowledge Dashboard

Internet-disconnected localhost dashboard for Knowledge-Engine graphs (papers, code, bridged).
Build: `npm install && python build_data.py --graph <g.json> [...] && npm test && npm run build`.
Development: `npm run dev` and open the printed localhost URL.
Production: `python -m http.server -d dist 8000` and open `http://localhost:8000/`.
The dashboard requires no internet connection or backend service; all application data, KaTeX fonts, and assets remain local.

## Attribution
UI paradigms and component patterns adapted from
[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) (MIT)
— guided tour, layer legend, filter panel, explain drawer — and
[TrueCourse](https://github.com/truecourse-ai/truecourse) (MIT) — insights
sidebar, context switcher, trace player, diff/staleness paradigms.
The /explain skill is adapted from Understand-Anything's understand-explain (MIT).
```

- [ ] **Step 3:** Full check: `npm test && npm run build && python -m pytest tests/ -q` all green. Then run `python -m http.server -d dist 8000` for the production smoke check.
- [ ] **Step 4: Commit** — `git commit -am "feat: explain skill port + dashboard README/attribution"`

### Review gate (slice 11b) — owner acceptance, network disabled

- [ ] With internet access disabled, run `cd dashboard && python -m http.server -d dist 8000` and open `http://localhost:8000/`: AIAYN cards render; tour Start→Next flies the camera through 5 concepts; insights panel lists ≥1 card and click-centers; drawer shows tiers with locally loaded KaTeX-rendered √dₖ and glossary tooltips; hovering an equation pill flashes anchored nodes; reading-path player walks in topo order; blast-radius toggle ghosts correctly on scaled-dot-product-attention; zooming out swaps to cluster cards; ELK layout runs in a Worker without freezing interaction; DevTools shows zero requests to non-local origins.
- [ ] Update INDEX status. Commit.

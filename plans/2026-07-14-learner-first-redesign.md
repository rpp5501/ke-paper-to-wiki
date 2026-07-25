# Learner-First Dashboard Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the guided, distilled learning path the *default* experience of the paper dashboard — plain-language first, math second, code third — with the full 24-node graph demoted to an explicit "Explore" mode.

**Architecture:** Add a two-mode shell (`learn` | `explore`) to the existing Zustand store. Learn mode replaces the diagnostics sidebar with a numbered concept path (the existing tour data, enriched with real per-step blurbs generated in `build_data.py`), filters the canvas to the current step's 1-hop neighborhood, and auto-opens the reordered explanation drawer (TL;DR always visible → Intuition → Mechanics → The Math → code last). Explore mode is today's app unchanged. No new dependencies, no new backend capability — this is a reorder/redesign of shipped pieces.

**Tech Stack:** Existing only — Vite + React 18 + TypeScript, Zustand, @xyflow/react + ELK worker, KaTeX, vitest + @testing-library, Python (`build_data.py`) + pytest.

**Working directory:** everything below is relative to `paper-skill-slice9-bridge/` (the canonical worktree, branch `slice9-bridge`). Do NOT touch the other `paper-skill-slice*` folders.

## Context you must know before starting

- **Data flow is one-way and locked:** `graph.json` + `pack.json` → `dashboard/build_data.py` → `dashboard/src/data.gen.ts` → app. Never fetch at runtime. `data.gen.ts` is generated — never hand-edit it; regenerate with the command in "Fast iteration loop" below.
- **Fully offline, zero network, no API keys.** No new fonts, CDNs, or packages.
- **What already exists (reuse, don't rebuild):**
  - `KE_DATA.tour` — 5 curated steps `{order, title, description, nodeIds}` (descriptions are currently boilerplate: *"Next stop on the dependency-ordered reading path."* — fixed in Task 3).
  - `splitTiers()` in `src/lib/mathHtml.ts` — splits page markdown into `tldr / intuition / mechanics / the-math / go-deeper` tiers.
  - `readingPathSteps()` in `src/components/PlayerBar.tsx` — ordered tour node ids.
  - `useNodeNavigation()` → `queueNavigation()` — selecting a node opens the drawer and centers the camera (via `NavigationCoordinator`).
  - `TourOverlay.tsx` — the current opt-in tour card (kept for explore mode only).
- **Design contract:** `plans/2026-07-09-slice11-UI-SPEC.md` (Deepwiki root). Locked tokens: `--bg #0b1220`, `--surface #111a2c`, `--border #1e293b`, `--text #e2e8f0`, `--muted #94a3b8`, `--accent #4a7ebb`, `--warn #eab308`, `--bad #ef4444`; `system-ui` type stack; hover/focus transitions 120–180ms, never `transition: all`; every interactive item gets a visible 2px accent focus outline with 2px offset; surface-shift depth, no gradients/shadows.
- **Note on the handoff's "sidebar TOC" observation:** the current `Sidebar.tsx` is actually Insights/Trace diagnostics. The "flattened 24-node outline with L1/L2/L3 tags" the owner saw is the *graph canvas itself* (ELK layered layout + `L{n}` badges on every node card reads like a PDF outline). Tasks 6 and 9 fix that; Task 4 gives the sidebar a real learning TOC.

## Global Constraints

- Fully offline; zero network calls; no API keys; no new npm/pip dependencies.
- One-way data flow (`build_data.py` → `data.gen.ts`); app never computes pipeline-side data at runtime.
- Keep `npm test` (vitest, `dashboard/`) and `pytest` (`dashboard/tests/`, repo root) green — update tests deliberately in the same task as the behavior change.
- Honor the locked UI-SPEC palette/typography/motion values verbatim (listed above).
- Semantic colors keep their meanings (concept blue, code slate, implements green `#4a9b5e`, prerequisite/builds-on `#cc8855` dashed, severity/ring colors).
- All work in `paper-skill-slice9-bridge/` on branch `slice9-bridge`; commit after every task.

## Fast iteration loop

```powershell
cd paper-skill-slice9-bridge/dashboard
npm install
python build_data.py --graph ..\fixtures\aiayn_concept_graph.json --pack ..\fixtures\aiayn_tiny_pack.json --pages-dir ..\fixtures\pages --wiki-dir ..\fixtures\wiki
npm run dev
```

---

### Task 1: Store — app mode + learn progress

**Files:**
- Modify: `dashboard/src/store.ts`
- Test: `dashboard/src/store.test.ts`

**Interfaces:**
- Produces: `Mode = "learn" | "explore"`; `AppState.mode: Mode`, `setMode(mode: Mode)`, `completedSteps: Set<string>`, `markStepComplete(nodeId: string)`. Default `mode === "learn"`, `completedSteps` empty. `setMode("explore")` must NOT clear progress. Later tasks (4, 5, 6, 7) consume these exact names.

- [ ] **Step 1: Write the failing tests** — append to `dashboard/src/store.test.ts`, following the file's existing reset pattern (if it resets via `useApp.setState(...)` in `beforeEach`, extend that reset with `mode: "learn", completedSteps: new Set()`):

```ts
describe("mode & learn progress", () => {
  it("defaults to learn mode with no completed steps", () => {
    expect(useApp.getState().mode).toBe("learn");
    expect(useApp.getState().completedSteps.size).toBe(0);
  });

  it("switches modes without clearing progress", () => {
    useApp.getState().markStepComplete("attention");
    useApp.getState().setMode("explore");
    expect(useApp.getState().mode).toBe("explore");
    expect(useApp.getState().completedSteps.has("attention")).toBe(true);
  });

  it("markStepComplete is idempotent and does not mutate the previous set", () => {
    const before = useApp.getState().completedSteps;
    useApp.getState().markStepComplete("transformer");
    useApp.getState().markStepComplete("transformer");
    const after = useApp.getState().completedSteps;
    expect(after).toEqual(new Set(["transformer"]));
    expect(before.size).toBe(0); // immutability, matches hiddenKinds pattern
  });
});
```

- [ ] **Step 2: Run to verify failure**

Run: `npx vitest run src/store.test.ts` (from `dashboard/`)
Expected: FAIL — `mode` undefined.

- [ ] **Step 3: Implement.** In `store.ts`, add after the `View` type:

```ts
export type Mode = "learn" | "explore";
```

Add to `AppState`:

```ts
  mode: Mode;
  setMode: (mode: Mode) => void;
  completedSteps: Set<string>;
  markStepComplete: (nodeId: string) => void;
```

Add to the `create` initializer (mirror the `hiddenKinds` copy-on-write style):

```ts
  mode: "learn",
  setMode: (mode) => set({ mode }),
  completedSteps: new Set(),
  markStepComplete: (nodeId) =>
    set((state) => {
      if (state.completedSteps.has(nodeId)) return {};
      const completedSteps = new Set(state.completedSteps);
      completedSteps.add(nodeId);
      return { completedSteps };
    }),
```

- [ ] **Step 4: Run tests** — `npx vitest run src/store.test.ts` → PASS.
- [ ] **Step 5: Commit** — `git add dashboard/src/store.ts dashboard/src/store.test.ts && git commit -m "feat(store): learn/explore mode and step progress"`

---

### Task 2: Pure learn-path logic — `lib/learnPath.ts`

**Files:**
- Create: `dashboard/src/lib/learnPath.ts`
- Test: `dashboard/src/lib/learnPath.test.ts`
- Modify: `dashboard/src/components/Drawer.tsx` (replace its private `pageKey` with the shared helper — behavior identical)

**Interfaces:**
- Consumes: `splitTiers` from `./mathHtml`; `KENode`, `KEEdge` from `../types`.
- Produces (exact signatures used by Tasks 4–6):

```ts
export type TourSourceStep = { order: number; title: string; description: string; nodeIds: string[] };
export type LearnStep = { nodeId: string; title: string; blurb: string };
export function pageMarkdownFor(node: KENode & { page?: string }, pages: Record<string, string>): string | undefined;
export function buildLearnSteps(tour: TourSourceStep[], nodes: KENode[], pages: Record<string, string>): LearnStep[];
export function focusNodeIds(stepNodeId: string, edges: KEEdge[], completed: Set<string>): Set<string>;
```

(The `TourSourceStep` type moves here from `TourOverlay.tsx`; TourOverlay re-exports it for backwards compatibility.)

- [ ] **Step 1: Write the failing tests** — create `dashboard/src/lib/learnPath.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { buildLearnSteps, focusNodeIds, pageMarkdownFor } from "./learnPath";

const NODES = [
  { id: "a", kind: "concept", label: "Alpha", page: "01_a.md" },
  { id: "b", kind: "concept", label: "Beta" },
];
const PAGES = {
  a: "## TL;DR {#tldr}\nAlpha is the core idea. It has $x^2$ math.\n\n## The Math {#the-math}\n$$x$$",
};
const TOUR = [
  { order: 2, title: "Beta", description: "fallback blurb", nodeIds: ["b"] },
  { order: 1, title: "Alpha", description: "generic", nodeIds: ["a"] },
];

describe("buildLearnSteps", () => {
  it("orders by tour order and prefers the TL;DR first sentence as blurb", () => {
    const steps = buildLearnSteps(TOUR, NODES, PAGES);
    expect(steps.map((s) => s.nodeId)).toEqual(["a", "b"]);
    expect(steps[0].blurb).toBe("Alpha is the core idea.");
  });

  it("falls back to the tour description when no page exists", () => {
    const steps = buildLearnSteps(TOUR, NODES, PAGES);
    expect(steps[1].blurb).toBe("fallback blurb");
  });

  it("skips steps whose node is missing", () => {
    const steps = buildLearnSteps(
      [{ order: 1, title: "Ghost", description: "", nodeIds: ["ghost"] }],
      NODES,
      PAGES,
    );
    expect(steps).toEqual([]);
  });
});

describe("pageMarkdownFor", () => {
  it("resolves by id, then by numbered-filename stem", () => {
    expect(pageMarkdownFor(NODES[0], PAGES)).toContain("Alpha is the core idea");
    expect(
      pageMarkdownFor({ id: "zzz", kind: "concept", label: "Z", page: "07_a.md" }, PAGES),
    ).toContain("Alpha is the core idea");
  });
});

describe("focusNodeIds", () => {
  const EDGES = [
    { src: "a", dst: "b", kind: "prerequisite" },
    { src: "c", dst: "a", kind: "builds-on" },
    { src: "d", dst: "e", kind: "prerequisite" },
  ];
  it("returns the step node, its 1-hop neighbors, and completed steps", () => {
    expect(focusNodeIds("a", EDGES, new Set(["e"]))).toEqual(new Set(["a", "b", "c", "e"]));
  });
  it("works with no edges", () => {
    expect(focusNodeIds("a", [], new Set())).toEqual(new Set(["a"]));
  });
});
```

- [ ] **Step 2: Run to verify failure** — `npx vitest run src/lib/learnPath.test.ts` → FAIL (module not found).

- [ ] **Step 3: Implement** — create `dashboard/src/lib/learnPath.ts`:

```ts
import type { KEEdge, KENode } from "../types";
import { splitTiers } from "./mathHtml";

export type TourSourceStep = {
  order: number;
  title: string;
  description: string;
  nodeIds: string[];
};

export type LearnStep = { nodeId: string; title: string; blurb: string };

export function pageMarkdownFor(
  node: KENode & { page?: string },
  pages: Record<string, string>,
): string | undefined {
  if (pages[node.id]) return pages[node.id];
  if (!node.page) return undefined;
  const stem = node.page.replace(/\.md$/i, "").replace(/^\d+_/, "");
  return pages[stem];
}

const MAX_BLURB = 180;

function firstSentence(markdown: string): string {
  const body = markdown
    .replace(/\$\$[\s\S]*?\$\$/g, "")
    .replace(/\\\([\s\S]*?\\\)/g, "")
    .replace(/[#*_`>[\]]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  if (!body) return "";
  const sentence = body.split(/(?<=[.!?])\s/)[0] ?? "";
  return sentence.length > MAX_BLURB
    ? `${sentence.slice(0, MAX_BLURB - 1).trimEnd()}…`
    : sentence;
}

export function buildLearnSteps(
  tour: TourSourceStep[],
  nodes: KENode[],
  pages: Record<string, string>,
): LearnStep[] {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  return [...tour]
    .sort((left, right) => left.order - right.order)
    .flatMap((step) => {
      const nodeId = step.nodeIds.find((candidate) => byId.has(candidate));
      if (!nodeId) return [];
      const node = byId.get(nodeId) as KENode & { page?: string };
      const markdown = pageMarkdownFor(node, pages);
      const tldr = markdown ? splitTiers(markdown).tldr : undefined;
      const blurb = (tldr && firstSentence(tldr)) || step.description;
      return [{ nodeId, title: step.title, blurb }];
    });
}

export function focusNodeIds(
  stepNodeId: string,
  edges: KEEdge[],
  completed: Set<string>,
): Set<string> {
  const visible = new Set([stepNodeId, ...completed]);
  edges.forEach((edge) => {
    if (edge.src === stepNodeId) visible.add(edge.dst);
    if (edge.dst === stepNodeId) visible.add(edge.src);
  });
  return visible;
}
```

- [ ] **Step 4: Deduplicate.** In `TourOverlay.tsx`, delete the local `TourSourceStep` type and replace with `export type { TourSourceStep } from "../lib/learnPath";` adjusted to its import style (`import type { TourSourceStep } from "../lib/learnPath"; export type { TourSourceStep };`). In `Drawer.tsx`, delete the private `pageKey` function and replace the lookup

```ts
  const fallbackPageKey = node ? pageKey(node) : null;
  const pageMarkdown = selected
    ? PAGES[selected] ?? (fallbackPageKey ? PAGES[fallbackPageKey] : undefined)
    : undefined;
```

with

```ts
  const pageMarkdown = node ? pageMarkdownFor(node, PAGES) : undefined;
```

importing `pageMarkdownFor` from `../lib/learnPath`.

- [ ] **Step 5: Run the full suite** — `npx vitest run` → all PASS (Drawer/App/TourOverlay tests confirm the refactor changed nothing).
- [ ] **Step 6: Commit** — `git commit -am "feat(lib): learnPath step/blurb/focus helpers; share page resolution"`

---

### Task 3: Real tour blurbs from `build_data.py`

**Files:**
- Modify: `dashboard/build_data.py` (`_tour`, its callsite ~line 268)
- Test: `dashboard/tests/test_build_data.py`
- Regenerate: `dashboard/src/data.gen.ts` (fixture command from "Fast iteration loop")

**Interfaces:**
- Produces: each tour step's `description` becomes the first sentence of that node's page TL;DR tier (math/markdown stripped, ≤180 chars); falls back to the current generic blurb when no page/TL;DR exists. Same JSON shape — no TS changes needed.

- [ ] **Step 1: Write the failing test** — append to `dashboard/tests/test_build_data.py` (match the module's existing import/fixture style):

```python
def test_tour_descriptions_use_page_tldr():
    plan_graph = {
        "meta": {"kind": "concept"},
        "nodes": [
            {"id": "a", "kind": "concept", "label": "Alpha", "level": 0,
             "page": "01_a.md"},
            {"id": "b", "kind": "concept", "label": "Beta", "level": 1},
        ],
        "edges": [{"src": "a", "dst": "b", "kind": "prerequisite"}],
    }
    pages = {"a": "## TL;DR {#tldr}\nAlpha is the core idea. More.\n"}
    tour = build_data._tour(plan_graph, [], pages)
    by_title = {t["title"]: t["description"] for t in tour}
    assert by_title["Alpha"] == "Alpha is the core idea."
    assert by_title["Beta"] == "Next stop on the dependency-ordered reading path."
```

(If the test module imports functions directly rather than via `build_data.`, follow that convention.)

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/test_build_data.py -k tour -x` (from `dashboard/`) → FAIL (`_tour` takes 2 args / description mismatch).

- [ ] **Step 3: Implement.** In `build_data.py`, add above `_tour`:

```python
_TLDR_RE = re.compile(r"^##\s+.+?\{#tldr\}\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)


def _page_for(node, pages):
    if node.get("id") in pages:
        return pages[node["id"]]
    stem = re.sub(r"\.md$", "", node.get("page") or "", flags=re.I)
    stem = re.sub(r"^\d+_", "", stem)
    return pages.get(stem)


def _first_sentence(markdown, limit=180):
    match = _TLDR_RE.search(markdown or "")
    body = (match.group(1) if match else markdown or "").strip()
    body = re.sub(r"\$\$.*?\$\$", "", body, flags=re.S)
    body = re.sub(r"\\\(.*?\\\)", "", body, flags=re.S)
    body = re.sub(r"[#*_`>\[\]]", "", body)
    body = " ".join(body.split())
    if not body:
        return ""
    sentence = re.split(r"(?<=[.!?])\s", body)[0]
    return sentence if len(sentence) <= limit else sentence[: limit - 1].rstrip() + "…"
```

Replace `_tour` with:

```python
def _tour(plan_graph, hotspots, pages):
    nodes = {n["id"]: n for n in plan_graph["nodes"]}
    if plan_graph["meta"].get("kind") == "code" and hotspots:
        picks = [h["id"] for h in hotspots[:5]]
        fallback = "High-churn, high-dependency hotspot — start here."
    else:
        picks = reading_path(plan_graph)[:5]
        fallback = "Next stop on the dependency-ordered reading path."
    steps = []
    for i, p in enumerate(picks):
        node = nodes.get(p, {"id": p, "label": p})
        blurb = _first_sentence(_page_for(node, pages)) or fallback
        steps.append({"order": i + 1, "title": node.get("label", p),
                      "description": blurb, "nodeIds": [p]})
    return steps
```

Update the callsite (~line 268): `"tour": _tour(plan_graph, hotspots, pages),` — the `pages` dict is already assembled in that scope for the `"pages"` bundle key; pass the same variable (check its local name and match it).

- [ ] **Step 4: Run tests** — `python -m pytest tests/ -x` → all PASS.
- [ ] **Step 5: Regenerate fixture data** — run the fixture command from "Fast iteration loop"; confirm `src/data.gen.ts` tour descriptions are now real sentences, then `npx vitest run` → PASS (tour tests use titles/order, not descriptions, but verify).
- [ ] **Step 6: Commit** — `git commit -am "feat(build_data): per-step tour blurbs from page TL;DR"`

---

### Task 4: LearnPanel — the learning TOC (new component)

**Files:**
- Create: `dashboard/src/components/LearnPanel.tsx`
- Test: `dashboard/src/components/LearnPanel.test.tsx`

**Interfaces:**
- Consumes: `buildLearnSteps` (Task 2); store fields `mode/setMode/tourIdx/setTourIdx/completedSteps/markStepComplete/selected/layoutPhase` (Task 1); `useNodeNavigation`; `navigationDisabledReason` from `../lib/navigation`; `CompactPill`.
- Produces: `export default function LearnPanel({ onCloseSheet }: { onCloseSheet: () => void })` — same prop contract as `Sidebar` so `App.tsx` can swap them (Task 5). Also `export const LEARN_STEPS: LearnStep[]` (module-level, from `KE_DATA`) — consumed by Tasks 5 and 6.

- [ ] **Step 1: Write the failing tests** — create `LearnPanel.test.tsx` (mirror the render/setup style of `Drawer.test.tsx`):

```tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import LearnPanel, { LEARN_STEPS } from "./LearnPanel";
import { useApp } from "../store";

beforeEach(() => {
  useApp.setState({
    mode: "learn",
    tourIdx: 0,
    completedSteps: new Set(),
    selected: null,
    layoutPhase: "ready",
  });
});

describe("LearnPanel", () => {
  it("renders one numbered step per tour entry with a blurb", () => {
    render(<LearnPanel onCloseSheet={() => {}} />);
    const items = screen.getAllByRole("listitem");
    expect(items).toHaveLength(LEARN_STEPS.length);
    expect(items[0]).toHaveTextContent(LEARN_STEPS[0].title);
    expect(items[0]).toHaveTextContent(LEARN_STEPS[0].blurb);
  });

  it("marks the current step and completed steps", () => {
    useApp.setState({ tourIdx: 1, completedSteps: new Set([LEARN_STEPS[0].nodeId]) });
    render(<LearnPanel onCloseSheet={() => {}} />);
    const buttons = screen.getAllByRole("button", { name: /step \d/i });
    expect(buttons[1]).toHaveAttribute("aria-current", "step");
    expect(buttons[0]).toHaveTextContent("✓");
  });

  it("clicking a step sets the index and marks it complete", () => {
    render(<LearnPanel onCloseSheet={() => {}} />);
    fireEvent.click(screen.getAllByRole("button", { name: /step \d/i })[2]);
    expect(useApp.getState().tourIdx).toBe(2);
    expect(useApp.getState().completedSteps.has(LEARN_STEPS[2].nodeId)).toBe(true);
  });

  it("offers an escape hatch to the full map", () => {
    render(<LearnPanel onCloseSheet={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /show the full map/i }));
    expect(useApp.getState().mode).toBe("explore");
  });
});
```

- [ ] **Step 2: Run to verify failure** — `npx vitest run src/components/LearnPanel.test.tsx` → FAIL.

- [ ] **Step 3: Implement** — create `LearnPanel.tsx`:

```tsx
import { KE_DATA } from "../data.gen";
import {
  buildLearnSteps,
  type LearnStep,
  type TourSourceStep,
} from "../lib/learnPath";
import { navigationDisabledReason } from "../lib/navigation";
import { useApp } from "../store";
import type { KENode } from "../types";
import CompactPill from "./CompactPill";
import { useNodeNavigation } from "./useNodeNavigation";

export const LEARN_STEPS: LearnStep[] = buildLearnSteps(
  KE_DATA.tour as TourSourceStep[],
  KE_DATA.nodes as KENode[],
  KE_DATA.pages as Record<string, string>,
);

const SOURCE = (KE_DATA.meta as { source?: string }).source ?? "this paper";

export default function LearnPanel({ onCloseSheet }: { onCloseSheet: () => void }) {
  const { tourIdx, setTourIdx, completedSteps, markStepComplete, setMode, layoutPhase } =
    useApp();
  const navigateToNode = useNodeNavigation();
  const done = LEARN_STEPS.filter((step) => completedSteps.has(step.nodeId)).length;

  const goTo = (index: number) => {
    const step = LEARN_STEPS[index];
    if (!step || navigationDisabledReason(layoutPhase, true)) return;
    setTourIdx(index);
    markStepComplete(step.nodeId);
    navigateToNode(step.nodeId);
  };

  return (
    <div className="sidebar-content learn-panel">
      <div className="sidebar-sheet-header">
        <span>Learning path</span>
        <CompactPill
          aria-label="Close learning path"
          className="sidebar-sheet-close"
          onClick={onCloseSheet}
        >
          Close
        </CompactPill>
      </div>

      <header className="learn-header">
        <h2>The {LEARN_STEPS.length} ideas that matter</h2>
        <p className="learn-subtitle">
          A guided path through {SOURCE}. Plain words first, math when you're ready.
        </p>
        <p className="learn-progress" role="status">
          {done} of {LEARN_STEPS.length} visited
        </p>
      </header>

      <ol className="learn-steps">
        {LEARN_STEPS.map((step, index) => {
          const isCurrent = tourIdx === index;
          const isDone = completedSteps.has(step.nodeId);
          return (
            <li key={step.nodeId}>
              <button
                aria-current={isCurrent ? "step" : undefined}
                aria-label={`Step ${index + 1}: ${step.title}`}
                className={`learn-step${isCurrent ? " is-current" : ""}${isDone ? " is-done" : ""}`}
                onClick={() => goTo(index)}
                type="button"
              >
                <span aria-hidden="true" className="learn-step-marker">
                  {isDone && !isCurrent ? "✓" : index + 1}
                </span>
                <span className="learn-step-body">
                  <strong>{step.title}</strong>
                  <span className="learn-step-blurb">{step.blurb}</span>
                </span>
              </button>
            </li>
          );
        })}
      </ol>

      <button
        className="learn-explore-link"
        onClick={() => setMode("explore")}
        type="button"
      >
        Show the full map ({(KE_DATA.nodes as KENode[]).length} concepts) →
      </button>
    </div>
  );
}
```

- [ ] **Step 4: Run tests** — `npx vitest run src/components/LearnPanel.test.tsx` → PASS.
- [ ] **Step 5: Commit** — `git commit -am "feat(ui): LearnPanel guided learning path"`

---

### Task 5: App shell — learn mode is the landing state

**Files:**
- Modify: `dashboard/src/App.tsx`
- Test: `dashboard/src/App.test.tsx`

**Interfaces:**
- Consumes: `LearnPanel`, `LEARN_STEPS` (Task 4); store `mode` (Task 1).
- Produces behavior later tasks rely on: in learn mode the left rail is `LearnPanel`, `TourOverlay` is not rendered, and on first layout-ready the app auto-selects step 1 (drawer opens with the TL;DR). Explore mode renders exactly today's shell.

- [ ] **Step 1: Write the failing tests** — add to `App.test.tsx` (reuse its existing render helper/mocks; ELK worker is presumably mocked there already — follow suit):

```tsx
it("lands in learn mode: learning path visible, diagnostics and tour card absent", () => {
  renderApp(); // the file's existing helper
  expect(screen.getByText(/ideas that matter/i)).toBeInTheDocument();
  expect(screen.queryByText("Insights & Health")).not.toBeInTheDocument();
  expect(screen.queryByLabelText("Guided tour")).not.toBeInTheDocument();
});

it("explore mode restores the diagnostics sidebar and tour card", () => {
  useApp.setState({ mode: "explore" });
  renderApp();
  expect(screen.getByText("Insights & Health")).toBeInTheDocument();
});

it("auto-opens the first step once layout is ready in learn mode", () => {
  useApp.setState({ layoutPhase: "ready", tourIdx: null, selected: null });
  renderApp();
  expect(useApp.getState().tourIdx).toBe(0);
  expect(useApp.getState().pendingNavigation?.nodeId ?? useApp.getState().selected)
    .toBe(LEARN_STEPS[0].nodeId);
});
```

- [ ] **Step 2: Run to verify failure** — `npx vitest run src/App.test.tsx` → FAIL.

- [ ] **Step 3: Implement.** In `App.tsx`:

1. Imports: add `LearnPanel, { LEARN_STEPS }` and `useNodeNavigation`.
2. Read mode + auto-start state inside `App`:

```tsx
  const mode = useApp((state) => state.mode);
  const tourIdx = useApp((state) => state.tourIdx);
  const setTourIdx = useApp((state) => state.setTourIdx);
  const layoutPhase = useApp((state) => state.layoutPhase);
  const markStepComplete = useApp((state) => state.markStepComplete);
  const navigateToNode = useNodeNavigation();

  useEffect(() => {
    if (mode !== "learn" || layoutPhase !== "ready") return;
    if (tourIdx !== null || selected !== null || LEARN_STEPS.length === 0) return;
    setTourIdx(0);
    markStepComplete(LEARN_STEPS[0].nodeId);
    navigateToNode(LEARN_STEPS[0].nodeId);
  }, [layoutPhase, markStepComplete, mode, navigateToNode, selected, setTourIdx, tourIdx]);
```

3. Left rail swap — replace `<Sidebar onCloseSheet={closeSidebar} />` with:

```tsx
          {mode === "learn"
            ? <LearnPanel onCloseSheet={closeSidebar} />
            : <Sidebar onCloseSheet={closeSidebar} />}
```

4. Tour card becomes explore-only — replace `<TourOverlay escapeEnabled={escapeLayer === "tour"} />` with:

```tsx
              {mode === "explore" && (
                <TourOverlay escapeEnabled={escapeLayer === "tour"} />
              )}
```

   and gate `tourVisible` accordingly: `const tourVisible = mode === "explore" && tourIsVisible({ ... })` so Escape layering stays correct in learn mode.

5. Desktop learn mode should show the panel without the "Open Insights / Trace" click: the `.sidebar` aside is already always rendered ≥900px; no change needed beyond the swap. On narrow viewports the existing sheet behavior applies to LearnPanel unchanged (same `onCloseSheet` contract).

- [ ] **Step 4: Run the app-level suite** — `npx vitest run src/App.test.tsx src/components/TourOverlay.test.tsx` → PASS (update any TourOverlay/App assertions that assumed the tour card renders by default — they should now set `mode: "explore"` in setup).
- [ ] **Step 5: Eyeball it** — `npm run dev`, confirm: landing = learning path left, focused drawer open on step 1. Toggle to explore via "Show the full map".
- [ ] **Step 6: Commit** — `git commit -am "feat(app): learn mode landing with auto-started first step"`

---

### Task 6: Canvas — focused subgraph in learn mode

**Files:**
- Modify: `dashboard/src/components/Canvas.tsx`
- Test: covered by `lib/learnPath.test.ts` (pure logic) + one App-level assertion below

**Interfaces:**
- Consumes: `focusNodeIds` (Task 2), `LEARN_STEPS` (Task 4), store `mode/tourIdx/completedSteps`.
- Produces: in learn mode the canvas shows only the current step's node, its 1-hop neighbors, and already-visited steps; camera refits on step change; clusters LOD never engages in learn mode. Explore mode rendering is byte-identical to today.

- [ ] **Step 1: Write the failing test** — add to `App.test.tsx`:

```tsx
it("learn mode canvas hides nodes outside the current step's neighborhood", async () => {
  useApp.setState({ mode: "learn", tourIdx: 0, completedSteps: new Set([LEARN_STEPS[0].nodeId]) });
  renderApp();
  // "why-self-attention" is not adjacent to the first tour step in the fixture graph
  expect(screen.queryByText("Why Self-Attention?")).not.toBeInTheDocument();
});
```

(Verify the chosen node id truly isn't adjacent to step 1 in `fixtures/aiayn_concept_graph.json` before relying on it; pick another non-adjacent node if needed.)

- [ ] **Step 2: Run to verify failure** — `npx vitest run src/App.test.tsx` → FAIL.

- [ ] **Step 3: Implement.** In `Canvas.tsx`:

1. Imports: `focusNodeIds` from `../lib/lod`'s sibling `../lib/learnPath`; `LEARN_STEPS` from `./LearnPanel`.
2. Pull state: add `mode`, `tourIdx`, `completedSteps` to the existing `useApp()` destructure.
3. After the `viewNodeIds` memo, add:

```tsx
  const learnFocus = useMemo(() => {
    if (mode !== "learn" || LEARN_STEPS.length === 0) return null;
    const bounded = Math.min(Math.max(tourIdx ?? 0, 0), LEARN_STEPS.length - 1);
    return focusNodeIds(LEARN_STEPS[bounded].nodeId, KE_EDGES, completedSteps);
  }, [completedSteps, mode, tourIdx]);
```

4. In the `nodes` memo, filter members: after `.filter((node) => !lod.hiddenNodes.has(node.id))` add `.filter((node) => !learnFocus || learnFocus.has(node.id))`, and suppress synthetic clusters in learn mode: `const syntheticClusters = learnFocus ? [] : clusterCards(...)`. Add `learnFocus` to the memo dep array.
5. Refit the camera when the focus set changes:

```tsx
  useEffect(() => {
    if (!learnFocus || layout.phase !== "ready") return;
    const frame = window.requestAnimationFrame(() => {
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      void flow.fitView({ padding: 0.3, duration: reducedMotion ? 0 : 400 });
    });
    return () => window.cancelAnimationFrame(frame);
  }, [flow, layout.phase, learnFocus]);
```

6. Edges already follow via `shownIds` → `makeFlowEdges`; no change.

- [ ] **Step 4: Run tests** — `npx vitest run` → PASS (fix any Canvas-adjacent tests that render in default mode and expected all nodes: set `mode: "explore"` in their setup — that keeps their original intent).
- [ ] **Step 5: Eyeball** — `npm run dev`: step 1 shows a small legible neighborhood; clicking step 3 in the panel reveals it plus neighbors; visited nodes accumulate; explore mode shows everything.
- [ ] **Step 6: Commit** — `git commit -am "feat(canvas): progressive focus subgraph in learn mode"`

---

### Task 7: TopBar — mode switch, de-cluttering, plain-language copy

**Files:**
- Modify: `dashboard/src/components/TopBar.tsx`
- Test: `dashboard/src/App.test.tsx` additions

**Interfaces:**
- Consumes: store `mode/setMode` (Task 1).
- Produces: a `[Guided] [Explore]` segmented control (radiogroup, `aria-label="Dashboard mode"`) always first in the bar. In learn mode the view radiogroup, edge-kind filters, blast-radius pill, and diagnostics trigger are hidden; search stays. Copy changes (both modes): search placeholder `"Find a concept… (Enter)"`; diagnostics trigger label `"Diagnostics"`; blast pill label `"impact radius"` with `title="Highlight everything that depends on the selected node"`.

- [ ] **Step 1: Write the failing tests** — add to `App.test.tsx`:

```tsx
it("learn mode topbar shows only the mode switch and search", () => {
  renderApp();
  expect(screen.getByRole("radiogroup", { name: "Dashboard mode" })).toBeInTheDocument();
  expect(screen.queryByRole("radiogroup", { name: "Graph view" })).not.toBeInTheDocument();
  expect(screen.queryByText("impact radius")).not.toBeInTheDocument();
  expect(screen.getByPlaceholderText(/find a concept/i)).toBeInTheDocument();
});

it("switching to Explore reveals the full toolbar", () => {
  renderApp();
  fireEvent.click(screen.getByRole("radio", { name: "Explore" }));
  expect(screen.getByRole("radiogroup", { name: "Graph view" })).toBeInTheDocument();
  expect(screen.getByText("impact radius")).toBeInTheDocument();
  expect(screen.getByText("Diagnostics")).toBeInTheDocument();
});
```

- [ ] **Step 2: Run to verify failure** — `npx vitest run src/App.test.tsx` → FAIL.

- [ ] **Step 3: Implement.** In `TopBar.tsx`:

1. Pull `mode, setMode` from `useApp()`.
2. Insert the mode switch as the first child of the returned fragment (pattern-match the existing `VIEWS` radiogroup for keyboard handling):

```tsx
      <div aria-label="Dashboard mode" className="topbar-group mode-switch" role="radiogroup">
        {([["learn", "Guided"], ["explore", "Explore"]] as const).map(([value, label]) => (
          <CompactPill
            active={mode === value}
            aria-checked={mode === value}
            key={value}
            onClick={() => setMode(value)}
            role="radio"
            tabIndex={mode === value ? 0 : -1}
          >
            {label}
          </CompactPill>
        ))}
      </div>
```

3. Wrap the diagnostics trigger, the `Graph view` radiogroup, the separator, and the `Graph filters` group in `{mode === "explore" && ( ... )}` (one wrapper around that contiguous block; move the diagnostics `CompactPill` inside it and change its child text to `Diagnostics`). Keep `sidebarTriggerRef` on it — App only focuses it on narrow-viewport close, which in learn mode targets the LearnPanel sheet: give LearnPanel's narrow-sheet trigger the same treatment by rendering the trigger in learn mode too, labeled `Learning path` (`aria-controls="left-panel"` unchanged).
4. Copy: `blast radius` → `impact radius` (+ the `title` above), placeholder `"search… (Enter)"` → `"Find a concept… (Enter)"`.

- [ ] **Step 4: Run** — `npx vitest run` → PASS (update any test asserting the old strings `blast radius` / `Open Insights / Trace` / `search…`).
- [ ] **Step 5: Commit** — `git commit -am "feat(topbar): mode switch, learn-mode decluttering, plain copy"`

---

### Task 8: Drawer — pedagogy-first ordering and progressive math

**Files:**
- Modify: `dashboard/src/components/Drawer.tsx`
- Test: `dashboard/src/components/Drawer.test.tsx`

**Interfaces:**
- Consumes: existing `splitTiers` tiers, `EquationList`, `BridgeButton`, `CodeViewer`.
- Produces the new section order inside `drawer-content`:
  1. heading (unchanged)
  2. **plain-words lead** — TL;DR tier rendered open, no toggle, class `drawer-lead`
  3. **tier stepper** — `Intuition` (`<details open>`), `Mechanics`, `The Math`, `Go Deeper` (closed `<details>`)
  4. **Key equations** — renamed heading (`Key equations — hover to highlight in the graph`), moved here from above the tiers
  5. **See it in code** — one closed `<details className="drawer-code">` wrapping the bridge list + `<CodeViewer>`
  6. meta line reworded and demoted to the bottom: `` `${node.kind} · ${node.source_ref ?? "—"} · unlocks ${immediateImpact} concept(s) directly, ${secondaryImpact} more downstream` ``

- [ ] **Step 1: Write the failing tests** — update/add in `Drawer.test.tsx` (keep its existing fixtures/render helper):

```tsx
it("shows the TL;DR as an always-visible lead, before any code or equations", () => {
  renderDrawerForNodeWithTiers(); // existing helper/fixture for a node with page tiers
  const content = document.querySelector(".drawer-content")!;
  const lead = content.querySelector(".drawer-lead");
  expect(lead).not.toBeNull();
  const order = Array.from(content.children).map((el) => el.className);
  expect(order.indexOf("drawer-lead")).toBeLessThan(order.findIndex((c) => c.includes("drawer-equations")));
  expect(order.findIndex((c) => c.includes("drawer-equations")))
    .toBeLessThan(order.findIndex((c) => c.includes("drawer-code")));
});

it("keeps Intuition open and The Math collapsed by default", () => {
  renderDrawerForNodeWithTiers();
  expect(screen.getByText("Intuition").closest("details")).toHaveAttribute("open");
  expect(screen.getByText("The Math").closest("details")).not.toHaveAttribute("open");
});

it("tucks the code bridge behind a closed disclosure", () => {
  renderDrawerForNodeWithBridge(); // existing bridge fixture
  const details = screen.getByText(/see it in code/i).closest("details");
  expect(details).not.toHaveAttribute("open");
});
```

(Adapt helper names to the file's actual setup utilities; the assertions are the contract.)

- [ ] **Step 2: Run to verify failure** — `npx vitest run src/components/Drawer.test.tsx` → FAIL.

- [ ] **Step 3: Implement.** In `DrawerPresentation`'s JSX, reorder to:

```tsx
    <div className="drawer-content">
      {/* heading block unchanged */}

      {tiers.tldr && (
        <section aria-label="In plain words" className="drawer-lead">
          <RichMarkdown glossary={glossary} markdown={tiers.tldr} />
        </section>
      )}

      {pageMarkdown && hasDeeperTiers && (
        <section aria-label="Explanation tiers" className="tier">
          {DEEPER_TIERS.filter((tier) => tiers[tier]).map((tier) => (
            <details key={tier} open={tier === "intuition"}>
              <summary>{TIER_LABEL[tier]}</summary>
              <div className="tier-body">
                <RichMarkdown glossary={glossary} markdown={tiers[tier] ?? ""} />
              </div>
            </details>
          ))}
        </section>
      )}

      {/* fallbackMarkdown / bare pageMarkdown / drawer-empty branches unchanged,
          but only when tiers.tldr is absent */}

      {equations.length > 0 && (
        <section aria-labelledby="drawer-equations-heading" className="drawer-section drawer-equations">
          <h3 id="drawer-equations-heading">Key equations — hover to highlight in the graph</h3>
          <EquationList equations={equations} key={selected} setHoverEq={setHoverEq} />
        </section>
      )}

      {(bridges.length > 0 || hasCode) && (
        <details className="drawer-section drawer-code">
          <summary>See it in code</summary>
          {bridges.length > 0 && (
            <div className="drawer-bridge-list">{/* existing BridgeButton map unchanged */}</div>
          )}
          <CodeViewer nodeId={selected} />
        </details>
      )}

      <p className="drawer-meta">
        {node.kind} · {node.source_ref ?? "—"} · unlocks {immediateImpact} concept(s) directly, {secondaryImpact} more downstream
      </p>
    </div>
```

with the supporting constants replacing `TIER_ORDER` usage in the JSX (keep `TIER_ORDER` itself — other logic uses it):

```tsx
const DEEPER_TIERS = ["intuition", "mechanics", "the-math", "go-deeper"] as const;
const hasDeeperTiers = DEEPER_TIERS.some((tier) => tiers[tier]);
```

**Note on the code wrapper (`hasCode`):** open `CodeViewer.tsx` and find the `KE_DATA` lookup it uses to decide whether it has an excerpt for a node. Export that check as `export function hasCodeFor(nodeId: string): boolean` from `CodeViewer.tsx` (moving the existing lookup into it so the component and the predicate share one implementation), then in `DrawerPresentation` compute `const hasCode = selected ? hasCodeFor(selected) : false;`. This prevents rendering an empty "See it in code" disclosure for concept nodes with no linked code. The fallback branches (`fallbackMarkdown` / bare `pageMarkdown` / `drawer-empty`) keep their current logic for nodes without tier pages.

- [ ] **Step 4: Run** — `npx vitest run src/components/Drawer.test.tsx src/components/CodeViewer.test.tsx` → PASS (update ordering-dependent existing assertions deliberately).
- [ ] **Step 5: Commit** — `git commit -am "feat(drawer): plain-words lead, progressive tiers, code demoted"`

---

### Task 9: Node cards + visual polish (`styles.css`, `nodePresentation.ts`)

**Files:**
- Modify: `dashboard/src/lib/nodePresentation.ts`, `dashboard/src/components/nodes.tsx`, `dashboard/src/styles.css`
- Test: `dashboard/src/lib/nodePresentation.test.ts`, `dashboard/src/styles.test.ts`

**Interfaces:**
- Produces: `export function levelBadgeLabel(level: number | undefined): string | null` in `nodePresentation.ts` — `undefined → null`, `0|1 → "core idea"`, `2 → "mechanism"`, `≥3 → "deep dive"`. `nodes.tsx` renders this instead of `L{n}` (accessible name via `nodeAccessibleName` updated to match). New CSS classes styled per UI-SPEC tokens: `.mode-switch`, `.learn-panel`, `.learn-header`, `.learn-subtitle`, `.learn-progress`, `.learn-steps`, `.learn-step`, `.learn-step-marker`, `.learn-step-body`, `.learn-step-blurb`, `.learn-explore-link`, `.drawer-lead`, `.drawer-code`.

- [ ] **Step 1: Write the failing tests** — in `nodePresentation.test.ts`:

```ts
import { levelBadgeLabel } from "./nodePresentation";

describe("levelBadgeLabel", () => {
  it.each([
    [undefined, null],
    [0, "core idea"],
    [1, "core idea"],
    [2, "mechanism"],
    [3, "deep dive"],
    [5, "deep dive"],
  ])("level %s → %s", (level, expected) => {
    expect(levelBadgeLabel(level as number | undefined)).toBe(expected);
  });
});
```

Check `styles.test.ts` to see what it asserts (it lints the stylesheet); add entries for the new classes if it enumerates required selectors.

- [ ] **Step 2: Run to verify failure** — `npx vitest run src/lib/nodePresentation.test.ts` → FAIL.

- [ ] **Step 3: Implement.**

`nodePresentation.ts`:

```ts
export function levelBadgeLabel(level: number | undefined): string | null {
  if (level === undefined) return null;
  if (level <= 1) return "core idea";
  if (level === 2) return "mechanism";
  return "deep dive";
}
```

Update `nodeAccessibleName` to use the same wording (read its current implementation and substitute the `L${level}` fragment).

`nodes.tsx` — replace `{data.level !== undefined && <span className="badge">L{data.level}</span>}` with:

```tsx
        {levelBadgeLabel(data.level) && (
          <span className="badge">{levelBadgeLabel(data.level)}</span>
        )}
```

`styles.css` — append (uses only locked tokens; verify variable names against the file's `:root` and substitute if it uses raw hex):

```css
/* ── Learn mode ─────────────────────────────────── */
.mode-switch { margin-right: 4px; }

.learn-panel { display: flex; flex-direction: column; gap: 12px; }
.learn-header h2 { font-size: 15px; margin: 0 0 4px; color: var(--text); }
.learn-subtitle { font-size: 12.5px; color: var(--muted); margin: 0; line-height: 1.5; }
.learn-progress { font-size: 11px; color: var(--accent); margin: 4px 0 0; }

.learn-steps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.learn-step {
  display: flex; gap: 10px; width: 100%; text-align: left;
  background: var(--bg); border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 12px; color: var(--text); cursor: pointer;
  transition: border-color 150ms, background-color 150ms;
}
.learn-step:hover { border-color: var(--accent); }
.learn-step:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.learn-step.is-current { border-color: var(--accent); background: #16233c; }
.learn-step.is-done .learn-step-marker { background: #16301f; color: #4a9b5e; border-color: #4a9b5e; }
.learn-step-marker {
  flex: none; width: 22px; height: 22px; border-radius: 50%;
  border: 1px solid var(--border); background: #1c2a44; color: var(--muted);
  font-size: 11px; display: grid; place-items: center;
}
.learn-step.is-current .learn-step-marker { background: var(--accent); color: #fff; border-color: var(--accent); }
.learn-step-body { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.learn-step-body strong { font-size: 13px; }
.learn-step-blurb {
  font-size: 11.5px; color: var(--muted); line-height: 1.45;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.learn-explore-link {
  margin-top: auto; background: none; border: 1px dashed var(--border); border-radius: 8px;
  color: var(--muted); font-size: 12px; padding: 8px; cursor: pointer;
  transition: color 150ms, border-color 150ms;
}
.learn-explore-link:hover { color: var(--text); border-color: var(--accent); }
.learn-explore-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ── Drawer pedagogy ────────────────────────────── */
.drawer-lead {
  font-size: 14px; line-height: 1.6; color: var(--text);
  border-left: 3px solid var(--accent); padding: 2px 0 2px 12px; margin: 4px 0 8px;
}
.drawer-lead p { margin: 0 0 8px; }
.drawer-code > summary { cursor: pointer; color: var(--muted); font-size: 12.5px; }
.drawer-code[open] > summary { color: var(--text); }
.drawer-content > .drawer-meta { margin-top: 12px; border-top: 1px solid var(--border); padding-top: 8px; }
```

- [ ] **Step 4: Run everything** — `npx vitest run` → PASS.
- [ ] **Step 5: Eyeball at three widths** — `npm run dev`; check desktop (1280), tablet (~900 boundary), narrow (<900 sheet behavior) for the learn panel, mode switch, drawer.
- [ ] **Step 6: Commit** — `git commit -am "feat(ui): plain-language level badges, learn-mode styling"`

---

### Task 10: Full verification + regenerate the real dashboards (live gate)

**Files:**
- Regenerate: `dashboard/src/data.gen.ts` (fixture), `tmp_dashboards/attention` (real paper)

- [ ] **Step 1: Full automated suites** (from `paper-skill-slice9-bridge/`):

```powershell
cd dashboard; npx vitest run; npx tsc --noEmit; python -m pytest tests/ -x
cd ..; python -m pytest -x
```

Expected: all PASS. Fix regressions before proceeding.

- [ ] **Step 2: Rebuild the AIAYN dashboard for before/after.** Locate the graph/pack inputs used for `tmp_dashboards/attention` (look for `graph.json` / `pack.json` / a build script next to it or under `tmp_dashboards/`; if absent, rerun the pipeline command recorded in `plans/2026-07-09-INDEX.md` slice 9/10 notes). Then:

```powershell
cd dashboard
python build_data.py --graph <attention-graph.json> --pack <attention-pack.json> --pages-dir <pages> --wiki-dir <wiki>
npm run build
# copy dist/* over tmp_dashboards/attention/ (keep a tmp_dashboards/attention-before/ copy first for comparison)
cd ../tmp_dashboards/attention; python -m http.server 8934
```

- [ ] **Step 3: Owner live-gate checklist** (this is the step every slice skipped — do not skip it):
  - Landing shows "The 5 ideas that matter" + focused mini-graph + step 1 drawer with a plain-English TL;DR — no 24-node wall.
  - Tour blurbs are real sentences from the paper, not "Next stop on the dependency-ordered reading path."
  - Math appears only after TL;DR/Intuition; "See it in code" is collapsed until asked.
  - "Explore" restores today's full graph, views, filters, diagnostics — nothing lost.
  - DevTools network tab: zero external requests.
- [ ] **Step 4: Restore the fixture `data.gen.ts`** (rerun the fixture build command) so the committed dev state matches tests, then commit: `git commit -am "chore: regenerate fixture data; rebuild attention dashboard"`

---

## Explicitly out of scope (YAGNI)

- No localStorage persistence of progress (candidate follow-up).
- No new pipeline capability, no LLM calls, no changes to `graph.json`/`pack.json` schemas.
- No touching `paper-skill-slice8-p6/`, `-slice9-complete/`, `-slice10-next-steps/`, or `research-mcp*`.
- `PlayerBar` ("reading path" autoplay) and `Legend` stay as-is; they cooperate with learn mode already (navigation marks nothing complete from PlayerBar — acceptable v1).

## Risk notes for the implementer

- Many existing tests assert default-mode behavior (full graph, tour card visible, sidebar = diagnostics). The intended fix is to set `mode: "explore"` in *their* setup — that preserves their original intent — not to weaken assertions.
- `App.test.tsx` mocks/stubs for the ELK worker and `matchMedia` already exist; reuse them rather than inventing new mocks.
- `data.gen.ts` is regenerated in Tasks 3 and 10 — never hand-edit; if a test needs different data, it should build its own fixtures (as `learnPath.test.ts` does).

# Adjustable Panels and Graph Legibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all three dashboard side panels adjustable, show complete graph-node labels with matching ELK dimensions, and preserve valid TeX through Markdown so KaTeX renders spacing and delimiter commands correctly.

**Architecture:** A pure panel-sizing module owns bounds, persistence, and keyboard calculations; a single controlled `PanelResizer` supplies pointer and keyboard interaction; `App` owns all three preferred widths and passes the Guided rail sizing into `ArticleView`. A shared node-dimension helper supplies both ELK and React Flow, while a delimiter-aware Markdown preprocessor protects complete math spans before CommonMark sees them.

**Tech Stack:** React 19, TypeScript, Zustand, @xyflow/react 12, ELK.js 0.9, React Markdown 10, KaTeX 0.16, Vitest 3, Vite 6, Python/pytest.

## Global Constraints

- Work only in `paper-skill-slice9-bridge/`; do not edit sibling slice directories.
- Keep the app fully offline: no network calls, API keys, fonts, packages, or runtime fetches.
- Preserve one-way generated data flow: graph/pack/pages → `dashboard/build_data.py` → `dashboard/src/data.gen.ts`.
- Do not hand-edit `dashboard/src/data.gen.ts`; restore the checked-in fixture after real-dashboard builds.
- Keep the current palette, typography, 4px spacing grid, surface-shift depth, focus outline, and 120–180ms interaction motion.
- Do not add docking, detachable windows, a new graph algorithm, or content-rewriting heuristics.
- Below 900px, preserve the existing modal-sheet widths and render no panel resizer.
- Retain at least 360px for the primary article or graph workspace.
- Use test-first red/green cycles and commit each task independently.

---

## File Structure

- Create `dashboard/src/lib/panelSizing.ts`: pure panel specs, bounds, persistence, and keyboard calculations.
- Create `dashboard/src/lib/panelSizing.test.ts`: unit coverage for every sizing and persistence rule.
- Create `dashboard/src/components/usePanelWidths.ts`: React state, viewport tracking, and storage synchronization for all panels.
- Create `dashboard/src/components/PanelResizer.tsx`: the reusable ARIA separator and pointer/keyboard behavior.
- Create `dashboard/src/components/PanelResizer.test.tsx`: server-rendered semantics plus pure interaction calculations.
- Create `dashboard/src/lib/nodeDimensions.ts`: one source of truth for graph-card width and height.
- Create `dashboard/src/lib/nodeDimensions.test.ts`: short, wrapped, and unbroken-label sizing tests.
- Modify `dashboard/src/App.tsx`: own widths, place Explore resizers, and retain modal behavior.
- Modify `dashboard/src/components/ArticleView.tsx`: receive Guided sizing and place its resizer.
- Modify `dashboard/src/components/Canvas.tsx`: use shared node dimensions.
- Modify `dashboard/src/components/nodes.tsx`: make node buttons fill measured cards and wrap labels.
- Modify `dashboard/src/lib/layout.ts`: give ELK shared dimensions and dimension-aware cache keys.
- Modify `dashboard/src/lib/layout.test.ts`: assert ELK dimension inputs and cache invalidation.
- Modify `dashboard/src/lib/mathHtml.ts`: protect complete inline and display math across Markdown parsing.
- Modify `dashboard/src/lib/mathHtml.test.ts`: reported-equation regression tests.
- Modify `dashboard/src/components/Drawer.tsx`: call the new math-preservation helper.
- Modify `dashboard/src/components/Drawer.test.tsx`: exercise the complete Markdown→KaTeX path.
- Modify `dashboard/src/styles.css`: panel variables, resizers, full node labels, and responsive rules.
- Modify `dashboard/src/styles.test.ts`: enforce the no-truncation and mobile-resizer contracts.

---

### Task 1: Pure Panel Sizing and Persistence

**Files:**
- Create: `dashboard/src/lib/panelSizing.ts`
- Create: `dashboard/src/lib/panelSizing.test.ts`

**Interfaces:**
- Produces: `PanelId`, `PanelWidths`, `PanelSpec`, `PANEL_SPECS`, `PANEL_STORAGE_KEY`, `DEFAULT_PANEL_WIDTHS`, `panelBounds()`, `clampPanelWidth()`, `resolveExplorePanelWidths()`, `widthFromKeyboard()`, `readPanelWidths()`, and `writePanelWidths()`.
- Consumes: only Web Storage-compatible `getItem`/`setItem` methods; no React or DOM dependency.

- [ ] **Step 1: Write failing tests for defaults, viewport bounds, and paired Explore widths**

```ts
import { describe, expect, it } from "vitest";
import {
  DEFAULT_PANEL_WIDTHS,
  panelBounds,
  resolveExplorePanelWidths,
} from "./panelSizing";

describe("panel sizing", () => {
  it("uses the approved defaults and ranges", () => {
    expect(DEFAULT_PANEL_WIDTHS).toEqual({
      "guided-rail": 264,
      diagnostics: 300,
      explanation: 380,
    });
    expect(panelBounds("guided-rail", 700, 0)).toEqual({ min: 220, max: 328 });
  });

  it("keeps a 360px workspace when both Explore panels are inline", () => {
    const widths = resolveExplorePanelWidths(
      { "guided-rail": 264, diagnostics: 480, explanation: 640 },
      1280,
      true,
    );
    expect(widths.diagnostics + widths.explanation).toBeLessThanOrEqual(896);
    expect(widths.diagnostics).toBeGreaterThanOrEqual(240);
    expect(widths.explanation).toBeGreaterThanOrEqual(320);
  });

  it("does not reserve drawer width while the drawer is closed", () => {
    expect(resolveExplorePanelWidths(DEFAULT_PANEL_WIDTHS, 1280, false))
      .toMatchObject({ diagnostics: 300, explanation: 380 });
  });
});
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `cd dashboard; npx vitest run src/lib/panelSizing.test.ts`

Expected: FAIL because `./panelSizing` does not exist.

- [ ] **Step 3: Add failing keyboard and persistence tests**

```ts
it("handles arrows, shifted arrows, Home, End, and unrelated keys", () => {
  expect(widthFromKeyboard("ArrowRight", false, 300, { min: 240, max: 480 })).toBe(316);
  expect(widthFromKeyboard("ArrowLeft", true, 300, { min: 240, max: 480 })).toBe(252);
  expect(widthFromKeyboard("Home", false, 300, { min: 240, max: 480 })).toBe(240);
  expect(widthFromKeyboard("End", false, 300, { min: 240, max: 480 })).toBe(480);
  expect(widthFromKeyboard("Escape", false, 300, { min: 240, max: 480 })).toBeNull();
});

it("round-trips versioned widths and recovers from corrupt storage", () => {
  const memory = new Map<string, string>();
  const storage = {
    getItem: (key: string) => memory.get(key) ?? null,
    setItem: (key: string, value: string) => { memory.set(key, value); },
  };
  writePanelWidths(storage, { ...DEFAULT_PANEL_WIDTHS, diagnostics: 412 });
  expect(readPanelWidths(storage).diagnostics).toBe(412);
  memory.set(PANEL_STORAGE_KEY, "not json");
  expect(readPanelWidths(storage)).toEqual(DEFAULT_PANEL_WIDTHS);
});
```

- [ ] **Step 4: Implement the pure sizing module**

```ts
export type PanelId = "guided-rail" | "diagnostics" | "explanation";
export type PanelWidths = Record<PanelId, number>;
export type PanelSpec = { defaultWidth: number; min: number; max: number };
export type PanelBounds = { min: number; max: number };
type StorageLike = Pick<Storage, "getItem" | "setItem">;

export const MIN_WORKSPACE_WIDTH = 360;
export const RESIZER_SPACE = 12;
export const PANEL_STORAGE_KEY = "paper-dashboard.panel-widths.v1";
export const PANEL_SPECS: Record<PanelId, PanelSpec> = {
  "guided-rail": { defaultWidth: 264, min: 220, max: 420 },
  diagnostics: { defaultWidth: 300, min: 240, max: 480 },
  explanation: { defaultWidth: 380, min: 320, max: 640 },
};
export const DEFAULT_PANEL_WIDTHS: PanelWidths = {
  "guided-rail": 264,
  diagnostics: 300,
  explanation: 380,
};

export function panelBounds(id: PanelId, viewportWidth: number, occupiedWidth = 0): PanelBounds {
  const spec = PANEL_SPECS[id];
  return {
    min: spec.min,
    max: Math.max(spec.min, Math.min(
      spec.max,
      viewportWidth - occupiedWidth - MIN_WORKSPACE_WIDTH - RESIZER_SPACE,
    )),
  };
}

export function clampPanelWidth(id: PanelId, width: number, viewportWidth: number, occupiedWidth = 0) {
  const bounds = panelBounds(id, viewportWidth, occupiedWidth);
  return Math.min(bounds.max, Math.max(bounds.min, Math.round(width)));
}

export function resolveExplorePanelWidths(preferred: PanelWidths, viewportWidth: number, drawerOpen: boolean) {
  const diagnostics = clampPanelWidth("diagnostics", preferred.diagnostics, viewportWidth);
  if (!drawerOpen || viewportWidth < 1280) {
    return {
      diagnostics,
      explanation: clampPanelWidth("explanation", preferred.explanation, viewportWidth),
    };
  }
  const explanation = clampPanelWidth(
    "explanation",
    preferred.explanation,
    viewportWidth,
    diagnostics + RESIZER_SPACE,
  );
  return {
    diagnostics: clampPanelWidth(
      "diagnostics",
      diagnostics,
      viewportWidth,
      explanation + RESIZER_SPACE,
    ),
    explanation,
  };
}

export function widthFromKeyboard(
  key: string,
  shiftKey: boolean,
  current: number,
  bounds: PanelBounds,
): number | null {
  const step = shiftKey ? 48 : 16;
  const next = key === "ArrowLeft" ? current - step
    : key === "ArrowRight" ? current + step
      : key === "Home" ? bounds.min
        : key === "End" ? bounds.max
          : null;
  return next === null ? null : Math.min(bounds.max, Math.max(bounds.min, next));
}

export function readPanelWidths(storage?: StorageLike | null): PanelWidths {
  if (!storage) return { ...DEFAULT_PANEL_WIDTHS };
  try {
    const value = JSON.parse(storage.getItem(PANEL_STORAGE_KEY) ?? "null") as Partial<PanelWidths> | null;
    const widths = { ...DEFAULT_PANEL_WIDTHS };
    for (const id of Object.keys(PANEL_SPECS) as PanelId[]) {
      const candidate = value?.[id];
      if (typeof candidate === "number" && Number.isFinite(candidate)) {
        widths[id] = Math.min(PANEL_SPECS[id].max, Math.max(PANEL_SPECS[id].min, Math.round(candidate)));
      }
    }
    return widths;
  } catch {
    return { ...DEFAULT_PANEL_WIDTHS };
  }
}

export function writePanelWidths(storage: StorageLike | null | undefined, widths: PanelWidths): void {
  if (!storage) return;
  try { storage.setItem(PANEL_STORAGE_KEY, JSON.stringify(widths)); } catch { /* storage can be disabled */ }
}
```

- [ ] **Step 5: Run tests and commit**

Run: `cd dashboard; npx vitest run src/lib/panelSizing.test.ts`

Expected: PASS.

```powershell
git add dashboard/src/lib/panelSizing.ts dashboard/src/lib/panelSizing.test.ts
git commit -m "feat(ui): add panel sizing model"
```

---

### Task 2: Controlled Accessible Resizer and Width Hook

**Files:**
- Create: `dashboard/src/components/usePanelWidths.ts`
- Create: `dashboard/src/components/PanelResizer.tsx`
- Create: `dashboard/src/components/PanelResizer.test.tsx`
- Modify: `dashboard/src/styles.css`

**Interfaces:**
- Consumes: Task 1 `PanelId`, `PanelWidths`, `PANEL_SPECS`, `readPanelWidths()`, `writePanelWidths()`, and `widthFromKeyboard()`.
- Produces: `usePanelWidths(): { preferred, viewportWidth, setWidth, resetWidth }` and `PanelResizer` props `{ id, label, side, value, bounds, onChange, onReset }`.

- [ ] **Step 1: Write the failing semantic rendering test**

```tsx
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import PanelResizer from "./PanelResizer";

it("renders an adjustable vertical separator with current bounds", () => {
  const markup = renderToStaticMarkup(
    <PanelResizer
      bounds={{ min: 240, max: 480 }}
      id="diagnostics"
      label="Resize diagnostics panel"
      onChange={() => {}}
      onReset={() => {}}
      side="left"
      value={312}
    />,
  );
  expect(markup).toContain('role="separator"');
  expect(markup).toContain('aria-orientation="vertical"');
  expect(markup).toContain('aria-valuemin="240"');
  expect(markup).toContain('aria-valuemax="480"');
  expect(markup).toContain('aria-valuenow="312"');
});
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `cd dashboard; npx vitest run src/components/PanelResizer.test.tsx`

Expected: FAIL because `PanelResizer.tsx` does not exist.

- [ ] **Step 3: Implement the hook and resizer**

Use one `usePanelWidths` state object initialized from `localStorage`, update `viewportWidth` on `resize`, and persist only explicit user changes. In `PanelResizer`, record `{ pointerId, startX, startWidth }` in a ref; use pointer capture; calculate `delta = side === "left" ? clientX - startX : startX - clientX`; clamp through `bounds`; and clear the ref on pointer-up or pointer-cancel.

```ts
export function usePanelWidths() {
  const [preferred, setPreferred] = useState<PanelWidths>(() => readPanelWidths(
    typeof window === "undefined" ? null : window.localStorage,
  ));
  const [viewportWidth, setViewportWidth] = useState(() => (
    typeof window === "undefined" ? 1440 : window.innerWidth
  ));

  useEffect(() => {
    const update = () => setViewportWidth(window.innerWidth);
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const commit = useCallback((id: PanelId, width: number) => {
    setPreferred((current) => {
      const next = { ...current, [id]: Math.round(width) };
      writePanelWidths(window.localStorage, next);
      return next;
    });
  }, []);

  const resetWidth = useCallback((id: PanelId) => {
    commit(id, PANEL_SPECS[id].defaultWidth);
  }, [commit]);

  return { preferred, viewportWidth, setWidth: commit, resetWidth };
}
```

```tsx
<div
  aria-label={label}
  aria-orientation="vertical"
  aria-valuemax={bounds.max}
  aria-valuemin={bounds.min}
  aria-valuenow={value}
  className={`panel-resizer panel-resizer-${side}`}
  onDoubleClick={onReset}
  onKeyDown={(event) => {
    const next = widthFromKeyboard(
      event.key,
      event.shiftKey,
      value,
      bounds,
    );
    if (next === null) return;
    event.preventDefault();
    onChange(next);
  }}
  role="separator"
  tabIndex={0}
/>
```

The pointer handlers use this exact calculation:

```tsx
const drag = useRef<{ pointerId: number; startX: number; startWidth: number } | null>(null);
const clamp = (width: number) => Math.min(bounds.max, Math.max(bounds.min, Math.round(width)));

const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
  drag.current = { pointerId: event.pointerId, startX: event.clientX, startWidth: value };
  event.currentTarget.setPointerCapture(event.pointerId);
};
const onPointerMove = (event: PointerEvent<HTMLDivElement>) => {
  const active = drag.current;
  if (!active || active.pointerId !== event.pointerId) return;
  const delta = side === "left"
    ? event.clientX - active.startX
    : active.startX - event.clientX;
  onChange(clamp(active.startWidth + delta));
};
const endPointer = (event: PointerEvent<HTMLDivElement>) => {
  if (drag.current?.pointerId !== event.pointerId) return;
  if (event.currentTarget.hasPointerCapture(event.pointerId)) {
    event.currentTarget.releasePointerCapture(event.pointerId);
  }
  drag.current = null;
};
```

- [ ] **Step 4: Add the resizer styling**

```css
.panel-resizer {
  position: relative;
  z-index: 5;
  width: 12px;
  flex: 0 0 12px;
  cursor: col-resize;
  touch-action: none;
}
.panel-resizer::after {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 5px;
  width: 2px;
  background: transparent;
  content: "";
  transition: background-color 150ms cubic-bezier(0.23, 1, 0.32, 1);
}
.panel-resizer:hover::after,
.panel-resizer:focus-visible::after { background: var(--accent); }
.panel-resizer:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
@media (max-width: 899px) { .panel-resizer { display: none; } }
```

- [ ] **Step 5: Run focused tests and commit**

Run: `cd dashboard; npx vitest run src/components/PanelResizer.test.tsx src/lib/panelSizing.test.ts`

Expected: PASS.

```powershell
git add dashboard/src/components/usePanelWidths.ts dashboard/src/components/PanelResizer.tsx dashboard/src/components/PanelResizer.test.tsx dashboard/src/styles.css
git commit -m "feat(ui): add accessible panel resizer"
```

---

### Task 3: Integrate All Three Adjustable Panels

**Files:**
- Modify: `dashboard/src/App.tsx`
- Modify: `dashboard/src/App.test.tsx`
- Modify: `dashboard/src/components/ArticleView.tsx`
- Modify: `dashboard/src/components/ArticleView.test.tsx`
- Modify: `dashboard/src/styles.css`
- Modify: `dashboard/src/styles.test.ts`

**Interfaces:**
- Consumes: `usePanelWidths`, `PanelResizer`, `panelBounds()`, `clampPanelWidth()`, and `resolveExplorePanelWidths()`.
- Produces: CSS variables `--diagnostics-width`, `--drawer-width`, and `--guided-rail-width`; `ArticleView` props `railWidth`, `railBounds`, `onRailResize`, and `onRailReset`.

- [ ] **Step 1: Write failing SSR and stylesheet tests**

Add an App assertion for `Resize guided reading panel`, an `ArticleView` presentation assertion for a separator between rail and article, and stylesheet assertions that fixed `flex: 0 0 300px`, `flex: 0 0 380px`, and `flex: 0 0 264px` have been replaced by CSS variables.

```ts
expect(markup).toContain('aria-label="Resize guided reading panel"');
expect(styles).toMatch(/\.sidebar\s*\{[^}]*width:\s*var\(--diagnostics-width\)/s);
expect(styles).toMatch(/\.drawer\s*\{[^}]*width:\s*var\(--drawer-width\)/s);
expect(styles).toMatch(/\.progress-rail\s*\{[^}]*width:\s*var\(--guided-rail-width\)/s);
```

- [ ] **Step 2: Run tests and verify RED**

Run: `cd dashboard; npx vitest run src/App.test.tsx src/components/ArticleView.test.tsx src/styles.test.ts`

Expected: FAIL because the separators and CSS variables are absent.

- [ ] **Step 3: Wire the panels in `App.tsx` and `ArticleView.tsx`**

At App render time, compute effective widths from the preferred widths and viewport. Render the diagnostics resizer after the sidebar, the drawer resizer before the drawer, and pass the Guided rail contract into `ArticleView`. Apply typed CSS custom properties with `CSSProperties`.

```tsx
const panels = usePanelWidths();
const exploreWidths = resolveExplorePanelWidths(
  panels.preferred,
  panels.viewportWidth,
  drawerOpen,
);
const guidedBounds = panelBounds("guided-rail", panels.viewportWidth);
const guidedWidth = clampPanelWidth(
  "guided-rail",
  panels.preferred["guided-rail"],
  panels.viewportWidth,
);
const shellStyle = {
  "--diagnostics-width": `${exploreWidths.diagnostics}px`,
  "--drawer-width": `${exploreWidths.explanation}px`,
  "--guided-rail-width": `${guidedWidth}px`,
} as CSSProperties;
```

Do not render separators below 900px. Preserve the existing backdrops, `inert`, modal roles, focus traps, and Escape ordering.

- [ ] **Step 4: Replace fixed panel dimensions in CSS**

```css
.sidebar { width: var(--diagnostics-width, 300px); flex-basis: var(--diagnostics-width, 300px); }
.drawer { width: var(--drawer-width, 380px); flex-basis: var(--drawer-width, 380px); }
.progress-rail { width: var(--guided-rail-width, 264px); flex-basis: var(--guided-rail-width, 264px); }
```

Keep the existing mobile sheet width declarations inside `@media (max-width: 899px)` so the variables cannot change mobile behavior.

- [ ] **Step 5: Run tests, build, and commit**

Run: `cd dashboard; npx vitest run src/App.test.tsx src/components/ArticleView.test.tsx src/components/PanelResizer.test.tsx src/styles.test.ts`

Run: `npm run build`

Expected: all tests PASS and build exits 0.

```powershell
git add dashboard/src/App.tsx dashboard/src/App.test.tsx dashboard/src/components/ArticleView.tsx dashboard/src/components/ArticleView.test.tsx dashboard/src/styles.css dashboard/src/styles.test.ts
git commit -m "feat(ui): make all side panels adjustable"
```

---

### Task 4: Full-Label Graph Cards with Shared Dimensions

**Files:**
- Create: `dashboard/src/lib/nodeDimensions.ts`
- Create: `dashboard/src/lib/nodeDimensions.test.ts`
- Modify: `dashboard/src/lib/layout.ts`
- Modify: `dashboard/src/lib/layout.test.ts`
- Modify: `dashboard/src/components/Canvas.tsx`
- Modify: `dashboard/src/components/nodes.tsx`
- Modify: `dashboard/src/styles.css`
- Modify: `dashboard/src/styles.test.ts`

**Interfaces:**
- Produces: `NODE_CARD_WIDTH = 220`, `NODE_MIN_HEIGHT = 72`, and `nodeCardSize(label: string): { width: number; height: number }`.
- Consumes: node labels already present on `KENode`; no DOM measurement or new dependency.

- [ ] **Step 1: Write failing node-dimension tests**

```ts
import { describe, expect, it } from "vitest";
import { nodeCardSize } from "./nodeDimensions";

describe("nodeCardSize", () => {
  it("keeps short labels compact", () => {
    expect(nodeCardSize("Attention")).toEqual({ width: 220, height: 72 });
  });

  it("allocates more height for a complete long concept label", () => {
    expect(nodeCardSize(
      "Disparity turns a weak attribute inference attack into a targeted threat",
    ).height).toBeGreaterThan(72);
  });

  it("accounts for unbroken identifiers without truncation", () => {
    expect(nodeCardSize("universal-post-training-backdoor-detection").height)
      .toBeGreaterThanOrEqual(90);
  });
});
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `cd dashboard; npx vitest run src/lib/nodeDimensions.test.ts`

Expected: FAIL because `nodeDimensions.ts` does not exist.

- [ ] **Step 3: Implement conservative word-aware dimensions**

```ts
export const NODE_CARD_WIDTH = 220;
export const NODE_MIN_HEIGHT = 72;
const CHARACTERS_PER_LINE = 24;
const LABEL_LINE_HEIGHT = 18;
const CARD_CHROME_HEIGHT = 54;

export function estimatedLabelLines(label: string): number {
  const words = label.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) return 1;
  let lines = 1;
  let used = 0;
  for (const word of words) {
    const chunks = Math.max(1, Math.ceil(word.length / CHARACTERS_PER_LINE));
    if (chunks > 1) {
      if (used > 0) lines += 1;
      lines += chunks - 1;
      used = word.length % CHARACTERS_PER_LINE;
    } else if (used === 0 || used + 1 + word.length <= CHARACTERS_PER_LINE) {
      used += (used ? 1 : 0) + word.length;
    } else {
      lines += 1;
      used = word.length;
    }
  }
  return lines;
}

export function nodeCardSize(label: string) {
  return {
    width: NODE_CARD_WIDTH,
    height: Math.max(NODE_MIN_HEIGHT, CARD_CHROME_HEIGHT + estimatedLabelLines(label) * LABEL_LINE_HEIGHT),
  };
}
```

- [ ] **Step 4: Make ELK and React Flow consume the same dimensions**

In `layout.ts`, include `[node.id, ...Object.values(nodeCardSize(node.label))]` in the cache key and pass each size to ELK children. In `Canvas.tsx`, use the same result for `width` and `height` on member and cluster nodes. Extend the fake ELK harness to capture the layout request and assert the dimensions match `nodeCardSize("Node")`.

- [ ] **Step 5: Remove visual truncation**

```css
.node-card {
  display: flex;
  width: 100%;
  height: 100%;
  flex-direction: column;
  justify-content: center;
}
.node-label {
  display: block;
  overflow: visible;
  white-space: normal;
  overflow-wrap: anywhere;
  text-overflow: clip;
  line-height: 1.3;
  text-wrap: pretty;
}
```

Add stylesheet tests that reject `white-space: nowrap`, `text-overflow: ellipsis`, and `overflow: hidden` inside `.node-label`.

- [ ] **Step 6: Run focused tests, build, and commit**

Run: `cd dashboard; npx vitest run src/lib/nodeDimensions.test.ts src/lib/layout.test.ts src/styles.test.ts`

Run: `npm run build`

Expected: PASS and build exit 0.

```powershell
git add dashboard/src/lib/nodeDimensions.ts dashboard/src/lib/nodeDimensions.test.ts dashboard/src/lib/layout.ts dashboard/src/lib/layout.test.ts dashboard/src/components/Canvas.tsx dashboard/src/components/nodes.tsx dashboard/src/styles.css dashboard/src/styles.test.ts
git commit -m "fix(graph): show complete node labels"
```

---

### Task 5: Lossless Markdown-to-KaTeX Math Preservation

**Files:**
- Modify: `dashboard/src/lib/mathHtml.ts`
- Modify: `dashboard/src/lib/mathHtml.test.ts`
- Modify: `dashboard/src/components/Drawer.tsx`
- Modify: `dashboard/src/components/Drawer.test.tsx`

**Interfaces:**
- Replaces: `preserveInlineMathForMarkdown(markdown: string)`.
- Produces: `preserveMathForMarkdown(markdown: string): string`, preserving every backslash inside complete `\(...\)` and `$$...$$` spans while skipping fenced and inline code.

- [ ] **Step 1: Write the failing exact-equation tests**

```ts
const ATTACK_SET = String.raw`$$
\mathbb{D}_{\text{attack}} \;=\; \big\{\, \big((n(x), y),\; s_i\big) \;:\; |Y_{\text{match}}(x)| = 1,\; i \in Y_{\text{match}}(x) \,\big\}
$$`;

it("protects TeX punctuation escapes in multiline display math", () => {
  const preserved = preserveMathForMarkdown(ATTACK_SET);
  expect(preserved).toContain("&#92;;=&#92;;");
  expect(preserved).toContain("&#92;,");
  expect(preserved).toContain("&#92;big");
  expect(preserved).toContain("&#92;text{attack}");
});

it("does not alter fenced or inline code", () => {
  expect(preserveMathForMarkdown("`\\(x\\)`\n```tex\n$$\\;$$\n```")).toBe(
    "`\\(x\\)`\n```tex\n$$\\;$$\n```",
  );
});

it("renders the reported attack-set equation with KaTeX", () => {
  const html = renderMathToString(ATTACK_SET);
  expect(html).toContain("katex-display");
  expect(html).not.toContain(ATTACK_SET);
});
```

- [ ] **Step 2: Run focused tests and verify RED**

Run: `cd dashboard; npx vitest run src/lib/mathHtml.test.ts src/components/Drawer.test.tsx`

Expected: FAIL because display-math backslashes before punctuation are not protected.

- [ ] **Step 3: Implement a delimiter-aware scanner**

Scan the full Markdown string so `$$` spans may cross lines. At line starts, copy complete backtick/tilde fences without modification. Copy complete inline-code runs without modification. For complete `\(...\)` or `$$...$$` spans, replace every `\` with `&#92;`; copy incomplete delimiters literally. Export the new helper and update `Drawer.tsx` to call it.

The scanner must use indexes, not a single regular expression, so multiline display math and code exclusions remain deterministic.

```ts
function protectMathInProse(text: string): string {
  let output = "";
  let cursor = 0;
  while (cursor < text.length) {
    if (text[cursor] === "`") {
      let ticks = 1;
      while (text[cursor + ticks] === "`") ticks += 1;
      const delimiter = "`".repeat(ticks);
      const close = text.indexOf(delimiter, cursor + ticks);
      if (close < 0) return output + text.slice(cursor);
      output += text.slice(cursor, close + ticks);
      cursor = close + ticks;
      continue;
    }

    const display = text.startsWith("$$", cursor);
    const inline = text.startsWith(String.raw`\(`, cursor);
    if (display || inline) {
      const closeDelimiter = display ? "$$" : String.raw`\)`;
      const openLength = display ? 2 : 2;
      const close = text.indexOf(closeDelimiter, cursor + openLength);
      if (close < 0) return output + text.slice(cursor);
      const end = close + closeDelimiter.length;
      output += text.slice(cursor, end).replace(/\\/g, "&#92;");
      cursor = end;
      continue;
    }

    output += text[cursor];
    cursor += 1;
  }
  return output;
}

export function preserveMathForMarkdown(markdown: string): string {
  const lines = markdown.match(/[^\n]*(?:\n|$)/g) ?? [];
  let output = "";
  let prose = "";
  let fence: { character: string; length: number } | null = null;

  for (const line of lines) {
    if (!line) continue;
    const withoutNewline = line.endsWith("\n") ? line.slice(0, -1) : line;
    const marker = withoutNewline.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);

    if (fence) {
      output += line;
      if (
        marker
        && marker[1][0] === fence.character
        && marker[1].length >= fence.length
        && marker[2].trim() === ""
      ) fence = null;
      continue;
    }

    if (marker) {
      output += protectMathInProse(prose);
      prose = "";
      output += line;
      fence = { character: marker[1][0], length: marker[1].length };
      continue;
    }

    prose += line;
  }

  return output + protectMathInProse(prose);
}
```

- [ ] **Step 4: Add the end-to-end Drawer regression assertion**

Render `RichMarkdown` with `ATTACK_SET` and assert the server markup contains `katex-display`, the complete `mathbb{D}`/`text{attack}` structure, and no `;=;` literal fallback.

- [ ] **Step 5: Run focused tests, KaTeX check, and commit**

Run: `cd dashboard; npx vitest run src/lib/mathHtml.test.ts src/components/Drawer.test.tsx src/components/blocks/blocks.test.tsx`

Run:

```powershell
$mathPages = Get-ChildItem ..\tmp_user_dashboards\2504-pages -Filter *.md | Select-Object -ExpandProperty FullName
node katexcheck.mjs $mathPages
```

Expected: tests PASS; KaTeX check exits 0 with no invalid equation report.

```powershell
git add dashboard/src/lib/mathHtml.ts dashboard/src/lib/mathHtml.test.ts dashboard/src/components/Drawer.tsx dashboard/src/components/Drawer.test.tsx
git commit -m "fix(math): preserve TeX through markdown"
```

---

### Task 6: Full Verification and Real Dashboard Rebuilds

**Files:**
- Regenerate temporarily: `dashboard/src/data.gen.ts`
- Rebuild: `tmp_user_dashboards/2504/`
- Rebuild: `tmp_user_dashboards/luna-run-2026-07-17/2205/dashboard/`
- Restore and commit: `dashboard/src/data.gen.ts` fixture state only if the restored file differs intentionally.

**Interfaces:**
- Consumes: all previous tasks and the existing `build_data.py` one-way data bundler.
- Produces: verified local dashboards with the updated shared UI bundle.

- [ ] **Step 1: Run the complete automated verification suite**

```powershell
cd dashboard
npx vitest run
npx tsc --noEmit
python -m pytest tests -x
npm run build
cd ..
python -m pytest -x
```

Expected: every command exits 0; no Vitest failures, TypeScript errors, pytest failures, or Vite build errors.

- [ ] **Step 2: Rebuild the 2504 dashboard from its existing inputs**

```powershell
cd dashboard
python build_data.py --graph ..\tmp_user_dashboards\2504-concept-graph.real.json --pack ..\tmp_user_dashboards\2504-pack.json --pages-dir ..\tmp_user_dashboards\2504-pages --out src\data.gen.ts
npm run build
Copy-Item -Recurse -Force dist\* ..\tmp_user_dashboards\2504\
```

Expected: bundler reports the node/tour counts, build exits 0, and `tmp_user_dashboards/2504/index.html` plus assets have current timestamps.

- [ ] **Step 3: Rebuild the 2205 Luna dashboard from its existing inputs**

```powershell
cd dashboard
python build_data.py --graph ..\tmp_user_dashboards\luna-run-2026-07-17\2205\concept-graph.json --pack ..\tmp_user_dashboards\luna-run-2026-07-17\2205\pack.json --pages-dir ..\tmp_user_dashboards\luna-run-2026-07-17\2205\pages --out src\data.gen.ts
npm run build
Copy-Item -Recurse -Force dist\* ..\tmp_user_dashboards\luna-run-2026-07-17\2205\dashboard\
```

Expected: build exits 0 and the 2205 dashboard assets have current timestamps.

- [ ] **Step 4: Restore the fixture-generated development state**

```powershell
cd dashboard
python build_data.py --graph ..\fixtures\aiayn_concept_graph.json --pack ..\fixtures\aiayn_tiny_pack.json --pages-dir ..\fixtures\pages --wiki-dir ..\fixtures\wiki --out src\data.gen.ts
npx vitest run
```

Expected: the fixture reports its normal node/tour counts and the full Vitest suite remains green.

- [ ] **Step 5: Verify visually at 1440×900, 1100×800, 900×800, and 640×800**

For both real dashboards:

- drag each visible separator to its minimum and maximum;
- resize each separator with Arrow keys, Shift+Arrow, Home, and End;
- double-click each separator and confirm the default returns;
- reload and confirm preferred desktop widths return;
- switch Guided/Explore and verify panel widths remain independent;
- open the explanation drawer and ensure the graph remains usable;
- confirm every graph node label is visible with no overlaps;
- inspect the `\mathbb{D}_{\text{attack}}` equation and other `\;`/`\,` equations;
- confirm mobile renders sheets without separators;
- confirm no page overflow, blank canvas, console error, or external network request.

- [ ] **Step 6: Review the final diff and commit generated dashboard artifacts only if tracked**

Run: `git status --short` and `git diff --check`.

Do not add existing untracked scratch directories. If the real dashboards are ignored/untracked, leave them local and commit only source/test changes already committed by Tasks 1–5. If tracked generated files changed, add only those exact paths and commit:

```powershell
git add dashboard/src/data.gen.ts tmp_user_dashboards/2504 tmp_user_dashboards/luna-run-2026-07-17/2205/dashboard
git commit -m "chore: rebuild local paper dashboards"
```

Expected: `git diff --check` prints nothing; only intended paths are staged.

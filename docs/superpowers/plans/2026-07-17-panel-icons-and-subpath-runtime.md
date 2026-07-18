# Panel Icons and Subpath Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one-click left/right panel icon controls that preserve graph context and make production dashboard assets work at both `/` and nested paper paths.

**Architecture:** Keep panel visibility explicit: the left panel remains App-owned responsive UI state, while the right panel visibility joins the selected node in the Zustand store so graph navigation and visualization actions can open it consistently. Render two accessible SVG icon buttons through the existing compact-pill control, and use Vite's relative base so every generated dashboard resolves chunks and the ELK worker from its own directory.

**Tech Stack:** React 19, TypeScript, Zustand 5, Vitest, Vite 6, CSS, Python dashboard fixture tooling.

## Global Constraints

- Panel controls appear only in Explore mode and use icons rather than visible text.
- Closing Details preserves the selected node and graph highlight.
- The right control is disabled until a node is selected.
- Existing modal focus traps, Escape behavior, focus restoration, and resizers remain functional.
- No external network access or runtime fetches are introduced.
- Both cached paper dashboards retain their existing `--viz-dir` content.

---

### Task 1: Separate right-panel visibility from graph selection

**Files:**
- Modify: `dashboard/src/store.ts`
- Modify: `dashboard/src/store.test.ts`

**Interfaces:**
- Produces: `drawerOpen: boolean` and `setDrawerOpen(open: boolean): void` on `AppState`.
- Produces: `setSelected(id)` opens Details for non-null selections and closes it when clearing selection.
- Produces: `openVisualization(nodeId)` selects the node and opens Details atomically.

- [ ] **Step 1: Write failing store tests**

Add tests which reset `selected` and `drawerOpen`, call `setSelected("attention")`, `setDrawerOpen(false)`, `setDrawerOpen(true)`, and `setSelected(null)`, then assert that selection survives the hide/show cycle and that the drawer cannot open without a selection. Extend the visualization action test to expect `drawerOpen: true`.

- [ ] **Step 2: Run the store tests and verify RED**

Run: `npm test -- src/store.test.ts`

Expected: FAIL because `drawerOpen` and `setDrawerOpen` do not exist.

- [ ] **Step 3: Implement the minimal store state**

Add the fields to `AppState` and initialize them as follows:

```ts
drawerOpen: false,
setDrawerOpen: (drawerOpen) => set((state) => ({
  drawerOpen: drawerOpen && state.selected !== null,
})),
setSelected: (selected) => set({
  selected,
  drawerOpen: selected !== null,
}),
```

Add `drawerOpen: true` to `openVisualization`.

- [ ] **Step 4: Run the store tests and verify GREEN**

Run: `npm test -- src/store.test.ts`

Expected: all store tests PASS.

- [ ] **Step 5: Commit the state slice**

```powershell
git add dashboard/src/store.ts dashboard/src/store.test.ts
git commit -m "feat(ui): preserve selection when details panel closes"
```

### Task 2: Add accessible panel icon toggles and responsive hide/show behavior

**Files:**
- Modify: `dashboard/src/components/TopBar.tsx`
- Modify: `dashboard/src/components/TopBar.test.tsx`
- Modify: `dashboard/src/components/Drawer.tsx`
- Modify: `dashboard/src/components/Drawer.test.tsx`
- Modify: `dashboard/src/App.tsx`
- Modify: `dashboard/src/App.test.tsx`
- Modify: `dashboard/src/styles.css`

**Interfaces:**
- Consumes: `drawerOpen`, `setDrawerOpen`, `selected` from Task 1.
- Produces: `PanelSideIcon({ side: "left" | "right" })` decorative SVG.
- Produces: TopBar callbacks `onToggleSidebar()` and `onToggleDrawer()`.
- Produces: `Drawer({ onClose(): void })` so Close hides without clearing selection.

- [ ] **Step 1: Write failing TopBar tests**

Update the Explore fixture props with `drawerOpen`, `drawerAvailable`, `onToggleDrawer`, and `onToggleSidebar`. Assert that Explore markup contains icon buttons named `Open left panel` and `Open right panel`, `aria-controls="left-panel"` and `aria-controls="drawer"`, no visible `Diagnostics` copy, and a disabled right button when `drawerAvailable` is false. Assert Guided markup contains neither panel button.

- [ ] **Step 2: Write failing App/Drawer lifecycle tests**

Update the lifecycle helper assertions so closing a visible drawer is modeled by `drawerOpen: false` while `selected` remains unchanged. Add a Drawer presentation test that invokes the supplied `onClose` callback rather than expecting `setSelected(null)`.

- [ ] **Step 3: Run the focused tests and verify RED**

Run: `npm test -- src/components/TopBar.test.tsx src/components/Drawer.test.tsx src/App.test.tsx`

Expected: FAIL because the icon controls and non-destructive Drawer close API do not exist.

- [ ] **Step 4: Implement the icon controls**

In `TopBar.tsx`, render two `CompactPill` controls only in Explore. Each contains an `aria-hidden="true"`, `focusable="false"`, 20×20 SVG showing an outlined rectangle with a vertical divider on the requested side. Use action labels and titles derived from state:

```tsx
aria-label={sidebarOpen ? "Close left panel" : "Open left panel"}
aria-controls="left-panel"
aria-expanded={sidebarOpen}
aria-pressed={sidebarOpen}
```

The right button uses the matching Details state, targets `drawer`, and is disabled when no node is selected.

- [ ] **Step 5: Wire panel state through App and Drawer**

Read `drawerOpen` and `setDrawerOpen` from the store. Toggle the left state rather than only opening it. Render each panel and its resizer only when its visibility state is true. Pass `onClose={() => setDrawerOpen(false)}` to Drawer, and make Escape perform the same hide action. Preserve `setSelected(null)` only for operations that genuinely clear graph selection, such as invalid node cleanup.

Initialize the left panel open on wide viewports and closed on narrow viewports. When the viewport becomes narrow, close the left sheet so resizing a desktop window cannot unexpectedly create a modal overlay.

- [ ] **Step 6: Add minimal icon/panel CSS**

Replace the mobile-only `.sidebar-sheet-trigger` rule with a shared `.panel-toggle` rule, size the SVG to 18–20px, and add a closed desktop state that removes the sidebar from layout. Reuse existing pill hover, focus, active, and disabled styles.

- [ ] **Step 7: Run focused tests and verify GREEN**

Run: `npm test -- src/components/TopBar.test.tsx src/components/Drawer.test.tsx src/App.test.tsx`

Expected: all focused tests PASS.

- [ ] **Step 8: Run the complete frontend suite**

Run: `npm test`

Expected: all Vitest tests PASS with zero failures.

- [ ] **Step 9: Commit the interface slice**

```powershell
git add dashboard/src/components/TopBar.tsx dashboard/src/components/TopBar.test.tsx dashboard/src/components/Drawer.tsx dashboard/src/components/Drawer.test.tsx dashboard/src/App.tsx dashboard/src/App.test.tsx dashboard/src/styles.css
git commit -m "feat(ui): toggle graph panels from icon controls"
```

### Task 3: Make nested dashboard assets self-relative

**Files:**
- Modify: `dashboard/vite.config.ts`
- Create: `dashboard/vite.config.test.ts`

**Interfaces:**
- Produces: Vite configuration property `base: "./"`.
- Guarantees: HTML entry assets and the ELK worker resolve beneath the directory hosting each dashboard.

- [ ] **Step 1: Write the failing Vite configuration test**

```ts
import { describe, expect, it } from "vitest";
import config from "./vite.config";

describe("Vite production paths", () => {
  it("keeps dashboard assets relative to the hosting directory", () => {
    expect(config).toMatchObject({ base: "./" });
  });
});
```

- [ ] **Step 2: Run the configuration test and verify RED**

Run: `npm test -- vite.config.test.ts`

Expected: FAIL because the config has no relative base.

- [ ] **Step 3: Add the minimal Vite base setting**

Add `base: "./"` beside `plugins` in `dashboard/vite.config.ts`.

- [ ] **Step 4: Run the configuration test and verify GREEN**

Run: `npm test -- vite.config.test.ts`

Expected: PASS.

- [ ] **Step 5: Build and inspect production paths**

Run: `npm run build`

Expected: TypeScript and Vite exit 0. Confirm `dist/index.html` uses `./assets/...` and the compiled bundle does not hardcode the ELK worker as `"/assets/elk-worker..."`.

- [ ] **Step 6: Commit the runtime slice**

```powershell
git add dashboard/vite.config.ts dashboard/vite.config.test.ts
git commit -m "fix(graph): resolve layout worker under nested paths"
```

### Task 4: Rebuild and verify both cached paper dashboards

**Files:**
- Regenerate: `tmp_user_dashboards/2504-real/**`
- Regenerate: `tmp_user_dashboards/luna-run-2026-07-17/2205/**`

**Interfaces:**
- Consumes: existing local graph/page caches and each paper's visualization pack via `--viz-dir`.
- Produces: refreshed live dashboard builds for ports 8504 and 8930.

- [ ] **Step 1: Recover the exact local rebuild commands**

Inspect each output's metadata and the existing trial/run documentation. Reuse its cached input paths and visualization directory; do not invoke the LLM pipeline.

- [ ] **Step 2: Rebuild both dashboards**

Run the repository's dashboard builder once for the 2504 root output and once for the 2205 nested output, passing the corresponding `--viz-dir` each time.

Expected: both builds exit 0 and emit new hashed assets.

- [ ] **Step 3: Refresh the two local servers**

Restart or reload the existing localhost servers so 8504 serves the refreshed 2504 build and 8930 serves the parent directory containing `/2205/`.

- [ ] **Step 4: Browser-check 8930**

At `http://127.0.0.1:8930/2205/`, enter Explore and verify the layout worker request returns 200, the loading message disappears, graph nodes render, and both panel icon controls close and reopen their panels.

- [ ] **Step 5: Browser-check 8504**

At `http://127.0.0.1:8504/`, open `Visuals (1)`, select the cached visual, and verify Explore opens, graph nodes render, Details opens, and the interactive iframe is visible. Close and reopen Details with the right icon and confirm the node remains selected.

- [ ] **Step 6: Run final verification**

Run from `dashboard`: `npm test` and `npm run build`.

Run the dashboard/viz Python suites documented for this branch.

Expected: every command exits 0 with zero failing tests.

- [ ] **Step 7: Review scope and working tree**

Run: `git status --short` and `git diff --check HEAD~3..HEAD`.

Expected: only intentional source/test/spec commits plus pre-existing ignored or untracked local fixture outputs; no whitespace errors and no accidental cached-dashboard commit.

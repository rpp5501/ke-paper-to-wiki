# Slice 11 — Knowledge Dashboard UI Design Contract

**Status:** Implementation contract derived from the approved Slice 11 design, 11a data/core plan, and 11b UI plan. This document does not reopen approved product, runtime, data, or technology decisions.

## 1. Product intent

The Knowledge Dashboard is a dense, technical exploration workspace for a researcher or developer who needs to learn a paper, inspect a code graph, or trace the bridge between concepts and their implementations. The primary task is to orient in a dependency graph, select one meaningful node, and understand its context, evidence, and blast radius without leaving the local application.

The experience should feel like a calm, precise graph workbench: dark slate, information-dense, structurally quiet, and responsive even when topology is large. The graph canvas is the focal surface. Side panels explain and diagnose it; they must never compete with it as independent destinations.

The product must support concept, code, and bridged graphs with the same interaction grammar. It is read-only in v1. Rich media, backend services, editing, mobile-specific UA components, export UI, file exploration, time-axis lineage, tensor-shape cards, citation sentiment, and per-variable formula hover are out of scope.

## 2. Layout hierarchy

### Desktop shell

- The application fills the viewport (`100vh`) and uses a three-region workbench around the graph canvas.
- Left sidebar: fixed `300px`, full height, scrolls independently, `1px` right divider. It contains the Insights & Health / Build Trace tabs and their cards.
- Main region: flexible remaining width, column layout.
- Top bar: fixed `52px` height, centered controls with `8px` gaps. It contains view pills, edge-kind pills, blast-radius toggle, and search.
- Canvas: consumes all remaining main-region height. React Flow controls, legend, tour card, player bar, and graph are layered within this region.
- Explain drawer: absent when no node is selected. At viewport widths `≥1280px`, it is a `380px` flex rail with independent scrolling, `16px` padding, and a `1px` left divider. Below `1280px`, the same `380px` drawer is positioned against the canvas/workspace container (`top:0; right:0; bottom:0`) and overlays the canvas instead of reducing its width; separation remains border-only with no drawer shadow.
- Player bar: floating above the bottom center of the canvas (`bottom:18px`), not a document-flow footer.
- Legend: floating at canvas bottom-left (`14px` from each edge).
- Guided tour card: `300px` wide, `26px` from bottom and right, above graph and player layers.

Hierarchy order is: selected graph node and its local topology → explanation/impact → active guided sequence → filters and health findings → legend/meta. The selected node, equation-linked nodes, and blast rings must remain distinguishable without relying on text in the side panels.

### Canvas geometry

- ELK uses layered, top-to-bottom layout with `40px` node-to-node spacing.
- Standard nodes are `180px × 64px` for layout calculation; rendered cards are `180px` wide.
- React Flow starts with `fitView` after positions are available.
- Canvas background dots use `#1e293b` at a `24px` gap.
- Centering a node targets its visual center (`+90px`, `+32px`) at zoom `1.2` over `600ms`.
- Semantic zoom threshold is exactly `0.5`: below it, clustered members are hidden and cluster cards replace them; zooming a cluster targets `0.9` over `500ms`.

## 3. Visual tokens

### Core palette (locked)

| Token | Value | Contract |
|---|---:|---|
| `--bg` | `#0b1220` | Canvas, inset cards, controls, tooltip surface |
| `--surface` | `#111a2c` | Sidebar, drawer, nodes, floating controls/cards |
| `--border` | `#1e293b` | Dividers and standard outlines |
| `--text` | `#e2e8f0` | Primary copy and values |
| `--muted` | `#94a3b8` | Supporting copy, metadata, LOW severity |
| `--accent` | `#4a7ebb` | Selected/active controls, concept identity, equation highlight |
| `--warn` | `#eab308` | MED severity, bridge badge, blast depth 2 |
| `--bad` | `#ef4444` | HIGH severity, hotspot badge, selected blast ring |

Supporting locked graph colors: code identity `#64748b`; implements `#4a9b5e`; prerequisite/builds-on `#cc8855`; ordinary edges `#475569`; blast depth 1 `#f97316`; cluster surface `#0e1626`; neutral badge surface `#1c2a44`; MED/bridge surface `#3b2f14`; HIGH/hotspot surface `#3a1420`; active pill text `#fff`.

Color is semantic, not decorative. Concept blue, code slate, implements green, dependency warm brown, and severity/ring colors must retain their meanings everywhere. Syntax highlighting may use Prism's locally bundled `nightOwl` theme inside code excerpts only.

### Edge and highlight grammar

- `implements`: green, dashed `6 3`, `2px` width.
- `prerequisite` / `builds-on`: `#cc8855`, dashed `4 3`.
- All other edges: `#475569`, solid.
- Equation hover: `3px solid #4a7ebb` around every node in the equation index.
- Blast radius: selected ring `3px #ef4444`; depth 1 `3px #f97316`; depth 2 `3px #eab308`; unrelated nodes opacity `0.1`.
- Hidden edge kinds are removed, not merely faded.

## 4. Typography

- Primary UI typeface is the local operating-system `system-ui, sans-serif` stack. No remote font requests are permitted.
- KaTeX uses its package-bundled local CSS and WOFF2 assets.
- Code excerpts use Prism rendering and a local monospace fallback.
- Node label: `13px`, weight `600`.
- Standard control and primary card copy: `13px`.
- Supporting copy, trace rows, equation labels, step counters, and code: `12px` where specified.
- Chips: `11px`; badges and severity tags: `10px`, severity weight `700`.
- Drawer title uses semantic `h2`; tour title uses `h3`. Preserve semantic heading order even if CSS changes visual size.
- Dynamic counts, ranks, dates, step counters, and centrality values use tabular numerals.
- Body content in the explanation drawer must remain readable at a minimum `1.45` line-height; code may use a tighter `1.5` line-height at `12px`.

## 5. Spacing and density

Use a `4px` base grid. Approved one-off measurements remain locked.

- Node card: `8px 12px` padding; badge row `4px` top gap and `4px` item gap.
- Sidebar tab group: `12px` padding, `8px` gap.
- Sidebar card: `10px` padding, `8px 12px` margin.
- Pill: `4px 12px`; topbar gaps `8px`; separator between view and graph controls `18px`.
- Search: `5px 10px`, `12px` left margin.
- Drawer: `16px` padding; bridge card uses `8px 0` margin.
- Player: `8px 18px`, `14px` internal gap.
- Tour: `16px` padding.
- Tooltip: `6px 8px`, fixed `240px` width.
- Tier rows: `6px 0` padding.

Controls must remain compact, but their interactive hit area must be at least `44 × 44px` through layout or an invisible non-overlapping hit target. Do not enlarge the visible pill measurements unless necessary for text wrapping.

## 6. Depth and radii

The primary depth strategy is surface-color shifts plus quiet `1px` borders. Do not add decorative gradients or broad card shadows.

- Standard node/card radius: `8px`.
- Cluster card: `2px` dashed accent border; `#0e1626` fill.
- Pill radius: `14px`; player radius: `22px`; chip radius: `10px`; badge radius: `8px`; severity radius: `6px`; tooltip radius: `6px`; tour radius: `10px`.
- Tour overlay alone receives the approved elevated shadow: `0 10px 25px #0008`, plus an accent border.
- The drawer and sidebar are structural planes, not floating cards; desktop rails and responsive drawer overlays use dividers, not elevation shadows.

## 7. Component contracts and states

### Graph node cards

- Types: concept, code, cluster.
- Concept card has a `4px` accent-blue left rule; code card has a `4px` slate left rule; cluster has the locked dashed treatment.
- Label is always visible. Optional badges follow in this order: level (`L{level}`), `bridge`, `hotspot #{rank}`. Cluster badge is `{count} nodes`.
- Selected, equation-hovered, and blast-ring states must compose predictably. Equation hover has precedence for the visible outline; selected state must still be conveyed through React Flow selection styling and accessibility state.
- Nodes are actionable buttons in behavior: pointer, Enter, or Space selects; selection opens the drawer. Cluster activation zooms to members instead of opening the drawer.
- While ELK is pending, show a canvas loading state rather than stacking every node at `(0,0)`.

### Insights & Health / Build Trace sidebar

- Tabs are mutually exclusive and exposed as a tablist with `aria-selected`.
- Insight cards show severity tag, rule name, then supporting text. Order is HIGH, MED, LOW from the pure logic result.
- Activating an insight or trace entry selects and centers its node.
- Empty insights copy is exactly: `no findings — healthy graph`.
- Empty trace copy: `no build trace available`.
- Cards must have hover, active, keyboard-focus, and selected-node correlation states.

### Top context switcher and filters

- View labels/copy are exactly: `concepts`, `clusters`, `code`, `bridged`.
- Edge filters/copy are exactly: `implements`, `prerequisite`, `builds-on`.
- Blast toggle copy is exactly: `blast radius`.
- Active pills use accent fill and white text. Inactive pills use surface fill and muted text.
- Edge pills express “visible/on” as active; turning one off hides that edge kind.
- Views are mutually exclusive; edge-kind and blast controls are toggles with `aria-pressed`.
- Search placeholder is exactly `search… (Enter)`. Enter selects the first case-insensitive label match, reveals any required ancestor/context visibility, centers it, and opens its drawer. No match must produce an inline, announced `No matching node` state without moving the camera.

### Explain drawer

- Opens when a node is selected and dismisses on empty-canvas click. It scrolls independently.
- Header: node label, then `{kind} · {source_ref or —} · depends-on-this: immediate {n}, secondary {n}`.
- Concept content order: bridge relationships, equation pills, tier accordion. Tier labels/copy are exactly `TL;DR`, `Intuition`, `Mechanics`, `The Math`, `Go Deeper`; only `TL;DR` starts open.
- Code content includes a locally bundled syntax-highlighted excerpt only when present, capped at 80 lines, plus graph facts and bridge relationships.
- Bidirectional bridge rows use the locked meanings/copy: `implemented by {id}` for concept → code and `implements {id}` for code → concept. Rows navigate to and center the linked node.
- Equation hover highlights every node in `eqIndex[eq_id]`; clearing pointer or keyboard focus clears the highlight. Per-variable hover is not implied.
- Glossary terms expose one-sentence definitions by hover and keyboard focus. Tooltip content must not be hover-only.
- Missing content copy is exactly: `no page or note for this node yet`.
- Math failure shows the original TeX text rather than a blank or crash.

### Player bar

- Paper/concept graphs expose only the idle action `▶ reading path`. Code and bridged graphs expose only `▶ trace blast radius`, disabled when no node is selected. The two modes are never shown together and are selected from `KE_DATA.meta.kind`.
- Active state shows previous, label, `step {current} / {total}`, next/play-pause controls, and close. Paper/concept graphs use deterministic tour/reading-path order; code/bridged graphs use dependent rings sorted by depth.
- Prev/Next and auto-advance select the step node and animate the camera. Boundary controls disable at first/last step. Closing clears player state but does not clear node selection.
- Auto-advance must never start implicitly and must stop at the last step, on close, or when reduced motion is requested.

### Guided tour

- Initial card title/copy: `Guided tour`, `Walk the {n} key concepts.`, `Start`.
- Active card shows the deterministic step title/description, `Back`, `{current}/{total}`, and `Next`; final action is `Finish`.
- Back is disabled on step 1. Starting or changing steps selects the first `nodeId`, centers the camera, and opens the drawer.
- The card must have a dismiss action in addition to Finish so it never permanently obscures graph content. Completion/dismissal hides the card for the current session; it must not immediately reopen.

### Legend

- Labels/copy are exactly: `concept`, `code`, `implements`, `prereq / builds-on`.
- It is explanatory, not interactive. It must ignore pointer events if it overlaps a graph interaction target.

### Code viewer

- Uses local Prism assets only, `12px` type, `10px` padding, `8px` radius, horizontal overflow, preserved whitespace, and an accessible label identifying the selected node.
- If no excerpt exists, omit the viewer rather than render an empty code surface.

## 8. Interaction and motion

- Empty-canvas click clears selection and closes the drawer.
- Insight, trace, search, bridge, tour, player, and graph-node actions all converge on the same store selection and camera-centering behavior.
- Camera transitions use the locked timings: node center `600ms`; cluster zoom `500ms`. Other hover/focus/color transitions should be `120–180ms` and limited to `opacity`, `transform`, `color`, `background-color`, `border-color`, or `outline-color`; never `transition: all`.
- Buttons may use restrained press feedback (`scale(.97)`) without moving surrounding layout.
- In `prefers-reduced-motion: reduce`, camera transitions become immediate, auto-advance is unavailable, and movement transforms are removed; state changes and focus indicators remain immediate and legible.
- Blast ghosting, equation hover, filter changes, and LOD swaps must not trigger a new main-thread topology calculation.

## 9. Accessibility

- Use native `button`, `input`, `details/summary`, and links where applicable. React Flow nodes must be keyboard-focusable and expose an accessible name from their label.
- All functionality is operable by keyboard. Tab order follows: sidebar tabs/content → top controls/search → canvas controls/nodes → player/tour → drawer content.
- Arrow keys move within tab groups and mutually exclusive view pills; Enter/Space activates buttons and nodes; Escape dismisses the tour or drawer context without unexpectedly clearing unrelated filters.
- Every interactive item has a visible focus indicator with at least a `2px` accent outline and `2px` offset. Focus is never represented by color fill alone.
- On drawer open, announce the selected node and drawer presence without forcibly stealing focus from repeated graph exploration. Direct user activation of a sidebar/bridge/tour target may move focus to the destination heading; closing returns focus to the initiator when available.
- Severity tags include text (`HIGH`, `MED`, `LOW`); graph identities and edge meanings are not communicated by color alone because the legend, labels, dash patterns, and badges remain visible.
- Use `aria-live="polite"` for layout-ready, search no-result, tour/player step, and loading/error announcements. Do not announce camera motion frame-by-frame.
- Text and controls must meet WCAG 2.2 AA contrast. Muted text is supporting text only; essential labels use primary text.
- Tooltips open on pointer hover and keyboard focus, remain available while hovered/focused, and do not obscure the triggering term.

## 10. Responsive behavior

The desktop measurements above are canonical. Responsiveness preserves graph interaction and avoids compressing panels below usable widths.

- `≥1280px`: full three-region shell with `300px` sidebar and a conditional `380px` flex-rail drawer.
- `900–1279px`: sidebar remains `300px`; the `380px` drawer becomes a right-side, border-only overlay positioned within the canvas/workspace at `top:0; right:0; bottom:0` and `min(380px, 90vw)`, with a dismiss affordance and no shadow. Topbar may wrap into two compact rows while retaining the `52px` minimum row height without overlapping the drawer.
- `<900px`: sidebar and drawer become mutually independent overlay sheets; the canvas remains full-viewport behind them. Provide labeled controls to open Insights/Trace and the selected-node drawer. Do not render three squeezed columns.
- `<640px`: top controls scroll horizontally or group into labeled overflow sections; they must not shrink below their readable/hit-target sizes. Player uses a bottom sheet-width treatment with safe insets; tour card uses `calc(100vw - 24px)` and `12px` side offsets. Legend may collapse to a labeled disclosure.
- At every width, React Flow controls, player, tour, legend, and open sheets must not overlap the same critical bottom-corner hit targets. Respect `env(safe-area-inset-*)`.
- Responsive changes alter presentation only. View/filter/selection/player/tour state and build-time data remain identical.

## 11. Offline and local runtime constraints

- The dashboard runs only from a localhost origin: development via `npm run dev`; production via `npm run build` then `python -m http.server -d dist 8000`, opened at `http://localhost:8000/`.
- No runtime data fetch is allowed. All graph, page, note, insight input, tour, trace, centrality, equation index, glossary, mtime, and excerpt data comes from build-time `KE_DATA` in `src/data.gen.ts`.
- No external CDNs, APIs, telemetry, web fonts, images, or remote assets. Markdown images are stripped at bundle time. KaTeX CSS/fonts, ELK worker, Prism code, React assets, and every other dependency are emitted as local Vite assets.
- Root-absolute or relative asset URLs are valid only when they resolve to the same localhost origin. `base:'./'` is neither required nor prescribed.
- ELK must run in a Vite-bundled Web Worker. A synchronous main-thread production fallback is prohibited. If the worker fails, show a recoverable layout error; do not silently execute ELK on the main thread.
- Preserve raw Unicode, including `√dₖ`, from the data bundle through rendering and production output.
- The existing single-file Cytoscape lite exporter is a separate portable artifact and is not modified by this UI contract.

## 12. UI considerations and required states

### Loading

- App/data module load: use the local shell and a concise `Loading knowledge graph…` status; never a remote spinner asset.
- Layout: keep panels usable, show `Laying out {n} nodes…` over the canvas, and prevent selection until positions are ready. Do not render all nodes at the origin.
- Tour/player actions that require layout are disabled until layout-ready and explain why via accessible description.

### Empty

- Zero graph nodes: show `No graph data in this build.` in the canvas with bundler guidance; disable search, blast radius, the graph-kind-appropriate player action, and tour.
- No insights: exact locked copy `no findings — healthy graph`.
- No trace: `no build trace available`.
- No page/note: exact locked copy `no page or note for this node yet`.
- No code excerpt: omit the viewer.
- No tour: omit the tour card and disable reading-path playback.

### Error

- Worker/layout failure: show `Graph layout failed.` with a `Retry layout` action and a diagnostic summary suitable for local debugging. Do not fetch or fall back to main-thread ELK.
- Render/content errors are contained to the drawer or code/math block; the canvas and filters remain usable.
- Search no-result is non-destructive and announced; existing selection remains unchanged.
- Invalid selected IDs clear the drawer safely and announce that the node is unavailable.

### Disabled

- Disabled controls use muted text, reduced opacity, default cursor, and remain readable; no hover/press animation.
- `trace blast radius` is disabled without selection; boundary navigation is disabled; controls dependent on absent data or pending layout are disabled.
- Disabled state is conveyed through the native `disabled` attribute and accessible explanation where the reason is not obvious.

### Focus

- Focus remains stable when filters, LOD, ghosting, or equation hover rerender the graph.
- If a focused node becomes hidden through a view/filter/LOD change, move focus to the relevant active control and announce the visibility change.
- Floating player/tour and overlay sheets have deliberate focus order; modal-style sheets trap focus and restore it on close, while the nonmodal desktop drawer does not.

### Large graphs

- Worker layout and state updates must keep pan, zoom, filters, and panels responsive. No main-thread ELK fallback.
- LOD below `0.5` replaces clustered members; unclustered nodes remain visible.
- Avoid rendering expensive drawer markdown/code for unselected nodes. Code is limited to the build-time top-20-hotspot/implements union and 80 lines per excerpt.
- During rapid view/filter/selection changes, coalesce camera actions and cancel superseded animations so the viewport does not queue motion.
- Labels may truncate visually on cards, but full labels must remain in the accessible name and a local tooltip/title.

## 13. Genuine plan conflicts requiring implementation interpretation

1. **Player controls:** the approved design requires Prev/Next/**Play (auto-advance)**, while the 11b component plan only specifies Prev/Next/Close after launch. This contract retains auto-advance because it is an explicit feature-level requirement.
2. **Search behavior:** the approved design requires search to reveal ancestors, center, and select, while the 11b code only finds the first label match, centers, and selects. This contract retains ancestor/context reveal and adds a no-result state.
3. **Drawer markdown path:** the 11b interface text says the drawer renders bundled markdown with `react-markdown` plus a KaTeX pass, but the provided tier implementation inserts the tier body with `dangerouslySetInnerHTML` after only math/glossary replacement, leaving non-math Markdown unparsed. The visual contract requires correctly rendered Markdown and KaTeX; the implementation mechanism must be reconciled without introducing runtime fetches.

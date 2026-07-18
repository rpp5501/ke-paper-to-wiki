# Adjustable Panels and Graph Legibility Design

**Date:** 2026-07-17  
**Status:** Approved direction, pending written-spec review

## Goal

Improve the paper dashboard as a research workbench by making all three side panels adjustable, ensuring graph-node labels remain visible, and preserving TeX syntax through Markdown so KaTeX receives the original equations.

The graph or article remains the focal workspace. Panels support that workspace without permanently consuming an arbitrary fixed width.

## Scope

This change covers:

- the Guided reading progress rail;
- the Explore diagnostics sidebar;
- the Explore explanation drawer;
- graph node dimensions and label wrapping;
- inline and display-math preprocessing before React Markdown and KaTeX;
- desktop, tablet, keyboard, pointer, and regression-test behavior.

It does not add detachable windows, arbitrary docking, graph-layout algorithms beyond the current ELK layered layout, new dependencies, or changes to generated paper content.

## Product Direction

The dashboard should feel like a focused research workbench: graphite and ink surfaces, blueprint-blue focus, restrained semantic color, dense supporting controls, and generous space for the primary reading or graph surface.

Domain concepts include research papers, dependency paths, notation, prerequisites, downstream impact, guided reading, and annotated equations. The existing palette already expresses this world through graphite surfaces, paper-like text, blueprint blue, theorem gold, verification green, and error red, so the change will extend the current tokens rather than introduce a new visual theme.

The signature interaction is a **focus corridor**: the reader can resize supporting context around a central article or graph, while graph cards expand vertically enough to expose their complete concept names.

The direction takes inspiration from Understand Anything's emphasis on graphs that teach and its searchable, selectable knowledge graph, and from TrueCourse's restrained analytical dashboard presentation:

- https://github.com/Egonex-AI/Understand-Anything
- https://github.com/truecourse-ai/truecourse

## Architecture

### Shared panel sizing model

Add a small panel-sizing module that owns:

- panel identifiers: `guided-rail`, `diagnostics`, and `explanation`;
- default, minimum, and maximum widths;
- width clamping against both the panel's range and the available viewport;
- keyboard resize calculations;
- versioned local persistence.

Panel ranges:

| Panel | Default | Minimum | Maximum |
| --- | ---: | ---: | ---: |
| Guided rail | 264px | 220px | 420px |
| Diagnostics | 300px | 240px | 480px |
| Explanation | 380px | 320px | 640px |

The main workspace must retain at least 360px when panel widths are clamped. On viewports below 900px, panels keep the existing modal-sheet behavior and ignore persisted desktop widths.

Widths are stored in a versioned local-storage record. Missing, corrupt, nonnumeric, or out-of-range values fall back to defaults and never prevent the app from rendering.

### Resizer component

Create one reusable vertical separator component rather than three unrelated drag implementations.

Behavior contract:

- pointer drag updates width continuously;
- `ArrowLeft` and `ArrowRight` resize by 16px;
- `Shift` plus an arrow resizes by 48px;
- `Home` sets the minimum;
- `End` sets the maximum allowed by the current viewport;
- double-click restores the default;
- the separator exposes `role="separator"`, `aria-orientation="vertical"`, `aria-valuemin`, `aria-valuemax`, and `aria-valuenow`;
- the visible grip remains subtle, while the interactive hit target is at least 12px wide and receives a clear focus treatment;
- pointer capture prevents the drag from dropping when the cursor crosses the graph canvas.

The left-side panels grow toward the right. The explanation drawer grows toward the left, so its delta is inverted. The component receives the side explicitly rather than inferring it from DOM position.

The shell and article layouts consume widths through CSS custom properties. This keeps React responsible for interaction state and CSS responsible for layout.

### Graph node sizing

Replace the fixed `180x64` layout contract with a shared pure `nodeCardSize()` helper used by both ELK input and React Flow node construction.

The helper will:

- use a wider 220px card for clearer phrases;
- estimate wrapped lines by words, with a conservative fallback for long unbroken tokens;
- reserve vertical space for the label and badge rows;
- return a minimum height but no label-truncation cap.

The card CSS will remove `white-space: nowrap`, ellipsis, and hidden overflow from `.node-label`. Labels will wrap with `overflow-wrap: anywhere` and balanced line height. The React Flow node and its button will share the helper's width and height, so the visual card, hit target, and ELK spacing agree.

Cluster cards use the same width and minimum-height system. Existing title and accessible names remain available, but they are no longer substitutes for visible labels.

### Math preservation

The root formatting defect occurs before KaTeX: CommonMark treats backslashes before punctuation as Markdown escapes. For example, `\;`, `\,`, and `\|` lose their backslashes, so valid TeX reaches KaTeX as literal semicolons, commas, and bars.

Replace the inline-only preprocessing with a delimiter-aware `preserveMathForMarkdown()` function that:

- skips fenced and inline code;
- recognizes `\(...\)` and `$$...$$` math spans;
- replaces every backslash inside a complete math span, including its delimiters, with an HTML character reference before React Markdown parses it;
- leaves incomplete delimiters unchanged so malformed prose is not swallowed;
- does not rewrite TeX semantics or guess at invalid source.

After Markdown parsing, the character references decode back to backslashes. The existing `tokenizeRichText()` and strict KaTeX configuration then receive the original TeX.

The reported equation is a required regression fixture:

```tex
$$
\mathbb{D}_{\text{attack}} \;=\; \big\{\, \big((n(x), y),\; s_i\big) \;:\; |Y_{\text{match}}(x)| = 1,\; i \in Y_{\text{match}}(x) \,\big\}
$$
```

## Component Integration

### `App.tsx`

- Load the diagnostics and explanation widths through the shared sizing hook.
- Set shell/workspace custom properties.
- Render the diagnostics resizer immediately after the left panel on desktop layouts.
- Render the explanation resizer immediately before the drawer.
- Preserve existing modal focus traps, backdrops, Escape ordering, and drawer focus restoration.

### `ArticleView.tsx`

- Load the Guided rail width.
- Apply it to the article shell.
- Render the shared resizer between the progress rail and article scroll region.
- Leave mobile behavior unchanged: the progress rail is hidden below 900px.

### `Canvas.tsx` and `layout.ts`

- Use `nodeCardSize()` for ELK child dimensions and React Flow node dimensions.
- Include dimensions in the layout cache key so future sizing changes cannot reuse stale positions.
- Keep the current layered, downward dependency layout and existing fit behavior.

### `nodes.tsx` and `styles.css`

- Make the button fill the dimensions supplied by React Flow.
- Render complete wrapped labels.
- Style resizers using existing surface, border, focus, and motion tokens.
- Avoid `transition: all`, decorative gradients, and new hardcoded theme colors.

### `Drawer.tsx` and `mathHtml.ts`

- Replace calls to the inline-only preservation helper with the new delimiter-aware helper.
- Keep strict KaTeX, untrusted input handling, and literal-source fallback for genuinely invalid TeX.

## Responsive Behavior

- **1280px and wider:** all visible side panels resize inline with the workspace.
- **900px–1279px:** the diagnostics panel remains inline and resizable; the explanation drawer remains an overlay but is resizable from its left edge.
- **Below 900px:** panels use the current modal-sheet widths and no resizer is rendered.
- **During viewport changes:** stored widths are clamped for the current viewport without overwriting the user's preferred desktop width merely because the window temporarily became smaller.

## Accessibility

- Resizers are keyboard operable and expose current limits and values.
- Focus styling uses the existing 2px accent outline.
- Node labels are visible text, not tooltip-only content.
- Resizing does not alter document order or focus ownership.
- Existing sheet/dialog semantics, inert regions, announcements, and Escape behavior remain intact.
- Reduced-motion preferences continue to suppress movement where the existing graph camera honors them; panel dragging itself is direct manipulation and does not animate.

## Error Handling

- Local-storage access is wrapped because it can be unavailable or throw.
- Invalid persisted data falls back independently per panel.
- Pointer cancellation ends a resize cleanly and releases drag state.
- Incomplete math delimiters remain literal text.
- KaTeX rejection continues to show the original source rather than unsafe or partially rendered HTML.

## Testing Strategy

Follow test-driven development for each behavior.

### Unit tests

- panel width defaults, clamping, keyboard deltas, reset, serialization, corrupt persistence, and viewport constraints;
- node-size estimates for short, long, and unbroken labels;
- ELK receives helper-derived dimensions and the cache key changes with dimensions;
- display and inline math preserve every backslash through Markdown preprocessing;
- the reported `\mathbb{D}_{\text{attack}}` equation renders through KaTeX instead of falling back.

### Component tests

- all three desktop panels render a separator with correct ARIA values;
- keyboard resizing changes the appropriate CSS variable;
- the drawer's resize direction is inverted correctly;
- mobile renders no separators;
- node markup contains the full label and no truncation class contract.

### Visual verification

Verify the generated dashboards at approximately 1440px, 1100px, 900px, and 640px:

- drag each panel to both limits;
- confirm the graph remains usable and labels do not overlap or clip;
- open and resize the explanation drawer;
- switch between Guided and Explore modes;
- inspect the reported equation and other spacing-heavy equations;
- confirm no horizontal page overflow, panel overlap, blank canvas, or console error.

### Completion commands

From `paper-skill-slice9-bridge/dashboard`:

```powershell
npm test
npm run build
python -m pytest tests -x
```

Then rebuild the real local dashboards from their existing graph, pack, and page inputs and repeat the browser checks.

## Success Criteria

- Every desktop/tablet side panel can be adjusted by pointer and keyboard.
- Panel widths survive reloads and safely reset when persisted data is invalid.
- Mobile sheet behavior remains unchanged.
- No graph node label is hidden by single-line ellipsis or a mismatched fixed height.
- ELK and React Flow use the same node dimensions.
- TeX spacing, delimiter, subscript, and `\text{}` commands survive Markdown unchanged.
- The reported equation renders as formatted KaTeX.
- Existing tests, the production build, dashboard Python tests, and responsive browser verification pass.

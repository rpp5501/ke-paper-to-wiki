# Panel Icons and Subpath Runtime Design

## Goal

Give researchers one-click control over both Explore side panels without sacrificing graph context, and make dashboards render correctly whether served at `/` or beneath a paper-specific path such as `/2205/`.

## Confirmed failures

- The `/2205/` graph stalls at `Laying out 20 nodes...` because the compiled ELK worker is requested from `/assets/...`; that URL returns 404 while the worker actually lives at `/2205/assets/...`.
- The current fresh `/` dashboard successfully opens its interactive visual in an iframe. The reported failure is consistent with an older cached build, so deployment verification must include a clean rebuild and reload rather than an unproven visualization-code change.

## Interface direction

Explore's top bar will contain two compact icon buttons:

- A left-panel icon toggles Insights and Build Trace.
- A right-panel icon toggles the selected node's Details panel.

The controls use the existing compact-pill visual language but display familiar panel-layout glyphs instead of text. They have visible hover/focus tooltips and explicit accessible names (`Open left panel`, `Close left panel`, `Open right panel`, or `Close right panel`). Their pressed/expanded state mirrors the panel state.

The pair is the interface signature: matching controls make the graph feel like a technical workbench whose surrounding instruments can be folded away. No new color system or floating controls are introduced.

## Behavior

### Left panel

- The icon toggles the panel on wide and narrow screens.
- On wide screens, closing it removes the panel and its resizer so the graph reclaims the space.
- On narrow screens, it retains the existing modal sheet, backdrop, focus trap, Escape handling, and focus restoration.

### Right panel

- Selecting a graph node opens Details automatically.
- Closing Details hides the panel and its resizer but preserves the selected node and graph highlight.
- Clicking the right-panel icon restores Details for that selected node.
- Until a node has been selected, the right-panel icon is disabled and explains why in its tooltip.
- The drawer's existing close button and Escape key perform the same non-destructive hide action.
- On narrow screens, the existing modal drawer focus behavior remains intact.

### Mode changes

- Panel controls are shown only in Explore mode.
- Panel visibility is retained while moving between Guided and Explore during the same session.
- The graph selection remains the source of Details content; panel visibility is a separate UI state.

## Runtime fix

The dashboard build will use a relative Vite asset base. This lets `index.html`, JavaScript chunks, and the ELK worker resolve from the directory containing each dashboard, supporting both `/` and `/2205/` without paper-specific source changes.

Both paper dashboards will be rebuilt from local cached inputs and their existing `--viz-dir` packs. The live servers will be refreshed so the browser receives the new hashed assets.

## Accessibility

- Buttons have stable accessible names describing their action, not only their icon.
- `aria-controls`, `aria-expanded`, and `aria-pressed` communicate state.
- Existing focus restoration and modal focus traps remain in place.
- Icons are decorative to assistive technology.
- Keyboard and Escape behavior are covered by component tests.

## Verification

- Unit/component tests cover both icon toggle states, disabled right-panel behavior, preserved selection, and resizer visibility.
- The dashboard TypeScript and Vitest suites pass.
- A production build is served at `/` and `/2205/`.
- The ELK worker returns 200 at the path requested by the `/2205/` bundle, and the graph reaches ready state with rendered nodes.
- The `/` visual gallery opens the cached interactive visual and mounts its iframe.
- Both icons are exercised at desktop and narrow viewport sizes.

# Reader v2 — Article-first learner experience + UI redesign

**Date:** 2026-07-16
**Status:** Approved design, pending user review of this written spec
**Scope:** `paper-skill-slice9-bridge/dashboard/` (app + build_data.py) and 2504 content (`tmp_user_dashboards/2504-pages/`)

## Problem

The slice-11 redesign shipped good pedagogy but the wrong reading surface. Live inspection of the 2504 dashboard (http://127.0.0.1:8504/) shows the tiered explanations — the core learning content, ~1700px of it per concept — rendered in a **380px-wide sidebar drawer at 14px `system-ui`**, while the graph canvas holds the center of the screen. Sidebar meta-text is 12.5px. Long-form learning content in a gutter reads as cramped and effortful regardless of its quality.

Inspiration targets (distill.pub, seeing-theory.brown.edu) do the opposite: prose is the primary surface — a centered ~700px column at 17–21px with generous line-height — and visuals are embedded in the reading flow.

**Goal:** a learner moves through the paper efficiently and finishes with *working understanding* — able to build on the paper's concepts — not just a skim.

## Decisions made (with user)

1. **Layout:** Article-first, distill-style. Learn mode becomes a full-width reading experience; the graph is demoted to a progress rail in Learn mode and survives unchanged as Explore mode.
2. **Scope:** Presentation layer rebuilt for all papers + content upgrade for **2504 only** (flagship). 1306/2205 get the new presentation with existing content.
3. **Math UX:** Annotated equations + stepped derivations + progressive reveal (scoped — see §4). Worked numeric examples: not in this slice.
4. **UI redesign:** Full visual redesign, **dark theme, refined** (user's explicit choice). Keep the dark-slate identity but tune it for long-form reading: raised body-text contrast, warmer/less saturated surface tones, clear elevation hierarchy. All colors live in one tokens file.
5. **Visuals feature:** planned now as a content contract (`figure` block + placeholder renderer), implemented in a later slice.

## 1. Article structure (per paper)

Learn mode renders a single scrollable article:

- **Opening:** paper title, one-paragraph claim/why-it-matters, estimated reading time, link to the notation guide.
- **Chapters** = reading-path concepts, in path order (5 for 2504). Each chapter renders the concept's tiers as **vertical sections in the flow**: TL;DR → Intuition → Mechanics → The Math → Go Deeper. No drawer; nothing hidden.
- **Progressive reveal, scoped:** only inside "The Math" sections. An equation/derivation first shows its *shape* (plain-words statement of what maps to what) with an expand affordance for full detail. TL;DR–Mechanics are always fully visible. A page-level **"Expand all math"** toggle defeats all reveals at once. This is the guard against re-creating the "depth hidden behind clicks" bug the last redesign fixed.
- **Inline concept links:** prose mentions of non-path concepts link to that concept's own article-style page (same layout, single concept). This keeps 2504's other 19 concepts reachable from reading flow, not only from the map.
- **Ending:** a "You can now…" checklist of capabilities the learner should have, then a handoff card into Explore mode.

**Code excerpts** ("See it in code") stay demoted: a collapsed disclosure at the end of a chapter, as today.

## 2. Typography system

One design-tokens file (CSS variables), consumed everywhere:

- Reading column: `max-width ≈ 700px`, centered.
- Body: 17–19px, line-height 1.6–1.7. Typeface: a vendored high-quality reading face (serif preferred, distill-style) — **bundled locally like the KaTeX fonts; no CDN/network fetch ever**. If vendoring stalls, fall back to a tuned system-serif stack rather than violating the offline constraint.
- Heading scale: clear h1/h2/h3 steps; tier headings visually distinct from chapter headings.
- Minimum font size anywhere in the app: **14px** (rail, captions, badges included).
- KaTeX display math sized relative to body, with vertical breathing room.

## 3. UI redesign (visual system)

- **Theme:** dark, refined for reading. Deep warm-slate surfaces with a clear elevation ladder (page < rail < cards), high-contrast off-white body ink (WCAG AA+ for long-form), one restrained accent color for links/active states. Annotated-equation term colors are a small bright categorical palette tuned for dark backgrounds. Defined entirely in the tokens file.
- **App chrome:** slim top header (paper id/title, Learn ↔ Explore switch, "Expand all math", search). No competing panels in Learn mode.
- **Progress rail** (Learn mode): slim left rail with chapter list (visited/current state), overall progress, and a small static minimap thumbnail of the graph that deep-links into Explore. Collapsible.
- **Explore mode:** full graph canvas as today, restyled to the refined dark tokens (node colors, edge colors, level badges, panel styling). Functionality unchanged.
- **States & polish:** consistent focus/hover states, reduced-motion-respecting transitions, tuned empty/loading states. Contrast meets WCAG AA for body text.
- **Responsive:** the article column degrades gracefully to narrow windows; the rail collapses first.

## 4. New content block types (app layer, paper-agnostic)

Authored in the markdown pages as fenced blocks with a small YAML payload; parsed by `build_data.py` into structured data in `data.gen.ts`; rendered by new React components. Plain markdown/KaTeX continues to work unchanged — these are **additive**, so 1306/2205 build with zero content changes.

| Fence | Component | Payload |
|---|---|---|
| ```` ```annotated-eq ```` | `<AnnotatedEquation>` | `latex:` + `terms:` list of `{tex-fragment, color-role, plain-words}` — renders KaTeX with color-coded terms and a legend |
| ```` ```derivation ```` | `<DerivationSteps>` | ordered `steps:` of `{latex, why}` — each line shows the transformation and why it is valid |
| ```` ```algorithm ```` | `<AlgorithmWalkthrough>` | `lines:` of `{code, intent}` — numbered pseudo-code, each line expandable to intent |
| ```` ```figure ```` | placeholder card (this slice) | `id:, caption:, props:` — the future-visuals contract, see §6 |

Validation: `katexcheck.mjs` is extended to extract and strict-check the LaTeX inside `annotated-eq` and `derivation` payloads, not just `$…$` blocks. A malformed payload fails the build with a pointed error (same philosophy as `require_ok`).

## 5. Content upgrade — 2504 flagship

Rewrite/extend `2504-pages` to use the new blocks:

- Every key equation → `annotated-eq` with plain-words legend.
- Every multi-step derivation → `derivation` blocks.
- The two attack algorithms (disparity inference; targeted attacks) and the Balanced Correlation Defense → `algorithm` walkthroughs.
- New paper-level **notation guide** page (every recurring symbol, one line each).
- New closing **"You can now…"** checklist.
- All content passes the extended `katexcheck.mjs` before build.

Content remains hand-authored (no `claude` CLI on this machine); the `require_ok`/`is_toc_graph` guard path is untouched.

## 6. Future visuals feature (contract only, this slice)

The ```` ```figure ```` block declares an interactive widget by `id` + `props`. This slice ships only a styled placeholder card ("Interactive figure — coming soon" + caption), so content can declare figures today. A later slice implements a small vendored widget runtime (seeing-theory-style: sliders/controls driving SVG or canvas, fully offline, no external libraries). Nothing in Reader v2 depends on that runtime.

## 7. Data flow & architecture

Unchanged direction: `graph.json` + `pack.json` + pages → `build_data.py` → `data.gen.ts` → React app. `build_data.py` gains the fenced-block parser (blocks become typed nodes in each page's tier content instead of raw markdown strings). The Zustand store keeps `mode: "learn" | "explore"`; `learnIdx` becomes scroll-synced chapter position. Explore-mode logic is otherwise untouched.

## 8. Testing & verification

- New unit tests: fenced-block parsing in `build_data.py` (pytest), each new component (vitest), expand-all-math toggle behavior, min-font-size token assertions.
- Existing suites stay green: dashboard vitest (135), `tsc --noEmit`, dashboard pytest (30), root guard tests (14). Pinned counts updated deliberately where new tests land.
- **Fixture discipline:** committed `dashboard/src/data.gen.ts` stays the pinned AIAYN fixture; any 2504 preview build restores it (`git diff --stat` clean at the end).
- **Offline check:** rebuilt 2504 dashboard verified with browser `read_network_requests` → 0 external requests (fonts vendored).
- Live in-browser verification of the article flow on 2504, and of 1306/2205 rendering with unchanged content.

## Out of scope

- Interactive figure runtime (§6 — later slice).
- Content deepening for 1306/2205.
- Worked numeric examples.
- Light mode (tokens make it a cheap later addition).
- Any pipeline/extraction changes (`concepts.py`, `build_dashboard.py`).

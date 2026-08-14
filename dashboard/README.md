# Knowledge Dashboard

An internet-disconnected localhost dashboard for Knowledge-Engine paper, code,
and bridged graphs. React + zustand + React Flow, laid out by ELK in a worker,
with math rendered by KaTeX.

Everything the app needs is compiled into one static module at build time.
There is no backend, no runtime fetch, and no runtime model. The Vite dev
server is local infrastructure, not an application backend.

## Development

```bash
npm install
```

```bash
python build_data.py --graph ../fixtures/aiayn_concept_graph.json --pack ../fixtures/aiayn_tiny_pack.json --pages-dir ../fixtures/pages --wiki-dir ../fixtures/wiki
```

By default, `build_data.py` reaches the network to classify resource urls (one
HEAD request per unique url, ~25s timeout each, sequential). A build citing many
slow or unresponsive hosts can take noticeably longer. Pass `--no-embed-probe` to
skip probing and build fully offline; this disables image and video embeds but
makes the build deterministic and fast.

```bash
npm run dev
```

## Production build

```bash
npm run build
```

```bash
python -m http.server -d dist 8000
```

The running dashboard stays 100% disconnected: no external API or CDN requests, no
runtime data fetch. Graph data, application assets, KaTeX styles and fonts, and
the ELK layout worker are all emitted locally by the build. (Build-time network
access for resource probing can be disabled with `--no-embed-probe`.)

---

## `build_data.py`

Compiles graph, pack, pages, wiki notes, and every optional feature input into
`src/data.gen.ts` as a single `KE_DATA` constant.

| Flag | Supplies |
|------|----------|
| `--graph` | the §5.1 graph (concept, code, or bridged) |
| `--pack` | the paper pack — also enables source provenance (`sections`) |
| `--pages-dir` | tiered concept pages |
| `--wiki-dir` | `_research_wiki/` notes |
| `--hotspots` | churn × centrality ranking for code views |
| `--repo-dir` | source excerpts and file mtimes for staleness |
| `--viz-dir` | R13 interactive explorables |
| `--next-steps` | R15.1 next-step ideas |
| `--quiz` | R15.2 quiz items |
| `--update` | patch an existing bundle in place |

**Optional means optional.** Every feature flag is opt-in and every consumer
reads its data through a single typed accessor (`lib/viz.ts`, `lib/quiz.ts`,
`lib/nextSteps.ts`, `lib/source.ts`). Omit a flag and the key is absent, the
accessor returns empty, and the feature's UI renders nothing — the bundle is
byte-identical to a build that never knew the feature existed.

---

## Features

### Views and modes

Four graph views — **concepts**, **clusters**, **code**, **bridged** — and two
modes:

- **Learn** — a linear path through the graph with a progress rail, guided tour
  overlay, and step completion.
- **Explore** — the full graph, free navigation, filters, and the mind map.

### The canvas

- **ELK layout in a worker**, so a large graph does not block the UI. Layout
  phases (`loading` / `ready` / `empty` / `error`) are explicit state, not
  inferred from an empty node list.
- **Level of detail** (`lib/lod.ts`) — clusters collapse to single nodes below a
  zoom threshold and expand above it.
- **Mind-map toggle** (R15.10, explore mode only) — swaps the ELK algorithm
  between layered reading order and a radial arrangement.
- **Branch collapse** (R16.B1) — folds a node's `part-of` subtree away; the
  parent stays put and reports how many nodes it swallowed. The control lives
  in the drawer, not on the node card, because the card is itself a `<button>`
  and a nested control would be invalid HTML *and* unreachable by keyboard.
- **Hover halo** (R16.B3) — hovering a node highlights its 1-hop neighborhood,
  direction- and kind-agnostic.
- **Blast radius** (`lib/blastRadius.ts`) — ghosts the graph by dependency ring
  distance from the selected node.
- **Fan-out sizing** — nodes scale with their out-degree, so hubs read as hubs.

### The drawer

Tiered explanation per concept — TL;DR, Intuition, Mechanics, Math — plus:

- **Visualize tier** (R13) — a sandboxed, **lazily mounted** explorable. The
  iframe mounts only on first open, so unopened visuals cost nothing at load.
- **Source panel** (R15.11) — the actual paper passage a node was extracted
  from. Silent when the bundle carries no sections or the ref does not resolve.
- **Code viewer** — Prism-highlighted source excerpts for code and bridged
  nodes, with staleness from file mtimes.

### Rich content blocks

Pages can emit typed blocks beyond markdown (`lib/contentBlocks.ts`):
annotated equations with role-colored terms, derivation steps, progressive math
reveal, algorithm walkthroughs, and figure placeholders. Math goes through
`lib/mathHtml.ts` (KaTeX) rather than being handed to a markdown plugin
directly, so inline and display math behave the same in every surface.

### Learning loop

- **Quiz** (R15.2) — build-time authored items graded **offline in the
  browser**. There is no runtime LLM, ever. Answering all of a node's items
  correctly marks that learn step complete.
- **Mastery ledger** (R16.A1) — evidence of understanding per node, at
  `unseen` → `seen` → `quizzed` → `mastered`. Levels only ever climb; the
  streak decays. Two sources feed one ledger: quiz answers and R13 viz **bet
  outcomes** — that is the R13 fold, an interactive visual that asks you to
  predict before it reveals is evidence of the same kind a quiz is.
- **Review queue** (R16.A3) — nodes whose evidence just broke (streak reset) or
  has gone stale (`REVIEW_AFTER_DAYS = 14`). Client-side date math only: no
  scheduler, no notifications. `scripts/quiz_to_anki.py` remains the export
  path for anyone who wants real spaced repetition.
- **Continue panel** (R15.1) — next-step ideas from the `next_steps` pipeline,
  each anchored to concept nodes.
- **Source chips** (R16.C2) — every quiz item and every visual that claims a
  paper span shows where it came from; clicking opens that node's source. The
  chip is silent when the ref does not resolve, so a bad ref degrades to no
  claim rather than a false one.

### Sidebar and trace

An insights panel (severity-ranked graph findings) and a trace tab showing what
the pipeline did to each node and when. The **player bar** steps through a
dependency-ordered walk of the graph.

### Layout ergonomics

Panels are independently resizable with persisted widths
(`lib/panelSizing.ts` + `lib/persist.ts`), clamped to per-panel min/max bounds.

---

## Security notes

The R13 visual runs in an iframe with `sandbox="allow-scripts"` and **without**
`allow-same-origin`. That gives it an opaque origin, which means:

- `event.origin` is the string `"null"`, not the page's origin — origin
  comparison alone is not a usable check.
- The listener therefore verifies `event.source === frameRef.current.contentWindow`
  before accepting anything.
- The message payload is validated structurally (`betOutcome`), and the node id
  the frame claims is **ignored** — the host already knows which node the frame
  belongs to, so trusting the frame's claim would let one visual write another
  node's mastery record.

`localStorage` is user-editable, so `readLedger` validates on the way in:
unknown mastery levels are dropped and streaks are coerced.

---

## Tests

```bash
npm test
```

328 tests across 44 files.

The suite runs in vitest with **`environment: "node"`** — no jsdom, no
`@testing-library/react`. Component tests assert against `renderToStaticMarkup`
output. This keeps the suite fast and forces components to be honest about what
they actually emit rather than what a virtual DOM lets them get away with.

Python tests for the compiler live in `tests/` and run from the repo root:

```bash
PYTHONPATH="../src;../../research-mcp/src" python -m pytest tests -q
```

---

## Attribution

UI paradigms and component patterns are adapted from
[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) (MIT) —
guided tour, layer legend, filter panel, and explain drawer — and
[TrueCourse](https://github.com/truecourse-ai/truecourse) (MIT) — insights
sidebar, context switcher, trace player, and diff/staleness paradigms.

The repository-level `/explain` skill is adapted from Understand-Anything's
`understand-explain` skill (MIT).

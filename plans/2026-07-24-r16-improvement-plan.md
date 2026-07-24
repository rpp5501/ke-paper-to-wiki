# R16 Improvement Plan — Mastery, Mind-map Restyle, Provenance (2026-07-24)

**Status:** PLANNED — owner elicitation answered 2026-07-24; build pending
(owner discipline: plans first, build in later sessions).
**Owner answers recorded:** directions = quizzes + gamified mastery,
mind-map restyle, source-passage provenance · R13 relation = **fold
together** (one slice; R13.1 rides along, viz bets feed the mastery ledger)
· notes = new resource batch triaged in §5.
**Working dir:** `paper-skill-slice9-bridge/` (branch `slice9-bridge`).
**Supersedes:** the "Suggested order" list in
`2026-07-18-feature-brainstorm-r15-candidates.md` (items 1, 2, 10 shipped;
this plan sequences what's next).

Pinned constraints unchanged: offline dashboard, keyless, no vector DBs, no
new runtime deps, no runtime LLM, opt-in token spend only, default build
byte-identical without flags.

## 1. Track A — Gamified mastery (quiz v2, folds with R13)

Grounded in what shipped: `QuizPanel` grades offline with per-option
explanations and calls `markStepComplete` on all-correct;
`scripts/quiz_to_anki.py` exports; `usePanelWidths.ts` is the localStorage
precedent; viz templates render in a sandboxed iframe via `srcDoc`
(`VizTier.tsx`).

**A1. Mastery ledger (store).** Per-node
`mastery: Record<nodeId, {level: "unseen"|"seen"|"quizzed"|"mastered", streak: number, lastAnswered: string}>`.
Sources of evidence: quiz item results (existing QuizPanel flow) **and R13
viz bet outcomes** — this is the fold. VizTier's iframe posts a
`{type: "ke-bet-resolved", node, correct}` message on predict-then-reveal
resolution; a listener in VizTier dispatches into the same ledger action the
quiz uses. Template delta is a few lines per template (they already know the
bet outcome to render the reveal). Persist ledger + `mode`/`learnIdx`/scroll
to localStorage (generalize the `usePanelWidths` pattern into a small
`persist.ts`) — this ships brainstorm idea 8 (resume-where-you-left-off) for
free.
→ verify: vitest — quiz all-correct raises level and streak; wrong answer
resets streak, keeps level ≥ "quizzed"; bet message from an iframe raises
"seen"→"quizzed"; reload restores ledger (jsdom localStorage).

**A2. Mastery surfaced, not scored.** Guardrail: no points, no XP, no
leaderboard — mastery is evidence of understanding (commit-then-reveal
philosophy, same as the viz bets). UI: (a) mastery ring segment per step in
`ProgressRail`; (b) node tint/badge in `nodes.tsx` (Canvas) keyed on level;
(c) TopBar count "n/N mastered" next to the existing pills.
→ verify: vitest presentation-component snapshots per level; tsc clean.

**A3. Review queue.** A "Review" pill (TopBar, near Quiz) listing nodes with
`streak == 0` or `lastAnswered` older than 14 days — pure client-side date
math, no scheduler, no notifications. Clicking goes to the node with the
quiz open. Anki export remains the heavy-SRS path (unchanged).
→ verify: vitest — queue membership for stale/failed fixtures; empty state
renders nothing.

## 2. Track B — Mind-map restyle (v2 of R15.10)

Grounded: `store.layoutMode` + radial ELK (`layout.ts`, "R15.10 mind-map
view"), `MapToggle`, cluster coloring, `part-of` hierarchy in `lib/deps.ts`,
`graph_to_mermaid.py` exporter.

**B1. Branch collapse/expand.** Deliberately deferred in v1; now in scope —
real-paper scale exists (2504 build). Collapse folds a `part-of` subtree
into its parent node (badge shows hidden count); state in store, layout
cache key includes collapse set.
→ verify: vitest — collapsing a parent removes descendants from visible
nodes, preserves non-tree edges to the parent; expand restores byte-equal
layout input.

**B2. Restyle pass.** In radial mode only: curved edges, node size by
`part-of` fan-out (degree — already computable from `deps.ts`), mastery tint
overlay from Track A (the second fold point), cluster legend kept.
→ verify: snapshot of nodes.tsx props for a fixture graph; no style change
in layered mode (explicit test).

**B3. Hover neighborhood (ResearchRabbit pattern, pattern-only — closed
SaaS).** Hover a node → 1-hop halo, rest dimmed. The Learn-mode focused-
subgraph LOD machinery is the precedent; this is its hover-scoped cousin in
Explore.
→ verify: vitest — hover sets highlight set = node + 1-hop; leave clears.

**B4 (cheap, optional). Mermaid exporter `--max-depth`** mirroring collapse.
→ verify: pytest alongside the existing 5.

## 3. Track C — Source-passage provenance

**C1. Build R15.11 exactly as designed.** `2026-07-19-show-source-design.md`
is approved with step-by-step verifies (sections emission in
`build_data.py`, `source.ts` key port, `SourcePanel` in Drawer). First build
item of R16 — highest value-per-line, zero design work left.

**C2. Provenance chips across features (the fold, part 2).** Once
`KE_DATA.sections` + `SourcePanel` exist: (a) `quiz.json` items accept
optional `source_ref`; QuizPanel renders a "§3.2" chip after answering that
opens the node's SourcePanel entry — contract-validated like the existing
quiz checks (unknown ref → build warning, chip dropped); (b) the R13 viz
manifest gains `source_ref` per entry, chip rendered in VizTier header.
Every claim, quiz item, and visual traceable to a paper span — the moat
(pedagogy + provenance) stated as a UI invariant.
→ verify: pytest — validator warns and drops bad refs, passes good ones;
vitest — chip renders only when ref resolves.

## 4. R13.1 folded in — viz placement + critique (paperbanana patterns)

Per the 07-18 brainstorm idea 4, now enriched by the paperbanana audit (MIT
✓, checked 2026-07-24). Their pipeline (Retriever over 13 curated exemplars
→ Planner → Stylist with explicit NeurIPS-style guidelines → Visualizer →
bounded Critic loop, default 3 iterations) maps onto ours with tokens
guarded:

- **Placement:** `anchor_tier` manifest field chosen by the skill
  (after-Intuition vs in-The-Math), owner-confirmed, as already designed.
- **Critique loop:** `viz review <node>` compares generated HTML + page and
  proposes **params-only** edits (better example values, sharper bet
  question) — adopt paperbanana's two disciplines: a written style-guidelines
  file the critic cites (`viz_templates/GUIDELINES.md`), and a hard iteration
  cap (≤2) instead of "until satisfied".
- **Judge rubric:** their faithfulness/conciseness/readability split becomes
  the review checklist headings — checklist, not a second LLM judge.

Runs only inside an explicit `visualize` invocation, never batch. Default
build untouched.

## 5. Resource triage — owner batch (checked 2026-07-24)

| Resource | License | Verdict | What we take |
|---|---|---|---|
| stair-lab/kg-gen (NeurIPS '25) | MIT ✓ | **Adopt patterns — best of batch** | (a) build-time LLM **clustering pass** for entity/relation dedup (`cluster=True` / cluster-after-generate) → a `graph dedupe` skill step inside the existing propose-confirm gates, opt-in, never runtime; (b) `aggregate([g1, g2])` shape is the reference design for cross-paper memory (idea 6) when paper №2 lands; (c) **MINE-benchmark idea, deterministic version**: extend `require_ok`/`is_toc_graph` with zero-token graph-quality metrics — orphan ratio, near-duplicate slug candidates (string-normalized), `part-of` tree coverage |
| Orbifold/knwler | MIT ✓ | Patterns only (own pipeline exists; their stack: LiteLLM-style local models) | (a) **schema-discovery-first**: `discover_schema` infers entity/relation types + reasoning *before* extraction — worth a trial in the concept-graph prompt (declare the paper's relation vocabulary first, then extract against it); (b) degree-threshold slider in their HTML report → density control idea for Explore; (c) their single-file offline HTML report independently validates our artifact stance |
| puppygraph.com text-to-graph (article) | n/a (blog) | Pattern taxonomy | Their dedup ladder: string normalization → embedding clustering (~0.92 cosine) → coref → entity linking. We take **string normalization** (canonical kebab slugs — partially have) + **LLM clustering at build time** (kg-gen style). Embedding clustering and Wikidata linking **declined** — keyless/no-model-babysitting pins |
| llmsresearch/paperbanana | MIT ✓ | Adopt patterns for R13.1 (§4) | Exemplar-retrieval + written style guidelines + bounded critic loop + rubric-as-checklist. Diagram-first bespoke viz stays a future seed (was already on the audit list 07-18) |
| khoj-ai/khoj | **AGPL-3.0 ⚠** | Pattern-only, **never port code** (AGPL) | "Second brain over your own corpus" ideas → research-mcp playbook: scheduled/repeatable research runs, per-topic digests into `_research_wiki/`. Their runtime chat model remains the banned interaction; our build-time FAQ (idea 9) is the compliant equivalent |
| ResearchRabbit | closed SaaS | Pattern-only (already on 07-18 audit list) | Hover-neighborhood trail → B3 now; collections-seed-recommendations → cross-paper memory design round later |

Rule stands: dated license check before anything enters the steal-list;
AGPL entries are permanently pattern-only.

## 6. Build order (cheapest real value first)

1. **C1** show-source (designed, verifies written — execute as-is)
2. **A1–A3** mastery ledger + surfacing + review queue
3. **B1–B3** mind-map collapse + restyle + hover halo (B4 if trivial)
4. **C2** provenance chips (needs C1; touches quiz + viz manifests)
5. **R13.1** placement + critique (§4)
6. **KG-quality gate metrics** (kg-gen MINE-lite, §5 row 1c) — pipeline-side,
   independent, can interleave
7. Then reassess: `graph dedupe` skill step, schema-discovery prompt trial,
   crawl4ai port (R11-2, still pinned, still first in the research lane)

Not doing: runtime LLM, embeddings/vector DBs, AGPL code, points/XP/
leaderboards, PDF-page rendering (R15.11 non-scope stands).

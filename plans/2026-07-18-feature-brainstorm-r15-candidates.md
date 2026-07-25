# Feature Brainstorm — R15 Candidates (2026-07-18)

**Status:** IDEATION — nothing here is decided. Owner ideas + assistant additions,
each checked against what already exists in the codebase. Numbered by suggested
priority, cheapest-delta-first.

## Owner ideas, grounded against the codebase

### 1. Quiz tab — "Check yourself" (genuinely new, highest value/effort)

Nothing like it exists. But every ingredient does: the R13 predict-then-reveal
mechanism IS a quiz interaction; `completedSteps`/`markStepComplete` in the
store is an unused-for-this progress tracker; Nicky Case's Puzzle-It-Out +
cognitive-gates patterns (already in our catalog) say quizzes should gate and
teach at once.

Sketch: build-time generated `quiz.json` (per-node items authored by a
`quiz` skill from pages — same params-file pattern as R13: LLM authors data,
never runtime code). Item kinds: multiple-choice with per-distractor
explanations (graded offline in-browser, no runtime LLM), "predict the
output" items that reuse existing viz templates with quiz params, and
notation-decode items ("what does √dₖ do here?"). Completing a node's items
feeds `markStepComplete` → the learn path shows mastery, not just visits.
Token discipline: same opt-in flag pattern (`--quiz-dir`), byte-identical
default build. **This is R13's architecture reused wholesale — cheapest big
feature on the list.**

### 2. Resources / next-steps tab (pipeline EXISTS, needs surfacing)

`src/paper_skill/next_steps.py` + `test_next_steps_{harvest,novelty,citations,synthesis}.py`
already implement next-step generation (slice 10, `plans/2026-07-09-slice10-next-steps.md`).
Delta is almost pure wiring: emit its output into `data.gen.ts` behind an
opt-in flag, render a "Continue" tab (similar papers, open questions, build
ideas) next to the gallery. Follow-on: each resource links back to the
concept node it extends (provenance discipline).

### 3. Hover definitions for unfamiliar terms (PARTIALLY EXISTS)

`KE_DATA.glossary` is already per-node `{term: definition}`, RichMarkdown
takes a `glossary` prop, and `pages["_notation"]` is a paper-wide notation
page. Deltas worth doing: (a) coverage — a pipeline pass that scans pages for
capitalized/greek/jargon terms with no glossary entry and asks the writer
phase to fill them (build-time, opt-in); (b) a persistent notation ribbon
sourced from `_notation` so any symbol is hoverable anywhere, not just in its
node; (c) cross-node fallback — if a term isn't in this node's glossary,
fall back to the paper-wide map. No runtime LLM anywhere.

### 4. LLM-placed / LLM-improved visuals (R13 extension, guard the tokens)

R13 already computes candidates deterministically (`viz propose`). The honest
delta: (a) **placement** — let the skill choose which tier the viz anchors to
(after Intuition vs inside The Math) per concept, recorded as a manifest
field `anchor_tier`, still owner-confirmed; (b) **critique loop** — a
`viz review <node>` skill step that opens the generated HTML + the page and
proposes param edits (better example values, sharper bet question) — params
only, never regenerated code, so the loop is cheap and gated; (c) tools-built
visuals = the bespoke path that already exists. Pin: placement/critique run
only inside an explicit `visualize` invocation, never batch.

### 5. Improve the research feature (mostly already pinned; new candidates below)

R11-2 already pins the crawl4ai port (BM25ContentFilter + PruningContentFilter
into `fetch_clean.py`) — that IS the reranker idea in zero-dep form. Do it
before adding any model-based reranker.

## Assistant additions

- **6. Cross-paper concept memory.** Concept ids are kebab slugs and
  `_research_wiki/` is a persistent cache. When a second paper's wiki shares a
  slug (softmax, layer-norm...), link them: "you learned this in AIAYN — diff
  view of how this paper uses it." This compounds with every paper processed
  and no competitor fixture has it. Candidate for the real moat.
- **7. Spaced-repetition export.** Quiz items (idea 1) export to Anki/Orbit
  deck format at build time. Nicky Case ships Orbit on his explorables; the
  learner keeps the paper after closing the tab. Trivial once quiz.json exists.
- **8. Resume-where-you-left-off.** localStorage is already used for panel
  widths; persist mode/step/scroll. Tiny.
- **9. Build-time FAQ.** "Ask the paper" needs runtime LLM (banned). The
  build-time version doesn't: the writer phase emits 5–8 anticipated
  questions with cited answers per paper ("why not RNNs?", "what breaks
  without positional encoding?") as a drawer section or quiz seed.

## Research-stack candidates (owner's list, R11-1 lens applied)

| Candidate | Verdict | Why |
|---|---|---|
| crawl4ai BM25/pruning port | **Do first — already pinned (R11-2)** | Zero deps, zero keys, solves the same problem as rerankers |
| FlashRank (local ONNX reranker) | Maybe, behind a flag, after BM25 ships | Keyless ✓, but a model artifact to fetch/cache = babysitting risk; only if BM25 measurably insufficient |
| LLMLingua compression | **Decline for now** | A local model in the ingest path is exactly the "manage/babysit" burden R11-1 bans; token savings overlap with BM25 sectioning |
| Aster (Allen AI workbench) | Adopt as **manual tier-2 tool**, not integration | Keyless web workbench fits "host-native/manual second"; export → `_research_wiki` by hand when useful |
| gpt-researcher | Pattern-only audit | Planner/executor + source-tracking patterns for research-mcp playbook; **license verify at adoption** |
| Weizhena/Deep-Research-skills (90★) | Audit for playbook prompts | Structured outline+investigation workflow with human-in-the-loop — matches our propose-confirm discipline; **license verify at adoption** |
| K-Dense-AI/claude-scientific-writer (937★) | Audit for writer-phase prompts + citation discipline | Could improve P4 writer + FAQ (idea 9); **license verify at adoption** |

### InternScience/Awesome-Scientific-Skills (researched 2026-07-18)

**What it is:** MIT, 483★, created 2026-03. An *awesome-list* of Agent Skills
for scientific research — currently **Phase 1: curated links only**. The
`skills/` dir is an empty placeholder ("Phase 2: import and reorganize —
coming soon"), so there is **no code to port yet**. Verdict: **scouting
index, not a steal-list source**. Re-check when Phase 2 lands.

**Immediate value — new leads it surfaces (all need license verify at adoption):**

| Lead | Stars | Why it matters to us |
|---|---|---|
| Intelligent-Internet/II-Commons-Skills | 2 | *Deterministic* keyless retrieval CLI across arXiv/PubMed/PMC — exactly the R11-1 tier-3 shape; audit its fetch patterns for research-mcp |
| yorkeccak/scientific-skills | 21 | Semantic literature search across PubMed/arXiv/ChEMBL — playbook pattern source |
| HughYau/AcademicForge | 250 | Curated academic-writing skill collection, "focused integration over quantity" — same philosophy as ours; audit for P4 writer |

It independently ranks the owner's two other picks (K-Dense #1 in Academic
Writing, Weizhena in Literature Search) — good sign the picks are sound.

**Positioning insight:** their taxonomy marks **Knowledge Graphs** (ontology
navigation, entity linking, relationship extraction) as an *unfilled gap* —
which is precisely what this project builds. When paper-skill stabilizes,
submitting it to this list is free distribution to exactly our audience.

Rule stands: nothing enters the steal-list without a dated license check
(MLU-Explain's CC-BY-SA near-miss is the cautionary tale).

## Suggested order (cheapest real value first)

1. ✅ **Next-steps tab — DONE 2026-07-18.** `build_data.py --next-steps ideas.yaml` (opt-in, anchor-node validation with drop warnings, confirmed-first sort) + `ContinuePanel` in the TopBar (title/kind/rationale, anchor chips → `goToNode`) + fixture `fixtures/next_steps/ideas.yaml` (3 grounded AIAYN ideas). 38 dashboard pytest green (3 new), vitest + tsc clean. Real `ideas.yaml` comes from running the next_steps pipeline (N2 confirm flow) per slice-10 plan.
2. ✅ **Quiz tab — DONE 2026-07-18.** `--quiz quiz.json` (opt-in, contract-validated: known node, ≥2 options each with explain, correct in range) + `QuizPanel` in the TopBar (offline grading, per-option explanations revealed on answer, all-of-a-node-correct → `markStepComplete`) + fixture (4 items grounded in 04_sdpa.md) + `scripts/quiz_to_anki.py` TSV export (idea 7 ✓). **Plus owner-requested `build_data.py --update`**: patches viz/next-steps/quiz into an existing `data.gen.ts` without a full rebuild (`parse_data_ts` roundtrip tested; untouched sections byte-equal). 44 dashboard pytest green (6 new), vitest + tsc clean.
3. **Glossary coverage + notation ribbon** (idea 3) — small pipeline pass + small UI.
4. **Viz placement/critique** (idea 4) — R13.1, params-only loop.
5. **crawl4ai port** (idea 5, already pinned) → then reassess FlashRank.
6. **Cross-paper memory** (idea 6) — biggest, needs its own design round once a second paper is processed end-to-end.

Not doing: runtime LLM in the dashboard (pinned), LLMLingua (R11-1),
anything requiring API keys.

---

## Second resource batch — triage (2026-07-19, owner-supplied list)

Triaged against pinned constraints (offline, keyless, no vector DBs, no new
deps, no runtime LLM). Verdicts, not research — license checks at adoption.

### Strong candidates (new R15 items)

**10. ✅ Mind-map view v1 — DONE 2026-07-19.** "Mind map" pill in explore
mode toggles the ELK algorithm layered↔radial (`layout.ts` parameterized,
cache keyed per algorithm, `store.layoutMode`); pairs with the existing
clusters view for theme coloring. Plus `python -m paper_skill.graph_to_mermaid`
→ shareable Mermaid mindmap from the part-of tree, non-tree edges preserved
as footer comments (5 pytest). Branch collapse/expand deliberately deferred
to real-paper scale. 38 pytest + 30 vitest in touched files + tsc clean.

**Original idea: Mind-map view of the concept graph** *(Mapify-inspired, pattern-only —
Mapify is closed SaaS, nothing to port).* What Mapify actually adds over our
Explore canvas: radial mind-map layout, color-by-theme, collapsible branches
— a spatial overview instead of the layered outline the 07-14 redesign
demoted. Delta: an ELK radial layout option in explore mode, color by
cluster (Leiden communities already computed), collapse/expand via existing
`part-of` folding. Bonus near-free artifact: `graph.json → Mermaid mindmap`
exporter for sharing outside the app.

**11. "Show source" — DESIGNED & APPROVED 2026-07-19, build pending.**
Full design + step-by-step implementation plan with verify checks:
`plans/2026-07-19-show-source-design.md`. Owner directive: plans complete
first, build in a later session.

**Original idea: "Show source" provenance affordance** *(Denser-Chat-inspired: highlight
the exact sourcing passage).* We already carry `source_ref` per node, pack
`sections` text, `excerpts`, and `eqIndex` — everything needed for a drawer
button that reveals the actual paper passage backing the current node,
offline. This deepens the project's stated moat (pedagogy + provenance)
with zero new deps. Likely the highest value-per-line in this batch.

### Research-lane audit leads (add to the audit queue)

| Lead | Why |
|---|---|
| federicodeponte/opendraft | Multi-agent verification against CrossRef/OpenAlex/S2/arXiv — the exact keyless sources research-mcp uses; audit its cross-referencing/anti-hallucination patterns for the playbook |
| llmsresearch/paperbanana | Auto-generates method flowcharts/sequence diagrams from papers — pattern source for a future bespoke-viz seed (diagram-first concepts) |
| ResearchRabbit (closed) | Citation-network map pattern feeds idea 6 (cross-paper memory) when a second paper lands |
| Elicit (closed) | Multi-paper comparison-table pattern — future, needs ≥2 processed papers |

### Covered already

Anki ecosystem → `quiz_to_anki.py` ships; gamified add-ons are downstream of
our export, nothing to build. StudyQuest-style "boss battles" → the
pedagogical core (commit-then-reveal, cognitive gates) is exactly what the
viz bets + quiz already do.

### Declined, with reasons

| Item | Reason |
|---|---|
| Ren'Py / paper2gal / visual-novel engines | Off-mission: sprites + branching dialogue add production weight without adding understanding; runtime LLM dialogue violates the no-runtime-LLM pin. If narrative framing ever proves wanted, the cheap version is story-framed tour blurbs — no engine. |
| Noto.ai / Ollama local models | Same R11-1 verdict as LLMLingua: a local model to install/update/babysit |
| Khoj / Flowise / RAG quiz backends | Vector-DB/self-hosted-app stacks — "No vector DBs entered the stack" is pinned in PLAN-v3 §6 |
| NotebookLM podcast, Consensus/SciSpace/Scholarcy | Cloud/closed; chat-with-PDF at runtime is the banned interaction model — our build-time FAQ (idea 9) is the compliant equivalent |
| Data Formulator (MIT) | Real OSS but aimed at tabular analytics canvases, not concept graphs — weak fit, skip |

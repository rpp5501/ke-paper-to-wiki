# Project Plan v3.0 — Week-1 Evidence Revision

**Status:** ACTIVE (v3.0, 2026-07-09) · Supersedes PLAN v2.0 (`PLAN (6).md`) only where stated; all unamended v2.0 sections (§1–§5, §7–§18) remain pinned.
**Trigger:** build evidence from Week 1, per v2.0's own rule ("further changes should come from build evidence, not research").

---

## 1. Week-1 build evidence

Built: `research-mcp` scaffold (briefs q01–q10, `fetch_clean.py`, `fetch_academic.py`, playbook SKILL.md, tests, `_research_wiki/`), `paper-skill` scaffold.

**Observed:** Semantic Scholar anonymous 429s (~100 req / 5 min, shared pool) after back-to-back runs of the paper skill + MCP under Claude Code. **Verdict: noise, not a bug.** `search_s2()` is independent of everything else; `academic_search()` already wraps each source in try/except and collects failures into an `errors` list — arXiv, OpenAlex, and CrossRef returned real data every run. Degraded-but-working is the intended keyless behavior and it worked.

**The real lesson:** the owner does not want to manage, key, or babysit external APIs — ever. So the design stance changes: APIs are demoted from "primary retrieval that must be hardened" to "opportunistic enhancers whose absence is normal."

Secondary: the `explorer.html` prototype UI is not acceptable as the product surface (subjective, but decisive).

---

## 2. Decision R11-1 — API-minimal retrieval (owner directive: no API management, ever)

**Standing rule:** no API keys, no per-provider tuning work, no retry engineering projects. External APIs are best-effort freebies; the system must produce full-quality notes with **zero** of them responding.

Retrieval priority order (playbook + `fetch_academic.py`):

1. **`_research_wiki/` cache first** — a covered sub-question makes zero network calls (P5 as designed).
2. **Host-native tools second** — the harness's own WebSearch/WebFetch (subscription-side, unmetered to us, no keys). This becomes the *primary* live-retrieval path, formalizing what v2.0 §4.1 Tier-2 already does for fetching.
3. **Keyless academic APIs last, opportunistic** — fire arXiv/OpenAlex/CrossRef/S2 as today; whatever answers, answers. A 429/timeout is logged to `errors` and forgotten (current behavior, kept). Only zero-effort courtesies allowed: S2 ordered last, skip a source for the rest of a run after it throttles. Nothing configurable, nothing to maintain.
4. **arXiv special case stays** — e-print LaTeX download is P1-critical for `paper2pack` and effectively unthrottled; unaffected by this decision.

Exit test: run the 10 AIAYN briefs with academic APIs force-disabled (env flag); all 10 notes still reach `complete` or an honest `partial` via cache + host-native retrieval alone.

## 3. Decision R11-2 — deep-searcher & crawl4ai: clone read-only, port narrowly

**No forks.** Both repos verified this session (2026-07-09):

- **deep-searcher (Apache-2.0):** README confirms Milvus/vector-DB core — wholesale reuse violates P1. Remains **pattern-only** exactly as pinned (§7 + round-3): strict parseable JSON sub-query plan, decompose → search → evaluate → reflect(1) → synthesize, dispatched deterministically by the CLI-spawn driver. Nothing new to adopt; Week-1's playbook already encodes this — the 429 was provider noise (see R11-1), not a loop failure.
- **crawl4ai (Apache-2.0, attribution required):** port `crawl4ai/content_filter_strategy.py` — `PruningContentFilter` (boilerplate/DOM pruning) and `BM25ContentFilter` (query-scored section keep) — into `fetch_clean.py`, applied at **every tier** (already the v2.0 intent, §4.1 Tier-3 note). Strip all browser/async-crawler machinery; keep only the scoring/pruning logic over the trafilatura-extracted DOM. **License duty:** add the Crawl4AI attribution badge/notice to `research-mcp` README per their attribution requirement — update §7 steal-list row accordingly.

Port order: BM25 scoring first (directly reduces tokens per fetch), pruning second (v2.0 round-2 already specs the Docusaurus/Sphinx/MkDocs selector strip it overlaps with).

## 4. Decision R11-3 — UI pivot: fork Graphify's app (amends M4)

**Decision:** the viewer is now a **fork of Graphify-Labs/graphify (MIT, verified)**, not a from-scratch `explorer.html`. Rationale: Week-1 prototype UI rejected; graphify ships a working HTML graph viz, `graph.json` pipeline, Leiden clustering with `--resolution`/`--exclude-hubs` dials, markdown-wiki export, MCP serve (stdio + HTTP), and `--backend claude-cli` (subscription-only extraction — independently P1-compliant). Round-9 already made M3 adapter-first on graphify's `graph.json`; this extends that from graph to viewer.

**What we keep from v2.0 (non-negotiable):**
- **Schema §5.1 stays canonical.** The bridge (M6) and the paper skill depend on it. Build a bidirectional adapter `graphify graph.json ↔ §5.1`; M3's existing exit test (lossless round-trip on a FastAPI-scale repo) now covers both directions.
- **Progressive disclosure + tiered concept pages + KaTeX** (the paper-side UX) must be added to the fork — graphify ingests arXiv URLs into a generic graph but has none of the pedagogy (v2.0 round-9 differentiation note stands: the moat is M5's pedagogy + provenance).
- **Offline/no-server as a degradation path, not a principle:** graphify's viz is generated HTML (static output; server only needed for MCP/team mode). Requirement: the forked viewer must render from a local `graph.json` + pages folder with no network. If the fork can't satisfy this, `explorer.html` returns as the export fallback — keep the M4 fixture demo as the acceptance harness either way.

**Features to port into the fork:**
- From **Understand-Anything (MIT):** reading paths / dependency-ordered walkthroughs (round-9 adoption), layer visualization, persona-adaptive detail levels (evaluate, low priority). **Caution pinned from round-10:** their Web-Worker layout is unused (Issue #491, synchronous d3-force stalls at ~3K nodes) — verify any layout code actually runs off-main-thread before lifting it; round-8's lazy two-stage layout rule still applies.
- From **codegraph (MIT):** staleness banners and composite `explore` tool (already adopted rounds 9) — these live in graph_query/MCP, unaffected by the UI pivot.

**New risks (added to §9):**

| Risk | Mitigation |
|---|---|
| Fork drift: graphify is fast-moving (1,000+ commits, v8 branch) | Fork pins a tag; upstream merges are deliberate, milestone-boundary events. Isolate our additions in separate modules/dirs to keep merges small. |
| Fork bloat: PR dashboards, video ingestion, multi-backend code we don't need | Delete aggressively at fork time; keep the viz, graph pipeline, cluster dials, wiki export, claude-cli backend. |
| Prompt-cache invalidation from `graphify-out/` writes | Known issue in their troubleshooting (round-9 confirmed): `.claudeignore` for `graph.json`, `graphify-out/` — apply round-8 artifact-hygiene rule day one. |
| Viewer requires their server stack | Acceptance test below forces static rendering; explorer.html fallback if it fails. |

**Amended milestones:**

| M | Change |
|---|---|
| **M3** | Unchanged in intent; adapter now bidirectional (§5.1 ↔ graphify). |
| **M4 (rewritten)** | Fork graphify at a pinned tag; strip unneeded features; render the hand-written AIAYN concept-graph fixture (converted via adapter) in the forked viewer, offline, with click-to-expand via `part-of` edges. Exit test: fixture renders with no network and no API key; concept panel shows tiered accordion; KaTeX renders the attention equation. |
| **M5** | P6 output target = forked viewer's input format (via adapter) instead of merged explorer.html. AIAYN acceptance criteria (§4.3) unchanged. |
| **M6** | Unchanged — depends on §5.1, which the adapter preserves. |

**Steal-list updates (§7):**

| Repo | License (verified 2026-07-09) | Take | How |
|---|---|---|---|
| Graphify-Labs/graphify | MIT | Whole app as viewer base + graph pipeline + cluster dials + claude-cli backend | **fork (pinned tag)** |
| Egonex-AI/Understand-Anything | MIT | Reading paths, layer viz, persona levels | code, with Issue-#491 layout caution |
| colbymchenry/codegraph | MIT | (unchanged from round-9: staleness banners, explore, affected, install pattern) | code/pattern |
| unclecode/crawl4ai | Apache-2.0 **+ attribution requirement** | `content_filter_strategy.py`: BM25ContentFilter, PruningContentFilter | code + README attribution badge |
| zilliztech/deep-searcher | Apache-2.0 | (unchanged: loop pattern only — Milvus core confirmed) | pattern |

---

## 5. Week-2 slice (ordered)

1. **R11-1 wiring:** cache-first + host-native retrieval as the playbook's primary path; API-disable env flag; skip-after-throttle. Run the exit test (10 briefs, APIs off). *Small change; proves API independence.*
2. Clone crawl4ai read-only; port `BM25ContentFilter` → `fetch_clean.py`; add attribution notice; measure tokens-per-fetch before/after on 5 cached pages.
3. Regrade the 10 AIAYN notes with the hardened stack (v2.0 M1 exit test, now actually runnable).
4. Fork graphify (pin tag); strip; run it on the `research-mcp` repo itself to learn the pipeline (dogfood).
5. Write the `§5.1 → graphify graph.json` half of the adapter; feed the AIAYN fixture through it; confirm the viewer renders it offline (amended M4 exit test).

Steps 1–3 are the research engine; 4–5 the viewer. They are independent — parallelizable across sessions if rate-limit windows interfere.

## R12 — Viewer lock + strip pass (2026-07-09, implemented)

**Renderer decision: Cytoscape wins.** Progressive disclosure via `part-of`
edges is the core UX (§4.4); the week-1 prototype's folding logic was ported,
vis-network has no hierarchical folding. Implemented as a NEW module
`graphify/exporters/explorer.py` — upstream `exporters/html.py` untouched.
Properties, all test-enforced (10 tests): fully offline (cytoscape.min.js
3.30.2 vendored at `exporters/vendor/`, inlined at build; zero CDN/`<link>`
refs), unicode-intact labels (`ensure_ascii=False`, √dₖ greppable),
`</script>` injection guard, search box, L0–L3 level colors
(Understand-Anything layer-viz idea), and a dependency-ordered **reading
path** (UA guided-tour idea, round-9): topo sort over prerequisite/builds-on.
KaTeX inlining deferred to M5 (no LaTeX fields in the fixture yet).

**`graph_query.impact` shipped early** (round-8 adoption, codegraph blast
radius): `research_mcp/graph_query.py`, reverse-BFS dependents with depth cap,
`max_results` truncation, success-shaped empty/not-found. Edge dependent-side
convention pinned: part-of→dst, prerequisite→dst, builds-on→src, code kinds→src.
6 tests. CLI: `python -m research_mcp.graph_query impact <graph.json> <node>`.

**Strip pass (import-graph verified):** deleted `prs.py`, `transcribe.py`,
`Dockerfile`, 13 other-IDE skill docs; stubbed the `prs` CLI command, the
youtube ingest branch, and removed the 3 PR MCP tools + handlers from
`serve.py`. Kept: `benchmark.py` (it IS the M3 validation protocol, round-9),
`google_workspace.py` (top-level import in core `detect.py`; inert without
credentials — removal not worth the surgery).

**Known sandbox caveat:** the OneDrive mount intermittently serves stale
truncated copies of freshly-edited large files (`cli.py`); canonical content
verified intact via direct reads. If `python -m py_compile graphify/cli.py`
fails locally, the file simply hasn't finished syncing.

## R13 — `visualize`: optional interactive explorables (2026-07-17, designed)

Opt-in per-concept interactive widgets (explorable-explanations style) for the few
math-heavy concepts a static page under-serves. **Never automatic; zero tokens
unless invoked.** Template library first (parametric self-contained HTML,
LLM only fills params), bespoke LLM-generated HTML only on explicit request.
Artifacts: `viz/<node>.html` + `viz/manifest.json` sidecar — **§5.1 untouched**.
Surfaced in the learner-first dashboard as a lazy "Visualize" drawer tier +
a TopBar gallery indexing all visuals; `build_data.py --viz-dir` optional flag,
default build byte-identical. Offline/injection/size gate: `gate_viz.py`.
Full design + exit tests: `plans/2026-07-17-visualize-and-skillopt-design.md`.

## R14 — SkillOpt-Sleep trial on `skills/explain` (2026-07-17, designed)

microsoft/SkillOpt (MIT) full training loop declined (optimizer backend +
benchmark env per skill = R11-1 friction). Adopt **SkillOpt-Sleep** via its
keyless `claude_code_exec` backend: nightly consolidate `skills/explain/SKILL.md`
behind a ~10-task held-out validation gate (AIAYN fixture + bridge graph);
edits accepted only on strict held-out improvement, owner reviews the diff.
Hard rule: any API-key demand → stop, fall back to pattern-only (validation-gated
manual skill edits). Steal-list row added. Details in the same plans doc.

## 6. Explicitly NOT changed

Zero-cost P1 · deterministic-first P2 · leases/budgets · note/brief schemas · `paper2pack` fidelity ladder · M6 propose-verify-confirm bridge · M7/M8 · all round-2→10 decisions not named above. deep-searcher is not forked. No vector DBs entered the stack.

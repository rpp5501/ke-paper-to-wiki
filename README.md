# paper-skill

Turns a research paper into an explorable, offline concept wiki.

You give it an arXiv id, a `.tex`, or a `.pdf`. It gives you a **concept graph**
(not a table of contents), a tiered explanation page per concept, and a
localhost dashboard where you can read, quiz, and visualize your way through
the paper — all with no network at runtime, no API keys, and no vector database.

This is the build half of the Knowledge Engine. The research half lives in
[`research-mcp`](../research-mcp), which supplies keyless academic search,
token-capped web fetch, and the compounding `_research_wiki/` note cache. The
two repos share one `§5.1` graph schema, which is what lets a paper graph and a
code graph be bridged into a single view.

---

## Quickstart

```bash
pip install -e ".[dev]"
```

Build a validated concept graph from a paper:

```bash
python -c "from paper_skill.build_dashboard import write_graph; write_graph('arXiv:1706.03762', 'artifacts/aiayn')"
```

That writes `pack.json` and `concept-graph.json`. Concept *pages* come from P4;
to see the dashboard immediately, build it against the shipped fixtures
instead:

```bash
cd dashboard && npm install
python build_data.py --graph ../fixtures/aiayn_concept_graph.json --pack ../fixtures/aiayn_tiny_pack.json --pages-dir ../fixtures/pages --wiki-dir ../fixtures/wiki
npm run dev
```

`build_dashboard.py` is the canonical build path — it wires in the anti-TOC
guard described below. Everything else in this README is a stage you can drive
directly when you want finer control.

---

## The pipeline

Each stage is a deterministic shell around an **injectable** `spawn`. The
default spawn shells out to the `claude` CLI; pass your own to run the pipeline
against any model, or against a stub in tests.

### P1 — `paper2pack`: fidelity-laddered ingestion

```bash
python -m paper_skill.paper2pack arXiv:1706.03762 -o pack.json
```

A paper arrives at whatever fidelity its source allows, so ingestion is a
ladder rather than a single parser:

| Rung | Source | Module | Equation fidelity | Table fidelity |
|------|--------|--------|-------------------|----------------|
| 1 | LaTeX source | `latex_pack.py` | exact | exact |
| 2 | ar5iv HTML | `paper2pack.py` | good | exact |
| 4 | PDF | `paper2pack.py` (PyMuPDF) | lossy | none |

Results tables are extracted into `pack["tables"]` as caption + rows, because a
page that reports what a paper measured can only do so if the numbers reach the
writer. LaTeX and ar5iv both carry real structure — `tabular` rows, `<tr>`/`<td>`
— so both are exact.

The PDF rung deliberately does not try, and `extraction.table_fidelity` says so
rather than leaving the absence ambiguous. PyMuPDF's `find_tables()` was run
against a real 19-page paper: it reported ordinary prose as a two-cell table and
returned the genuine results grid with whole columns collapsed into single cells.
A number sitting against the wrong condition is a fabricated result, which is
worse than no table at all.

`latex_pack.py` walks TeX with `pylatexenc` — it never regexes over TeX, which
is the standard way equation extraction silently corrupts.

`upgrade.py` climbs the ladder: one free OpenAlex lookup can find the arXiv
sibling of a bare PDF and promote a rung-4 pack to rung 1.

`references.py` parses `.bbl` into structured records so citation text is never
hauled through the token budget whole.

### P2 — `concepts`: pack → concept graph

```python
from paper_skill.concepts import extract_concepts, require_ok
result = require_ok(extract_concepts(pack, spawn))
```

Produces 15–25 concept nodes with exactly one level-0 thesis node, typed edges
(`part-of`, `prerequisite`, `builds-on`, `defined-in`, `contrasts-with`), and a
`source_ref` on every node that must resolve to a real section id. Invalid
output is retried once with its own validation errors fed back in.

**The anti-TOC guard.** The historical failure mode of this project was a
dashboard that was just the paper's table of contents. It happened because a
missing `claude` CLI raised an opaque `FileNotFoundError`, orchestration
swallowed it, and the pipeline fell back to section headings. Three defences
now sit on that path:

- `llm_spawn.py` centralizes every shell-out to a model and fails **loudly**,
  naming the injectable-spawn escape hatch instead of raising a bare
  `FileNotFoundError`.
- `require_ok()` raises `ConceptExtractionError` rather than degrading.
- `is_toc_graph()` is a defensive tripwire: `sec_N`-shaped ids plus
  structure-only edges aborts the build even if validation passed.

**Graph quality metrics** (`graph_quality`, `graph_quality_findings`) are the
deterministic, zero-token half of kg-gen's MINE benchmark idea: orphan ratio,
near-duplicate slug candidates via pure string normalization, and `part-of`
tree coverage. These are **advisory** — printed by `build_graph`, never fatal.
A TOC graph is the *wrong* graph and must stop the build; a graph with orphans
is merely a *thin* graph, and refusing to build it would be the wrong trade.

### The `concept_toc.yaml` checkpoint

`toc.py` writes a YAML row per concept with an `include` flag. **This is the
human checkpoint before any token spend on page writing.** Nothing in P3 or P4
runs against a concept you did not approve.

### P3 — `p3_research`: fill the gaps

```bash
python -m paper_skill.p3_research concept_toc.yaml --graph concept-graph.json
```

One leased researcher run per concept the extractor flagged `research: true`
— i.e. where the paper's own text is insufficient. Checkpointed per concept, so
resuming after an interruption costs nothing. `briefs.py` converts a TOC row
into a schema-valid brief for `research-mcp`'s playbook loop.

### P4 — `p4_context` + `p4_write`: tiered pages

`p4_context` assembles context at two levels with zero tokens: global context
for TL;DR and Intuition, local context for Mechanics and Math — plus the
section's equations and any extracted results tables. `p4_write` then does one
spawn per concept page against the writing contract in
[`skills/write-paper-tutor/SKILL.md`](skills/write-paper-tutor/SKILL.md), which
is a single reviewable artifact rather than a prompt buried in Python.

**Pedagogy gates** (`pedagogy.py`) run in the retry loop, so a page that fails
one is sent back to the writer rather than failing the build:

| Gate | Rule |
|------|------|
| Paragraph length | >100 prose words is an error; >60 capped at 10% of paragraphs |
| Diagram | prose that repeatedly walks the reader along edges must carry a ` ```mermaid ` graph |
| Results | a page whose own title says results/experiment/evaluation owes the reader the figures |

The diagram gate counts graph relations *and* dataflow language (`sub-layer`,
`residual connection`, `stack of`, `feeds into`, `followed by`). An earlier
version was built while looking at one causal paper and scored every page of the
Transformer build zero — including the encoder-decoder stack — while flagging
six pages of a backdoor-attack paper on the homonym. It now flags ~45% of the
SID pages, ~18% of the Transformer pages, and none of either empirical paper.

These live in the retry loop and **not** in `p5_lint` on purpose: every lint
problem is blocking, which would turn a formatting preference into a build
failure.

### P5 — `p5_lint`: deterministic validation

Anchors resolve, every claim is anchored, links are live, Mermaid blocks parse
(via `scripts/mermaid_parse.mjs`). No model involved.

Mermaid ≥ 11 initialises DOMPurify against a browser DOM, so under bare node the
parse check reports *skipped* rather than failing — an environment that cannot
run the check must not report every valid diagram as broken. The real check on a
diagram is the dashboard, which renders it and falls back to showing the source.

### P6 — `p6_explorer`: single-file offline explorer

```bash
python -m paper_skill.p6_explorer pack.json graph.json pages/ -o explorer.html
```

---

## Beyond the linear pipeline

### Bridge (M6) — paper concepts ↔ code entities

`bridge.py` is a three-step, human-terminated pipeline:

1. `propose_candidates()` — **deterministic** token-overlap matching between a
   concept graph and a code graph. Zero tokens.
2. `verify_candidates()` — one leased spawn per candidate, `YES:`/`NO:` with a
   reason.
3. `load_confirmed()` / `merge_bridge()` — a **human** confirms before anything
   merges into the graph.

The result is a `bridged` graph the dashboard renders as its own view.

### Next steps (M7) — what to do after the paper

`next_steps.py` harvests gaps deterministically (limitation/future-work
sections, `TODO`/`FIXME`/`HACK` markers in a linked repo, forward citations via
`research-mcp`'s citation walk), then synthesizes anchored directions.
`lint_ideas()` enforces that **every idea traces back to a harvested gap** —
un-anchored speculation is rejected, not ranked lower.

### Visualize (R13) — opt-in interactive explorables

An explicitly gated feature, driven by `skills/visualize/SKILL.md`. It never
runs as part of any default pipeline.

```bash
python -m paper_skill.viz propose graph.json --pages-dir pages/
python -m paper_skill.viz build --params params.json --pages-dir pages/ --out viz/
python -m paper_skill.viz review <node> --viz-dir viz/ --pages-dir pages/
```

`propose` prints a capped candidate list and **stops** — no params are authored
until a human confirms the list.

Six self-contained templates ship in `viz_templates/`: attention heatmap,
gradient descent 2D, positional encoding, softmax temperature, vector
projection, and **DAG adjustment** — a graph with a toggleable adjustment set,
for causal-inference and Bayes-net papers. It enumerates the paths itself and
classifies each as causal, blocked, or open, so its verdict is computed rather
than authored; GUIDELINES.md's faithfulness rule does not survive a canned
answer. The first five are all transformer- or optimization-shaped, which is why
a causal paper previously matched nothing and fell through to the bespoke path.

Each is offline HTML with a `{{PARAMS_JSON}}` placeholder; output is one HTML
per node plus a `viz/manifest.json` sidecar keyed by node id. The §5.1 schema is
never touched. A template reports its resolved predict-then-reveal bet to the
host with `postMessage({type: "ke-bet-resolved", correct})`, which is what feeds
the dashboard's mastery ledger.

`review` is the paperbanana-pattern critic: a **bounded** critique pass, capped
at `MAX_REVIEWS = 2`, working from a written style guide (`GUIDELINES.md`) that
the critic must cite, against a fixed rubric-as-checklist (faithfulness,
conciseness, readability). It can edit `params`, `prompt`, and `caption` — never
the template HTML, never the page. The packet deliberately omits the rendered
HTML so the critic reasons about parameters rather than redesigning.

### The writing contract and its benchmark

`skills/write-paper-tutor/SKILL.md` is the page-writing contract. `p4_write`
composes its prompt from that file, so the rules live in one reviewable artifact
instead of a string literal. `skillopt-trial/` is an offline benchmark over that
one file — a locked task manifest, a weighted rubric, hashed evidence, six
deterministic gates, and a hash-chained `tuning → selection → final-test →
human-review` ledger. It never invokes a model; it checks recorded scores.

```bash
cd skillopt-trial
python validation/validate_skillopt.py policy
python validation/validate_skillopt.py accept --baseline ... --candidate ... --run-record ...
```

The rubric weights `visual_explanation` at 15, taken from
`factual_evidence_accuracy` — which carried 30 while six deterministic gates
already enforced it. Without that dimension a candidate that drew a diagram on
every structural page scored exactly the same as one that drew none, so the
optimizer could never be asked for diagrams.

### Mermaid mind map (R15.10)

```bash
python -m paper_skill.graph_to_mermaid concept-graph.json --out map.mmd --max-depth 3
```

Mermaid mindmaps are strictly trees, so only the `part-of` hierarchy becomes
the map. Every non-tree edge is preserved as a footer comment — nothing is
silently dropped. `--max-depth` emits a `%% N node(s) hidden below depth N`
note rather than truncating in silence. Renders natively in GitHub and
Obsidian.

---

## The dashboard

A React + zustand + React Flow app under [`dashboard/`](dashboard) — see
[`dashboard/README.md`](dashboard/README.md) for the full feature list. In
short: four graph views (`concepts` / `clusters` / `code` / `bridged`), two
modes (`learn` / `explore`), ELK layout in a worker, KaTeX math, mermaid
diagrams, mastery tracking with a spaced-review queue, inline checkpoints,
source provenance chips, and the Visualize tier.

A ` ```mermaid ` fence in a page is lifted out by `parseContent` as its own
segment — the same path `derivation`, `algorithm`, and `figure` already take —
and rendered from a lazily imported bundle, falling back to the diagram source
if it will not parse.

`dashboard/build_data.py` compiles everything into one static
`src/data.gen.ts`. Optional inputs are strictly opt-in — omit the flag and the
bundle is byte-identical to a build without the feature:

```
--graph --pack --pages-dir --wiki-dir --hotspots --repo-dir
--viz-dir         # R13 visuals
--next-steps      # R15.1 ideas
--quiz            # R15.2 quiz
--learning-path   # reviewed chapter order + checkpoint placement
--release         # refuse to build unless qualityReport.releasePass
--update          # patch an existing bundle in place
```

`qualityReport` carries the build's own verdict on itself: paragraph
readability, section and worked-example coverage, unresolved references, and
**checkpoint density** — at least one checkpoint per 800 prose words and no
chapter below two. Density feeds `releasePass`, so `--release` refuses a build
whose retrieval practice is too thin to do anything. Fenced blocks are excluded
from that word count; otherwise every diagram added would raise the checkpoint
budget and charge the author for illustrating.

---

## Design constraints

These are pins, not preferences. They are why the code looks the way it does:

- **Offline at runtime.** The dashboard makes zero external requests. Graph
  data, assets, KaTeX fonts, and the ELK worker are all emitted locally.
- **Keyless.** No API keys anywhere in the pipeline. Every academic source used
  is one that answers unauthenticated.
- **No vector databases.** Dedup is pure string normalization; the embedding
  and entity-linking rungs of the usual ladder are declined deliberately.
- **No runtime LLM.** Models run at build time only.
- **Opt-in token spend.** Expensive stages require explicit invocation. The
  `concept_toc.yaml` checkpoint and `viz propose`-then-stop exist for this.
- **Byte-identical default builds.** Adding a feature flag must not perturb the
  output of a build that does not use it.
- **AGPL sources are pattern-only, permanently.** Where a design idea comes
  from an AGPL project, only the pattern is adopted — never the code.

## Tests

```bash
pip install -e ".[dev]"
PYTHONPATH="src;../research-mcp/src" python -m pytest tests dashboard/tests -q
```

```bash
cd dashboard && npm test
python skillopt-trial/validation/validate_skillopt.py policy
```

527 Python tests (384 pipeline + 122 `build_data` + 21 skillopt gate) and 399
vitest tests.

The dashboard suite runs in vitest with `environment: "node"` — no jsdom, no
`@testing-library/react`. Component tests assert against `renderToStaticMarkup`
output. This keeps the suite fast and forces components to be honest about what
they actually emit.

If `tests/test_router.py` and `tests/test_pack_schema_contract.py` fail with
`ModuleNotFoundError: fitz`, the PDF rung's optional dependencies are not
installed — `pip install -e ".[dev]"` fixes it.

## Repository layout

```
src/paper_skill/     pipeline stages, one module per stage
  viz_templates/     self-contained offline HTML explorables + GUIDELINES.md
  schemas/           §5.1 JSON schemas
dashboard/           React dashboard + build_data.py compiler
skills/visualize/    the opt-in R13 skill definition
skills/write-paper-tutor/  the page-writing contract p4_write composes from
skillopt-trial/      offline benchmark + hash-chained ledger for that contract
scripts/             explorer/viz fixture builders, acceptance gates, Anki export
fixtures/            small hand-built inputs the tests run against
artifacts/           built deliverables (aiayn-live and friends)
plans/               design docs, one per slice/round
docs/superpowers/    plans and specs for the dashboard redesign rounds
```

## Attribution

The `/explain` skill and several dashboard UI paradigms are adapted from
[Understand-Anything](https://github.com/Egonex-AI/Understand-Anything) (MIT)
and [TrueCourse](https://github.com/truecourse-ai/truecourse) (MIT); see
[`dashboard/README.md`](dashboard/README.md) for the component-level breakdown.
Graph-quality metrics take the benchmark *idea* from kg-gen's MINE and drop the
tokens. The bounded-critic and rubric-as-checklist patterns in `viz review`
follow paperbanana. In every case the pattern was adopted, not the
implementation.

## License

See [LICENSE](LICENSE).

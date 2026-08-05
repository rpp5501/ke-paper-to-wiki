# Article depth, term lookup, and the bridged re-run — design

**Date:** 2026-08-04
**Status:** implemented 2026-08-05. Deviations from the design as written, all
deliberate:

- **`figure` blocks left out of the prompt.** They reference pre-registered
  explorables by id and the writer cannot invent those; asking for them buys
  broken refs.
- **The block syntax lives in `dashboard/src/lib/contentBlocksExample.md`,** not
  a top-level `fixtures/`. Vite refuses to load files outside its root, and
  next to the parser it pins is where the contract belongs anyway.
- **Two harvest rules, not three, and the reason inverted.** I predicted a thin
  harvest; it was noisy. See Part 2.
- **The miss queue is dropped.** Nothing read it — persistence, validation and a
  cap in service of no reader. Worth adding once something displays it.
**Motivating feedback:** reader review of the arXiv:1306.1043 (SID) dashboard —
no visuals in the article, no pseudocode, math too high level, filler tiers, no
hover explanations, no way to look up a term the hover missed.

## Premise

Three of the four parts below are **not new features**. The dashboard already
contains the mechanisms; nothing emits the data they consume. This has now been
the shape of five separate defects this round (`page` field, glossary,
`implements` edges, content blocks, and the macro table), so the default
assumption when something "doesn't exist" is that it exists and is unfed.

| Capability | Renderer | Why it shows nothing |
|---|---|---|
| Algorithm walkthrough | `AlgorithmWalkthrough` via `BlockRenderer` | no page emits an `algorithm` block |
| Derivation steps | `DerivationSteps` | no page emits a `derivation` block |
| Annotated equations | `AnnotatedEquation` | no page emits an `annotated-eq` block |
| Term hover | `mathHtml` tokenizer + `ArticleView`/`Drawer` | glossary map was empty (partly fixed) |
| Diagrams | `lint_page` mermaid validator, `MermaidBlock` | `PAGE_PROMPT` never mentions mermaid |

`ArticleView` already calls `parseContent` and `BlockRenderer`, so a block in a
page's markdown renders in the article with no component work at all.

## Pinned constraints

Unchanged, and this design does not spend any of them:

- Offline at runtime; no external request from the dashboard.
- Keyless; no API key anywhere.
- No runtime LLM. Term definitions are generated **at build time**, which is
  possible because the set of terms is finite and known once pages exist.
- Opt-in token spend; every new stage is a flag, and omitting it leaves the
  bundle byte-identical.

---

## Part 0 — Renderable equations (DONE, not deferred)

The reader's first complaint, measured: **8 of 11 SID equations threw in KaTeX**
and fell back to printing raw LaTeX. Fixed at extraction, so every consumer of a
pack benefits, and verified against four further papers.

### Three general LaTeX rules, in `latex_pack.normalize_math`

1. **Strip bookkeeping** — `\label`, `\nonumber`, `\notag`, the counter family
   (`\addtocounter`, `\setcounter`, `\stepcounter`, `\refstepcounter`),
   `\the<counter>`, and an `\tag{}` left empty once its argument is gone. KaTeX
   implements none of it, and one occurrence loses the *whole* equation.
2. **Collapse blank lines** — our own artefact: `_strip_comments` deletes `%`
   lines and leaves the holes. Illegal inside LaTeX math anyway, and they end
   the markdown paragraph, tearing the `$$` block in half.
3. **Give orphaned alignment markers a home** — an `align`/`eqnarray` *body*
   keeps the `&` and `\\` that only mean something inside the wrapper this
   extractor drops, so wrap in `aligned`. The test is whether a marker sits at
   environment depth 0, not whether the body contains an environment at all —
   SID's eq_9 opens an array, closes it, and only then uses a top-level `&`.

Applied on the ar5iv rung too: `alttext` is the original LaTeX and carries the
same hazards.

### Bookkeeping hides one level up

`extract_macros` exported VAE's `\eqnr` = `\addtocounter{equation}{1}\tag{\theequation}`
verbatim — a pure numbering macro that killed 22 of its 30 equations. Macro
bodies are stripped by the same rule; one that reduces to nothing exports as
empty, which is correct, and one with real maths around its bookkeeping keeps
the maths.

### The empty-pack guard

Adam (arXiv:1412.6980) produced 0 sections, 0 equations, 0 macros and an empty
title, and `paper2pack` still reported `path=latex`. The fidelity ladder only
ever descended on a thrown exception, so a rung that *parsed* and yielded
nothing counted as success. `_require_content` now refuses such a pack: rung 1
descends to ar5iv, and when ar5iv is also empty (it serves an "Untitled
Document" stub when its own conversion failed — which is the real story for
Adam) the result is a success-shaped `empty_extraction` pointing at the PDF
rung. Without this, P2 would extract concepts from nothing: the TOC-shaped
garbage the anti-TOC guard catches, arriving a stage earlier and cheaper.

### Measured, five papers

| paper | before | after |
|---|---|---|
| SID 1306.1043 | 3/11 (27%) | **11/11** |
| Batch Normalization 1502.03167 | 0/3 (0%) | **3/3** |
| GANs 1406.2661 | 2/6 (33%) | **6/6** |
| Auto-Encoding VB 1312.6114 | 1/30 (3%) | **30/30** |
| Adam 1412.6980 | 0/0 | refused, `empty_extraction` |
| **total** | **6/50 (12%)** | **50/50 (100%)** |

Each pack rendered with its own macro table, under the dashboard's exact KaTeX
options (`strict: "error"`, `throwOnError: true`).

### Still owed

The 24 committed SID pages hold the pre-fix LaTeX copied verbatim. They are
corrected by the Part 4 re-run, not separately.

---

## Part 1 — Rich content blocks in P4

### What changes

`PAGE_PROMPT` gains a description of the four block types and their fenced-YAML
syntax, e.g.

````
```algorithm
title: Algorithm 2 — reachability under d-separation
lines:
  - code: "for _ in range(ceil(log2(n))):"
    intent: "Each squaring doubles the path length covered, so ceil(log2 n)
             reaches every simple path in a p-node DAG [§sec_4]"
```
````

### Gating

Blocks are **earned, not forced**. An `algorithm` block appears only where the
LOCAL context actually contains an algorithm; `derivation` only where there are
real steps; `annotated-eq` only where terms of an equation carry distinct
roles. A concept with none of these stays prose. Without this rule every page
sprouts decorative widgets and the signal is lost.

### Known trap

`lint_page` splits paragraphs on blank lines, and a fenced YAML block contains
them. Left alone, a block is torn in half and its anchor-less first half is
reported as an unanchored claim — the identical failure already fixed for
`$$…$$` display math. Fenced blocks must be folded the same way before the
paragraph split.

### Tests

- A block survives the lint paragraph split intact.
- A block with no anchor anywhere is still caught (the fold is not an amnesty).
- `parseContent` accepts what the prompt describes — the prompt's example is
  used as a test vector, so prompt and parser cannot drift apart.
- Generalization: a paper with no algorithms produces no `algorithm` blocks.

---

## Part 1b — Scannable formatting, with a check

### Measured baseline (24 SID pages, before the re-run)

| | pages with none |
|---|---|
| tables | 24 / 24 |
| mermaid | 24 / 24 |
| content blocks | 24 / 24 |
| bullet lists | 17 / 24 |
| bold lead-ins | 20 / 24 |

Longest paragraph 101 words; four pages over 80. These pages were written before
the "Format for scanning" rule was added to `PAGE_PROMPT`, so the rule is not
failing — it has never run. This baseline is the before-picture for the re-run.

### Prompt: name the shapes, keep the gate

The existing rule says to use a list "where the content is genuinely a list".
That is true and useless — it names no trigger. Replace with the shapes this
kind of paper actually produces, each still earned:

- **Table** when two or more named things are compared on shared axes — two
  metrics, two graph classes, two algorithms and their costs.
- **Bullets** when the content is an enumerated set the paper itself
  enumerates — the conditions of a criterion, the cases of a proof, the steps
  of a procedure that is not pseudocode (pseudocode is an `algorithm` block).
- **Bold lead-in** when a paragraph turns on one term, so the eye can find it.
- **Mermaid** when a relationship is structural and small — a graph, a
  dependency, a state change. Not for decoration, and not where an `algorithm`
  block is the better fit.

A tier that is genuinely one argument stays one paragraph. Anchors still
terminate list items and table rows.

### Lint: nothing. Formatting is the writer's judgement

A >90-word paragraph ceiling was built, measured, and **removed** at the
reader's direction: a soft limit, not a hard one.

The design error was structural, not the threshold. Every entry `lint_page`
returns is blocking — `scripts/gate_slice7.py` gates on "all pages lint clean"
— so there was no way to express "prefer shorter" as a preference. A style
opinion became a build failure, and the judgement moved from the writer, which
can see the content, to a word count, which cannot.

Measured before removal, on the first regenerated page: the ceiling fired twice
(101 and 134 words) on paragraphs that were genuinely dense rather than
malformed. The rule worked; it just should not have had a veto.

Formatting now lives entirely in `PAGE_PROMPT`, as preferences with reasons:
short paragraphs over long, bolded colon lead-ins acting as subtitles, bullets
wherever the content enumerates at all, a table for things compared on shared
axes, mermaid for small structural relationships — and an explicit "you can see
the content, so you pick the form".

The only formatting-adjacent thing the linter still does is fold fenced blocks
so the paragraph split cannot tear one in half.

### Tests

- A 100-word prose paragraph is flagged; an 80-word one is not.
- A long `$$…$$` block is not flagged.
- A page of short paragraphs with no table and no list passes — absence of
  structure is not a defect.

---

## Part 2 — Build-time term harvest

### New module `paper_skill/terms.py`

- `harvest_terms(pages, known) -> list[str]` — deterministic, **zero tokens**.
  A term qualifies when it appears in **two or more pages** and is either an
  all-caps acronym of 2–6 letters (`CPDAG`, `SHD`) or a hyphenated lowercase
  compound (`d-separation`, `pre-metric`). Anything already in `known` is
  dropped, as is anything outside prose. Ordered by page count, then
  alphabetically, so the list is stable across runs.

  **What measuring changed.** The capitalised-multi-word rule is not
  implemented. Run against the real 24 pages, two rules produced 24 candidates —
  not thin, as predicted, but *noisy*, and adding a third rule would only have
  made it noisier. Two genuine defects surfaced and are fixed:
  the tier headings scored above every real term in the paper (`TL`, `DR`,
  `the-math`, `go-deeper`), and `\HH`/`\CC` leaked from display math because a
  `$…$` pattern matches the empty span between the two dollars of `$$…$$` and
  leaves the body exposed. Non-prose is now stripped display-math-first, taking
  24 candidates to 18.

  The residue (`ground-truth`, `data-generating`, `re-deriving`) is ordinary
  English compounding, which no regex separates from `d-separation`. So the
  scan is deliberately a **recall** net and the single batched call does
  **precision**: it is told to omit candidates that are not terms of art, and
  omission costs nothing because `define_terms` only returns what came back.
  Same deterministic-gather-then-one-judgement shape as `next_steps` and bridge
  propose/verify.
- `define_terms(terms, pages, spawn) -> dict[str, str]` — **one batched call**.
  Definitions grounded in the page text only, with the same anti-fabrication
  rule the quiz contract uses: never invent what the pages do not support.
- Output merges into the `_paper` glossary note, which already applies to every
  concept.

CLI, opt-in like every other spend:

```
python -m paper_skill.terms <pages-dir> --glossary artifacts/<id>/wiki/_paper.yaml
```

### Why build time

The dashboard cannot call a model at runtime without giving up offline, keyless,
or backend-free — all three are load-bearing. It does not need to: the terms are
the words in the finished pages, so the same call can happen once, during the
build, and ship in the bundle. Pre-generating turns the lookup cascade's first
rung into the common case instead of the fallback.

### Tests

- Harvest is deterministic and returns nothing already defined.
- Single-occurrence terms are not harvested.
- A page set with no repeated terms yields an empty list, not a crash.
- `define_terms` failure is loud (`LLMUnavailable` path), never silently empty.

---

## Part 3 — Select-to-look-up

### `lib/lookup.ts` — pure, testable without a DOM

`lookup(phrase, data) -> LookupResult | null`, cascading:

1. **Glossary** — exact, then case- and plural-normalised.
2. **Concept node** — label match; returns definition plus the node id so the
   caller can navigate.
3. **Paper section** — first section whose text contains the phrase, returned as
   an excerpt with its `sectionRef` so the existing `SourceChip` can render it.

No match returns `null`. It never returns a loosely-related paragraph as if it
were an answer.

### `SelectionLookup.tsx`

- Listens for `selectionchange`; a popover anchored to the selection.
- Dismiss on Escape and click-away; reachable by keyboard, so the feature is not
  mouse-only.
- **Defers to the hover**: if the selection lies entirely within an existing
  glossary term, no popover — two explanations stacked on one phrase is worse
  than one.
- Split presentational/behavioural so the presentational half is testable under
  vitest's `environment: "node"` with `renderToStaticMarkup`, and the
  `selectionchange` wiring stays a thin shell.

### Miss queue — dropped

Not built. Persistence, validation and a cap in service of a list nothing ever
displays; "readable as a glossary to-do list" meant opening devtools. Worth
adding the day something surfaces it.

### Tests

- Each cascade rung, in order, with a case/plural variant.
- Unknown phrase returns `null`.
- A selection inside a known glossary term yields no popover.
- Miss queue is capped and survives a corrupted stored value.

---

## Part 4 — Merge the bridge, then one P4 re-run

Verification produced **7 confirmed** concept↔code pairs (23 rejected, 0
unparseable). Sequence:

1. Confirm the 7 in `bridge_candidates.yaml`, `merge_bridge` into a bridged
   graph.
2. **One** P4 re-run with `repo_dir` pointed at pgmpy, so a single pass gets:
   content blocks, the depth rules, no filler tiers, the container-section
   fallback, and the implementation excerpts.
3. Re-lint all 24 (expect 0 filler; currently 11 of 24 carry it).
4. Rebuild the bundle with `--wiki-dir` and verify in the browser.

Re-running P4 once rather than per-change is deliberate: it is 24 model calls,
and every input to it is now ready.

---

## Out of scope

- Moving R13 explorables into `ArticleView` — content blocks are the article's
  visual vocabulary; explorables stay a Drawer tier.
- Changing the guided tour — reviewed and explicitly deferred in favour of
  article depth.
- Runtime LLM lookup — costs offline, keyless, and backend-free for a feature
  that build-time generation covers.

## Risks

- **Block overuse.** Mitigated by the earned-not-forced rule and a
  generalization test on a paper with no algorithms.
- **Harvest noise.** Mitigated by requiring repetition and dropping known terms;
  worst case is a glossary entry nobody hovers.
- **P4 re-run regression.** The 24 current pages are committed, so a bad run is
  recoverable with `git checkout`.

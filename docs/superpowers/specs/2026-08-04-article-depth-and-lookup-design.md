# Article depth, term lookup, and the bridged re-run — design

**Date:** 2026-08-04
**Status:** approved, not yet implemented
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

## Part 2 — Build-time term harvest

### New module `paper_skill/terms.py`

- `harvest_terms(pages, known) -> list[str]` — deterministic, **zero tokens**.
  A term qualifies when it appears in **two or more pages** and matches one of:
  a capitalised multi-word phrase (`Markov Equivalence Class`), an all-caps
  acronym of 2–6 letters (`CPDAG`, `SHD`), or a hyphenated lowercase compound
  (`d-separation`, `pre-metric`). Anything already in `known` is dropped, as is
  any term inside a `$…$` span — those are notation, and the macro table
  already handles them. Ordered by page count, then alphabetically, so the list
  is stable across runs.
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

### Miss queue

Phrases that resolve to `null` are appended to a capped localStorage list via
the existing `persist.ts` helpers, readable as a glossary to-do list. Capped and
validated on read, because localStorage is user-editable.

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

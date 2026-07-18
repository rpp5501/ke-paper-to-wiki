---
name: visualize
description: Use ONLY when the owner explicitly asks for interactive visuals (explorables) for a paper's concepts. Generates per-node explorable HTML for a Knowledge-Engine concept graph via the R13 template library, surfaced in the dashboard's Visualize tier and Visuals gallery. Never runs as part of paper2pack or any default pipeline.
---

# Visualize a Concept (R13)

Turn the few genuinely hard concepts in a paper into offline interactive
explorables. Design contract: `plans/2026-07-17-visualize-and-skillopt-design.md`;
pattern catalog: `plans/2026-07-17-viz-exemplar-research.md`.

## Hard token rules

- **Never run unprompted.** No viz work inside paper2pack, page writing, or
  explain. Zero tokens unless the owner invoked this skill.
- **Propose first, generate never (until confirmed).** `propose` prints a
  capped candidate list and stops. Do not author params before the owner
  confirms the list.
- **Templates before bespoke.** Bespoke HTML generation requires the owner to
  name the node explicitly; it is the expensive path.

## Workflow

1. **Propose** (deterministic, zero LLM work):
   `python -m paper_skill.viz propose <concept_graph.json> --pages-dir <pages> [--k 4]`
   Candidates = nodes whose page exists and has a The-Math tier, ranked by
   degree. Show the owner the list; STOP for confirmation.
2. **Author params** (the only LLM step). For each confirmed node, read only
   its page (anchored tiers, not the whole pages dir) and write one entry in
   `viz_params.json`:

   ```json
   {"scaled-dot-product-attention": {
     "template_id": "attention-heatmap",
     "title": "Scaled dot-product attention, live",
     "caption": "Scrub d_k; watch QK^T -> softmax reweight the values.",
     "prompt": "Before you scrub: which token do you bet 'it' attends to most?",
     "page": "04_sdpa.md",
     "params": {"tokens": ["the","animal","crossed","it"], "queryIndex": 3,
                 "biasTarget": 1, "seed": 42}}}
   ```

   `prompt` is the place-your-bets question (required). Take tokens, labels,
   logits, and equation values from the page's own example — toy-sized honest
   data, 3–5 items, the paper's notation.
3. **Build + gate** (deterministic):
   `python -m paper_skill.viz build --params viz_params.json --pages-dir <pages> --out viz`
   Exit 1 = gate findings; fix params, never hand-edit generated HTML.
4. **Surface**: rebuild the dashboard with `build_data.py ... --viz-dir viz`.
   Without the flag the build is untouched — that is the contract.

## Design rules (pinned, from exemplar research)

Seeded state, never a blank sandbox. Predict-then-reveal wherever there is a
right answer. Scrub-only, no autoplay. MathML inside iframes, never KaTeX.
Fully offline — no CDN, no fetch, no `<link>`.

## Bespoke path (explicit request only)

If the owner names a concept no template covers: write a single self-contained
HTML file obeying every design rule above, with a
`<script id="params" type="application/json">` block (escape `</` as `<\/`),
place it in the viz dir, add its manifest entry by hand (`kind: "bespoke"`,
all required fields incl. `page` + `page_sha256`), then run
`python scripts/gate_viz.py viz` and get owner review before commit.

## Common mistakes

- Do not generate visuals for every node — the cap exists because visuals are
  for concepts a static page under-serves, not decoration.
- Do not invent example values; pull them from the node's page. If the page
  lacks a worked example, say so and ask, don't fabricate.
- Do not load KaTeX or any asset into a template — the 150 KB gate will fail.
- Do not skip the confirmation stop after `propose`.
- A stale-page warning from `build_data.py` means regenerate params from the
  current page, not suppress the banner.

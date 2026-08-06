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
     "anchor_tier": "after-intuition",
     "params": {"tokens": ["the","animal","crossed","it"], "queryIndex": 3,
                 "biasTarget": 1, "seed": 42}}}
   ```

   `prompt` is the place-your-bets question (required). Take tokens, labels,
   logits, and equation values from the page's own example — toy-sized honest
   data, 3–5 items, the paper's notation.

   `anchor_tier` is where the visual sits (R13.1). `after-intuition` is the
   default — build intuition before the formalism. Use `in-the-math` only
   when the visual is unreadable without the notation already on the page,
   e.g. a term-by-term decomposition. **Propose the placement and let the
   owner confirm it**; never infer it silently.
3. **Build + gate** (deterministic):
   `python -m paper_skill.viz build --params viz_params.json --pages-dir <pages> --out viz`
   Exit 1 = gate findings; fix params, never hand-edit generated HTML.
4. **Review (optional, ≤2 passes)** — R13.1's bounded critique loop:
   `python -m paper_skill.viz review <node> --viz-dir viz --pages-dir <pages>`
   It prints the page, the current params, and a faithfulness / conciseness /
   readability checklist, and points at `viz_templates/GUIDELINES.md`. Judge
   each heading **citing the guideline you apply**, then propose *params-only*
   edits (params, prompt, caption) and re-run `build`. Never edit generated
   HTML, never edit the page. The third call refuses by design — accept the
   visual or take it back to propose-and-confirm. Runs only inside an explicit
   visualize invocation, never in a batch.
5. **Surface**: rebuild the dashboard with `build_data.py ... --viz-dir viz`.
   Without the flag the build is untouched — that is the contract.

## Template catalog

`attention-heatmap`, `softmax-temperature`, `positional-encoding`,
`gradient-descent-2d`, `vector-projection` — transformer and optimization
shapes. `dag-adjustment` — a graph with a toggleable adjustment set, for
causal-inference and Bayes-net papers; it enumerates the paths itself, so the
verdict it shows is computed from the params, never authored.

A paper whose shape is not in this list is the signal to add a template, not
to reach for the bespoke path for every node.

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

# Visualize Feature — Exemplar Research + Design Thinking (feeds R13)

**Status:** research complete (2026-07-17). Deltas folded into `plans/2026-07-17-visualize-and-skillopt-design.md` (R13) same day.
**Method:** design-thinking pass (Empathize→Define→Ideate/SCAMPER→Prototype→Test) grounded in primary sources: Bret Victor's Explorable Explanations essay, Nicky Case's two design-pattern posts, and license checks on the portable exemplar repos.

---

## 1. Sources & verified licenses (2026-07-17)

| Exemplar | License | Portability verdict |
|---|---|---|
| vicapow/explained-visually (Setosa EV: eigenvectors, Markov chains, OLS, PCA) | **MIT** (verified) | **Port code** — small d3 explorables, closest existing code to our template library |
| poloclub/transformer-explainer (CHI 2026; GPT-2 live in browser) | **MIT** (verified) | Port *patterns + selected components* (attention matrix interactions, abstraction-level transitions); whole app too heavy for 150 KB budget |
| seeingtheory/Seeing-Theory (Brown; probability/stats) | **Apache-2.0** (verified) | Port code with attribution notice (crawl4ai precedent, §7 discipline) |
| aws-samples/aws-mlu-explain (MLU-Explain) | **CC-BY-SA 4.0** (verified) | **Pattern-only** — ShareAlike would contaminate; do not copy code |
| bbycroft/llm-viz | **No license file** (GitHub license API, verified) | **Pattern-only** — all-rights-reserved by default |
| tensorflow/playground | Apache-2.0 (well-known; re-verify at port) | Pattern-only for us (whole-app scale, see deep-end caveat below) |
| VisuAlgo, Immersive Math, Mathigon, Brilliant | Closed / mixed | Pattern-only |
| Nicky Case explorables | Blog/art CC0 ("dedicated to the public domain", verified on-page); code repos vary | Verify per repo at port time; patterns free |
| poloclub/cnn-explainer | MIT (known; re-verify at port) | Pattern source: symbol↔visual linking |
| Distill.pub | CC-BY articles | Pattern source: prose-embedded playgrounds |

2025–26 field check: Transformer Explainer (CHI 2026 paper) is now the canonical transformer explorable — its key trick is **smooth transitions across abstraction levels** of the same math operation. AnimatedLLM (arXiv 2601.04213), InTraVisTo, AttentionViz, and Xenova's Vision-Transformer Explorer confirm the trend: live-model-in-browser. That whole class is **out of scope** for us (offline, 150 KB, no deps) — we visualize the *mechanism with toy inputs*, not the trained model.

## 2. Pattern catalog (what the exemplars actually teach us)

**Bret Victor (2011), the foundations:**
- **Reactive document** — the reader adjusts the author's numbers in-line; consequences update. Text becomes "an environment to think in," not information to consume.
- **Explorable example** — a live model embedded beside the prose it explains.
- **Contextual information** — question assumptions without leaving the document.

**Nicky Case (meetup post + "4 More Design Patterns", 2018):**
- **See, Model, Apply** — let the learner create their own data points, notice the pattern themselves, then hit embedded micro-problems.
- **Cognitive gates** — progress requires demonstrating understanding.
- **Procedural rhetoric** — guide play with explicit goals or by acting out the algorithm.
- **#1 Puzzle It Out** — solving proves understanding; teaching and assessment in one.
- **#2 Place Your Bets** — force a prediction *before* revealing the answer (NYT You-Draw-It). Strogatz: traditional math teaching fails because "it answers questions the student hasn't thought to ask."
- **#4 Sandbox Mode + the deep-end warning** — Case names TensorFlow Playground specifically: well-designed, but "information overload" for novices. Fixes: keep the sim tiny, or put the sandbox at the *end* after guided steps introduce its pieces.

**From the ML explainers specifically:**
- **Symbol↔visual linking** (CNN Explainer, Transformer Explainer): hover an equation term, the corresponding visual element highlights — and vice versa. This is the single highest-value pattern for our "The Math" tier.
- **Abstraction-level zoom** (Transformer Explainer): the same operation viewable as box-diagram → matrix picture → per-element arithmetic.
- **Toy-sized honest data** (Setosa): 3–5 tokens/points, real arithmetic, no fake animation.

## 3. Design thinking

**Challenge:** make the few genuinely hard concepts in a paper manipulable, inside the dashboard, without blowing the token budget or the offline/150 KB constraints.
**Users:** the owner (and later, any learner) working through a paper in learn mode — motivated, math-capable, but forming intuition; currently leaves the app for 3B1B/YouTube when a mechanism won't click.

### Empathize

| | |
|---|---|
| Say | "I get the TL;DR and intuition tiers, but The Math tier is still a wall"; "why √dₖ?" |
| Think | If I could poke it, I'd trust that I understand it — reading right answers isn't the same as predicting them |
| Do | Alt-tab to YouTube/explorables mid-read; loses the paper's notation and provenance; rarely comes back to the same spot |
| Feel | Notation anxiety on dense tiers; satisfaction when a prediction lands |

Pain points: static math tier (high, workaround: external videos); notation mismatch between external explainers and the paper (medium); no way to test understanding before moving on (medium, workaround: none).

### Define

**POV:** A paper-learner needs the paper's key mechanisms to be *manipulable in the paper's own notation* because intuition forms by testing predictions against behavior, not by re-reading equations.

How might we make the equation itself the interface, not an illustration beside it? How might we get the learner to commit to a prediction before we reveal the answer? How might we keep every visual tied to a graph node's provenance and staleness machinery? How might we do all this at near-zero marginal tokens?

### Ideate (SCAMPER over the R13 baseline)

| # | SCAMPER | Idea | Type |
|---|---|---|---|
| 1 | Substitute | Reactive equation: bind scrubbable values into The Math tier's equation (Victor's reactive document; MathML, not KaTeX, inside the iframe) | Safe |
| 2 | Combine | Symbol↔visual linking: hover eq term ↔ highlight visual element, both directions | Safe |
| 3 | Adapt | You-Draw-It micro-moment: "sketch the softmax weights for these logits" → reveal overlay | Moderate |
| 4 | Modify | Abstraction-level toggle inside a template: diagram ↔ matrix ↔ per-element arithmetic | Moderate |
| 5 | Put to other use | Same params JSON renders a static SVG fallback (print/export, gate failure path) | Safe |
| 6 | Eliminate | No blank sandboxes, no autoplay animation; scrub-only, seeded state (deep-end warning) | Safe |
| 7 | Eliminate | Drop play/pause chrome entirely — every template opens mid-example | Safe |
| 8 | Reverse | Puzzle-it-out: learner re-orders the operation pipeline (QKᵀ → scale → softmax → ×V) before it runs | Wild |
| 9 | Combine | Completing a viz micro-challenge feeds learn-mode `markStepComplete` (cognitive gate, opt-in) | Moderate |
| 10 | Adapt | "Why √dₖ?" toggle: same attention template with scaling on/off at growing dₖ — variance visibly explodes | Safe |

Top picks: #1+#2 become **core template affordances** (every template gets them); #3 becomes the standard **predict-then-reveal** overlay; #6/#7 become hard design rules; #10 ships in the attention template; #8/#9 logged as backlog, not v1.

### Prototype

**What:** the M-viz acceptance fixture — `attention-heatmap` template with seeded 4-token example, predict-then-reveal overlay, MathML equation with term↔visual hover linking, √dₖ on/off toggle.
**Testing assumptions:** params JSON extractable from the fixture page alone; MathML replaces KaTeX inside the iframe (KaTeX css+fonts would blow 150 KB); term↔visual linking works inside `sandbox="allow-scripts"`; the whole thing stays under budget.

### Test

With the owner, on AIAYN, in learn mode. **Success:** at least one wrong-prediction→aha moment; owner does not leave the app for YouTube during the attention step; file <150 KB; zero network. **Failure:** viz opened once and ignored; params extraction needed hand-fixing; bespoke path consumed more tokens than writing the page did.

Next iteration loops back to Ideate/Prototype if predict-then-reveal feels like a quiz rather than play — the fix per Case is smaller sims, not more chrome.

## 4. Deltas applied to R13

1. Manifest gains a required `prompt` field (the place-your-bets question) and templates gain two standard affordances: reactive parameters + symbol↔visual linking.
2. Design rules pinned: seeded state, no blank sandboxes, scrub-only, MathML inside iframes, toy-sized honest data.
3. Template seed set re-specified with per-template interaction pattern (see R13 doc).
4. Steal-list: + explained-visually (MIT, code), + Seeing-Theory (Apache-2.0 + attribution, code), + transformer-explainer (MIT, patterns/components); MLU-Explain and llm-viz explicitly pattern-only.
5. Bespoke prompt contract must cite this pattern catalog (generation prompt includes the design rules, not vibes).

# Limitations

## TL;DR {#tldr}

This paper's central claim is that remaining output length is linearly decodable from hidden states — a claim about representation, not mechanism. The evidence for dynamic re-estimation is qualitative, the tested models are homogeneous in scale and training regime, dataset coverage is incomplete, and training/evaluation are restricted to completions that terminate naturally.

## Intuition {#intuition}

A thermometer bolted to the wall accurately reports the room's temperature, but that doesn't mean the thermostat reads it — the heater could be running on a timer that happens to correlate. A linear probe is the thermometer: it shows that length information sits in the residual stream, not that generation reads that subspace to decide when to stop.

Every limitation below tightens or loosens that same gap: between a direction being present in the residual stream and the model actually depending on it to generate.

## Mechanics {#mechanics}

**Decodability is not mechanism.** A linear probe shows that remaining-length information is recoverable from the residual stream. It does not show the forward pass reads that subspace to decide when to stop generating [§sec_6][S1].

**What a probe alone can conflate:**
- Correlated surface cues — token count, punctuation density, positional statistics — that a probe can latch onto instead of a true length representation [S1].
- Probe expressivity itself: a powerful enough probe can extract structure the network encodes only as an incidental byproduct of unrelated computation [S1].
- A control task, training a probe on a shuffled or randomized target, is the standard way to check a probe isn't simply memorizing [S1].

**What would close the gap.** Establishing causal use requires an intervention — ablating, patching, or editing the identified subspace and checking whether generation changes as predicted, the approach ROME used to localize, not merely detect, factual associations in GPT [S2][S3].

The natural follow-up is an activation-patching study that ablates or steers the length-tracking direction at inference time and measures the effect on realized output length [§sec_6].

**The dynamic-tracking evidence is qualitative, not aggregate.** The five supporting cases — one in the main text, four in the appendix — are surfaced by sorting eval-set completions on per-completion MAE, not by an aggregate measurement [§sec_6].

**Those cases are drawn from the worst-performing region.** The five examples are selected from the worst-MAE part of the eval set by construction, and on those completions the probe's absolute predictions are far from ground truth — single digits against $r_t \approx 800$ [§sec_6].

**So the panels license only a shape claim.** Given predictions that far off, the panels can support a claim about the direction of the per-position update, not its level [§sec_6].

**The two supporting behaviors haven't been shown together.** Within-distribution absolute tracking and the directional retraction-spike behavior are both present in the probe, but on different subsets of the eval set — not yet on the same example [§sec_6].

**What would strengthen this reading:**
- Show the upward shift is significantly larger at retraction tokens than at length-matched non-retraction controls, within the same MAE regime [§sec_6].
- Recover the same directional behavior on completions where the probe's absolute predictions track $r_t$ closely [§sec_6].

Both are tractable on the existing eval cache and are the immediate next step [§sec_6].

**Scale and training regime are unexplored.** All three evaluated models are 78B-parameter instruction-tuned checkpoints, so it is unknown whether the length-tracking direction sharpens, weakens, or relocates at frontier scale, or in base (non-instruction-tuned) models with a structurally different completion-length distribution [§sec_6].

**The layer sweep doesn't generalize.** The per-layer sweep is run on one model only and should not be read as a claim about layer localization in the three headline models [§sec_6].

**What the grid gap costs in coverage:**

| Models | Dataset coverage |
|---|---|
| Mistral-7B / TriviaQA | Dropped throughout [§sec_6] |
| Llama, Mistral (cross-dataset matrices) | 5 of 7 datasets [§sec_6] |
| Olmo (cross-dataset matrix) | All 7 datasets [§sec_6] |

Compute limits forced these omissions [§sec_6].

**Evaluation is conditioned on successful termination.** Training and evaluation are restricted to completions that emit EOS before the max-length cutoff; sequences that run to the cutoff are excluded by construction [§sec_6].

So these results speak to length estimation conditional on successful termination — not to whether the model knows its own generation is going to overrun [§sec_6].

## The Math {#the-math}

**What "single digits against $r_t \approx 800$" means in error terms.** If the probe predicts roughly 5–9 remaining tokens where the true remaining length is about 800, the absolute error is on the order of 790+ tokens and the relative error exceeds 99% [§sec_6].

That two-orders-of-magnitude gap is why the panels are read only for the sign and shape of the per-position update, not the predicted count itself [§sec_6].

**What the coverage fractions add up to.** Five of seven datasets is roughly 71% of the intended grid for Llama and Mistral; Olmo alone reaches the full 7/7. Add the Mistral-7B / TriviaQA cell dropped everywhere, and two of the three models fall short of complete cross-dataset coverage [§sec_6].

**The condition that would separate decodability from causal use.** Ablate or patch the identified length-tracking subspace at inference time and check whether the realized output length changes as predicted. If generation is unaffected, the direction is decodable but inert; if it changes as predicted, that is the ROME-style demonstration of causal use [§sec_6][S2][S3].

**A second separating condition: the control task.** Train the same probe architecture on a shuffled or randomized length target. If accuracy holds up on the shuffled target too, the original probe's decodability reflects probe capacity rather than a genuine length representation [S1].

## Go Deeper {#go-deeper}

- [Belinkov, "Probing Classifiers: Promises, Shortcomings, and Advances"](https://arxiv.org/abs/2102.12452) — the canonical survey on exactly this gap: why decodability isn't causal use, and how control tasks and causal probing try to close it. Start here.
- [Neel Nanda, "A Comprehensive Mechanistic Interpretability Explainer & Glossary"](https://www.neelnanda.io/mechanistic-interpretability/glossary) — a diagrammed contrast between passive probing/decoding and active causal interventions like activation patching and ablation.
- [Meng et al., "Locating and Editing Factual Associations in GPT" (ROME)](https://arxiv.org/abs/2202.05262) — the concrete worked example this page points to: causal tracing plus an edit that changes model output, not just a correlational probe.

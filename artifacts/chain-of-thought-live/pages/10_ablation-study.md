# Ablation Study

## TL;DR {#tldr}
- Chain-of-thought's gain isn't just "produce an equation," "spend more tokens," or "activate relevant pretrained knowledge" — each of those pieces was isolated, and none alone reproduces the effect.
- On GSM8K with PaLM 540B, only full chain-of-thought reaches 56.5% solve rate; equation-only, dot-padding, and reasoning-after-answer all land within a few points of the 17.9% baseline.
- The improvement holds across different prompt writers and exemplar sources, though the exact solve rate swings by several points depending on which exemplars are used.

## Intuition {#intuition}
CoT prompting bundles three things at once: writing an equation, spending extra tokens, and rehearsing reasoning in natural language.

The ablation study swaps out one ingredient at a time — an equation with no prose, a string of dots the same length as the reasoning, or the same reasoning moved after the answer — to see which piece is doing the work.

## Mechanics {#mechanics}
The ablation compares standard prompting and full chain-of-thought against three stripped-down variants, each removing one candidate explanation while holding the rest of the prompt fixed. All results below are solve rate on GSM8K with PaLM at 137B and 540B parameters [§sec_3_3].

| Condition | 137B | 540B |
|---|---|---|
| Standard prompting (baseline) | 6.3% | 17.9% |
| Equation only | 5.7% | 21.7% |
| Variable compute only (dots) | 6.0% | 17.7% |
| Reasoning after answer | 5.9% | 18.0% |
| Chain-of-thought | 14.8% | 56.5% [§sec_3_3] |

Equation-only prompting asks the model to output just the arithmetic expression before answering, testing whether CoT's benefit comes from producing a computable equation. On GSM8K this barely moves the needle: at 540B it reaches 21.7% versus 17.9% for standard prompting, far short of CoT's 56.5% [§sec_3_3].

The paper attributes this gap to question difficulty: GSM8K's word problems are hard to translate directly into an equation without the intermediate natural-language reasoning, whereas one- and two-step problems in simpler datasets let the equation be read off the question almost directly [§sec_3_3].

Variable-compute-only prompting replaces the reasoning with a string of dots matching the character length of the equation, isolating whether extra inference-time tokens alone help. It performs about the same as standard prompting — 17.7% versus 17.9% at 540B — so token budget by itself is not the mechanism [§sec_3_3].

Reasoning-after-answer keeps the full chain of thought but moves it after the final answer, testing whether the model needs to depend on the reasoning to produce that answer, rather than merely being cued to recall relevant pretraining knowledge. It too tracks the baseline, at 18.0% versus 17.9% at 540B [§sec_3_3].

Since neither extra tokens nor delayed reasoning reproduces CoT's gain, the paper concludes the benefit lies specifically in expressing intermediate steps as natural language before the answer, not in token count or knowledge activation alone [§sec_3_3].

A separate check varies who wrote the exemplars and where they came from, on GSM8K and MAWPS. Three different annotators, an intentionally concise rewrite, and three sets of exemplars drawn directly from GSM8K all outperform standard prompting, though the exact solve rate shifts by several points depending on which exemplars are used [§sec_3_3].

| Condition | GSM8K | MAWPS |
|---|---|---|
| Standard prompting | 6.5% | 43.2% |
| CoT, default annotator | 14.3% | 57.9% |
| CoT, annotator B | 15.5% | 58.2% |
| CoT, annotator C | 17.6% | 60.1% |
| CoT, concise style | 11.1% | 59.6% |
| CoT, GSM8K exemplars (set 1) | 13.2% | 54.2% |
| CoT, GSM8K exemplars (set 2) | 13.3% | 61.1% |
| CoT, GSM8K exemplars (set 3) | 12.8% | 54.1% [§sec_3_3] |

Every CoT variant beats the standard-prompting baseline on both datasets, but the range across variants is wide: GSM8K solve rate spans 11.1% to 17.6%, a 6.5-point spread from prompt-writer and exemplar choice alone [§sec_3_3].

## The Math {#the-math}
At 540B, chain-of-thought reaches 56.5% against a 17.9% standard-prompting baseline: a 38.6-point absolute gain, or a 3.16× multiple of the baseline rate [§sec_3_3].

At 137B the same comparison gives 14.8% against 6.3%, an 8.5-point gain and a 2.35× multiple — a smaller absolute gain but a comparable relative one, showing the effect isn't simply proportional to baseline scale [§sec_3_3].

Equation-only prompting recovers only a fraction of that gain: its 21.7% at 540B is 3.8 points above baseline, about one-tenth of chain-of-thought's 38.6-point lift. At 137B equation-only is not even above baseline — 5.7% versus 6.3% — a small net loss [§sec_3_3].

Variable-compute-only and reasoning-after-answer move the 540B solve rate by -0.2 and +0.1 points respectively, both under 1% of the baseline value itself — indistinguishable from noise next to chain-of-thought's 38.6-point lift [§sec_3_3].

## Go Deeper {#go-deeper}
The ablation study appears only for PaLM 137B and 540B on GSM8K in the main text; the paper reports the same three variants against other arithmetic datasets in an appendix table not reproduced in this evidence [§sec_3_3].

This result frames chain-of-thought as bridging exactly the gap equation-only prompting can't cross: translating multi-step natural-language problems into a computable form, not just deriving an equation once that translation is already easy [§sec_3_3].

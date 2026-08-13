# Arithmetic Experimental Setup

## TL;DR {#tldr}
The setup pits plain few-shot prompting against chain-of-thought few-shot prompting on five math word-problem benchmarks, holding the exemplars fixed and varying only whether they show reasoning, across five model families spanning roughly three orders of magnitude in scale.

## Intuition {#intuition}
Picture the same eight questions asked twice: once with a bare final answer, once with the reasoning that produced it. Nothing else about the prompt changes. If the two conditions only start to disagree once the model is large enough, that gap is evidence about what scale unlocks, not about clever prompt engineering.

The exemplars themselves were never tuned to the benchmarks — written once and reused everywhere — which is what lets a single comparison stand in for the whole study instead of five bespoke ones.

## Mechanics {#mechanics}

**Two prompting conditions.** The baseline is standard few-shot prompting: in-context question-answer pairs, then a direct answer for the test example. The treatment augments the same exemplars with a chain of thought leading to the answer, so the two conditions differ only in whether the reasoning is shown [§sec_3_1].

Five math word-problem benchmarks are evaluated:
- A benchmark of math word problems [§sec_3_1]
- A dataset of math word problems with varying structures [§sec_3_1]
- A dataset of diverse math word problems [§sec_3_1]
- A dataset of algebraic word problems, AQuA, the only multiple-choice benchmark of the five [§sec_3_1]
- A fifth benchmark, whose description does not survive in this extracted evidence [§sec_3_1]

**Fixed exemplar sets.** Because most benchmarks have only an evaluation split, the authors hand-wrote one set of eight chain-of-thought exemplars and reused it across every benchmark but AQuA, which needed four multiple-choice exemplars with solutions instead — reusing one set is what rules out per-benchmark prompt tuning as an explanation for any gain [§sec_3_1].

**Model lineup.** Three of the five evaluated model families come with reported parameter counts spanning multiple scales each:

| Family | Sizes tested |
|---|---|
| GPT-3 variants (ada/babbage/curie/davinci-002) | 350M · 1.3B · 6.7B · 175B [§sec_3_1] |
| LaMDA | 422M · 2B · 8B · 68B · 137B [§sec_3_1] |
| PaLM | 8B · 62B · 540B [§sec_3_1] |

Two further model families are evaluated in this study, but the evidence does not carry their parameter sizes [§sec_3_1].

**Decoding and variance protocol.** All models are sampled by greedy decoding, with the note that later work improves on this by taking a majority vote over multiple samples [§sec_3_1]. GPT-3 alone is run five times with independently shuffled exemplar orders and the results averaged; every other family is run with a single fixed order because the seed-to-seed variance observed for GPT-3 was not large [§sec_3_1].

## The Math {#the-math}

**Scale coverage, in ratios.** Every model family spans multiple orders of magnitude between its smallest and largest tested size, which is the resolution needed to see whether chain-of-thought's benefit turns on at a particular scale rather than growing smoothly with it:

- GPT-3: 350M to 175B, a 500× range [§sec_3_1]
- LaMDA: 422M to 137B, roughly 326× [§sec_3_1]
- PaLM: 8B to 540B, roughly 68× [§sec_3_1]

**The seeded-comparison trades depth for coverage.** Running five shuffled-order seeds for each of five model families would cost 5 × 5 = 25 seed-runs; limiting that repetition to GPT-3 and using one fixed order for the other four families costs only 5 + 4 = 9 — a 64% cut bought by treating GPT-3's empirically small seed variance as evidence the other four families need no re-check [§sec_3_1].

## Go Deeper {#go-deeper}
- The identities behind four of the five benchmark descriptions, and the names of two of the five model families, are not preserved in this extraction — AQuA is the only benchmark named directly, and GPT-3, LaMDA, PaLM the only families with reported sizes.
- Full exemplar sets and example problems are placed in the paper's appendix rather than the main text.
- The eight exemplars were deliberately not prompt-engineered; the paper points to separate robustness studies of that choice, which sit outside this evidence.
- Follow-up work referenced here improves on greedy decoding by sampling multiple chains and taking a majority vote over final answers — a self-consistency idea this setup does not itself implement.

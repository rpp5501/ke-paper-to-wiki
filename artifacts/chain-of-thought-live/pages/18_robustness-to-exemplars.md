# Robustness to Exemplars
## TL;DR {#tldr}
Chain-of-thought prompting keeps its accuracy gains even when the annotator, the exemplar source, the exemplar order, or the exemplar count changes. That stability contrasts with the sharp swings seen in ordinary few-shot prompting. [§sec_3_4]

## Intuition {#intuition}
In-context learning is notoriously touchy: swap the order of few-shot exemplars and GPT-3's accuracy on SST-2 can swing from near chance (54.3) to near state of the art (93.4) [§sec_3_4].

Chain-of-thought prompting could suffer the same fragility. The paper tests that directly, varying who wrote the reasoning steps, where the exemplars came from, their order, and how many were used. [§sec_3_4]

## Mechanics {#mechanics}
The original chain-of-thought exemplars for GSM8K and MAWPS were written by Annotator A. Two co-author annotators, B and C, independently wrote their own chains of thought for the identical few-shot exemplars, and Annotator A additionally wrote a more concise version. [§sec_3_4]

All four annotation variants were evaluated on the 137B model on GSM8K and MAWPS. Despite variance across annotators, every variant beat the standard baseline by a large margin, showing the gain does not depend on one writer's linguistic style. [§sec_3_4]

| Axis | What was varied | Outcome |
|---|---|---|
| Annotator style | Original A, concise A, independent B, independent C | All outperform standard prompting by a large margin [§sec_3_4] |
| Exemplar source | Three sets of 8 exemplars randomly sampled from the GSM8K training set, an independent source | Performs comparably to the manually written exemplars [§sec_3_4] |
| Exemplar order | Different orderings of the same exemplar set | Robust to reordering [§sec_3_4] |
| Exemplar count | Different numbers of exemplars | Robust to the number used [§sec_3_4] |

The paper also reports robustness to exemplar order and to the number of exemplars used, though the supporting numbers for those two checks sit in an appendix that is not part of the supplied evidence. [§sec_3_4]

## The Math {#the-math}
Start from the one swing the evidence does quantify: GPT-3 prompted with reordered SST-2 exemplars ranges from 54.3% (roughly chance, since SST-2 is binary) to 93.4% (near state of the art). [§sec_3_4]

That is a 39.1-point spread, or a 1.72x gap between the low and high ends, produced by nothing more than shuffling exemplar order. It sets the scale for what "sensitive to exemplars" means in this literature. [§sec_3_4]

Against that yardstick, the paper runs seven independent perturbation trials on chain-of-thought prompting: four annotation styles (original A, concise A, B, C) and three randomly sampled exemplar sets from GSM8K. [§sec_3_4]

If chain-of-thought prompting were as fragile as the SST-2 case, at least one of those seven trials should have collapsed toward baseline accuracy or below it. None does; every trial clears the standard-prompting baseline by a large margin. [§sec_3_4]

Seven independent trials clearing the same threshold is stronger evidence than one favorable result: each variant is a separate roll of the annotator-and-exemplar dice, and every roll lands on the same side of the baseline. [§sec_3_4]

## Go Deeper {#go-deeper}
This sits inside Arithmetic Reasoning (part-of) and builds on the broader Prompt Engineering Sensitivity concept that motivates why exemplar order and wording matter for in-context learning at all. [§sec_3_4]

The same 137B model and the GSM8K/MAWPS pair used here recur across the paper's other ablations—annotator, exemplar source, order, and count—so the results read as one four-axis robustness argument, not four separate footnotes. [§sec_3_4]

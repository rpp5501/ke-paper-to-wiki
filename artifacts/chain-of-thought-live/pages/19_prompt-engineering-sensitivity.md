I don't need that tool for this task — I'm just regenerating the page content. Here's the corrected page with the flagged paragraphs split at their claim seams and The Math tier rebuilt with anchored, real quantitative content instead of the "no equation" placeholder.

```markdown
# Prompt Engineering Sensitivity

## TL;DR {#tldr}
Chain-of-thought prompting is robust to who writes the exemplars, which dataset they come from, and how many are used. It is not robust to everything: exemplar order and annotation style can still swing accuracy sharply on individual tasks, and at least one task needed careful prompt engineering to work at all.

## Intuition {#intuition}
Treat the exemplars as demonstrating a reasoning style, not a fixed template. Because the model is shown how to think step by step rather than given exact wording to copy, many surface changes in the demonstration — different authors, different source datasets, more or fewer examples — don't change whether the method works.

But the demonstration is still natural language, and natural-language prompts are known to be sensitive to phrasing, framing, and order in ways that are hard to predict ahead of time. Chain-of-thought inherits that sensitivity even where it resists other kinds of variation.

## Mechanics {#mechanics}
Robustness held along several axes tested in the paper:

- **Annotator identity:** three different annotators each wrote their own chain-of-thought exemplars, with no shared instructions beyond "write the step-by-step reasoning." All three beat the standard-prompting baseline by a large margin across eight datasets in arithmetic, commonsense, and symbolic reasoning [§sec_11_2].
- **Exemplar source:** three sets of eight GSM8K exemplars, written by crowd workers with no machine-learning background, outperformed the baseline on all four arithmetic datasets — including datasets the exemplars weren't drawn from [§sec_11_2].
- **Exemplar count:** gains from chain-of-thought held across a varying number of few-shot exemplars, tested on five datasets [§sec_11_2].

Two axes showed more sensitivity. Exemplar order produced only minimal standard deviation in most tasks, but the coin flip task was an exception with high variance, likely because repeating exemplars of the same output in a row biases the model the same way it does for classification prompts [§sec_11_2].

Transfer across models was also imperfect: with identical prompts, chain-of-thought improved every model on every dataset except two commonsense tasks on one model, meaning the same prompt does not guarantee the same gain elsewhere [§sec_11_2].

The strongest limit is the list-reversal task. Two co-authors could not write a chain-of-thought prompt that solved it despite repeated attempts, while a third co-author's prompt solved it perfectly [§sec_11_2]. This is a case where the method's success depended entirely on how the prompt was engineered, not merely on whether chain-of-thought was used at all [§sec_11_2].

## The Math {#the-math}
The coin flip numbers show how much annotator variance alone can move the result. Annotator A reached 99.6% accuracy and Annotator C reached 71.4%, against a baseline of 50.0 (chance on a binary task) [§sec_11_2]. That is a 28.2-point spread between the two best and worst chain-of-thought annotators — larger than Annotator C's own 21.4-point gain over baseline [§sec_11_2].

Annotator choice, on this task, is not a minor detail: it can matter as much as whether chain-of-thought is used at all [§sec_11_2].

The cited GPT-3 permutation result puts an outer bound on how large a pure ordering effect can be. Keeping the same exemplars and changing only their order moved SST-2 accuracy from 54.3, barely above the 50-point chance level for binary classification, to 93.4, near state of the art — a 39.1-point swing from order alone [§sec_11_2].

The exemplar-count result rules out a simpler explanation for chain-of-thought's gains. If chain-of-thought worked only because it gave the model more examples to pattern-match against, doubling the standard-prompting exemplar count from 8 to 16 should have closed the gap [§sec_11_2].

It did not produce a significant improvement, which points to the reasoning structure of the exemplars as the source of the gain rather than their quantity [§sec_11_2].

| Factor | Condition | Accuracy | Comparison |
|---|---|---|---|
| Annotator (coin flip) | Annotator A | 99.6 | 49.6 pts above baseline [§sec_11_2] |
| Annotator (coin flip) | Annotator C | 71.4 | 21.4 pts above baseline [§sec_11_2] |
| Baseline (coin flip) | standard prompting | 50.0 | chance [§sec_11_2] |
| Exemplar order (SST-2, cited work) | worst permutation | 54.3 | near chance [§sec_11_2] |
| Exemplar order (SST-2, cited work) | best permutation | 93.4 | near SOTA [§sec_11_2] |

## Go Deeper {#go-deeper}
This robustness profile builds on [[Robustness to Exemplars]]: that page establishes the exemplar-order and exemplar-count experiments this page interprets for their limits and exceptions.

Two open questions follow from the evidence. First, why gains from chain-of-thought transfer imperfectly between models is unexplained here — the paper attributes it to differences in pre-training data or architecture without testing either [§sec_11_2].

Second, the paper suggests generating chain-of-thought annotations automatically, by prompting a large language model and optimizing the result over a validation set, as a way to make prompt engineering less dependent on finding the right human annotator [§sec_11_2].
```

# MAE Relative to Baseline Floor
## TL;DR {#tldr}

**Dividing each probe's MAE by the constant-median baseline's own MAE turns a raw token count into a difficulty-adjusted score.** Below 1 the probe beats a predictor that always guesses the dataset's median remaining length; at or above 1 it ties or loses to that trivial baseline.

## Intuition {#intuition}

A golf score of 72 means something different on a course with par 70 than one with par 90 — the raw number hides how hard the course was. Dataset MAE works the same way: 30 tokens of error is a strong result on an easy-to-predict dataset and a weak one on a hard-to-predict dataset.

The par is the constant-median baseline — a predictor that just always guesses the middle value. Scoring each probe relative to that par, rather than in raw tokens, is what makes a Count-dataset result and a TriviaQA result comparable.

## Mechanics {#mechanics}

Raw MAE is reported in tokens, so a value of 30 means something different depending on the dataset's own spread: 30 tokens of error against a constant-median baseline of 50 is a much weaker result than the same 30 against a baseline of 200 [§sec_8_2].

Tables 4 and 5 fix this by dividing each MAE entry by the MAD-about-the-median floor of the matching constant-median statistical baseline. Below 1 the probe beats that trivial baseline; above 1 it loses to it; the constant-baseline row itself is 1.00 by construction and is omitted from Table 5 [§sec_8_2].

Read this way, the natural-language datasets — GSM8K, MATH, MMLU-Pro, OpenThoughts-1k, TriviaQA — cluster in the 0.5–0.9 range, meaning the probe closes roughly 10–50% of the baseline's gap to zero error [§sec_8_2].

The synthetic Count and Countdown datasets sit lower still, in the 0.04–0.7 range, meaning the probe extracts most of the baseline's gap on those tasks [§sec_8_2].

The one clear null result is Llama-3.1-8B on TriviaQA: the Exact countdown predictor lands at exactly 1.00, tied with the constant-median baseline it is meant to beat [tab_5].

The Remaining Count Probe does slightly better at 0.82, but that is only an 0.18 improvement over the baseline — the smallest natural-language gain anywhere in the table [tab_5].

Table 4 gives the relative prompt-end AE (probe MAE ÷ baseline MAE) for the Completion Length Probe across all seven datasets and three models [tab_4].

| Model | Count | Countdown | GSM8K | MATH | MMLU-Pro | OpenThoughts-1k | TriviaQA | Anchor |
|---|---|---|---|---|---|---|---|---|
| Llama-3.1-8B | 0.20 | 0.04 | 0.72 | 0.69 | 0.57 | 0.67 | 0.76 | [tab_4] |
| Olmo-3-7B | 0.21 | 0.06 | 0.69 | 0.68 | 0.66 | 0.73 | 0.69 | [tab_4] |
| Mistral-7B | 0.51 | 0.14 | 0.88 | 0.76 | 0.67 | 0.84 | -- | [tab_4] |

Table 5 gives the same ratio for the per-token predictors — both the Exact countdown baseline and the Remaining Count Probe — split by model and dataset [tab_5].

| Model / Predictor | Count | Countdown | GSM8K | MATH | MMLU-Pro | OpenThoughts-1k | TriviaQA | Anchor |
|---|---|---|---|---|---|---|---|---|
| Llama-3.1-8B – Exact countdown | 0.25 | 0.04 | 0.63 | 0.82 | 0.71 | 0.69 | 1.00 | [tab_5] |
| Llama-3.1-8B – Remaining Count Probe | 0.29 | 0.04 | 0.52 | 0.73 | 0.72 | 0.70 | 0.82 | [tab_5] |
| Olmo-3-7B – Exact countdown | 0.27 | 0.07 | 0.76 | 0.74 | 0.69 | 0.88 | 0.93 | [tab_5] |
| Olmo-3-7B – Remaining Count Probe | 0.29 | 0.04 | 0.62 | 0.69 | 0.72 | 0.89 | 0.77 | [tab_5] |
| Mistral-7B – Exact countdown | 0.70 | 0.19 | 0.90 | 0.82 | 0.82 | 0.88 | -- | [tab_5] |
| Mistral-7B – Remaining Count Probe | 0.35 | 0.10 | 0.73 | 0.76 | 0.81 | 0.74 | -- | [tab_5] |

## The Math {#the-math}

A ratio converts directly to a percent reduction: reduction = (1 − ratio) × 100. For Count on Llama-3.1-8B the prompt-end ratio is 0.20, so the probe's MAE is 80% smaller than the constant-median baseline's MAE on that dataset [tab_4].

Countdown is the extreme case: a ratio of 0.04 means the probe's MAE is 96% smaller than the baseline's, the largest reduction of any dataset in the table [tab_4].

GSM8K sits at the other end for this model: a ratio of 0.72 is only a 28% reduction, close to the 10–50% range that defines the natural-language cluster [tab_4] [§sec_8_2].

The TriviaQA null result is the boundary case at the other extreme: a ratio of 1.00 is a 0% reduction, meaning the Exact countdown predictor for Llama-3.1-8B carries no information beyond the dataset's median remaining length [tab_5].

Its Remaining Count Probe counterpart reaches only 0.82, an 18% reduction — smaller than every ratio in the natural-language cluster and the weakest gain in Table 5 [tab_5] [§sec_8_2].

## Go Deeper {#go-deeper}

No external resources were supplied for this concept. For the absolute token-count numbers this tier normalizes, see the underlying MAE tables referenced at [§sec_8_2]; for how the constant-median statistical baseline and its MAD-about-the-median floor are defined, see the baseline-construction discussion at [§sec_8_2].

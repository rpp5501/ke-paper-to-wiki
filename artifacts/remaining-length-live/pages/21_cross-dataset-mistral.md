I don't need external tools for this — I'll just write the corrected page directly.

# Cross-Dataset Generalization on Mistral-7B

## TL;DR {#tldr}

Remaining Count Probes trained on Mistral-7B-Instruct-v0.3 beat their baseline on every dataset they were trained on, but transfer unevenly to other datasets. The OpenThoughts-1k probe generalizes best, beating baseline on 3 of 4 unseen datasets. The Countdown probe generalizes worst despite having the strongest in-distribution fit of the four.

## Intuition {#intuition}

A probe that has truly learned "how many tokens are left" should work no matter which dataset generated the prompt. A probe that has instead memorized one dataset's typical answer lengths will look great on that dataset and fall apart elsewhere — like a delivery-time estimator tuned on one city's traffic that mis-predicts the moment it's asked about a different city.

Cross-dataset evaluation is the test that tells the two apart: train on dataset A, score on datasets A through E, and see whether the drop-off from A to the others looks like generalization or overfitting.

## Mechanics {#mechanics}

A Remaining Count Probe reads the number of output tokens still to be generated from Mistral-7B-Instruct-v0.3's hidden states. The table below reports cross-token MAE for probes trained on one dataset and evaluated on all five, with a per-row median-baseline for comparison [tab_9].

| Train ↓ / Eval → | Count | Countdown | GSM8K | MMLU-Pro | OpenThoughts-1k |
|---|---|---|---|---|---|
| Count | 71.75 | 188.31 | 120.75 | 229.31 | 262.99 |
| Count baseline | 197.45 | 200.48 | 147.94 | 170.32 | 179.64 |
| Countdown | 257.66 | 21.09 | 124.40 | 208.53 | 226.64 |
| Countdown baseline | 197.77 | 200.23 | 158.71 | 172.72 | 179.93 |
| GSM8K | 247.25 | 277.57 | 60.93 | 142.28 | 170.10 |
| GSM8K baseline | 228.80 | 236.82 | 91.67 | 187.53 | 215.33 |
| OpenThoughts-1k | 181.93 | 219.30 | 139.60 | 128.60 | 132.99 |
| OpenThoughts-1k baseline | 197.54 | 200.27 | 153.61 | 171.51 | 179.71 [tab_9] |

Bold-diagonal reading: rows and columns with the same name are the in-distribution cell for that probe [tab_9].

MMLU-Pro appears only as an eval column here: Mistral was evaluated on it but never supplied a matching train split, so it has no row and no diagonal cell [tab_9].

On its own training distribution, every probe beats its baseline. Count falls from 197.45 to 71.75 MAE (63.7% lower), GSM8K from 91.67 to 60.93 (33.5% lower), and OpenThoughts-1k from 179.71 to 132.99 (26.0% lower) [tab_9].

Countdown's own-distribution MAE is the lowest in the table, 21.09 against a 200.23 baseline (89.5% lower) — the strongest in-distribution fit of the four trained probes [tab_9].

Off-distribution, the ranking reverses. The OpenThoughts-1k probe beats its baseline on 3 of its 4 off-diagonal evals — Count, GSM8K, MMLU-Pro — losing only on Countdown, the best generalization record of the four trained probes [tab_9].

**Countdown generalizes worst:** trained on Countdown, the probe beats baseline on only 1 of 4 off-diagonal evals (GSM8K). Evaluated on Count it scores 257.66 against a 197.77 baseline, 30.3% worse, and far above its own 21.09 in-distribution MAE [tab_9].

## The Math {#the-math}

The baseline is not one fixed number. Each train row fits its own median-baseline on that split, so the same eval column carries a different baseline depending on which dataset trained the probe. Comparing MAE across rows means comparing against a moving reference, not a shared one [tab_9].

| Train probe | Off-diagonal wins vs. its own baseline | Off-diagonal losses |
|---|---|---|
| Count | 2 of 4 (Countdown, GSM8K) | 2 of 4 (MMLU-Pro, OpenThoughts-1k) |
| Countdown | 1 of 4 (GSM8K) | 3 of 4 (Count, MMLU-Pro, OpenThoughts-1k) |
| GSM8K | 2 of 4 (MMLU-Pro, OpenThoughts-1k) | 2 of 4 (Count, Countdown) |
| OpenThoughts-1k | 3 of 4 (Count, GSM8K, MMLU-Pro) | 1 of 4 (Countdown) [tab_9] |

Win/loss counts compare each off-diagonal cell to the baseline in that same train row [tab_9].

Take the largest single MAE in the grid: the GSM8K-trained probe evaluated on Countdown scores 277.57 against a 236.82 baseline for that row — 40.75 tokens worse, 17.2% above baseline. The same probe in-distribution on GSM8K scores 60.93, a 4.6x smaller error [tab_9].

The largest relative miss is Countdown-trained-on-Count: 257.66 against a 197.77 baseline is 30.3% worse than guessing the median, and 12.2x the probe's own 21.09 in-distribution MAE — a sign the probe fit one dataset's length distribution rather than a general notion of remaining length [tab_9].

## Go Deeper {#go-deeper}

No resources were supplied for this concept.

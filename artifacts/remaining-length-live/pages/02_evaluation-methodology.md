# Evaluation Methodology

## TL;DR {#tldr}

The paper evaluates every regression result with per-token mean absolute error (MAE), reported two ways: as a token-weighted average across all completion positions, and as the error at just the prompt-end position when comparing the Completion Length Probe to its constant baseline [§sec_3_6]. Classification-probe accuracy and Cohen's κ appear only as a secondary ablation [§sec_3_6].

## Intuition {#intuition}

MAE is the natural counterpart to the constant-median baseline: whatever loss you minimize determines what statistic your best constant predictor should output, and minimizing absolute error picks the median, not the mean [S1].

Choosing MAE as the headline metric keeps the comparison to that baseline honest — both are anchored to the same statistic [§sec_3_6].

Because absolute error grows linearly with the size of a mistake while squared error grows quadratically, one badly-predicted token cannot dominate an MAE average the way it would dominate an MSE average [S1].

## Mechanics {#mechanics}

Every regression result is scored with per-token MAE, aggregated as a token-weighted dataset-wide average: each token position across every completion contributes one term to the mean, so longer completions contribute proportionally more terms than shorter ones [§sec_3_6].

When comparing the Completion Length Probe against its constant-median baseline, the paper additionally reports absolute error at the prompt-end position alone, isolating the probe's very first prediction from the average over an entire completion [§sec_3_6].

Classification-probe metrics — accuracy and Cohen's κ — are reported only as a complementary ablation in the appendix, kept secondary because the paper's core claims concern a continuous quantity (remaining length) that a regression metric like MAE is built to score [§sec_3_6].

Beyond the paper's own two MAE variants, evaluation of this kind commonly reports scale-free, percentage-based error to compare per-token error across tokens or sequences of different magnitude, and the full error distribution (median, quantiles) rather than a single scalar, since MAE's optimality guarantee is tied specifically to the median [S1][S3].

## The Math {#the-math}

MAE's headline status rests on a loss-matching argument: minimizing average absolute error over a set of targets is minimized by predicting their median, exactly as minimizing squared error is minimized by predicting their mean [S1]. Five example per-token targets make this concrete.

Take targets $y = [10, 20, 30, 15, 5]$ tokens-remaining. Sorted, $y = [5, 10, 15, 20, 30]$, so the median is 15 and the mean is 16 [S1].

| Constant predictor | Value | Per-token abs. errors | MAE | Per-token sq. errors | MSE |
|---|---|---|---|---|---|
| Median | 15 | 5, 5, 15, 0, 10 | 7.0 | 25, 25, 225, 0, 100 | 75.0 [S1] |
| Mean | 16 | 6, 4, 14, 1, 11 | 7.2 | 36, 16, 196, 1, 121 | 74.0 [S1] |

The median predictor scores lower MAE (7.0 vs. 7.2) while the mean predictor scores lower MSE (74.0 vs. 75.0) — each constant is optimal for exactly the loss it was chosen to minimize, which is why the paper pairs its MAE headline metric with a median, not a mean, baseline [S1] [§sec_3_6].

The same asymmetry sharpens under an outlier: replace the 30 with a heavy outlier of 100, giving $y = [10, 20, 100, 15, 5]$, whose median stays 15 while its mean jumps to 30 [S1].

| Case | Median predictor | MAE | MSE |
|---|---|---|---|
| No outlier: $y=[10,20,30,15,5]$ | 15 | 7.0 | 75.0 [S1] |
| One outlier: $y=[10,20,100,15,5]$ | 15 | 21.0 | 1475.0 [S1] |

Moving one target from 30 to 100 — a 70-token error — triples MAE (7.0 → 21.0) but multiplies MSE by roughly 19.7× (75.0 → 1475.0), because squaring the same 85-token residual amplifies it quadratically while MAE only sums it linearly [S1].

This isn't only an evaluation-time property: in deep vector-to-vector regression settings structurally similar to per-token prediction, MAE-based objectives admit tighter analyzable error bounds than MSE-based ones, part of why the paper treats MAE as a primary evaluation criterion rather than only a training convenience [S2].

## Go Deeper {#go-deeper}

- [RMSE or MAE? Use their natural counterparts](https://doi.org/10.5194/gmdd-7-1525-2014) — the core justification for the choice of MAE over RMSE as the unambiguous measure of average error magnitude; read this first to see why the paper anchors on MAE at all.
- [Mean absolute deviation (Khan Academy)](https://www.khanacademy.org/math/statistics-probability/summarizing-quantitative-data/mean-absolute-deviation/v/mean-absolute-deviation) — a few-minute visual build-up of why the median, not the mean, minimizes the sum of absolute deviations, the fact underlying the worked table above.
- [On Mean Absolute Error for Deep Neural Network Based Vector-to-Vector Regression](https://arxiv.org/abs/2008.07281v1) — analyzes MAE as the training/eval objective for vector-valued neural regression, the same structural setup as per-token prediction, and where the tighter-bound claim above comes from.
- [Using the Mean Absolute Percentage Error for Regression Models](https://arxiv.org/abs/1506.04176v1) — motivates the scale-free percentage-error metric mentioned as a complement to raw MAE for comparing error across tokens or sequences of different magnitude.

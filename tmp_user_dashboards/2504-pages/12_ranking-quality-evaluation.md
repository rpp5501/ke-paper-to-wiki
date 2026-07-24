# Measuring a ranking attack: Kendall's Tau, Spearman's R, and the auxiliary-data baseline

## TL;DR {#tldr}

The disparity inference attack doesn't output predictions, it outputs an ordering of groups by risk, so it has to be graded on how well that ordering matches reality.

Ranking is a different kind of output from a yes/no prediction, so accuracy doesn't apply. The paper scores its disparity inference attack with two standard rank-correlation statistics — Kendall's Tau and Spearman's Rank Correlation — computed against the true vulnerability ordering of groups, and compares against a baseline adversary who has something the paper's threat model deliberately withholds: a full-size auxiliary dataset. The gap between the two is the paper's evidence that angular difference, not brute-force auxiliary data, is doing the real work.

## Intuition {#intuition}

Suppose you rank ten neighborhoods by how likely a scam is to succeed there, and I have the real numbers. How do I check whether your ranking is any good? I can't just subtract your numbers from mine — you never produced numbers, only an order. What I can do is compare *orderings*: for every pair of neighborhoods, did you get the relative order right?

That's the idea behind rank-correlation statistics. Kendall's Tau essentially counts, over every pair of items, how often your ranking agrees with the true ranking versus how often it disagrees, and turns that into a score between −1 and 1. Spearman's Rank Correlation does something similar but works with the rank positions directly, more like an ordinary correlation computed on ranks instead of raw values. Both land at 1 for a perfect match, −1 for an exactly reversed match, and near 0 for something that looks like chance.

The zero point matters more than it sounds like it should. A ranking that scores −1 is not useless — it's perfectly informative, just backwards, and trivially fixable by flipping it. A ranking that scores near 0 is the actual failure case: it means the ranking carries no information about the true order at all. So "how far from zero" is the real measure of quality, not "how close to +1."

This is exactly why the paper's baseline is interesting. Give an adversary a full-size auxiliary dataset with a different distribution from the training data, let them run CSMIA on it, and rank groups by that performance — this baseline scores near zero. It's not merely a weak ranking, it's a ranking that provides essentially no signal, despite having *more* raw data than the paper's own attack, which needs no auxiliary data at all. That contrast is the entire point of the evaluation.

## Mechanics {#mechanics}

**What's being ranked.** The disparity inference attack ranks a dataset's groups by descending angular difference, producing an ordering meant to approximate the true ordering by attack success rate [§sec_5_2]. Ranking quality is evaluated by comparing that predicted ordering to the actual attack-performance ordering measured directly (with ground-truth sensitive values available only for evaluation, not to the attacker) [§sec_6_3].

**The two metrics.** The paper uses Kendall's Tau and Spearman's Rank Correlation, chosen for their robustness to outliers and their extensive use across scientific domains, both ranging from −1 to 1 [§sec_6_3]. Values near 0 indicate a poor ranking; values far from 0 in either direction indicate a good one, since a negative score still implies the relative order carries information, just reversed [§sec_6_3].

**The baseline it's compared against.** The paper considers an adversary who possesses a full-size auxiliary dataset with the same size as the training dataset but a different distribution — obtained by randomly sampling from the full versions of Census19 and Texas-100X — and who ranks groups by running CSMIA on that auxiliary data and measuring attack performance there [§sec_6_3]. This baseline is deliberately given more raw material than the paper's own attack (a same-size labeled dataset versus zero auxiliary data), which makes it a meaningful point of comparison rather than a strawman.

**The results.** On Census19, the disparity inference attack reaches Kendall's Tau of 0.6914 for CSMIA and 0.7579 for LOMIA, and Spearman's R of 0.8767 and 0.9104 respectively, with p-values as small as 7.23e-17 [§sec_6_3]. The baseline scores near zero on both metrics (e.g. −0.0759 Kendall's Tau for CSMIA) with p-values around 0.4, meaning the null hypothesis of no correlation cannot be rejected [§sec_6_3]. On Texas-100X the disparity inference attack's scores are strongly *negative* rather than positive (−0.7778 Kendall's Tau, −0.9273 Spearman's R for CSMIA), which — per the interpretation above — still counts as a strong, informative ranking, just one where higher angular difference corresponds to lower rather than higher vulnerability in that dataset's labeling convention; the baseline again sits far closer to zero [§sec_6_3].

## The Math {#the-math}

The paper does not restate the formal definitions of Kendall's Tau or Spearman's Rank Correlation — it cites the original sources (Kendall, 1938; Spearman, 1904) and reports the computed values directly [§sec_6_3]. For completeness, and without attributing the derivation to this paper: given a predicted ranking and a true ranking over \(k\) items, Kendall's Tau counts concordant and discordant pairs,

$$
\tau \;=\; \frac{(\text{concordant pairs}) - (\text{discordant pairs})}{\tfrac{1}{2}k(k-1)}
$$

while Spearman's Rank Correlation is the ordinary Pearson correlation computed on the rank values themselves rather than the raw measurements. Both statistics are reported by the paper alongside a p-value against the null hypothesis of no association between the predicted and true rankings; the extremely low p-values for the disparity inference attack (as small as 1.12e-04 to 5.06e-20 depending on dataset and metric) are what let the paper claim the ranking quality is not attributable to chance [§sec_6_3].

## Go Deeper {#go-deeper}

- **[§sec_6_3] Disparity Inference Attack Performance** — the full results table with both metrics, both datasets, both underlying attacks (CSMIA and LOMIA), and the baseline comparison.
- **[§sec_5_2] Disparity Inference Attack** — defines what the ranking is trying to approximate, and why the true per-group attack success rate is something the adversary cannot access directly.
- **[§sec_6_1] Experimental Setup** — describes how the 51 Census19 groups (by state) and 10 Texas-100X groups (by diagnosis code) were assigned distinct correlation levels to create a real spread of vulnerability to rank.
- Related concepts: `disparity-inference-attack` for the attack whose output is being scored here, `angular-difference` for the black-box quantity used as the ranking key, and `correlation-controlled-sampling` for how the graded groups were constructed with known-different correlations in the first place.

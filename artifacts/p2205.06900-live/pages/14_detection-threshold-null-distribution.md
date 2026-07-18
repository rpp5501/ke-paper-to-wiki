# Detection Threshold via Null Distribution
## TL;DR {#tldr}
This concept is the decision rule that turns MM-BD's per-class maximum-margin scores into a yes/no backdoor call: it fits a statistical "null" distribution from the scores of all-but-the-largest class, then checks whether the largest score is too extreme to have come from that same distribution. If it is, the model is flagged as backdoored and the outlier class is named as the attack target.

## Intuition {#intuition}
Think of every class as submitting one number describing "how easily can inputs be pushed to be classified as me with minimal effort." Most classes should produce similar, unremarkable numbers. A backdoored target class, however, has a hidden shortcut (the trigger) that makes it suspiciously easy to reach, so its number should stand out from the crowd. Rather than pick an arbitrary cutoff by hand, this step lets the other classes' numbers define what "normal" looks like, and then asks whether the top scorer is a believable member of that normal group or a statistical outlier — the same logic as spotting the one outlier in a set of test scores by seeing how far it sits from the rest of the class average.

## Mechanics {#mechanics}
The procedure first requires an estimation step: for every putative target class, gradient ascent with projection is run to solve an optimization problem that yields that class's maximum-margin (MM) statistic, using multiple random initializations and keeping the best solution to guard against local optima [§sec_3_2]. This per-class optimization is independent of any presumed backdoor pattern type and does not require clean samples from every non-target class, which is why the method remains valid even when a backdoor attack has only a small or arbitrary set of source classes — a scenario where reverse-engineering-based detectors (REDs) that rely on presumed embedding functions or on clean samples from all non-target classes can fail [§sec_3_2].

Once every class has an MM statistic, the largest of these is set aside as the candidate anomaly, and a null distribution is estimated from all the remaining (non-largest) statistics [§sec_3_2]. Because the MM statistic is strictly positive both in theory and empirically, this null is modeled with a single-tailed density, such as a Gamma distribution, rather than a two-sided form [§sec_3_2]. The atypicality of the held-out largest statistic is then quantified as an order-statistic p-value under this fitted null, and a detection is declared when that p-value falls below a chosen confidence level such as the classical 0.05, with the corresponding class inferred as the backdoor target [§sec_3_2].

This generalizes an older, simpler thresholding rule used in Neural Cleanse, which assumes an approximately normal/Laplacian null and flags a class once its anomaly statistic exceeds median + k·MAD, with the MAD scaled by 1.4826 for consistency under normality and k calibrated to roughly 2 for a target false-positive rate [S2]. Because MM-BD instead fits the null empirically from the other classes' own statistics rather than assuming a fixed symmetric shape, controlling the false-positive rate still requires setting the tail probability against that fitted null and accounting for the fact that every class is being tested simultaneously, analogous to a multiple-comparisons correction [S2][S3]. This leave-one-out null estimation is also more fragile when there are only a handful of classes to draw from (e.g., 9 leave-out statistics for CIFAR-10) than when hundreds are available (e.g., ImageNet), so the exact calibration behavior is dataset-dependent [S1].

## The Math {#the-math}
The per-class MM statistic used as input to the null-distribution test is obtained by solving the following maximization over the input domain [eq_2]:

$$
\maximize_{{\bf x}\in{\mathcal X}} \quad g_c({\bf x}) - \max_{k\in{\mathcal Y}\setminus c} g_{k}({\bf x})
$$ [eq_2]

Given the estimated null $H_0$ fit from the non-largest statistics and the largest observed statistic $r_{\rm max}$ (associated with the suspected target class), the detection p-value is computed as an order statistic over the $K$ classes in the domain [eq_3]:

$$
{\rm pv}=1-H_0(r_{\rm max})^{K-1},
$$ [eq_3]

which, under the null hypothesis of no attack, is shown to follow a uniform distribution on $[0,1]$, making the confidence-level threshold (e.g., flagging when ${\rm pv} \le 0.05$) directly interpretable as a false-positive rate [§sec_3_2].

## Go Deeper {#go-deeper}
- **MM-BD (arXiv:2205.06900)** — the primary source defining the MM statistic, the leave-one-out null estimation, and the order-statistic p-value threshold described above. https://arxiv.org/abs/2205.06900
- **Neural Cleanse (Wang et al., IEEE S&P 2019)** — the earlier MAD-based anomaly-index rule (median + k·MAD) that this null-distribution approach builds on and generalizes. https://people.cs.uchicago.edu/~ravenben/publications/pdf/backdoor-sp19.pdf
- **Median absolute deviation (Wikipedia)** — background on the MAD statistic and the 1.4826 consistency constant referenced when comparing thresholding schemes. https://en.wikipedia.org/wiki/Median_absolute_deviation

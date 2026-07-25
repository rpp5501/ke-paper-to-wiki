# The payoff: accuracy rises as the attack budget shrinks

## TL;DR {#tldr}

Attacking only the riskiest slice of a dataset makes attribute inference noticeably more accurate than attacking everyone, and the smaller the slice, the bigger the accuracy edge.

This page reports what happens when the disparity ranking from earlier is actually used to aim an attack. On Census19, single-attribute targeted CSMIA rises from 62.56% (untargeted) to 73.27% at a budget of 0.05, and LOMIA rises from 61.24% to 73.78%. The paper describes these as gains of "17.12%" and "20.48%" — those are *relative* percentages computed against the untargeted baseline, not additional percentage points, and this page states the raw before/after numbers first so the relative figures can't be misread as absolute accuracy jumps.

## Intuition {#intuition}

A metal detector that beeps for 6 out of every 10 people walking through an airport isn't impressive. But if you learn it beeps for 9 out of 10 people wearing a specific shoe brand and 3 out of 10 everyone else, you don't need a better detector — you just need to only check people wearing that shoe brand. Your hit rate on the people you actually bother to check goes way up, even though the detector itself never changed.

That is the entire mechanism behind targeted attribute inference. The untargeted accuracy numbers reported earlier in the paper — 62.56% for CSMIA, 61.24% for LOMIA on Census19 — are averages across every group, mixing highly vulnerable groups with barely-vulnerable ones. The targeted attacks don't improve the underlying attack algorithm at all; CSMIA is still CSMIA, LOMIA is still LOMIA. What changes is which records get attacked. As the attack budget shrinks — meaning the adversary insists on attacking only a smaller and smaller fraction of the dataset — the selection process can afford to be pickier, and it picks the groups the angular-difference ranking says are most exposed. Accuracy on that shrinking, increasingly curated subset climbs steadily.

The nested version pushes this further by intersecting several attributes' risky segments at once — risky occupation *and* risky state, for instance — carving out an even smaller, even more exposed target set. On Texas-100X, nesting five attributes at a very small budget (0.01) drives both CSMIA and LOMIA to 100% accuracy. That number is real, but it needs a caveat attached: at a 0.01 budget the target set is a sliver of the data, so a perfect score there says the sliver was chosen extremely well, not that the attack has become perfect in general.

## Mechanics {#mechanics}

**Move 1 — single-attribute results, Census19.** CSMIA accuracy across budgets \(\kappa = 1, 0.75, 0.5, 0.375, 0.25, 0.1, 0.05\) is 62.56%, 64.73%, 67.43%, 69.02%, 70.42%, 72.54%, 73.27%. LOMIA over the same budgets is 61.24%, 63.71%, 67.56%, 69.45%, 70.82%, 72.92%, 73.78%. Both rise monotonically (with only minor noise) as the budget shrinks [§sec_6_4].

**Move 2 — single-attribute results, other datasets.** On Texas-100X, CSMIA moves from 60.95% (\(\kappa=1\)) to 62.82% (\(\kappa=0.1\)); LOMIA moves from 61.50% to 69.68% over the same range. On Adult, CSMIA moves from 69.96% to 81.61%, and LOMIA from 70.61% to 81.68%, both at \(\kappa=0.1\) [§sec_6_4]. The paper summarizes these three datasets' CSMIA gains as 17.12%, 5.65%, and 16.66% respectively, and the LOMIA gains as 20.48%, 13.31%, and 15.68% — all computed relative to the untargeted baseline [§sec_6_4].

**Move 3 — nested attribute results push further.** Intersecting the above-average-risk segments of multiple attributes narrows the target set faster than a single attribute can. On Census19, nested CSMIA reaches 69.36% and LOMIA reaches 70.26% at depth 4 (\(\kappa=0.1\)), both above their single-attribute counterparts at the same budget. On Adult, nested CSMIA and LOMIA reach 86.74% and 86.77% at depth 4 (\(\kappa=0.1\)). On Texas-100X, both reach 100.00% at depth 5 (\(\kappa=0.01\)) [§sec_6_4].

**Move 4 — the trend is attack-specific, not budget-specific.** The practical imputation baseline (ImpP) does not show this improving trend as the budget shrinks — confirming that a targeted imputation attack gains nothing from an adversary with a distribution-mismatched auxiliary dataset. The ideal imputation baseline (ImpI) does improve with a shrinking budget, but more slowly than CSMIA or LOMIA, which the paper attributes to group-level attack success on ImpI's auxiliary data correlating imperfectly with success on the real data [§sec_6_4].

**Move 5 — architecture doesn't matter.** Repeating the targeted attacks on MLPs with 2, 3, and 4 hidden layers produces essentially the same accuracy-vs-budget pattern at each depth, indicating that the vulnerability being exploited lives in what the training data taught the model, not in how deep the model is [§sec_6_4].

## The Math {#the-math}

The paper's headline percentages are relative gains, computed against the untargeted (\(\kappa=1\)) accuracy as baseline:

$$
\text{relative gain} = \frac{ASR(\kappa_{\min}) - ASR(\kappa=1)}{ASR(\kappa=1)} \times 100\%
$$

Plugging in the Census19 CSMIA numbers, \(ASR(\kappa=1) = 62.56\) and \(ASR(\kappa=0.05) = 73.27\):

$$
\frac{73.27 - 62.56}{62.56} \times 100\% \approx 17.12\%
$$

which matches the paper's reported figure. The same formula on the LOMIA numbers, \(61.24 \to 73.78\), gives

$$
\frac{73.78 - 61.24}{61.24} \times 100\% \approx 20.48\%
$$

again matching exactly [§sec_6_4]. The formula is arithmetic, not a new claim by this page — it just makes explicit what the paper's percentages mean, so they aren't mistaken for absolute accuracy-point increases (a 17.12-point jump from 62.56% would be 79.68%, which is not what happened).

## Go Deeper {#go-deeper}

- **[§sec_6_4] Targeted Attribute Inference Attack** — the full results tables for single-attribute and nested attacks across Census19, Texas-100X, and Adult, plus the MLP-depth robustness check.
- **[§sec_5_3_1] Single Attribute-based Targeted Attack** — the mechanism producing the single-attribute numbers on this page.
- **[§sec_5_3_2] Nested Attribute-based Targeted Attack** — the mechanism producing the nested numbers, including why depth increases as the budget shrinks.
- **[§sec_6_2] Ideal vs. Practical Imputation Attacks** — explains why ImpP fails to show this trend while ImpI shows a weaker version of it.
- Related concepts: `single-attribute-targeted-attack` and `nested-attribute-targeted-attack` for the attack mechanics behind these numbers, and `targeted-attack-objective-and-budget` for the formal budget constraint \(\kappa\) that this page's tables sweep across.

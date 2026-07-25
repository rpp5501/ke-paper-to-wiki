# ASRD: measuring disparity as a spread in attack success rate

## TL;DR {#tldr}

ASRD scores how unfair a privacy attack is by measuring the gap between its best-case and worst-case success rate across groups.

Once you accept that averaging attack success across a whole dataset hides disparity, you need a number that captures the disparity itself rather than papering over it. ASRD (Attack Success Rate Difference) is that number: for a chosen way of splitting the dataset into groups, it's simply the highest group-level attack success rate minus the lowest. It's the metric the paper uses to state, evaluate, and eventually try to shrink disparity — including as the target that the BCorr defense is explicitly built to minimize.

## Intuition {#intuition}

Imagine two hospitals report the same overall complication rate, 8%. One hospital's rate is a flat 8% across every patient group. The other's is 25% for one group and 1% for another, averaging out to the same 8%. Those are not the same hospital, and a single averaged number can't tell you which one you're looking at.

ASRD is built to answer exactly this question for privacy attacks. Pick an attribute to split the dataset by — gender, occupation, state, whatever the analyst cares about — and measure the attack's success rate separately within each resulting group. ASRD is the distance between the most-attacked group and the least-attacked group. A model with ASRD near zero treats every group roughly the same, for better or worse. A model with a large ASRD is hiding a serious problem behind whatever number gets reported for the dataset as a whole.

The reason this needs its own metric, rather than reusing fairness metrics like equalized odds or demographic parity, is that those measure disparities in *model performance* — whether the model is equally accurate or equally likely to predict positively for different groups. ASRD measures disparities in *how easily an attacker can extract secrets* from different groups, which is a related but genuinely different quantity: two groups can have identical model accuracy and wildly different privacy vulnerability, because vulnerability tracks correlation between the sensitive attribute and the output, not predictive performance [§sec_13_1].

ASRD plays two roles in the paper. First, it's a diagnostic: applied to the undefended model, it quantifies exactly how bad the disparity problem is. Second, it's an optimization target: the BCorr defense is judged by how much it can drive ASRD down without destroying the model's overall usefulness.

## Mechanics {#mechanics}

**What it measures.** ASRD is defined for a model \(\mathcal{M}\) trained on \(\mathbb{D}\), a chosen non-sensitive grouping attribute \(a\) (such as sex or state), and an attack algorithm \(\mathcal{A}\): compute the attack success rate within each group the attribute defines, then take the maximum minus the minimum across groups [§sec_7_2].

**Why fairness metrics don't substitute for it.** The paper is explicit that existing fairness work focuses on equalizing model *performance* across groups, while ASRD parallels those metrics conceptually but targets disparities in *attacker* success rate instead — a genuinely different axis, since a group's model accuracy and its privacy vulnerability are shown to be uncorrelated at the group level in the paper's own data [§sec_13_1], which is also why fairness-constraint defenses fail to reduce ASRD even when they succeed at their own stated goal.

**How it's used to grade defenses.** For binary attributes (SEX in Census19, SEXCODE in Texas-100X), the undefended model shows ASRD of 12.52 (CSMIA) and 14.97 (LOMIA) on Census19, and 12.12/14.45 on Texas-100X; BCorr drives these down to 2.06/3.59 and 0.94/2.48 respectively, while a Fairness Constraint baseline (FC) only reaches 11.45/11.90 and 11.45/13.28 — barely moving the needle [§sec_7_2]. For multi-valued attributes (51 Census19 states, 10 Texas-100X diagnosis groups), ASRD starts far higher (22.94/26.75 and 17.27/20.54) and BCorr still achieves a substantial reduction, though the paper notes explicitly that shrinking ASRD across 51 groups is much harder than across 2 [§sec_7_2].

**A caution the paper builds in.** ASRD alone can be gamed by degrading the model until every group performs equally badly against both the model and the attacker. The paper guards against this reading by always reporting model accuracy (MA) alongside ASRD: BCorr's headline result is that it drives ASRD down to near zero on binary attributes *while* model accuracy stays essentially flat (73.21% to 73.89% for Male group accuracy on Census19, for instance) [§sec_7_2] — so the reduction in disparity is not a side effect of destroying utility for everyone.

## The Math {#the-math}

For a grouping attribute \(a\) that partitions the dataset into groups \(\mathbb{D}_1, \ldots, \mathbb{D}_k\), with \(ASR_i = ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}_i), \mathcal{A})\) denoting the attack success rate measured on group \(i\), ASRD is defined as

$$
ASRD(\mathcal{M}, \mathbb{D}, a, \mathcal{A}) \;=\; \max_i \, ASR_i \;-\; \min_j \, ASR_j
$$

[§sec_7_2]. This is a single scalar per (model, attribute, attack) triple — it collapses the whole vector of group-level success rates down to the width of its spread, discarding information about how many groups are near the top versus the bottom. That's a deliberate simplification: it makes ASRD directly comparable to how the paper's own definition of disparate vulnerability is framed, as an inequality between the success rates of two subsets exceeding a threshold \(\varepsilon\) [§sec_2] — ASRD is exactly the largest such gap achievable by any two groups under the chosen partition \(a\).

Because the max and min are taken over whichever groups the partition \(a\) happens to produce, ASRD is not an intrinsic property of the model alone — it depends on the choice of grouping attribute, and a defense that lowers ASRD for one attribute is not guaranteed to lower it for another, though the paper argues via the Berkeley-admissions-style example that reducing disparity in a correlation-driving attribute (e.g. occupation) is likely to also reduce it in a correlated demographic attribute (e.g. gender) that shares the same underlying cause [§sec_7_2].

## Go Deeper {#go-deeper}

- **[§sec_7_2] Balanced Correlation Defense (BCorr)** — where ASRD is defined and where it's used as the primary metric to evaluate BCorr against the Fairness Constraint baseline.
- **[§sec_2] Preliminaries** — the formal definition of disparate vulnerability that ASRD operationalizes into a single number.
- **[§sec_13_1] Model Utility vs. Vulnerability at Group Level** — the evidence that group-level model accuracy and group-level vulnerability are uncorrelated, which is the reason fairness metrics can't stand in for ASRD.
- **[§sec_7_1] Disparity-Aware Mutual Information Regularization (DAMIR)** — a defense evaluated with the same ASRD metric, showing a far weaker reduction than BCorr achieves.
- Related concepts: `bcorr-defense` for the mitigation ASRD is built to evaluate, `disparate-vulnerability` for the underlying phenomenon, and `damir-defense` for a contrasting defense that ASRD exposes as insufficient.

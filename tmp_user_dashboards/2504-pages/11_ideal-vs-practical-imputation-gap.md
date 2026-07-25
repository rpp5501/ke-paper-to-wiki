# Ideal vs practical imputation: why the baseline collapses under drift

## TL;DR {#tldr}

An imputation attack that never queries the model can look scary in a lab test, but only if its outside data matches the target data almost exactly — which a real attacker can't arrange.

Prior work compared attribute inference attacks against imputation attacks and found imputation usually won, concluding that querying the model wasn't buying an adversary much. This paper shows that comparison silently assumed an "ideal" imputation attacker whose auxiliary dataset shares the training data's statistics down to the group level. Once the auxiliary data drifts even slightly from that — at the dataset level or, more damagingly, at the group level — imputation's advantage evaporates, and the attacks that actually query the model (CSMIA, LOMIA) pull ahead in the groups that matter most.

## Intuition {#intuition}

Imagine two students preparing for the same exam. One (the AI attacker) sits in the actual classroom and pays close attention to what the teacher emphasizes — a slow process, but the intel is guaranteed current. The other (the imputation attacker) skips class and instead studies an old copy of the textbook they found — faster, since they never have to interact with the teacher, but only useful if that textbook happens to match this year's material.

"Ideal" imputation is the scenario where the old textbook happens to be identical to this year's syllabus, chapter for chapter. Under that assumption, the imputation student does great without ever showing up to class — which is exactly the comparison prior work made, and exactly why it concluded that going to class (querying the model) wasn't worth much.

"Practical" imputation is what happens when the textbook is close but not identical — a slightly different edition, or one written for a different school entirely. The paper runs this experiment two ways. First, it skews the overall balance of the outside data away from the training data's balance and watches imputation's accuracy fall as the skew grows. Second — and this is the sharper result — it keeps the outside data's *overall* statistics matched to the training data, but lets the statistics *within specific groups* drift, because that is what a real auxiliary dataset actually looks like: right on average, wrong within any given slice. In exactly the groups where that micro-level drift bites hardest — the highly vulnerable groups — the imputation attacker's outside knowledge stops helping, and the attacker who actually queried the model wins instead.

The upshot reframes the earlier "attribute inference is weak" conclusion: it was weak only against an imputation attacker with unrealistically perfect intel. Against the imputation attacker any real adversary could actually build, querying the model is the better move — which is itself evidence of privacy leakage, independent of whether it beats the unrealistic ideal.

## Mechanics {#mechanics}

**Move 1 — define the two imputation attackers.** An ideal imputation attack assumes the adversary's auxiliary dataset precisely matches the target distribution, including group-level properties like correlation and marginal priors. A practical imputation attack uses auxiliary data that differs from the target distribution, whether at the whole-dataset (macro) level or within specific subsets (micro) level — which is what any adversary external to the data owner would actually be stuck with [§sec_6_2].

**Move 2 — dataset-level drift.** On the Adult dataset, the paper varies the auxiliary set's marginal prior (fraction of positive-class samples) from 0.5 down to 0.1, away from the training data's true marginal prior of 0.52, across auxiliary set sizes from 100 to 5,000 records. Performance declines as the marginal prior deviates further from the true value; when the deviation is largest, imputation falls below both CSMIA (69.97%) and LOMIA (70.61%) regardless of how much auxiliary data is used. Imputation only beats CSMIA and LOMIA when its marginal prior is close to the true one [§sec_6_2].

**Move 3 — group-level drift, the sharper test.** Here the auxiliary dataset's *overall* correlation is set to -0.44, matching the training data's dataset-level correlation of -0.4412 almost exactly — so a macro-level check would call this auxiliary data a good match. But the training data's actual group-level correlations, computed by occupation, range from -0.17 to -0.55: the "average" auxiliary dataset misrepresents almost every individual group. Run against the five occupation groups with above-average correlation, CSMIA and LOMIA outperform the practical imputation attack in three of the five, while the ideal imputation attack (which does have correct group-level statistics) tracks CSMIA and LOMIA closely in two of those three [§sec_6_2].

**Move 4 — the reframing.** Practical imputation, the only version a real adversary can build, tends to underperform relative to attacks that simply query the model — even though the imputation attacker holds an auxiliary dataset the AI attacker doesn't have at all. The paper's conclusion is that practical imputation attacks are the correct baseline for evaluating attribute inference, while ideal imputation attacks are better understood as an upper-bound benchmark rather than a realistic competitor [§sec_6_2]. This directly undercuts the "attribute inference is weak" reading of prior evaluations, and it foreshadows a pattern seen again later: only the ideal-imputation baseline (ImpI) improves as a targeted attack's budget shrinks, while the practical baseline (ImpP) does not [§sec_6_4].

## The Math {#the-math}

This section of the paper is evidentiary rather than derivational — the gap between ideal and practical imputation is established with sweep tables and group-level comparisons, not a closed-form expression. The two quantities being compared are worth stating precisely, though.

Dataset-level marginal prior is the fraction of positive-class records in a dataset \(X\):

$$
p(X) = \frac{|\{x \in X : y(x) = 1\}|}{|X|}
$$

The paper's macro-drift experiment varies \(p(D_{aux})\) away from \(p(\mathbb{D}_{train}) = 0.52\) [§sec_6_2].

Group-level correlation is Pearson's correlation between the sensitive attribute and output, computed separately within each group \(\mathbb{D}_g\) defined by a grouping attribute (here, occupation):

$$
c_g = \operatorname{corr}\big(s(x),\, y(x)\big) \quad \text{for } x \in \mathbb{D}_g
$$

The paper's finding is that an auxiliary dataset can match \(\bar{c} = \frac{1}{|G|}\sum_g c_g \approx -0.44\) at the dataset level while every individual \(c_g\) sits far from that average — the reported range is \([-0.55, -0.17]\) — and it is this per-group mismatch, not the dataset-level number, that determines where practical imputation fails [§sec_6_2].

## Go Deeper {#go-deeper}

- **[§sec_6_2] Ideal vs. Practical Imputation Attacks** — the source for everything on this page: both experiments, both figures, and the reframing of practical imputation as the correct baseline.
- **[§sec_6_4] Targeted Attribute Inference Attack** — where this distinction resurfaces: ImpI improves with a shrinking attack budget, ImpP does not, mirroring the ideal/practical gap shown here.
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — establishes why group-level correlation, not dataset-level correlation, is the quantity that actually predicts vulnerability, which is exactly what this page's group-drift experiment exploits.
- Related concepts: `imputation-attack-baseline` for the original attack this page complicates, `correlation-drives-vulnerability` for why group-level statistics are the ones that matter, and `targeted-attack-performance-gains` for where the ideal/practical asymmetry shows up again.

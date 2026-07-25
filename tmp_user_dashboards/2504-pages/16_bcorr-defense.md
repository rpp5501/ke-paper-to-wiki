# Balanced Correlation Defense: equalize the cause, not the symptom

## TL;DR {#tldr}

Instead of hiding a model's confidence scores or suppressing predictions, this defense resamples training data so every group has the same weak correlation as the least-correlated group — closing the gap at its root.

BCorr (Balanced Correlation Defense) targets the disparity between groups directly, not the average attack accuracy. It works by finding the group with the lowest sensitive-attribute-to-output correlation, then downsampling every other group's records until its correlation matches that floor. The resulting balanced dataset trains a model where no group is more correlated — and therefore no group is more attackable — than any other. On Census19, this drives the attack-success-rate gap between the most and least vulnerable groups from 12.52 down to 2.06 for CSMIA, without hurting model accuracy or fairness metrics.

## Intuition {#intuition}

Suppose a hospital's records show that nurses are disproportionately female, and that "nurse" happens to be an occupation the model has learned to predict very confidently — which, per this paper's earlier finding, makes nurses an easy target for attribute inference. Women aren't inherently more vulnerable as a group; they are just overrepresented in a highly-correlated occupation. That is structurally the same pattern behind the UC Berkeley admissions paradox, where women faced higher overall rejection rates but were *favored* within individual departments — the aggregate story and the group-level story pointed in opposite directions because of how people were distributed across departments.

Given that picture, there are two very different ways to respond. One is to try to make the model perform worse at attribute inference across the board — add noise, regularize, obscure confidence scores. The paper already investigated a version of this (DAMIR, adapting mutual information regularization to focus on vulnerable groups) and found it could only close the gap by sacrificing a large amount of model accuracy, and even then only inconsistently.

BCorr takes the other route: since the paper has already established that correlation between the sensitive attribute and the output is *the* driver of vulnerability, the fix is to make that correlation the same everywhere. Rather than fighting the symptom (confident, accurate attacks on vulnerable groups) the defense removes the cause (those groups having disproportionately strong correlation in the first place) by resampling — throwing out just enough records from each group so its correlation drops to match the group that was already least correlated. No group ends up more correlated than the floor, so no group ends up more attackable than the floor.

The intuition that this doesn't wreck other groups matters too: lowering the correlation within the "nurse" occupation group also lowers the correlation within the female subset of nurses, so a defense applied along one attribute (occupation) tends to help related groups defined by a different attribute (gender) rather than leaving them exposed.

## Mechanics {#mechanics}

**Objective.** BCorr aims to reduce ASRD (Attack Success Rate Difference) — the gap between the most and least vulnerable group's attack success rate under a chosen grouping attribute — while preserving the target model's task accuracy [§sec_7_2].

**Defender's threat model.** Unlike the adversary elsewhere in the paper, the defender is assumed to have full access to the dataset and the trained model, and to already know which groups are more vulnerable — a realistic assumption, since the defender can simulate attacks and directly compute correlations per group using data it already owns [§sec_7_2].

**Design steps.** First, rank the groups defined by grouping attribute \(a\) by their correlation between the sensitive attribute and the output. Let \(c_m\) be the lowest correlation among these groups. Second, for every other group \(D_i\), sample a subset \(D_i'\) whose correlation equals \(c_m\); the group that already had the lowest correlation, \(D_m\), needs no resampling (\(D_m' = D_m\)). The union \(D' = D_1' \cup D_2' \cup \cdots \cup D_k'\) becomes the training set for a new model \(M'\) [§sec_7_2].

**Results — binary attribute case.** On both Census19 (SEX) and Texas-100X (SEX_CODE), BCorr essentially eliminates disparity between Male and Female groups without sacrificing model accuracy or fairness metrics, despite training on only 66.67% of the original data. A Fairness Constraint baseline (Exponentiated Gradient with Equalized Odds), by contrast, fails to meaningfully reduce disparity in either dataset, even though it does preserve fairness metrics [§sec_7_2].

**Results — multi-valued attribute case.** For the harder setting — 51 State groups on Census19, 10 PAT_STATUS groups on Texas-100X — BCorr substantially reduces disparity, lowering the most vulnerable group's attack success rate from 73.8% to 62.92% (Census19, CSMIA) and from 72.59% to 59.07% (Texas-100X, CSMIA). The paper notes this is a harder problem than the two-group case, since equalizing 51 groups leaves much less room to maneuver than equalizing 2 [§sec_7_2].

**Robustness.** BCorr's effectiveness does not depend on model architecture — ASRD stays low across MLPs with 2, 3, and 4 hidden layers, because the defense operates at the dataset level, before any particular model is trained on it [§sec_7_2].

**Why it isn't just a fairness technique.** Standard fairness metrics (equalized odds, demographic parity) are about equalizing model *performance* across groups. BCorr's target is different: it equalizes attack *success rate* across groups, which is why the paper introduces ASRD as a distinct metric rather than reusing existing fairness measures — and why BCorr can succeed at its actual goal even where a fairness-only defense (FC) fails [§sec_7_2].

## The Math {#the-math}

The defense itself is a resampling procedure, run by a defender who owns the data and can compute true per-group correlations:

```algorithm
title: "Balanced Correlation Defense (BCorr) — equalize the cause, not the symptom"
lines:
  - code: "partition D by grouping attribute a; compute each group's sensitive-output correlation"
    intent: "The defender, unlike the attacker, can measure correlation directly — it owns the training data [§sec_7_2]."
  - code: "c_m = the lowest correlation among the groups"
    intent: "The least-correlated group sets the target: correlations can be lowered by dropping records, not raised."
  - code: "for every other group D_i: sample D_i' ⊂ D_i with correlation c_m"
    intent: "Use the correlation-controlled sampling machinery (the four-cell-count derivation) to hit c_m exactly; D_m itself is kept whole."
  - code: "train M' on D' = D_1' ∪ ... ∪ D_k'"
    intent: "Every group now leaks at the same low rate — the cause of disparity is gone, not masked. On Census19/Texas-100X this eliminates the Male/Female gap while keeping accuracy, on ~67% of the data [§sec_7_2]."
```

BCorr's key advantage over DAMIR (the paper's disparity-aware adaptation of mutual information regularization) is what it targets. DAMIR tries to lower mutual information between the sensitive attribute and the output for the vulnerable group specifically — a symptom-level fix applied during training. In evaluation on a Census19 subset with Male correlation -0.4 and Female correlation -0.1, DAMIR only reduces disparity to a degree, and only with a real cost to model utility; under LOMIA it essentially cannot close the gap without severe utility loss. MIR, its non-disparity-aware ancestor, only reduces disparity at high regularization strength, at the cost of substantial utility [§sec_7_1].

The paper does not provide theoretical guarantees for BCorr's disparity reduction — it notes that bounding attack disparity for non-linear DNNs is inherently hard, given both the non-linearity of the models and the variability of attack strategies. What BCorr offers instead is consistent empirical mitigation across datasets, attributes, and model depths, plus a mechanistic explanation (correlation causes disparity, so equalizing correlation removes the cause) [§sec_7_2]. This page has no dedicated equation of its own beyond the ASRD metric, defined on the `disparate-vulnerability` page; BCorr's contribution is the sampling procedure above, not a new formalism.

## Go Deeper {#go-deeper}

- **[§sec_7_1] Disparity-Aware Mutual Information Regularization (DAMIR)** — the defense BCorr is contrasted against; read this to see what "attacking the symptom" costs in practice.
- **[§sec_7_2] Balanced Correlation Defense (BCorr)** — the full design, threat model, and Table 5/6 results this page summarizes.
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — the earlier result (correlation drives vulnerability) that BCorr's whole design rests on.
- **[§sec_13_1] Model Utility vs. Vulnerability at Group Level** — evidence that group-level vulnerability doesn't track group-level model utility, which is why fairness-only defenses like FC don't transfer to this problem.
- Related concepts: `asrd-metric` for the quantity BCorr minimizes, `correlation-drives-vulnerability` for the causal claim the defense is built on, `damir-defense` for the contrasting approach, `correlation-controlled-sampling` for the sampling machinery BCorr's design step reuses.

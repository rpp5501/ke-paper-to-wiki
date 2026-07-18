# Balanced Correlation Defense (BCorr)

## TL;DR {#tldr}
BCorr is a potential mitigation strategy for disparate privacy vulnerability, sitting alongside other defenses under the broader umbrella of Potential Mitigation Strategies. It works by equalizing correlation levels across groups in the training data, and its concrete workflow is spelled out by the Balanced Correlation Defense Process. It is often discussed in contrast with Disparity-Aware Mutual Information Regularization (DAMIR), an alternative approach to the same disparity problem.

## Intuition {#intuition}
The core idea is simple: if some groups are more vulnerable to attribute inference attacks than others because their data has a stronger statistical link between a sensitive attribute and the model's output, then flattening that link should flatten the vulnerability gap too. Rather than changing the model's training algorithm or adding a fairness penalty, BCorr changes the data itself — it curates a training subset where every group exhibits the same (low) correlation level, so no group is disproportionately "leaking" its sensitive attribute through the model. This makes it a data-centric counterpart to regularization-based ideas like DAMIR.

## Mechanics {#mechanics}
The defense assumes a defender who controls the full dataset and the trained target model, can identify which groups (defined by a non-sensitive grouping attribute) are more vulnerable, and can compute per-group correlation between the sensitive attribute and model output as a proxy for attack risk [§sec_7_2].

The process itself has a fixed sequence: first rank the groups by their correlation level; identify the group with the lowest correlation; then sample records from every other group so that each group's correlation in the sampled subset matches that lowest-correlation group, while the lowest-correlation group's records are kept in full without needing to be sampled; the model is then trained only on this balanced subset [§sec_7_2].

Empirically, this curated subset can be substantially smaller than the original data (about two-thirds of it in the reported experiments) yet still preserve model utility and group fairness while sharply narrowing the gap in attack success rate between groups, including in harder multi-valued attribute settings with many groups rather than just two [§sec_7_2].

A notable side effect illustrated by a nurse/gender example: applying BCorr to the more severely disparate attribute (e.g., occupation) tends to also reduce vulnerability in a correlated attribute (e.g., gender), because balancing correlation within the shared subgroup lowers leakage for both, so the defender does not need to run BCorr redundantly on every attribute [§sec_7_2].

## The Math {#the-math}
The local context describes BCorr's target metric, ASRD (Attack Success Rate Difference), in prose as a function of the target model, the attack algorithm, and group-membership sets, but the source material does not preserve a rendered formula for it — no [eq_N] entries are available in the local context to reproduce verbatim, so no equation block is included here [§sec_7_2].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.

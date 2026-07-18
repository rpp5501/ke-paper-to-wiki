# Potential Mitigation Strategies
## TL;DR {#tldr}
Potential Mitigation Strategies is the defensive counterpart to the paper's Attack Methodology work: having shown that attribute inference attacks succeed disproportionately against certain subgroups (Disparate Privacy Vulnerability), the authors turn to asking how that disparity itself can be reduced. This concept is the umbrella for two concrete proposals, Disparity-Aware Mutual Information Regularization (DAMIR) and Balanced Correlation Defense (BCorr), both introduced as part of this effort.

## Intuition {#intuition}
Most privacy defenses are built and evaluated to shrink an attacker's *average* success rate, not to close the gap between how well an attacker does on one group versus another. A defense can look effective in aggregate while still leaving a minority subgroup far more exposed than the majority — the average simply hides the imbalance. The motivating idea here is to treat that gap as the thing to be minimized directly, rather than treating disparity as an incidental side effect of a generic defense.

## Mechanics {#mechanics}
The starting observation is a gap in existing work: prior literature offers defenses against attribute inference attacks in general, or against disparity in other, unrelated domains, but nothing purpose-built to close disparity gaps specifically for attribute inference [§sec_7]. Dibbo et al. tried repurposing these off-the-shelf techniques — applying disparity-mitigation methods from other domains, or applying standard attribute-inference defenses without any disparity objective — and found both approaches had limited success at actually narrowing the gap between groups [§sec_7]. Motivated by that gap, the section introduces two defensive strategies of the authors' own design: DAMIR, which adapts mutual information regularization to explicitly target disparity, and BCorr, a novel approach centered on balancing correlation across the dataset [§sec_7].

## The Math {#the-math}
The local context for this section is a prose overview of the mitigation strategy landscape and does not itself contain any equations; the formal objectives for DAMIR and BCorr belong to their own concept entries rather than to this umbrella section [§sec_7].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here. For the mechanics behind each strategy, see the dedicated pages for Disparity-Aware Mutual Information Regularization (DAMIR) and Balanced Correlation Defense (BCorr), and for the problem they're designed to address, see Disparate Privacy Vulnerability.

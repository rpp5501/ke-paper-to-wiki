# Null Distribution of Class Margins

## TL;DR {#tldr}
The detector fits a one-sided null distribution to the class margins other than the largest candidate outlier.

## Intuition {#intuition}
If one score is suspiciously high, do not let it teach the reference distribution what normal looks like. MM-BD removes the maximum, then uses the remaining scores as its empirical picture of ordinary class separations.

## Mechanics {#mechanics}
Let $r_{\max}$ be the largest class statistic. MM-BD estimates $H_0$ from the other $K-1$ values and uses a positive-support density such as a Gamma distribution [§sec_1]. This is an unsupervised reference, not a bank of clean models or labeled attack examples [§sec_1].

## The Math {#the-math}
The null fit is evaluated at $r_{\max}$ through its cumulative distribution: $$H_0(r_{\max})=\Pr_{H_0}(R\le r_{\max})$$ [§sec_1]. Larger values of the maximum make $1-H_0(r_{\max})^{K-1}$ smaller, which increases evidence for an attack [§sec_1].

## Go Deeper {#go-deeper}
- Unsupervised Anomaly Inference puts the fit into the full decision rule.
- Order-Statistic p-Value explains the multiple-class correction.
- Empirical Scope and Failure Modes describes small-class-count effects.

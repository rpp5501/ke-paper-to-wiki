# Order-Statistic p-Value

## TL;DR {#tldr}
The p-value corrects for selecting the largest among K class statistics, then compares the result with a significance threshold.

## Intuition {#intuition}
Looking at the tallest building in a city is more surprising when the city has only five buildings than when it has thousands. The exponent in the p-value accounts for the fact that MM-BD deliberately searches across all classes for the maximum.

## Mechanics {#mechanics}
The paper computes the largest statistic, estimates the null from the remaining statistics, and forms an order-statistic p-value [§sec_1]. With $\theta=0.05$, it reports an attack when $p_v<\theta$ and assigns the target label to the class that produced $r_{\max}$ [§sec_1].

## The Math {#the-math}
For $K=|\mathcal{Y}|$, the paper uses $$p_v=1-H_0(r_{\max})^{K-1}$$ [§sec_1]. The associated detection confidence is $1-\theta$ when the p-value falls below $\theta$ [§sec_1].

## Go Deeper {#go-deeper}
- Null Distribution of Class Margins supplies $H_0$.
- Unsupervised Anomaly Inference explains the threshold decision.
- Empirical Scope and Failure Modes records the nominal-versus-observed false-positive issue.

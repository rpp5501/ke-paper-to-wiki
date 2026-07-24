# Unsupervised Anomaly Inference

## TL;DR {#tldr}
MM-BD declares an attack when the largest class margin is too atypical under a one-sided null fit to the remaining class margins.

## Intuition {#intuition}
Suppose a panel of thermometers contains one reading far above the rest. You do not need a labeled example of a faulty thermometer to ask whether that maximum is plausible under the distribution of the other readings.

## Mechanics {#mechanics}
After computing all $r_c$, the method selects $r_{\max}$ and fits $H_0$ using the other $K-1$ statistics. The paper uses a one-sided density such as a Gamma distribution because the estimated margins are positive [§sec_1]. A detection is made when the order-statistic p-value is below $\theta$, with $\theta=0.05$ in the experiments [§sec_1].

## The Math {#the-math}
The p-value is $$p_v=1-H_0(r_{\max})^{K-1}$$ [§sec_1]. Under the no-attack null, the paper states that this order-statistic p-value is uniform on $[0,1]$, so the nominal detection confidence is $1-\theta$ when $p_v<\theta$ [§sec_1].

## Go Deeper {#go-deeper}
- Null Distribution of Class Margins details the leave-one-out fit.
- Order-Statistic p-Value explains the exponent $K-1$.
- Empirical Scope and Failure Modes covers false positives and class imbalance.

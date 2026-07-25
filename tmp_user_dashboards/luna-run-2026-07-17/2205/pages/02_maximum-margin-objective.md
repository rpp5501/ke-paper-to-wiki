# Maximum-Margin Objective

## TL;DR {#tldr}
For every class, MM-BD maximizes the gap between that class's logit and the largest competing logit over valid inputs.

## Intuition {#intuition}
Instead of asking whether a class can shout loudly, ask whether it can shout while silencing the loudest rival. That contest is harder for ordinary neighboring classes and becomes conspicuous when a backdoor target has learned an over-specialized route.

## Mechanics {#mechanics}
The estimation stage solves one optimization problem per class. It uses the full input domain as the search space, performs multiple random starts, and keeps the largest local optimum found for that class [§sec_1]. The resulting $r_c$ values are the only model-derived features needed by the unsupervised detector [§sec_1].

## The Math {#the-math}
The core program is $$\underset{\mathbf{x}\in\mathcal{X}}{\operatorname{maximize}}\;g_c(\mathbf{x})-\max_{k\in\mathcal{Y}\setminus\{c\}}g_k(\mathbf{x})$$ [§sec_1]. Comparing against the maximum rival makes the statistic robust to classes whose logits rise together, a failure mode the paper illustrates for logit-only alternatives [§sec_1].

## Go Deeper {#go-deeper}
- Projected Gradient Estimation explains the numerical solver.
- Null Distribution of Class Margins consumes one statistic per class.
- Order-Statistic p-Value converts the maximum into a decision.

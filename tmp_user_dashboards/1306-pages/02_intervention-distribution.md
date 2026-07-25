# Intervention Distribution

## TL;DR {#tldr}
An intervention distribution is what you predict for an outcome *after forcing* a variable to a value — written $\operatorname{do}(X=x)$ — rather than after merely observing it. SID compares two graphs entirely through the intervention distributions they predict.

## Intuition {#intuition}
Observing that people who take a drug recover faster is not the same as making everyone take the drug. Conditioning on "took the drug" mixes in the reasons people chose it; intervening cuts those reasons away. The $\operatorname{do}$ operator is the paper's formal way of saying "reach in and set the knob, ignoring why it was where it was."

This matters because the point of a causal graph is to answer intervention questions. So the right way to ask whether two graphs are "the same" is to ask whether they answer every such question the same way.

## Mechanics {#mechanics}
Under a DAG $\mathcal{G}$, intervening on $X$ deletes the arrows into $X$ and replaces the rest of the factorization by adjusting for $X$'s parents. If $X$ has no parents the intervention distribution is just the marginal; otherwise you average over the parent set [§sec_1_2].

Because the adjustment set is read directly off the graph, two graphs that assign $X$ different parents will generally disagree about the effect of $\operatorname{do}(X=x)$ [§sec_1_2].

## The Math {#the-math}
When the intervened node has no parents, the graph predicts

$$ p_{\mathcal{G}}\!\left(y \mid \operatorname{do}(X=\hat{x})\right) = p(y). $$

With parents, the prediction is the parent-adjustment (truncated factorization) formula

$$ p_{\mathcal{G}}\!\left(y \mid \operatorname{do}(X=\hat{x})\right) = \sum_{\operatorname{pa}(X)} p\!\left(y \mid \hat{x},\, \operatorname{pa}(X)\right)\, p\!\left(\operatorname{pa}(X)\right). $$

These two cases [eq_2] and [eq_3] are exactly the quantities SID checks for agreement across all ordered pairs [§sec_1_2].

## Go Deeper {#go-deeper}
- Parent Adjustment explains *why* conditioning on the parents is a valid adjustment set.
- The linear-Gaussian appendix shows how to compute these effects in closed form [§sec_11].

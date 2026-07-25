# Parent Adjustment

## TL;DR {#tldr}
The adjustment formula that averages an outcome conditional on the intervention over the intervened node's parents. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
To estimate the effect of forcing X, average over the values of X's parents rather than conditioning on X itself. Those parents summarize the pre-intervention causes entering X.

## Mechanics {#mechanics}
The paper uses pa_G(X) as the adjustment set for a DAG G. The adjustment is a graph-derived operation, so an estimated graph H can be wrong even when it differs from G by only a few edges. [§sec_1]

## The Math {#the-math}
The parent-adjustment formula is [§sec_1]

$$p_G(y\mid\operatorname{do}(X=\hat{x}))=\sum_{\operatorname{pa}(X)}p(y\mid\hat{x},\operatorname{pa}(X))p(\operatorname{pa}(X)).$$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

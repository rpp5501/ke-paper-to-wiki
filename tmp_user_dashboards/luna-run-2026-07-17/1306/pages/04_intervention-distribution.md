# Intervention Distribution

## TL;DR {#tldr}
The distribution of an outcome after a variable is forced to a value with the do-operator. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
Conditioning asks what is typical among units already at X=x; intervention asks what would happen after setting X to x and cutting the causes that normally enter X.

## Mechanics {#mechanics}
The do-operator creates an intervention distribution by modifying the factorization at the intervened node. SID evaluates graphs by whether their implied intervention distributions agree for every ordered source and target. [§sec_1]

## The Math {#the-math}
For a parentless intervention the paper gives the marginal result [§sec_1]

$$p_G(y\mid\operatorname{do}(X=\hat{x}))=p(y).$$ [§sec_1]

With parents, the corresponding parent-adjustment expression is used. [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

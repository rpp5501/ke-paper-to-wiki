# Markov Factorization

## TL;DR {#tldr}
The factorization of a distribution into one conditional factor per node given its parents in a DAG. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
The Markov property turns a graph into a recipe for a joint distribution: each variable only needs its parents as conditioning information.

## Mechanics {#mechanics}
For a distribution Markov with respect to G, the joint density factors along the parent sets. This is why changing parent structure can change the causal predictions even before any numerical parameters are chosen. [§sec_1]

## The Math {#the-math}
The paper uses the DAG factorization [§sec_1]

$$p(x_1,\ldots,x_p)=\prod_{j=1}^{p}p\!\left(x_j\mid x_{\operatorname{pa}_G(j)}\right).$$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

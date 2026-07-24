# SID Scalability

## TL;DR {#tldr}
The runtime behavior of the SID computation as graph size and sparsity change. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
SID gets more expensive as graphs grow because the algorithm combines global path information with many source-target checks, but sparsity helps.

## Mechanics {#mechanics}
The scalability experiment measures processor time on random sparse and dense graphs. The paper reports approximately quadratic scaling for sparse settings and cubic scaling for dense settings in the tested range. [§sec_1]

## The Math {#the-math}
The empirical summary is [§sec_1]

$$T(p)\approx O(p^2)\;\text{for sparse graphs},\qquad T(p)\approx O(p^3)\;\text{for dense graphs}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

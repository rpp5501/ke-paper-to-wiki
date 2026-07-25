# Linear-Gaussian Effect Check

## TL;DR {#tldr}
The appendix's analytic setting for checking causal effects from known structural coefficients and noise variances. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
The appendix provides a concrete numerical world where the graph's causal predictions can be checked analytically: linear structural equations with Gaussian noise.

## Mechanics {#mechanics}
Given structural coefficients and noise variances, the covariance matrix and intervention effects can be computed from the model. This supports the paper's proofs and sanity checks without changing SID's graph-level definition. [§sec_1]

## The Math {#the-math}
In a linear-Gaussian structural equation model, intervention means are linear in the forced value while the intervention variance does not depend on that value. The appendix uses this structure to compare effects. [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

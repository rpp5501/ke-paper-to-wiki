# Directed Path Matrix

## TL;DR {#tldr}
A matrix whose entry records whether one node is reachable from another by a directed path. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
The PathMatrix is a cached answer to a common question: can one node reach another by following arrows forward?

## Mechanics {#mechanics}
Its (i,j) entry is one exactly when a directed path exists from i to j. The SID implementation computes it once because many ordered-pair checks need descendant information. [§sec_1]

## The Math {#the-math}
Write the reachability indicator as [§sec_1]

$$P_{ij}=\mathbf{1}\{\text{there is a directed path from }i\text{ to }j\}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

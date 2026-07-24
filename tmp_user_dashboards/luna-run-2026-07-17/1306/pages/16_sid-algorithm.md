# SID Algorithm

## TL;DR {#tldr}
The efficient procedure that counts invalid causal predictions using adjacency, path, and reachability matrices. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
The implementation turns the graphical criterion into a reusable matrix computation: precompute reachability, then inspect each intervention pair.

## Mechanics {#mechanics}
The pseudocode takes adjacency matrices for G and H, computes a directed PathMatrix, and invokes a non-directed-path reachability procedure. It counts errors from the two parts of the adjustment condition and sums them. [§sec_1]

## The Math {#the-math}
At a high level, the computation is [§sec_1]

$$\operatorname{SID}=\sum_{i\ne j}\mathbf{1}\{\text{the estimated adjustment prediction for }(i,j)\text{ is incorrect in }G\}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

# Graphical SID Formulation

## TL;DR {#tldr}
A graphical characterization that evaluates parent sets and adjustment validity without computing densities. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
Instead of simulating or estimating every intervention distribution, inspect whether H's parent set would be a valid adjustment set in G.

## Mechanics {#mechanics}
The graphical formulation splits each pair according to whether j is a descendant of i in G and whether j is a parent of i in H. It then checks H's parent set against the two-part adjustment criterion in G. [§sec_1]

## The Math {#the-math}
The paper's criterion is represented schematically by [§sec_1]

$$\operatorname{SID}(G,H)=\#\{(i,j):\text{the H-parent adjustment for }(i,j)\text{ fails in }G\}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

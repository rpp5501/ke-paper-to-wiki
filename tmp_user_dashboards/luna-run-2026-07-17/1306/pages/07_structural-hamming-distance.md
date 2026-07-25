# Structural Hamming Distance (SHD)

## TL;DR {#tldr}
A baseline graph score counting pairs of vertices whose edge type differs between two graphs. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
SHD is an edit counter: compare every pair of vertices and count whether the edge type is missing, extra, or oriented differently.

## Mechanics {#mechanics}
SHD is intuitive and widely used, but it treats each structural disagreement as one unit. SID asks a different question: how many intervention statements become wrong because of those disagreements? [§sec_1]

## The Math {#the-math}
The paper defines SHD by counting vertex pairs whose edge type differs: [§sec_1]

$$\operatorname{SHD}(G,H)=\#\{(i,j):G\text{ and }H\text{ do not have the same edge type between }i\text{ and }j\}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

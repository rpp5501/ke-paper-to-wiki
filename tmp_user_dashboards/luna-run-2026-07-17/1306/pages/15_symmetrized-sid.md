# Symmetrized SID

## TL;DR {#tldr}
A symmetric comparison obtained by considering SID in both graph directions when neither graph is designated as the estimate. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
If two graphs are peers rather than truth and estimate, score both directions so one graph is not privileged.

## Mechanics {#mechanics}
The paper discusses a symmetric comparison obtained by combining the two directed SID values. This is a reporting choice for pairwise comparison, not the directed evaluation definition used in simulations. [§sec_1]

## The Math {#the-math}
A natural symmetric score is [§sec_1]

$$\operatorname{SID}_{\mathrm{sym}}(G,H)=\operatorname{SID}(G,H)+\operatorname{SID}(H,G).$$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

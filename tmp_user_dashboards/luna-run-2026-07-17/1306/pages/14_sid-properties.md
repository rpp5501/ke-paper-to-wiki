# Properties of SID

## TL;DR {#tldr}
The non-negativity, zero-identity, asymmetry, and non-triangle-inequality behavior that makes SID a pre-distance. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
SID behaves like a useful distance but not a perfectly symmetric geometric metric. It is zero when the causal predictions agree in the relevant sense, yet direction matters.

## Mechanics {#mechanics}
The paper studies non-negativity, the zero case, asymmetry, and bounds involving SHD. The estimate-to-truth direction is part of the definition, so swapping G and H can change the score. [§sec_1]

## The Math {#the-math}
The basic range is [§sec_1]

$$0\leq\operatorname{SID}(G,H)\leq p(p-1).$$ [§sec_1]

The paper calls SID a pre-distance because symmetry and the triangle inequality need not hold. [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

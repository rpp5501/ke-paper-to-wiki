# SID versus SHD

## TL;DR {#tldr}
The paper's comparison showing that edge disagreement and causal-effect disagreement can rank graph estimates differently. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
Two estimates can make the same number of edge mistakes but very different numbers of causal mistakes. SHD sees the edits; SID sees the consequences for interventions.

## Mechanics {#mechanics}
The paper's simulations report SID and SHD for random graphs and compare methods such as CPC, PC, GES, and random baselines. The measures can rank methods differently because an edge error may affect many ordered intervention pairs. [§sec_1]

## The Math {#the-math}
The contrast is not a conversion formula; it is two different objectives: [§sec_1]

$$\operatorname{SHD}\;\text{counts edge-type errors},\qquad\operatorname{SID}\;\text{counts false intervention distributions}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

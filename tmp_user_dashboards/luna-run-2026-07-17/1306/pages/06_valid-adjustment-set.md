# Valid Adjustment Set

## TL;DR {#tldr}
A set that blocks the relevant non-directed paths without conditioning on descendants of nodes on a directed causal path. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
An adjustment set is safe when it blocks spurious routes without blocking the causal routes we want to measure or conditioning on their descendants.

## Mechanics {#mechanics}
For an ordered pair (X,Y), the paper's criterion requires that no member of Z is a descendant of a node on a directed X-to-Y path, and that Z blocks all non-directed paths from X to Y. [§sec_1]

## The Math {#the-math}
The adjustment criterion can be summarized as [§sec_1]

$$Z\text{ valid for }(X,Y)\Longleftrightarrow Z\text{ has no forbidden descendants and blocks every non-directed path}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

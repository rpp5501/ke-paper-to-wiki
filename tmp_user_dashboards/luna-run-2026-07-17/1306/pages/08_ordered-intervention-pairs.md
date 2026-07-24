# Ordered Intervention Pairs

## TL;DR {#tldr}
The ordered pairs (i,j), with i not equal to j, that index the causal questions counted by SID. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
SID treats an intervention source and its outcome as an ordered pair: the effect of forcing i on j is not the same question as forcing j on i.

## Mechanics {#mechanics}
The count ranges over i and j with i not equal to j. Each pair is one causal query, and the total possible number for p variables is p(p-1). [§sec_1]

## The Math {#the-math}
The index set is [§sec_1]

$$\{(i,j):i,j\in V,\;i\ne j\},\qquad |V|=p\Longrightarrow p(p-1)\text{ ordered questions}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

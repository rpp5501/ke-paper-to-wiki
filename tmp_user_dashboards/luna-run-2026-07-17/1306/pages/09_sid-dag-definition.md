# SID for DAG Estimates

## TL;DR {#tldr}
The definition of SID when the true graph and the estimated graph are both DAGs. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
For two DAGs, SID is simply the number of source-target intervention questions where the estimate does not reproduce the true graph's causal distribution.

## Mechanics {#mechanics}
The true graph G supplies the reference distribution class, while H supplies the predicted intervention. This asymmetry is deliberate: it matches the evaluation setting in which H is an estimate of G. [§sec_1]

## The Math {#the-math}
For DAGs the definition is [§sec_1]

$$\operatorname{SID}:\mathbb{G}\times\mathbb{G}\to\mathbb{N},\qquad(G,H)\mapsto\#\{(i,j):H\text{ is causally wrong relative to }G\}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

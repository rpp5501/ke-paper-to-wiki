# SID Bounds for CPDAGs

## TL;DR {#tldr}
Lower and upper bounds that summarize SID behavior when an estimate is a CPDAG rather than one DAG. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
When an estimate is a CPDAG, report an interval: the best and worst causal error over the DAGs compatible with that partial orientation.

## Mechanics {#mechanics}
The paper defines lower and upper SID quantities for a true DAG versus a CPDAG. They distinguish intervention distributions identifiable from the class from those that can vary across its DAG members. [§sec_1]

## The Math {#the-math}
The CPDAG comparison returns two values: [§sec_1]

$$\operatorname{SID}(G,C)=\bigl(\operatorname{SID}_{\mathrm{lower}}(G,C),\operatorname{SID}_{\mathrm{upper}}(G,C)\bigr). $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

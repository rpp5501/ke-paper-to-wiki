# Non-directed Reachability

## TL;DR {#tldr}
The algorithmic representation of nodes reachable along non-directed paths that can remain open under an adjustment set. The paper evaluates graphs by causal consequences rather than edge edits alone.

## Intuition {#intuition}
Not every path in the adjustment test points forward. The reachability routine explores combinations of incoming and outgoing edge orientations to find non-directed routes that remain open.

## Mechanics {#mechanics}
The `rondp` procedure starts from parents and children of a node, propagates reachability under the adjustment-set rules, and then uses the resulting reachability-path matrix to catch additional nodes. [§sec_1]

## The Math {#the-math}
The algorithm records whether a node can be reached without orienting the whole route as a directed causal path: [§sec_1]

$$R_{ij}=1\Longleftrightarrow j\text{ is reachable from }i\text{ on a relevant non-directed path}. $$ [§sec_1]

## Go Deeper {#go-deeper}
- Read the paper's full-text PDF section for the formal definition, examples, proofs, and implementation details. [§sec_1]
- This page is grounded in the supplied local PDF; no external research note was used. [S1]

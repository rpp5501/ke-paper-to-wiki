# Implementation of SID
## TL;DR {#tldr}
This page covers how the Structural Intervention Distance (SID) is actually computed in code, translating the theoretical distance measure into an efficient algorithm. It builds on the broader question of how SID scales to larger graphs, and it is one part of the overall SID framework, with the concrete pseudo-code spelled out in the SID Algorithms.

## Intuition {#intuition}
Computing SID by definition would mean checking, for every pair of nodes, whether a certain conditional independence-like condition holds — a process that sounds simple but hides real computational cost. The implementation's key trick is to reduce this pairwise checking to matrix operations: reachability between nodes in a DAG can be read off from powers of the adjacency matrix, so instead of re-deriving paths from scratch for every pair, the algorithm builds shared matrices once and reuses them. This is why the authors chose to write custom code rather than lean on existing separation-checking libraries — the reuse of intermediate computations across all node pairs is where the practical speed comes from.

## Mechanics {#mechanics}
The implementation follows directly from a structural proposition whose condition splits into two parts that must each be checked for every relevant node pair. Part (1) asks whether any node in the conditioning set is a descendant of a node lying on a directed path between the pair being tested; this is answered using the PathMatrix, whose entries record whether a directed path exists between two nodes [§sec_4].

The PathMatrix is built by squaring the adjacency matrix of the DAG a number of times determined by its idempotence, giving an efficient way to compute all directed-path reachability information at once rather than per-pair [§sec_4].

Part (2) of the condition asks whether the conditioning set blocks every non-directed path between the pair; this is handled by a function (called rondp in the pseudo-code) that computes all nodes reachable via non-directed paths [§sec_4].

The rondp function works via a breadth-first search over node–orientation combinations, producing a reachabilityMatrix; the corresponding PathMatrix is then computed from it, and a reachableNodes vector — seeded with the parents and children of the source node — is read off and filtered to keep only nodes reached along non-directed paths [§sec_4].

Because computing the PathMatrix is the most computationally expensive step, the algorithm is structured so this computation happens only once and is reused across all node pairs, which is the central reason the authors avoided existing off-the-shelf implementations (e.g., for d-separation) [§sec_4].

The implementation also extends to computing SID between a DAG and a completed PDAG by enumerating all DAGs consistent with a partially directed graph, though these extra steps are omitted from the published pseudo-code for readability; the full code is distributed by the authors as R-code on the first author's homepage [§sec_4].

## The Math {#the-math}
The local context describes computational complexity in prose rather than as a discrete labeled equation: computing the SID between dense matrices is dominated by matrix squaring, with a naive implementation costing more than the reported improved bound, and this cost can be reduced further for sparse matrices [§sec_4]. No `[eq_N]`-tagged equations are present in the local context for this concept, so no display equation is reproduced here.

## Go Deeper {#go-deeper}
No research note is attached to this concept. For implementation-level detail beyond this summary, the neighborhood points to the SID Algorithms (where the full pseudo-code this section sketches is defined) and to the discussion of Scalability of the SID (which this implementation builds on, particularly regarding sparse-matrix complexity).

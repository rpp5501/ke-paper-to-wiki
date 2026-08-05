# Implementation of SID
## TL;DR {#tldr}
Implementing SID means turning the abstract generalized adjustment criterion into a concrete matrix algorithm: for every ordered pair of nodes, decide whether the estimated graph's parent set is a valid adjustment set in the true graph. The implementation reduces this to two reachability computations over the true DAG's adjacency matrix, reusing the expensive one across all pairs sharing a source. The dominant cost is building directed reachability by repeated matrix squaring, which is why the paper singles out implementation efficiency as a design goal rather than an afterthought.

## Intuition {#intuition}
Checking the adjustment criterion by hand for every pair of nodes would mean re-deriving path structure from scratch each time — wasteful, since most of that structure is shared across pairs. The implementation instead precomputes "who can reach whom" once as a matrix, then answers each pair's yes/no question by reading off entries and running one graph traversal per source rather than per pair. This is the classic trick of trading a symbolic separation criterion for numerical linear algebra: matrix squaring stands in for path-finding, and a single breadth-first pass standing in for many.

## Mechanics {#mechanics}
The criterion behind SID has two parts that the implementation checks separately. Part (a) asks whether any node in the adjustment set is a descendant of a node lying on a directed path from source to target — an ancestry check. Part (b) asks whether the adjustment set blocks every *non-directed* path between them — a separation check that must specifically exclude directed causal paths, which is why it cannot be delegated to a generic d-separation routine [§sec_4].

Part (a)'s ancestry check relies on the **PathMatrix**: entry `(i, j)` is true iff a directed path runs from `i` to `j`. Computing it once for the whole true graph and reusing it for every source is deliberate — the paper notes this reuse is one reason the implementation avoids existing separation libraries, which would recompute path structure per query [§sec_4].

```algorithm
title: Algorithm 1 — _sid_matrix, checking the adjustment criterion per source
lines:
  - code: "path_matrix = compute_path_matrix(true_graph)"
    intent: "Computed once for the whole graph and reused for every source, since building it is the dominant cost [sid.py:L256]"
  - code: "for source in nodes:"
    intent: "The generalized adjustment criterion is checked once per source against every target in a single pass [sid.py:L183]"
  - code: "    if true_parents(source) == est_parents(source): continue"
    intent: "A source whose estimated parents match the truth already has the correct back-door set for every target, so it can be skipped entirely [sid.py:L183]"
  - code: "    path_matrix_no_tails = compute_path_matrix(true_graph minus est_parents' outgoing edges)"
    intent: "Removing the adjustment set's outgoing edges lets rondp later tell a path that dodges a conditioned tail from one that does not [sid.py:L183]"
  - code: "    reachable = rondp(source, est_parents, path_matrix, path_matrix_no_tails)"
    intent: "One breadth-first traversal answers condition (b) — non-causal-path blocking — for every target at once [sid.py:L1]"
  - code: "    for target in nodes: incorrect[source,target] = criterion fails"
    intent: "Condition (a) is evaluated only for targets with a real causal path; a null true effect needs only condition (b) [sid.py:L183]"
```

Part (b)'s traversal, `rondp`, cannot reuse ordinary d-separation because "open path" here excludes directed causal paths on purpose — those are the effect being measured, not a confound to block. The routine tracks, for each node, *which direction* the path arrived from, since whether a collider opens a path depends on that direction. This is why the state space is doubled: each node gets two indices, one for "arrived via an edge into it" and one for "arrived via an edge out of it," and the collider rule is applied per-direction rather than per-node [sid.py:L1].

Two special cases shortcut the general check. If the target itself is in the adjustment set, its estimated intervention distribution collapses to a marginal, which is correct exactly when the source has no true causal effect on it at all — no traversal needed. And if the estimated parent set exactly matches the true parent set for a source, that source is skipped outright, since a matching back-door set is valid for every target simultaneously [sid.py:L183].

The DAG–CPDAG and CPDAG–CPDAG variants layer on top of this same per-pair check by enumerating the DAGs consistent with a partially directed graph and evaluating each; the paper omits this enumeration from its pseudocode purely for readability, not because it's a separate algorithm [§sec_4].

## The Math {#the-math}
The PathMatrix is built by squaring `I | G` rather than by explicit path enumeration, and the number of rounds needed is a direct consequence of how far each squaring reaches.

```derivation
shape: Why ceil(log2(n)) squarings of (I | G) suffice to close the directed reachability of an n-node DAG.
steps:
  - latex: "M_0 = I \\lor G"
    why: "Reflexive one-step reachability: every node reaches itself and its direct children [sid.py:L1]"
  - latex: "M_{t+1} = M_t \\lor (M_t \\, @ \\, M_t)"
    why: "If M_t marks every path of length <= 2^t, then M_t @ M_t marks every path of length <= 2^{t+1} formed by chaining two such paths, since boolean matmul composes 'a reaches b and b reaches c' into 'a reaches c' [sid.py:L1]"
  - latex: "M_{\\lceil \\log_2 n \\rceil}[i,j] = \\text{true} \\iff i \\text{ reaches } j"
    why: "A simple path in an n-node DAG has at most n-1 edges, and 2^{\\lceil \\log_2 n \\rceil} \\geq n-1, so this many doubling rounds cover every possible path length [sid.py:L1]"
```

This squaring is the cost driver the paper flags: recomputing a PathMatrix is far more expensive than any other step, and the general implementation must build one such matrix per source — the shared `path_matrix` once, plus a source-specific `path_matrix_without_conditioned_tails` whenever that source's estimated parent set is non-empty, since the removed edges differ per source [sid.py:L183].

That per-source recomputation is why cost grows roughly with the fourth power of the node count `p`: `p` sources, each needing `O(log p)` squarings, each squaring costing polynomial time in `p`. The docstring reports this empirically rather than asymptotically — a 100-node pair takes a few seconds, a 200-node pair around a minute [sid.py:L256]. Doubling `p` under quartic growth predicts roughly a 16x slowdown; going from "a few seconds" (~4s) to "around a minute" (~60s) is about 15x, consistent with that prediction and a useful sanity check on the complexity claim [sid.py:L256].

Sparse graphs change this picture directly: fewer nonzero entries mean cheaper matrix products at every squaring round, so the paper notes sparse implementations improve on the dense-matrix bound without changing the algorithm's structure [§sec_4].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the parent concept this code implements; read it first for what the adjustment criterion is actually deciding.
- **SID Algorithms** — the pseudocode (Algorithms 1 and 2) this implementation follows line-for-line, including the parts elided here for readability.
- **Scalability of the SID** — the complexity and sparse-matrix discussion this implementation's cost model builds on.
- **sid.py** — the full source file, including `_compute_path_matrix` and `_reachable_on_non_directed_path` in complete form.
- **`_sid_matrix()`** — the core per-source loop summarized in the algorithm block above.
- **`SID` class** — the metric-facing wrapper that aligns two graphs' adjacency matrices and sums `_sid_matrix`'s output.

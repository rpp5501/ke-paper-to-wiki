# Implementation of SID
## TL;DR {#tldr}
- SID's definition is combinatorial — check an adjustment condition for every ordered pair of nodes — but the reference implementation turns that combinatorics into two matrix routines, each computed once per source node and then reused across every target, rather than re-derived pair by pair.
- The two routines mirror the two halves of the generalized adjustment criterion: one is a directed-reachability closure (does a causal path exist, and does the estimated parent set sit on it), the other is a breadth-first search over "arrived from which direction" states that finds every node reachable by a path that stays open but is not itself causal.
- Sharing the expensive closure computation across all p−1 targets for a fixed source — instead of calling a general d-separation routine once per pair — is the specific choice that keeps SID computable at all on graphs with a few hundred nodes.

## Intuition {#intuition}
Picture the source node as a spigot: everything the true graph reaches downstream by a directed path is a genuine causal effect, and every other route out of the source is a spurious channel that a valid adjustment set has to plug. Checking this the naive way means re-deriving "is this path open" once per (source, target, adjustment-set) triple — that's what a generic d-separation call would cost. The implementation instead fixes the source and its estimated parent set once, builds two matrices that jointly answer both halves of the criterion for *every* possible target in a single pass, and only then loops over targets to read off a yes/no.

That's also why this concept sits between *SID Algorithms*, which specifies what has to be checked, and *Scalability of the SID*, which is a direct consequence of how expensive that check turns out to be — the implementation is the bridge between the definition and its cost.

## Mechanics {#mechanics}
**The Proposition splits into two checks, and the code splits into two matrices to match:** part (1) asks whether any node in the estimated parent set descends from a node on a directed source→target path, and part (2) asks whether that same parent set blocks every non-directed path between source and target [§sec_4].

| Condition | Question | Answered by |
|---|---|---|
| (a) | Does an adjustment-set node descend from a node on the source→target directed path? | PathMatrix, the transitive closure, computed once per source [§sec_4] |
| (b) | Does the adjustment set block every non-causal path? | `rondp`, a BFS over direction-doubled states [§sec_4] |

**Part (a) reduces to a transitive closure, computed by squaring:** the PathMatrix's entry (i, j) is 1 iff a directed path runs from i to j, and it is built by repeated squaring because the relation is idempotent once the closure is reached — further squarings stop changing anything [§sec_4].

```algorithm
title: Transitive closure via repeated squaring (_compute_path_matrix)
lines:
  - code: "path_matrix = graph | I"
    intent: "Reflexive one-step reachability: every node reaches its direct children and, via the identity, itself [sid.py:L1]"
  - code: "for _ in range(ceil(log2(n))):"
    intent: "Each squaring doubles the path length covered; a p-node DAG's longest simple path has p-1 edges, so ceil(log2 p) rounds are enough, and the matrix stops changing once it is idempotent [sid.py:L1]"
  - code: "    path_matrix = path_matrix @ path_matrix"
    intent: "Boolean matmul composes 'a reaches b' with 'b reaches c' into 'a reaches c', so squaring doubles the reachable horizon each round [sid.py:L1]"
```

**Part (b) needs more than plain reachability, because direction matters:** a collider is open only if it or a descendant is conditioned on, so whether a path may continue through a node depends on whether the path arrived via an incoming or an outgoing edge at that node [sid.py:L1]. `rondp` handles this by doubling the state space — node *v* gets two indices, one for "arrived via an edge into v" and one for "arrived via an edge out of v" — and running a breadth-first search over that 2p-state graph before closing it into a reachabilityPathMatrix [§sec_4].

**One traversal per source, not one per pair, is the point:** `_sid_matrix` computes PathMatrix and runs `rondp` once for each source node, then loops over all targets reusing both results, because recomputing the closure per pair is exactly the cost this design avoids [sid.py:L183].

```algorithm
title: Per-source loop (_sid_matrix)
lines:
  - code: "if true_parents == est_parents: continue"
    intent: "A matching parent set is automatically the true back-door set for every target, so the whole source can be skipped without touching the matrices [sid.py:L183]"
  - code: "path_matrix_wo_tails = closure(true_graph with est_parents' out-edges removed)"
    intent: "Removing the adjustment set's outgoing edges lets the later check tell a directed path that avoids conditioned tails from one that does not [sid.py:L183]"
  - code: "reachable = rondp(source, est_parents, path_matrix, path_matrix_wo_tails)"
    intent: "One rondp call answers condition (b) for every target at once, instead of once per (source, target) pair [sid.py:L183]"
  - code: "for target: check condition (a) using path_matrix and reachable"
    intent: "Both halves of the adjustment criterion are now read off already-built matrices, so the inner loop over targets does no further matrix work [sid.py:L183]"
```

**The heavy lifting is deliberately not delegated to an existing d-separation routine:** the paper is explicit that computing PathMatrix only once per source, and sharing it across all targets, is the reason a generic library implementation was not reused — a generic call would rebuild that closure per pair [§sec_4].

## The Math {#the-math}
No display equation is carried in this section of the paper, but the squaring recurrence that drives PathMatrix has a definite closed form worth writing out, since it is what fixes the round count and hence the cost.

```annotated-eq
latex: "P \\leftarrow (A \\lor I)^{2^{k}}, \\qquad k = \\lceil \\log_2 p \\rceil"
terms:
  - tex: "P"
    role: 1
    words: "PathMatrix, the reflexive transitive closure of the true DAG's adjacency matrix [§sec_4]"
  - tex: "A \\lor I"
    role: 2
    words: "One-step reachability plus the identity, so every node reaches itself and its direct children before any squaring happens [sid.py:L1]"
  - tex: "2^{k}"
    role: 3
    words: "The effective path length covered after k squarings; boolean matrix exponentiation composes reachability, doubling the horizon each round [sid.py:L1]"
  - tex: "k = \\lceil \\log_2 p \\rceil"
    role: 4
    words: "The smallest round count guaranteeing 2^k exceeds p-1, the longest possible simple path in a p-node DAG, so no true path is missed [sid.py:L1]"
```

**Why the cost is quartic, not cubic:** each squaring is an O(p³) matmul under naive multiplication, and O(log p) of them are needed per source, but PathMatrix (or its tails-removed variant) is rebuilt for every one of the p sources — so the total is on the order of p⁴ (with a slowly-growing log p riding along), which is exactly what the implementation's own complexity note claims [sid.py:L256].

**A concrete check against that claim:** the implementation reports a 100-node pair taking a few seconds and a 200-node pair taking around a minute [sid.py:L256]. Doubling p from 100 to 200 under pure p⁴ scaling predicts a (200/100)⁴ = 16× slowdown; going from "a few seconds" to "around a minute" is in that same 15–20× range, which is consistent with the quartic bound rather than, say, cubic (which would predict only 8×) [sid.py:L256].

**Where the exponent could shrink, and why the code doesn't chase it:** the paper notes that naive matrix multiplication is what yields this bound, and that fast matrix-multiplication results report a smaller exponent, with sparse matrices improving things further still [§sec_4]. The implementation described here works with dense NumPy arrays and pays the naive cost, leaving the sparse and CPDAG-enumeration variants the paper mentions as separate, unshown code paths [§sec_4].

## Go Deeper {#go-deeper}
- **SID Algorithms** — specifies Algorithm 1 and the `rondp` procedure (Algorithm 2) that this page's two matrix routines directly implement.
- **Structural Intervention Distance (SID)** — the metric this implementation ultimately computes: the count of ordered pairs this per-source loop flags as incorrect.
- **Scalability of the SID** — builds directly on the p⁴ cost argument made here; explains why SID is impractical on very large graphs.
- **sid.py / `_sid_matrix()`** — the actual source referenced throughout this page; read it alongside `_compute_path_matrix` and `_reachable_on_non_directed_path` for the full traversal logic past what's excerpted here.

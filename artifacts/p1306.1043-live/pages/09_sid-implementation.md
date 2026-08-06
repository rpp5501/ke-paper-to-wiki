# Implementation of SID
## TL;DR {#tldr}
- SID's definition is combinatorial — check an adjustment condition for every ordered pair of nodes — but the reference implementation turns that combinatorics into two matrix routines, each computed once per source node and then reused across every target, rather than re-derived pair by pair.
- The two routines mirror the two halves of the generalized adjustment criterion: one is a directed-reachability closure (does a causal path exist, and does the estimated parent set sit on it), the other is a breadth-first search over "arrived from which direction" states that finds every node reachable by a path that stays open but is not itself causal.
- Sharing the expensive closure computation across all p−1 targets for a fixed source — instead of calling a general d-separation routine once per pair — is the specific choice that keeps SID computable at all on graphs with a few hundred nodes.

## Intuition {#intuition}
Picture the source as a spigot. Directed downstream paths are genuine causal effects; other open routes are channels a valid adjustment set must block.

A naive check re-derives path openness for every source, target, and adjustment set. A generic d-separation call has that shape.

The implementation fixes a source and its estimated parent set, then builds two matrices that answer both checks for every target. The target loop only reads a yes/no result.

This page bridges *SID Algorithms*, which states the checks, and *Scalability of the SID*, which follows from their cost.

### Running four-node example: trace the code

Trace the harder direction, $\mathrm{SID}(H,G)$, for the shared graphs $G: A\to B, A\to C, B\to D, C\to D$ and $H=G+(B\to C)$.

In `_sid_matrix`, source $C$ has true parents $\{A,B\}$ in $H$ but estimated parents $\{A\}$ in $G$. The fast parent-equality branch therefore cannot skip this source [sid.py:L183-L253].

The path matrix says $C$ reaches $D$. The non-directed-path traversal also exposes the omitted-parent route to $B$. The target loop consequently marks $(C,B)$ and $(C,D)$, while every other source either has matching parents or produces no error [sid.py:L29-L253].

**Counterexample/debug checkpoint:** if an implementation returns zero here, inspect whether it incorrectly uses $G$ as truth after the arguments swap, or silently truncates `_reachable_on_non_directed_path()` before its final state-collapse return [sid.py:L29-L180].

## Mechanics {#mechanics}
**The proposition has two checks, so the code has two matrix routines.** One tests a problematic descendant on a directed source-to-target path. The other tests whether the estimated parent set blocks every non-directed path [§sec_4].

| Condition | Question | Answered by |
|---|---|---|
| (a) | Does an adjustment-set node descend from a node on the source→target directed path? | PathMatrix, the transitive closure, computed once per source [§sec_4] |
| (b) | Does the adjustment set block every non-causal path? | `rondp`, a BFS over direction-doubled states [§sec_4] |

**Part (a) reduces to a transitive closure.** PathMatrix$(i,j)$ is 1 exactly when a directed path runs from $i$ to $j$ [§sec_4].

Repeated squaring reaches that closure. Once it is idempotent, further squarings change nothing [§sec_4].

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

**Part (b) needs more than reachability because direction matters.** Whether a path may continue through a collider depends on whether the collider or one of its descendants is conditioned on [sid.py:L1].

`rondp` gives node *v* two states: arrival along an edge into *v* or out of *v*. It runs BFS over this $2p$-state graph and closes it into a reachabilityPathMatrix [§sec_4].

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

**Why no generic d-separation routine is used:** PathMatrix is computed once per source and shared across targets [§sec_4]. A generic call would rebuild that closure per pair.

## The Math {#the-math}
**The PathMatrix recurrence fixes the round count and cost:** repeated squaring doubles the maximum represented path length on each iteration, so only logarithmically many squarings are required to cover paths up to length $p-1$ [§sec_4].

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

| Claim | Scope | Reason |
|---|---|---|
| $O(p^4)$ | Dense-matrix worst-case upper bound | A naive $p\times p$ matrix multiplication costs $O(p^3)$ and source-specific reachability can repeat for $p$ sources [§sec_4; sid.py:L256] |
| Approximately quadratic/cubic | Observed sparse/dense timing curves | Finite sampled graph families can avoid worst-case work [§sec_3_3; §sec_4] |

**A concrete check:** the implementation reports a 100-node pair taking a few seconds and a 200-node pair taking around a minute [sid.py:L256].

Pure $p^4$ scaling predicts a $16\times$ slowdown when $p$ doubles from 100 to 200. The reported $15$--$20\times$ range is consistent with that bound; cubic scaling would predict only $8\times$ [sid.py:L256].

**Why these statements do not contradict each other:** Section 3.3 measures sampled sparse and dense random graphs over a finite size range [§sec_3_3].

Sparsity, graph structure, constants, and reused matrix work can reduce exercised work. The quartic result is a dense worst-case ceiling; the quadratic/cubic results are empirical behavior for the tested distributions [§sec_3_3; §sec_4].

**Where the exponent could shrink:** naive matrix multiplication yields this bound. Fast multiplication has a smaller exponent, and sparse matrices can improve it further [§sec_4].

This implementation uses dense NumPy arrays and pays the naive cost. Sparse and CPDAG-enumeration variants are separate, unshown code paths [§sec_4].

## Go Deeper {#go-deeper}
- **SID Algorithms** — specifies Algorithm 1 and the `rondp` procedure (Algorithm 2) that this page's two matrix routines directly implement.
- **Structural Intervention Distance (SID)** — the metric this implementation ultimately computes: the count of ordered pairs this per-source loop flags as incorrect.
- **Scalability of the SID** — compares the dense worst-case $O(p^4)$ ceiling here with the paper's approximately quadratic and cubic empirical timing curves.
- **sid.py / `_sid_matrix()`** — the complete source listing maps the paper's two graphical conditions to `_compute_path_matrix` and `_reachable_on_non_directed_path` [sid.py:L10-L253].

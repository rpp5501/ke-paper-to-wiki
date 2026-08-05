# SID Algorithms
## TL;DR {#tldr}
SID Algorithms is the operational layer beneath the SID metric: two procedures that turn "does the estimated graph correctly predict this pair's intervention effect?" into something a computer can check pair by pair. The first algorithm sweeps every ordered pair of nodes and tallies where the estimated graph's parent set fails as an adjustment set; the second is a reachability subroutine it calls to test whether that adjustment set actually blocks every non-causal path. Together they implement the SID metric and its matrix-level computation, building on the linear-Gaussian intervention-effect machinery that tells you what a "correct" effect even means.

## Intuition {#intuition}
You can't get SID by diffing two adjacency matrices, because a wrong edge doesn't always break a prediction and a missing edge doesn't always matter — what matters is whether adjusting for the estimated graph's parents still recovers the right intervention distribution in the true graph. That's a question about paths, not about edges: does some route from source to target sneak past the chosen adjustment set? Algorithm 1 asks this question once per ordered pair; Algorithm 2 answers the "is there an unblocked route" part by walking the graph outward from the source, tracking which direction each edge was crossed in, since that determines whether the path counts as blocked.

## Mechanics {#mechanics}
Algorithm 1 fixes a source node, reads off its parent set under the estimated graph, and reuses it as the candidate adjustment set for every target simultaneously — one traversal answers all targets at once rather than repeating work per pair [§sec_12]. It first builds the transitive closure of the true graph, `PathMatrix`, which tells it whether *any* causal path exists at all — the ground truth the estimated prediction gets checked against [§sec_12].

```algorithm
title: Algorithm 1 — computing the incorrect-intervention matrix
lines:
  - code: "PathMatrix = computePathMatrix(G)"
    intent: "Transitive closure of the true graph gives the ground-truth answer to whether source has any causal effect on target at all [§sec_12]"
  - code: "for source in nodes: PaH = parents(source) in H"
    intent: "The estimated graph's parent set of source is the adjustment set every target for that source gets checked against [§sec_12]"
  - code: "PathMatrix2 = computePathMatrix(G with edges leaving PaH removed)"
    intent: "Deleting PaH's outgoing edges simulates conditioning on it, isolating which paths survive adjustment [sid.py:L183]"
  - code: "reachable = rondp(G, source, PaH, PathMatrix, PathMatrix2)"
    intent: "Algorithm 2 finds every target still reachable from source on a path PaH fails to block — condition (b) of the adjustment criterion [sid.py:L183]"
  - code: "for target in nodes: compare PathMatrix[source,target] to (target in PaH)"
    intent: "True effect is null iff no path exists; estimated effect is null iff target sits inside the adjustment set itself [sid.py:L183]"
  - code: "incorrectCausalEffects[source, target] = mismatch OR unblocked non-causal path"
    intent: "A pair counts as wrong on a null/non-null mismatch, or when rondp shows PaH lets a non-causal path through [sid.py:L183]"
  - code: "output sum(incorrectCausalEffects)"
    intent: "SID counts pairs, not error magnitude, so every wrong adjustment contributes exactly one regardless of severity [§sec_12]"
```

Algorithm 2 (`rondp`) is where the direction-sensitivity lives: each reachable node is tagged with whether it was entered through an outgoing or incoming edge, because that tag — not just "reachable or not" — decides which of the node's own edges can legally continue the path [§sec_12]. A neighbor outside the adjustment set never blocks anything, so reachability propagates through it unconditionally; a neighbor that loops back to an ancestor of the source re-opens the path and forces the rule to re-apply to that ancestor's parents [§sec_12]. The same pair of rules is applied symmetrically to the source's children, since a back-door path can leave through either side [§sec_12].

```algorithm
title: Algorithm 2 — reachable nodes on a non-directed path (rondp)
lines:
  - code: "Pa(x), Ch(x) = parents(x), children(x) in G"
    intent: "The walk starts at source x and explores both directions at once, since a blocked-or-not path can leave through a parent or a child edge [§sec_12]"
  - code: "mark each neighbor with the direction it was reached by"
    intent: "Direction of entry, not just reachability, decides which further edges keep the path unblocked at that node [§sec_12]"
  - code: "if a parent of cN is reachable and cN not in PaH: mark cN reachable"
    intent: "A node outside the adjustment set cannot block, so reachability passes through it for free [§sec_12]"
  - code: "if cN reachable via outgoing edge and cN is an ancestor of x: propagate to parents(cN)"
    intent: "A path curling back to an ancestor of x re-opens once that ancestor's own parents are considered, so the rule recurses [§sec_12]"
  - code: "apply the analogous rules to Ch(x)"
    intent: "The traversal is symmetric across parents and children of the source [§sec_12]"
  - code: "reachabilityPathMatrix = computePathMatrix(reachabilityMatrix)"
    intent: "Closing the one-step reachability graph turns local propagation into full reachability, exactly as PathMatrix does for G [§sec_12]"
  - code: "recover missed nodes via PathMatrix2, then remove blocked (x,y) entries"
    intent: "A directed path from x to y surviving adjustment implies every parent of y is reachable too — a case local propagation alone misses [§sec_12]"
  - code: "output the completed reachability set"
    intent: "This set is exactly the targets for which PaH fails to block a non-causal route, feeding condition (b) back into Algorithm 1 [§sec_12]"
```

## The Math {#the-math}
The pairwise verdict Algorithm 1 produces reduces to comparing two booleans per pair — whether a causal path exists, and whether the target lies inside the adjustment set — with the reachability check as a tiebreaker on the remaining case [sid.py:L183].

| True effect (`PathMatrix[source,target]`) | Estimated effect (`target ∈ PaH`) | Verdict |
|---|---|---|
| path exists | target in PaH (est. says null) | mismatch → incorrect [sid.py:L183] |
| no path | target not in PaH (est. says non-null) | mismatch → incorrect [sid.py:L183] |
| path exists | target not in PaH, but rondp finds an unblocked non-causal path | condition (b) fails → incorrect [sid.py:L183] |
| path exists | target not in PaH, PaH blocks every non-causal path, and no PaH member descends from a mediator on the causal path | condition (a)+(b) hold → correct [sid.py:L183] |

When the estimated and true parent sets of a source are identical, `_sid_matrix` skips the whole per-target loop for that source: a graph's own parent set is always a valid adjustment set for itself, so every target is guaranteed correct and the extra `PathMatrix2` closure is unnecessary [sid.py:L183]. This shortcut matters for cost, not just cleanliness. Algorithm 1 calls `computePathMatrix` once globally, then once more per source whenever that source's parent sets differ — each closure costing roughly O(n³) over an n-node graph — so the total is bounded by O(n⁴) source-target work in the worst case where every source's estimated parents diverge from the truth [sid.py:L256]. That bound is exactly what the implementation's own scaling note reports: a few seconds at n=100 and around a minute at n=200, since quadrupling n roughly sixteen-folds the runtime under a fourth-power law [sid.py:L256].

## Go Deeper {#go-deeper}
- **SID** — the metric these two algorithms exist to compute; read it first to know what "correct" and "incorrect" intervention distribution mean before tracing the pseudocode.
- **_sid_matrix()** — the concrete NumPy implementation of Algorithm 1 (and its `_reachable_on_non_directed_path` helper for Algorithm 2); the actual code these blocks are transcribed from.
- **Causal Effects in Linear Gaussian SEMs** — prerequisite: defines the intervention distributions whose equality Algorithm 1 is testing pair by pair.
- **Implementation of SID** — the parent page this concept is defined under; useful for how the two algorithms fit into the surrounding module.

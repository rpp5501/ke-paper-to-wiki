# SID Algorithms
## TL;DR {#tldr}
Two algorithms turn the definition of SID from a pairwise check into something you can actually run. Algorithm 1 walks every ordered pair of variables once and decides whether the estimated graph's parent set is a valid adjustment set for that pair; Algorithm 2 (rondp) is the traversal it leans on to answer the hard half of that question — whether the adjustment set blocks every non-causal path — for an entire source node's targets in one pass instead of one target at a time. Together they implement the metric defined in SID and are what `_sid_matrix()` actually runs.

## Intuition {#intuition}
Checking, for a single pair of variables, whether one graph's parent set is a valid adjustment set for another graph's causal effect is itself a small graph problem — you'd normally solve it by searching the graph fresh for that one pair. Naively repeating that search for every ordered pair scales badly.

The move both algorithms make is to fix a *source* node and answer the question for every possible target at once, by computing reachability information a single time and reading off each target's verdict from it. That reachability computation is exactly Algorithm 2's job, and it in turn depends on the effect definitions from Causal Effects in Linear Gaussian SEMs: an effect is "real" only when a directed path exists, so blocking and reachability are checked against that same causal structure.

## Mechanics {#mechanics}
**Skip when the parent sets already match:** if the estimated graph gives a source node exactly the same parents as the true graph, that parent set is the true back-door set and is valid for *every* target — the whole source can be skipped without touching any target [sid.py:L183].

**Removing conditioned tails before the second pass:** before checking paths, the algorithm deletes the outgoing edges of nodes in the estimated adjustment set from a copy of the true graph, then recomputes reachability on that pruned graph. This is what lets a later check distinguish a directed path that truly reaches the target from one that only appears to, because it leaves through a node the adjustment set already controls for [sid.py:L183].

**One reachability call answers condition (b) for every target:** `_reachable_on_non_directed_path` — the `_sid_matrix()` counterpart of Algorithm 2's rondp — is invoked once per source and returns which nodes are reachable from it along paths that the adjustment set fails to block. Every target's condition-(b) verdict is then a lookup into that one result rather than a fresh traversal [§sec_12].

**Per-target verdict splits on whether the target is itself in the adjustment set:** if the target is a parent of the source in the estimated graph, the estimated intervention distribution collapses to the marginal — correct only if the source truly has no causal effect on the target. Otherwise, with a causal path assumed to exist, the check falls to condition (a): the adjustment set is rejected if it contains a descendant of a child of the source that still reaches the target, since adjusting for a mediator or its descendant is the classic case that breaks an intervention estimate [sid.py:L183].

**rondp's traversal state carries how a node was reached:** the pseudocode tags each visited node with whether it was entered via an outgoing or an incoming edge, because whether a path is still "non-blocked" past that node depends on that direction — a node reached with an incoming edge propagates reachability to its parents only under different conditions than one reached with an outgoing edge [§sec_12].

**The traversal has to patch itself:** the pseudocode notes that some directed, non-blocked paths get missed by the direction-tagged pass alone, and adds a correction step that uses the auxiliary path matrix (computed with conditioned tails removed) to find descendants reachable with no adjustment-set node in between, before folding those back into the reachable set [§sec_12].

## The Math {#the-math}
No display equations are given for this concept, but the module's own worked example makes the counting rule concrete. For `true_dag = DAG([(1, 2)])` and `est_dag = DAG([(2, 1)])`, `SID()(true, est)` returns `2` [sid.py:L256].

**Why it's exactly 2, not 0 or 4:** there are two ordered pairs to check, (1→2) and (2→1). For source 1, the true graph gives node 1 no parents, but the estimated graph makes 2 a parent of 1 (since the estimated edge runs 2→1). Node 2 is the target, so `est_parents[target]` is true — the estimate says target 2 belongs to source 1's own adjustment set, collapsing the predicted effect to the marginal, i.e. "no effect." But the true graph has the real edge 1→2, so the true effect is *not* null: mismatch, one incorrect pair. For source 2, the true graph gives it no causal path to target 1 (`path_matrix[2,1]` is false, so the true effect is null), while the estimated graph's parent set for source 2 is empty, so the estimate predicts a nonzero effect: mismatch again. Both ordered pairs land on the wrong side, giving SID = 2 out of a maximum of 2 for a 2-node graph [sid.py:L183].

**Where the fourth-power cost comes from:** the path matrix that Algorithm 1 relies on is a transitive closure, computable in roughly O(n³) time over an n-node graph. That closure is recomputed once per source rather than once overall, because the conditioned-tail pruning depends on that source's estimated parent set. n sources times an O(n³) closure each gives the O(n⁴) total the implementation documents — cheap at 100 nodes (seconds), heavy by 200 (about a minute) [sid.py:L256].

**Why the traversal in rondp is guaranteed to terminate:** each node is tagged with the direction it was entered from, giving at most two live states per node (entered via an outgoing edge, entered via an incoming edge). The reachable set only grows by adding new (node, direction) states and never revisits one already recorded, so the traversal is bounded by 2n additions regardless of how many paths actually exist in the graph [§sec_12].

## Go Deeper {#go-deeper}
- **Implementation of SID** — the parent page these two algorithms live under; this page is the pseudocode-to-code mapping for it.
- **Causal Effects in Linear Gaussian SEMs** (prerequisite) — defines what a "real" causal effect is, which is exactly what Algorithm 1's null/non-null check is deciding per pair.
- **SID** (implements) — the metric whose value is the sum of incorrect pairs these algorithms produce.
- **`_sid_matrix()`** (implements) — the concrete function that carries out Algorithm 1's per-source, all-targets-at-once loop described above.

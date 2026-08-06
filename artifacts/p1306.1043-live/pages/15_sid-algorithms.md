# SID Algorithms
## TL;DR {#tldr}
Two algorithms make SID's pairwise definition executable. Algorithm 1 tests whether the estimated parent set is valid for each ordered pair.

Algorithm 2, `rondp`, answers the hard path-blocking question for all targets of one source in one pass. Together they are what `_sid_matrix()` runs.

## Intuition {#intuition}
Checking, for a single pair of variables, whether one graph's parent set is a valid adjustment set for another graph's causal effect is itself a small graph problem — you'd normally solve it by searching the graph fresh for that one pair. Naively repeating that search for every ordered pair scales badly.

Both algorithms fix one *source* and answer for every target from shared reachability information. Each target's verdict is then a lookup.

Algorithm 2 provides that reachability. It uses the same causal structure as linear-Gaussian effects: a real effect requires a directed path.

## Mechanics {#mechanics}
**Skip when the parent sets already match:** if the estimated graph gives a source node exactly the same parents as the true graph, that parent set is the true back-door set and is valid for *every* target — the whole source can be skipped without touching any target [sid.py:L183].

**Removing conditioned tails before the second pass:** the algorithm deletes outgoing edges of estimated-adjustment nodes from a copy of the true graph, then recomputes reachability [sid.py:L183].

This distinguishes a path that truly reaches the target from one leaving through a node already controlled by the adjustment set [sid.py:L183].

**One reachability call answers condition (b) for every target.** `_reachable_on_non_directed_path`, Algorithm 2's `_sid_matrix()` counterpart, runs once per source [§sec_12].

It returns nodes reachable on paths the adjustment set fails to block. Each target's condition-(b) verdict is a lookup rather than a new traversal [§sec_12].

**Per-target verdict has two cases:**

- If the target is in the estimated adjustment set, the estimate predicts the marginal; this is correct only when the true effect is null.
- Otherwise, condition (a) rejects an adjustment set containing a descendant of a source child that still reaches the target [sid.py:L183].

**`rondp` records arrival direction.** Each node is tagged as entered by an outgoing or incoming edge because non-blocking depends on that direction [§sec_12].

A node reached through an incoming edge propagates to parents under different conditions than one reached through an outgoing edge [§sec_12].

**The traversal needs a correction step.** Direction-tagged traversal can miss directed, non-blocked paths [§sec_12].

The auxiliary tails-removed path matrix finds reachable descendants with no adjustment node between. They are added back to the reachable set [§sec_12].

## The Math {#the-math}
**A two-node boundary case makes the count concrete:** for `true_dag = DAG([(1, 2)])` and `est_dag = DAG([(2, 1)])`, `SID()(true, est)` returns `2` because both possible ordered intervention pairs are wrong [sid.py:L256-L308].

**Why it is exactly 2:** the ordered pairs are $(1,2)$ and $(2,1)$.

For source 1, the estimate places target 2 in its adjustment set and predicts no effect. The true edge $1\to2$ makes the effect non-null, so this pair is wrong [sid.py:L183].

For source 2, `path_matrix[2,1]` is false, but the empty estimated parent set predicts a nonzero effect. This pair is also wrong, giving SID $=2$ out of 2 [sid.py:L183].

**Where fourth-power cost comes from:** transitive closure costs roughly $O(n^3)$ on an $n$-node graph [sid.py:L256].

Tails pruning depends on the source's estimated parent set, so closure is recomputed per source. $n$ sources times $O(n^3)$ gives $O(n^4)$: seconds at 100 nodes and about a minute at 200 [sid.py:L256].

**Why `rondp` terminates:** each node has at most two live states, one per arrival direction [§sec_12].

The reachable set adds each `(node, direction)` state once. Its at-most-$2n$ additions bound traversal regardless of the number of graph paths [§sec_12].

## Go Deeper {#go-deeper}
- **Implementation of SID** — the parent page these two algorithms live under; this page is the pseudocode-to-code mapping for it.
- **Causal Effects in Linear Gaussian SEMs** (prerequisite) — defines what a "real" causal effect is, which is exactly what Algorithm 1's null/non-null check is deciding per pair.
- **SID** (implements) — the metric whose value is the sum of incorrect pairs these algorithms produce.
- **`_sid_matrix()`** (implements) — the concrete function that carries out Algorithm 1's per-source, all-targets-at-once loop described above.

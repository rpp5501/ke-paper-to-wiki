# Metric Properties of SID
## TL;DR {#tldr}
SID behaves like a *pre-metric*, not a full metric: it is always non-negative and a graph has zero distance to itself, but it is not symmetric, and zero distance between two different DAGs does not mean they are the same graph. A wrong graph can still get an SID of 0 if it happens to preserve the right adjustment sets — even while having many extra edges. SID also relates to the more familiar Structural Hamming Distance (SHD) only in one direction: identical graphs (SHD = 0) always get SID = 0, but a small SHD gives no guarantee that SID is small.

## Intuition {#intuition}
Think of SID as asking "does this estimated graph give you the right answer for every intervention?" rather than "does this graph look like the true one edge-for-edit?" Two graphs can look very different edge-by-edit and still always give the right interventional answer — for instance, an estimate that draws in a pile of superfluous edges but never breaks a valid adjustment set. Conversely, a graph that is edit-distance-close to the truth can still get every intervention wrong, because SHD counts local edge mistakes while SID cares about a global, distributional consequence of those mistakes.

## Mechanics {#mechanics}
**SID satisfies non-negativity and reflexivity** — it is never negative, and a graph compared with itself scores zero — but it fails symmetry, so it only earns the weaker label of a pre-metric rather than a metric [§sec_2_3]. The asymmetry is concrete: comparing a non-empty graph against the empty DAG gives different scores depending on which one is treated as ground truth, because when the empty DAG is the truth, every node set is a trivially valid adjustment set, so an estimate built from it can never be "wrong" in that direction [§sec_2_3].

A more striking consequence is that **SID = 0 does not imply the two DAGs are equal**: a proposition characterizes exactly which graphs achieve zero distance to a fixed true DAG, and shows that an estimate can contain strictly more edges than the truth and still be perfect, because adding edges never invalidates a parent set that was already a correct adjustment set [§sec_2_3]. SID only penalizes an estimate when its parent-based adjustment set fails to match the true intervention distribution for some pair of nodes; overshooting the edge count doesn't trigger that failure the way undershooting it does [§sec_2_3].

Because zero SID admits this whole family of superset graphs, SID alone cannot distinguish the true DAG from any of its edge-supersets that preserve valid adjustment — recovering a metric with the identity-of-indiscernibles property requires pairing SID with a second measure that does penalize extra edges [§sec_2_3]. In practice, this superset condition is also only checkable approximately: computing whether the estimated parent set matches the true intervention distribution ultimately relies on a regression or feature-selection procedure applied to finite samples, so exact equality is a statistical question, not just a graphical one [§sec_2_3].

## The Math {#the-math}
The pre-metric property is the joint statement that $\mathrm{SID}(G,H) \geq 0$ and $\mathrm{SID}(G,G) = 0$, while symmetry, $\mathrm{SID}(G,H) = \mathrm{SID}(H,G)$, is explicitly **not** guaranteed — the empty-versus-non-empty-graph example above is a concrete witness that the two directions can differ [§sec_2_3].

The zero-distance characterization is an edge-set inclusion condition: for the true DAG $G$ and estimate $H$, if $G$ is a subgraph of $H$ (written $G \subseteq H$, i.e. every edge of $G$ is also an edge of $H$) and the resulting parent sets $\mathrm{pa}^H(j)$ remain valid adjustment sets, then $\mathrm{SID}(G,H) = 0$ regardless of how many additional edges $H$ has beyond $G$ [§sec_2_3]. This works because parent adjustment is validated pair-by-pair — a superset estimate can only add covariates to the adjustment set, and adjusting on more of the true ancestral structure never breaks the back-door-style argument that makes the parent set valid in the first place [§sec_2_3].

The relationship to SHD is a one-directional bound, not an equivalence:

| | triggers on | zero implies | bounded by the other? |
|---|---|---|---|
| SHD | any single edge insertion/deletion/reversal | graphs identical | no — SHD can be minimal while SID is maximal [§sec_2_3] |
| SID | any pair whose intervention distribution is computed wrong | interventional correctness for every pair (not graph identity) | SID = 0 whenever SHD = 0, but not conversely [§sec_2_3] |

Formally, $\mathrm{SHD}(G,H) = 0 \implies \mathrm{SID}(G,H) = 0$, and this implication is sharp: there exist $G, H$ with SHD as small as a single edge difference for which SID nonetheless attains its maximal possible value, which is exactly why SHD cannot be bounded in terms of SID [§sec_2_3].

## Go Deeper {#go-deeper}
- **Equivalent Graphical Formulation** (builds-on) — supplies the graphical criterion for when a parent set is a valid adjustment set, which is the mechanism this page's zero-distance proposition depends on.
- **Proof: SID for Superset Estimates** — the full proof that $G \subseteq H$ with valid $\mathrm{pa}^H(\cdot)$ forces $\mathrm{SID}(G,H) = 0$, only sketched here.
- **Proof: SID and SHD Relationship** — the full proof of the sharp bound showing SHD = 0 implies SID = 0 and why the converse direction cannot hold.

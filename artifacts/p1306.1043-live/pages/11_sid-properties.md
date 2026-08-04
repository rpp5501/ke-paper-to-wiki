# Metric Properties of SID
## TL;DR {#tldr}
The Structural Intervention Distance (SID) is not a true metric between DAGs — it satisfies the weaker properties of a pre-metric, and it is explicitly asymmetric: swapping the estimated and true graph can change the distance dramatically. Despite this, SID admits a clean characterization of when it equals zero, and it can be bounded in terms of the more familiar Structural Hamming Distance (SHD), though only in one direction.

## Intuition {#intuition}
Because SID counts intervention distributions that come out wrong, it behaves less like a symmetric notion of "distance" and more like a directional measure of how well one graph's adjustment sets work for the other. A graph with too many extra edges can still get every intervention distribution right, so it can achieve zero SID relative to the truth even though it looks structurally very different — this is why SID and SHD, which simply counts edge differences, can disagree sharply. Understanding these properties matters for interpreting SID scores in practice: a low SID doesn't necessarily mean a nearly-identical graph, and a small SHD doesn't guarantee a small SID.

## Mechanics {#mechanics}
The SID satisfies non-negativity and a form of triangle-like behavior sufficient to qualify as a pre-metric, but it fails symmetry: for a non-empty graph and the empty graph, the two directions of SID differ, since the empty DAG makes every set of nodes a valid adjustment set and therefore trivially "correct" in one direction but not the other [§sec_2_3]. Parent adjustment producing identical intervention distributions between two DAGs does not imply the reverse equality holds, and an accompanying example is used to illustrate graphs with matching intervention distributions in only one direction [§sec_2_3]. A key structural result characterizes exactly which DAGs achieve zero SID relative to a true DAG: an estimate can contain strictly more edges than the truth and still receive zero SID, provided it remains a supergraph in the appropriate subgraph-relation sense, because a superset of the true parent set is still a valid adjustment set [§sec_2_3]. This means SID does not penalize over-estimation of edges the way SHD does, which is the mechanical root of the loose/sharp bounds relating SID to SHD: SHD equal to zero forces SID to zero, but the converse bound is only sharp in the sense that SID can attain its maximal possible value even while SHD remains small, so SHD cannot be bounded from SID [§sec_2_3].

## The Math {#the-math}
The local context describes the pre-metric and zero-distance characterization propositions in prose but does not include the explicit equation blocks (no [eq_N] entries were provided), so no formal display equations can be reproduced here [§sec_2_3].

## Go Deeper {#go-deeper}
- **Equivalent Graphical Formulation** (builds-on) — provides the subgraph/adjustment-set formulation that this page's zero-SID characterization directly relies on.
- **Proof: SID for Superset Estimates** (defined-in) — contains the proof underlying the claim that supergraphs of the true DAG can achieve zero SID.
- **Proof: SID and SHD Relationship** (defined-in) — contains the proof of the loose/sharp bounds relating SID to SHD referenced above.
- No research note is attached to this concept, so no external research resources are listed.

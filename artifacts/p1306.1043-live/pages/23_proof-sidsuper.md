# Proof: SID for Superset Estimates

## TL;DR {#tldr}
This proof establishes a key robustness property of the Structural Intervention Distance: when an estimated causal graph is a valid supergraph-style relaxation of the true DAG (agreeing on directed reachability and separations), the SID between them is exactly zero, and conversely, adding a spurious edge that violates this relationship forces the SID to be nonzero. It is one of the metric-property results that justify treating SID as a meaningful, non-arbitrary measure of causal-graph estimation quality rather than an ad hoc score.

## Intuition {#intuition}
The core idea is that SID counts how many interventional distributions are gotten wrong, so a graph estimate can still be judged "correct" for causal purposes even if it isn't a perfect edge-for-edge match to the truth. As long as an estimated graph preserves the essential structural relationships — every directed path in the true graph survives, and every path that should be blocked stays blocked — no intervention prediction actually goes wrong, so the distance is zero. The proof's other half shows this can't be cheated: introduce even one edge that breaks that alignment, and there exists a concrete data-generating scenario where a valid intervention prediction is guaranteed to fail, pinning the SID above zero.

## Mechanics {#mechanics}
The proof proceeds by cases on a hypothesized structural relationship between the true DAG and its estimate, first assuming the relationship holds and then assuming it is violated. In the first case, any node lying on a directed path in the estimated graph is shown to also lie on a directed path in the true graph, which secures the first of the two conditions needed for a zero SID contribution [§sec_9]. The second condition is handled by an argument about path-blocking: any non-directed path present in the estimated graph is also a path in the true graph and must therefore be blocked there too, and the proof notes the general fact that a path blocked in a DAG remains blocked in any smaller DAG derived from it [§sec_9].

The converse direction is established by explicit construction: assuming the estimated graph contains an edge that violates the structural relationship, the proof builds an observational distribution consistent with the true DAG using a specified parameterization, choosing coefficients so that most edges carry a fixed weight except one designated edge, which is set to zero [§sec_9]. Under this construction, the resulting distribution yields differing conditional-independence behavior between the true and estimated graphs for the endpoints of that edge, which directly forces the SID to be nonzero rather than merely large [§sec_9].

## The Math {#the-math}
The local context for this proof is presented entirely in prose rather than as tagged display equations — the argument references a parameterized structural equation model and a specific edge-weight assignment, but no [eq_N]-labeled formulas are given in the provided material, so none are reproduced here [§sec_9].

## Go Deeper {#go-deeper}
No research note or additional resources were provided alongside this concept.

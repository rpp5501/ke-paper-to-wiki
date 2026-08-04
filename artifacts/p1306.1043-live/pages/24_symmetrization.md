# Symmetrization of SID {#symmetrization-of-sid}

## TL;DR {#tldr}
When neither DAG in a comparison can be treated as ground truth relative to the other, SID needs a symmetric variant — Symmetrization of SID builds on Structural Intervention Distance (SID) by combining the two directional distances into a single score that doesn't privilege one graph as "true" and the other as "estimated."

## Intuition {#intuition}
Ordinary SID is inherently directional: it counts how many interventional distributions from one DAG fail to be reproduced when treating the other DAG as an estimate. That makes sense when you're grading an estimated graph against a known ground truth, but it breaks down when comparing two graphs on equal footing — say, two estimates from different algorithms, or two hypotheses with no privileged "correct" one. The symmetrized version fixes this by folding the two one-directional comparisons into one number, so swapping the order of the two graphs doesn't change the result.

## Mechanics {#mechanics}
The motivating case is two DAGs where neither can be regarded as an estimate of the other, which calls for a symmetrized version of the SID rather than the directional definition [§sec_2_4_4]. The authors note that while they believe this symmetrized construction suits most practical purposes, it is not the only way to build a symmetric variant of SID [§sec_2_4_4]. As an alternative construction, one could instead count all node pairs for which the intervention distributions coincide for every distribution that is Markov with respect to *both* graphs [§sec_2_4_4]. That alternative has a notable degeneracy: it would always yield a distance of zero whenever one of the two argument graphs is the empty graph, since the empty graph is trivially compatible with any distribution [§sec_2_4_4].

## The Math {#the-math}
The local context describes the symmetrization construction and its alternative in prose rather than supplying a labeled display equation; no [eq_N] entries are available for this concept, so no equation block is reproduced here [§sec_2_4_4].

## Go Deeper {#go-deeper}
No research note is attached to this concept — none (no research note for this concept).

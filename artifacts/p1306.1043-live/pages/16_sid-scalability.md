# Scalability of the SID
## TL;DR {#tldr}
This concept looks at how the runtime of computing the Structural Intervention Distance grows as graphs get bigger, building directly on the practical implementation of SID. The short version: cost grows roughly quadratically for sparse graphs and cubically for dense graphs as the number of nodes increases.

## Intuition {#intuition}
Knowing an algorithm's correctness is only half the story — you also need to know whether it stays usable as problems grow. Here the authors empirically clock how long SID takes to compare two random graphs as node count increases, separately for sparse and dense graph structures, since density can change how expensive the underlying computation becomes. The takeaway is a practical scalability profile rather than a tight theoretical bound: SID remains tractable at moderate scale, but its cost climbs faster for densely connected graphs than for sparse ones.

## Mechanics {#mechanics}
The experiment measures processor time to compute the SID between two random graphs, repeating this for a range of node counts and using the same sparse/dense graph generation setup established earlier in the paper [§sec_3_3]. For each node count, results are summarized as box plots over 100 pairs of graphs, separately for the sparse and dense settings, to capture the spread of runtimes rather than just a single average [§sec_3_3]. Reading across these box plots, the runtime trend as node count grows appears approximately quadratic for sparse graphs and approximately cubic for dense graphs, meaning denser structure imposes a noticeably steeper computational cost [§sec_3_3].

## The Math {#the-math}
The local context describes this scaling behavior only qualitatively, from the shape of the box plots, and does not provide an explicit equation or derived complexity formula for the runtime [§sec_3_3].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no additional external resources to list here.

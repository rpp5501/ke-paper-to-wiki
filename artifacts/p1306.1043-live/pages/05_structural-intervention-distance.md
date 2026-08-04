# Structural Intervention Distance (SID)
## TL;DR {#tldr}
Structural Intervention Distance (SID) is a metric for scoring how well an estimated causal DAG matches a true causal DAG, focused specifically on whether the two graphs would yield the same interventional predictions rather than just the same edges. It sits alongside Structural Hamming Distance (SHD) as a way of Comparing Estimated and True Causal Graphs, but where SHD counts edge-level mismatches, SID asks a causal question: for each pair of nodes, does the estimated graph give the correct adjustment set to compute the effect of intervening on one variable on another? This makes SID a more causally meaningful metric when the end goal is estimating Intervention Distributions rather than merely recovering graph topology.

## Intuition {#intuition}
Two DAGs can differ by only a single edge yet disagree wildly on which interventional queries they answer correctly, or conversely can look structurally different under SHD while still supporting the same valid adjustment sets for most variable pairs — SID is built to capture this gap. The core idea is to check, for every ordered pair of nodes in the graph, whether the parent set implied by the estimated DAG would let you correctly compute the causal effect of intervening on the first node on the second, using the true DAG's actual generating structure as the reference. Counting the pairs where this fails gives a distance that is directly tied to intervention correctness rather than pure graph-edit distance, which is why it contrasts with SHD and builds on standard DAG Terminology and definitions of Intervention Distributions.

## Mechanics {#mechanics}
The local context provided for this concept is limited to the section header "Structural Intervention Distance" (sec_2) with no accompanying body text describing the step-by-step procedure, so a detailed mechanical walkthrough cannot be honestly reproduced from the local context alone [§sec_2].

## The Math {#the-math}
No equations were supplied in the local context for this concept (no [eq_N] entries are present under sec_2), so no formal SID equation can be reproduced here without fabricating content [§sec_2].

## Go Deeper {#go-deeper}
- Motivation and Definition of SID — the part-of section that should contain the formal definition and rationale this page's Mechanics/Math sections are missing.
- SID between a DAG and a CPDAG — extends the base definition to handle Markov equivalence classes, relevant once the true graph is only known up to a CPDAG.
- Penalizing Additional Edges — addresses how SID treats false-positive edges, a subtlety not covered here.
- Symmetrization of SID — needed because base SID is asymmetric between estimated and true graphs.
- SID versus SHD Simulation — empirical comparison showing where the two metrics diverge in practice.
- Implementation of SID — practical reference for computing the metric.
- Hidden Variables (Future Work) / Multiple Interventions (Future Work) — noted extensions beyond the current definition.

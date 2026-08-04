# Alternative Adjustment Sets
## TL;DR {#tldr}
Structural Intervention Distance (SID) needs an adjustment set to determine whether an intervention's effect is correctly identified by a candidate DAG, and the parent set is the default choice — but it isn't the only valid one. Minimal adjustment sets offer a smaller, whole-graph-dependent alternative, and swapping between the two choices turns out to barely change the resulting SID score in practice.

## Intuition {#intuition}
Think of an adjustment set as the "control variables" you'd condition on to isolate a causal effect. The most convenient choice is a node's direct parents, since they're cheap to read off the local neighborhood of the intervened node. A more surgical choice is the smallest possible set that still blocks all confounding paths — harder to find because it requires looking at the entire graph, not just the immediate neighborhood, but rewarding in principle because a smaller conditioning set is easier to reason about and estimate. The reassuring finding behind this concept is that SID's verdict on how well one DAG approximates another doesn't hinge much on which of these two adjustment strategies you pick.

## Mechanics {#mechanics}
This work computes SID using the parent set as the adjustment set for each intervened node, favoring it because it is easy to compute and depends only on the neighbourhood of the intervened nodes, which is why it is widely used in practice [§sec_2_4_5]. The authors note that this is a design choice rather than a necessity: any other method for computing adjustment sets in a graph could be substituted in its place [§sec_2_4_5]. The competing option is an adjustment set of minimal size, which is harder to compute but yields a smaller conditioning set, and unlike the parent set it depends on the whole graph rather than just local structure [§sec_2_4_5]. Because a minimal adjustment set need not be unique, the authors resolve ties by taking the smallest set their computational algorithm finds first [§sec_2_4_5].

## The Math {#the-math}
The local context describes this comparison qualitatively — via an experiment on randomly generated dense graphs comparing SID under parent adjustment versus minimal adjustment — but provides no equations for how either adjustment set or SID itself is computed, so no display equations can be reproduced here [§sec_2_4_5]. The empirical result of that experiment is that the two SID variants are exactly equal in about of the cases (figure value not resolved in the source text), and their differences are rather small overall, especially compared to the gap between SID and SHD [§sec_2_4_5].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.

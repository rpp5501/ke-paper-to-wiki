# Alternative Adjustment Sets
## TL;DR {#tldr}

SID needs *some* adjustment set at each node to compute the interventional distribution it compares against. The paper's default choice is the parent set, but it is not the only valid one — any set that satisfies a valid adjustment criterion works, and different choices can, in principle, give different SID values for the same pair of graphs.

## Intuition {#intuition}

Think of the parent set as the "local" answer: look at a node's direct causes in the DAG and you're done, no need to consult the rest of the graph. A minimal adjustment set is the "global" answer: it asks, across the whole graph, what is the *smallest* set of variables that still blocks every confounding path into the node. Smaller conditioning sets are statistically nicer — fewer variables to condition on, less variance, less risk of accidentally conditioning on a collider — but finding them costs more, because you can't determine them from a single node's neighborhood.

## Mechanics {#mechanics}

The parent set is attractive for exactly the reason SID uses it by default: it is read directly off the local structure of the DAG, requiring no search over the rest of the graph, and it is guaranteed to satisfy the back-door criterion because any confounding path into a node must pass through one of its parents [§sec_2_4_5].

A **minimal adjustment set** trades that locality for size: it is the smallest set of variables satisfying a valid adjustment criterion, and unlike the parent set it can depend on nodes arbitrarily far away in the graph, not just on the intervened node's immediate neighborhood [§sec_2_4_5].

Concretely, suppose node $X$ has two parents, $Z_1$ and $Z_2$, but only $Z_2$ also has a path into the outcome $Y$ that doesn't go through $X$ — $Z_1$ affects $X$ but nothing else relevant to $Y$. The parent set $\{Z_1, Z_2\}$ still blocks the back-door path (it's always valid), but it is not minimal: $\{Z_2\}$ alone already blocks it, since $Z_1$ never lies on a back-door path to $Y$ in the first place [§sec_2_4_5].

Minimality is not the same as uniqueness: a graph can have several different minimal adjustment sets of the same smallest size, and the paper's implementation resolves this by taking whichever one its search algorithm happens to find first, not by any canonical tie-breaking rule [§sec_2_4_5].

## The Math {#the-math}

No display equation is attached to this section — the contribution here is empirical, not formal, so the load-bearing content is the comparison itself rather than a derivation [§sec_2_4_5].

The comparison is run on randomly generated dense DAGs, computing SID once with parent-set adjustment and once with minimal-adjustment-set adjustment for every pair, and then measuring how often the two values coincide and how large the gap is when they don't [§sec_2_4_5].

The headline result is a near-equivalence: the two SID variants agree exactly in a large majority of the sampled graph pairs, and where they disagree, the gap between them is small — markedly smaller than the gap between SID and SHD reported elsewhere in the paper [§sec_2_4_5]. That last comparison is the one doing the real work: it says the *choice of adjustment set* is a second-order concern for SID, dwarfed by the first-order fact that SID and SHD measure genuinely different things [§sec_2_4_5].

The practical payoff is a justification for the default: since minimal adjustment sets are more expensive to compute (they require examining the whole graph, versus a constant-time local lookup for parents) and recent polynomial-time algorithms for finding them are a comparatively recent development, the parent set is the better engineering trade-off when the resulting SID values are nearly the same anyway [§sec_2_4_5].

## Go Deeper {#go-deeper}

- **Motivation and Definition of SID** — this is the concept alternative adjustment sets builds on; read it first to see what SID's own default adjustment (the parent set) is being compared against, and why an adjustment set is needed at all.

# Multiple Interventions (Future Work)
## TL;DR {#tldr}

SID as defined only scores predictions about intervening on *one* node at a time. Extending it to simultaneous interventions on several nodes is flagged as an open problem: the core comparison idea survives, but the machinery that made the single-node case tractable — parent sets as automatic adjustment sets, a small number of things to enumerate — does not carry over cleanly, and the graphical criterion at SID's heart still cannot weigh how strong an edge is.

## Intuition {#intuition}

SID's whole strategy is to ask, for each node, "does the estimated graph's parent set let me correctly predict this node's response to an intervention?" and count the failures. That strategy leans on a convenient fact about single-node interventions: the parents of the intervened node are always a valid adjustment set in the true DAG, so the comparison is well-defined and cheap to compute for every node.

Move to interventions on several nodes at once, and that convenience disappears. There's no longer one obvious adjustment set to fall back on, and the number of things you'd need to check explodes combinatorially instead of growing linearly with the number of nodes. The extension is conceptually straightforward to state and hard to make concrete — which is exactly the status the text itself assigns it.

## Mechanics {#mechanics}

**The comparison still makes sense, but the adjustment set doesn't come for free:** a modified version of the underlying lemma continues to hold for sets of intervened nodes, but the union of their parent sets is no longer guaranteed to be a valid adjustment set — even in the *true* causal graph. Single-node SID gets this validity for free; multi-node SID would need a separate, explicitly defined canonical rule for choosing a valid adjustment set before any comparison could even be attempted [§sec_2_4_7].

**Enumeration replaces a single loop:** single-node SID walks over each node once. Multi-node SID would need to walk over every possible *set* of intervened nodes, of every possible size, crossed with every possible target node — turning one manageable pass over the graph into a combinatorial search whose cost is discussed below [§sec_2_4_7].

**The practical fallback is k = 2:** given that full generality is expensive, the suggested starting point is restricting to interventions on exactly two nodes at a time, which keeps the counting problem to a single binomial term instead of a sum over all set sizes [§sec_2_4_7].

**A graphical criterion still can't see edge strength:** even setting aside the multi-intervention question, SID's use of a graphical (adjustment-set) criterion means it is blind to *how strong* an edge is — it can only see whether the graphical relationship needed for a correct prediction is present or absent. Two estimated graphs that differ from the truth by the same single edge get the same SID penalty regardless of whether that edge represents a strong or a negligible causal effect [§sec_2_4_7].

**The section's own status is unsettled:** the local text carries embedded reviewer commentary suggesting the multiple-interventions discussion is a "very loose description of open problems" worth cutting, and that the broader Extensions material should instead be reorganized around the symmetrized version and PDAGs. That is a signal about how load-bearing this material is, not a result to build on [§sec_2_4_7].

## The Math {#the-math}

No adjustment-set formula is fixed for the multi-intervention case in the text — that is precisely the open problem. What *is* concrete is the shape of the combinatorial blowup, which is worth working through with numbers.

For a graph on $p$ nodes, fix an intervention-set size $k$ (the number of nodes intervened on simultaneously). The number of ways to choose which $k$ nodes are intervened on is $\binom{p}{k}$, and for each choice, any of the remaining $p-k$ nodes can serve as the target whose response distribution you're predicting. So the number of intervention distributions to check at multiplicity $k$ is $\binom{p}{k}(p-k)$, and the total across all multiplicities is the sum of this term over $k$ [§sec_2_4_7].

```derivation
shape: How many intervention distributions multi-node SID would need to check, worked for a small graph.
steps:
  - latex: "\\#\\{\\text{distributions at multiplicity } k\\} = \\binom{p}{k}(p-k)"
    why: "Choose which k of p nodes are intervened on, then pick a target from the p-k that remain — this is the combinatorial cost single-node SID (k=1) avoids by only ever having p choices total [§sec_2_4_7]"
  - latex: "\\text{single-node SID}\\ (k=1),\\ p=5:\\quad \\binom{5}{1}(5-1) = 20"
    why: "This is the baseline: 20 node-level checks, linear in p, matches how SID actually scales today [§sec_2_4_7]"
  - latex: "\\text{practical proposal}\\ (k=2),\\ p=5:\\quad \\binom{5}{2}(5-2) = 30"
    why: "Already larger than the single-node case despite p being unchanged — this is the case the text recommends tackling first, before the general problem [§sec_2_4_7]"
  - latex: "\\text{full generality},\\ p=5:\\quad \\sum_{k=1}^{4}\\binom{5}{k}(5-k) = 20+30+20+5 = 75"
    why: "Summing over every multiplicity from 1 to p-1 shows the total blows up well past linear even at p=5 — this is the computational-complexity obstacle the text points to, without yet naming a fix [§sec_2_4_7]"
```

The graph-strength blindness noted in Mechanics has a similarly concrete boundary case: take two estimated graphs $H_1, H_2$ that are identical to each other and to the true graph $G$ except for one edge, where $H_1$'s edge implies a near-zero causal effect and $H_2$'s implies a large one. Because SID is defined purely by whether the adjustment-set criterion succeeds or fails, both $H_1$ and $H_2$ receive the same SID score relative to $G$ — the metric cannot distinguish a cosmetic structural error from one that materially changes predictions [§sec_2_4_7].

## Go Deeper {#go-deeper}

- **[[structural-intervention-distance]]** — the base metric this section is extending; read it first since every limitation described here (adjustment-set validity, single-node scope) is a property of that definition being pushed past where it was built to work.

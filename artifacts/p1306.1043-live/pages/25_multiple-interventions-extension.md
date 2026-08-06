# Multiple Interventions (Future Work)
## TL;DR {#tldr}

SID scores interventions on one node at a time. Simultaneous multi-node interventions remain an open problem.

The comparison idea survives, but automatic parent adjustment and small enumeration do not. SID's graphical criterion also cannot weigh edge strength.

## Intuition {#intuition}

SID asks whether the estimated parent set correctly predicts each node's intervention response, then counts failures.

For one-node interventions, the intervened node's parents are always a valid true-DAG adjustment set. That makes comparison well-defined and cheap.

For several simultaneous interventions, no obvious adjustment set remains.

The number of checks grows combinatorially, not linearly. The extension is easy to state but hard to make concrete.

**Boundary case:** when an intervention set has size one, the proposal collapses to ordinary SID and parent adjustment is canonical. At size two, even the union of the two parent sets need not be valid, which is why the extension remains open [§sec_2_4_7].

## Mechanics {#mechanics}

**The comparison still makes sense, but adjustment no longer comes for free.** A modified lemma holds for intervention sets, but their union of parents need not be valid even in the true graph [§sec_2_4_7].

Multi-node SID needs an explicit canonical rule for choosing a valid set before comparison begins [§sec_2_4_7].

**Enumeration replaces a quadratic baseline:** one-node SID has $p(p-1)$ ordered source-target intervention distributions [§sec_2_4_7].

Multi-node SID combines every intervention set at every size with every remaining target. The count is combinatorial [§sec_2_4_7].

**The practical fallback is k = 2:** given that full generality is expensive, the suggested starting point is restricting to interventions on exactly two nodes at a time, which keeps the counting problem to a single binomial term instead of a sum over all set sizes [§sec_2_4_7].

**A graphical criterion cannot see edge strength.** SID records whether a needed graphical relationship is present, not how strong its causal effect is [§sec_2_4_7].

The same one-edge error receives the same penalty whether its causal effect is large or negligible [§sec_2_4_7].

**The section's status is unsettled:** embedded reviewer commentary calls this a loose open-problems description and suggests reorganizing Extensions around symmetrization and PDAGs [§sec_2_4_7].

That is a signal about the material's load-bearing status, not a result to build on.

## The Math {#the-math}

No multi-intervention adjustment-set formula is fixed; that is the open problem.

The combinatorial blowup is concrete enough to count.

For $p$ nodes and intervention-set size $k$, choose the set in $\binom{p}{k}$ ways.

Each choice leaves $p-k$ targets. The multiplicity-$k$ count is $\binom{p}{k}(p-k)$, and the full count sums it over $k$ [§sec_2_4_7].

```derivation
shape: How many intervention distributions multi-node SID would need to check, worked for a small graph.
steps:
  - latex: "\\#\\{\\text{distributions at multiplicity } k\\} = \\binom{p}{k}(p-k)"
    why: "Choose which k of p nodes are intervened on, then pick a target from the p-k that remain — this is the combinatorial cost single-node SID (k=1) avoids by only ever having p choices total [§sec_2_4_7]"
  - latex: "\\text{single-node SID}\\ (k=1),\\ p=5:\\quad \\binom{5}{1}(5-1) = 20"
    why: "This is the baseline: p(p-1), which is quadratic in p; at p=5 it gives 20 ordered source-target checks [§sec_2_4_7]"
  - latex: "\\text{practical proposal}\\ (k=2),\\ p=5:\\quad \\binom{5}{2}(5-2) = 30"
    why: "Already larger than the single-node case despite p being unchanged — this is the case the text recommends tackling first, before the general problem [§sec_2_4_7]"
  - latex: "\\text{full generality},\\ p=5:\\quad \\sum_{k=1}^{4}\\binom{5}{k}(5-k) = 20+30+20+5 = 75"
    why: "Summing over every multiplicity from 1 to p-1 shows the total blows up well past linear even at p=5 — this is the computational-complexity obstacle the text points to, without yet naming a fix [§sec_2_4_7]"
```

Consider $H_1,H_2$ differing from true $G$ by one edge. In $H_1$ it has near-zero effect; in $H_2$ it has a large effect [§sec_2_4_7].

Both receive the same SID because adjustment validity either succeeds or fails. SID cannot distinguish a cosmetic error from one that materially changes predictions [§sec_2_4_7].

## Go Deeper {#go-deeper}

- **[[structural-intervention-distance]]** — the base metric this section is extending; read it first since every limitation described here (adjustment-set validity, single-node scope) is a property of that definition being pushed past where it was built to work.

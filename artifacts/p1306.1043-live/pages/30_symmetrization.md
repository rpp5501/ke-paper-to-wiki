# Symmetrization of SID
## TL;DR {#tldr}
SID is directional: `SID(G,H)` need not equal `SID(H,G)` because one graph is truth and one estimate.

When neither graph is privileged, symmetrization avoids choosing truth arbitrarily.

## Intuition {#intuition}
SID counts source-target pairs with wrong intervention predictions from estimated parent sets.

This is inherently one-way: swapping the true graph generally changes the count.

Learned versus known graphs have a natural SID direction. Two experts' models, two outputs, or two hypotheses do not.

Symmetrization combines both directions into one number.

## Mechanics {#mechanics}
**Why symmetrization is needed:** SID fixes a true DAG, so it is a pre-metric that can be asymmetric and fail triangle inequality [§sec_2_4_4].

When neither DAG is an estimate, standard ordering is undefined. A rule must combine both orderings [§sec_2_4_4].

**The suggested construction:** compute SID in both directions and take their arithmetic mean, rather than picking a direction by fiat [§sec_2_4_4].

```algorithm
title: Symmetrized SID
lines:
  - code: "d1 = SID(G, H)"
    intent: "Treat G as ground truth and H as the estimate, exactly as in the base definition [§sec_2_4_4]"
  - code: "d2 = SID(H, G)"
    intent: "Swap roles since neither graph is privileged as the true one [§sec_2_4_4]"
  - code: "return (d1 + d2) / 2"
    intent: "Average the two directed distances, including the normalization by two stated in the paper [§sec_2_4_4]"
```

**This is one choice, not the only one.** The arithmetic mean suits most practical cases but is not uniquely correct [§sec_2_4_4].

**The alternative:** directly count `(i,j)` pairs whose intervention distributions fail to agree for every distribution Markov to both graphs [§sec_2_4_4].

**Why the alternative is broken:** an empty graph forces mutual independence for distributions Markov to both graphs [§sec_2_4_4].

Pairwise agreement then becomes vacuous, yielding zero distance against any non-empty graph. The arithmetic mean avoids this failure [§sec_2_4_4].

## The Math {#the-math}
The base object is the directed distance itself, taken in each order:

```derivation
shape: Build a symmetric distance out of two directed SID evaluations.
steps:
  - latex: "\\mathrm{SID}(G,H) \\neq \\mathrm{SID}(H,G) \\text{ in general}"
    why: "SID fixes one graph as ground truth, so the two orderings answer different questions and need not agree [§sec_2_4_4]"
  - latex: "\\mathrm{SID}_{\\mathrm{sym}}(G,H) = \\frac{\\mathrm{SID}(G,H) + \\mathrm{SID}(H,G)}{2}"
    why: "Neither graph is designated the truth, so the two directed evaluations are averaged; dividing by two preserves the original SID scale [§sec_2_4_4]"
```

**The rejected alternative, made explicit:** define a pair `(i,j)` as "matching" only if the two graphs' induced intervention distributions coincide for every distribution Markov with respect to *both* `G` and `H`, then count the non-matching pairs [§sec_2_4_4].

```annotated-eq
latex: "\\#\\{(i,j): i\\neq j,\\ \\lnot\\big(p(y\\mid \\mathrm{do}(x_i=a)) \\text{ agrees } \\forall\\, P \\text{ Markov to } G \\text{ and } H\\big)\\}"
terms:
  - tex: "\\forall\\, P \\text{ Markov to } G \\text{ and } H"
    role: 2
    words: "The intersection of two Markov constraints — the source of the degeneracy, since intersecting with the empty graph's Markov class is very restrictive [§sec_2_4_4]"
  - tex: "\\#\\{(i,j): \\dots\\}"
    role: 1
    words: "A pair-count, structurally the same shape as base SID, but symmetric by construction rather than by combining two directed scores [§sec_2_4_4]"
```

**Boundary case:** let `H` be empty. Its Markov distributions make every variable mutually independent [§sec_2_4_4].

The shared Markov class therefore makes intervention and observation agree for every pair. Non-matching count is always zero [§sec_2_4_4].

The alternative declares empty `H` indistinguishable from every `G`, the opposite of a useful distance. This explains the two-direction recommendation [§sec_2_4_4].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the parent concept this section modifies; read it first, since symmetrization only makes sense once you know why the base definition is directional (one graph fixed as ground truth, the other supplying adjustment sets) [§sec_2_4_4].

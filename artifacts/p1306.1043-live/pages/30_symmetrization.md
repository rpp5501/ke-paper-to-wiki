# Symmetrization of SID
## TL;DR {#tldr}
SID is directional: it treats one graph as ground truth and the other as an estimate of it, so `SID(G,H)` need not equal `SID(H,G)`. When neither graph is privileged — you just have two candidate causal structures to compare — you need a version that doesn't force an arbitrary choice of which one plays "truth." Symmetrization builds that version out of the original SID.

## Intuition {#intuition}
Structural Intervention Distance is built on top of intervention distributions: it counts how many (source, target) pairs would give the wrong interventional prediction if you used the estimated graph's parent sets to compute a causal effect that's actually determined by the true graph. That's inherently a one-way comparison — swap which graph you call "true" and the count generally changes.

Most uses of SID have a natural direction (a learned graph estimating a known one), so the asymmetry is fine. But sometimes you're comparing two graphs on equal footing — two experts' models, two algorithms' outputs, two hypotheses — where calling either one "ground truth" is arbitrary. Symmetrization removes that arbitrary choice by combining both directions into a single number.

## Mechanics {#mechanics}
**Why symmetrization is needed:** SID is defined relative to a fixed true DAG, so it is a pre-metric rather than a metric — it can be asymmetric and doesn't have to satisfy the triangle inequality. Comparing two DAGs where neither is designated as the estimate of the other means the ordering used in the standard definition is undefined, so some rule for combining the two possible orderings is required [§sec_2_4_4].

**The suggested construction:** compute SID in both directions and combine them into one symmetric number, rather than picking a direction by fiat [§sec_2_4_4].

```algorithm
title: Symmetrized SID
lines:
  - code: "d1 = SID(G, H)"
    intent: "Treat G as ground truth and H as the estimate, exactly as in the base definition [§sec_2_4_4]"
  - code: "d2 = SID(H, G)"
    intent: "Swap roles since neither graph is privileged as the true one [§sec_2_4_4]"
  - code: "return combine(d1, d2)"
    intent: "Fold the two directed distances into a single symmetric distance [§sec_2_4_4]"
```

**This is one choice, not the only one:** the note is explicit that other symmetrizations are possible, and the two-direction combination is offered because it fits most practical use cases, not because it's uniquely correct [§sec_2_4_4].

**The alternative construction:** instead of combining two directed SID scores, redefine what counts as a "wrong" pair directly in symmetric terms — count `(i,j)` such that the intervention distribution for that pair agrees across *every* distribution consistent with both graphs' Markov properties simultaneously [§sec_2_4_4].

**Why that alternative is broken:** if one of the two graphs is the empty graph, then "Markov with respect to both graphs" collapses to a degenerate class of distributions (Markov to the empty graph already forces mutual independence), and the pairwise agreement condition becomes vacuously satisfiable — producing zero distance regardless of how different the non-empty graph is from the empty one [§sec_2_4_4]. That failure mode is precisely why the min-style, two-direction combination is the recommended default rather than this coincidence-counting variant.

## The Math {#the-math}
The base object is the directed distance itself, taken in each order:

```derivation
shape: Build a symmetric distance out of two directed SID evaluations.
steps:
  - latex: "\\mathrm{SID}(G,H) \\neq \\mathrm{SID}(H,G) \\text{ in general}"
    why: "SID fixes one graph as ground truth, so the two orderings answer different questions and need not agree [§sec_2_4_4]"
  - latex: "\\mathrm{SID}_{\\mathrm{sym}}(G,H) = \\mathrm{combine}\\big(\\mathrm{SID}(G,H),\\ \\mathrm{SID}(H,G)\\big)"
    why: "Neither graph is designated the truth, so both directed evaluations are computed and folded into one number [§sec_2_4_4]"
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

**Boundary case that exposes the problem:** let `H` be the empty graph (no edges at all). Every distribution Markov with respect to the empty graph already has all variables mutually independent, so the "Markov to both `G` and `H`" class only contains distributions where interventional and observational predictions trivially agree for any pair [§sec_2_4_4]. The non-matching-pair count is then always zero, so this alternative reports the empty graph as indistinguishable from every `G` — the opposite of a useful distance, since the empty graph is the sparsest possible hypothesis and should generally score *worse*, not identically, against a non-trivial `G` [§sec_2_4_4]. This is the concrete failure the note uses to explain why the two-direction combination is the recommended default instead.

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the parent concept this section modifies; read it first, since symmetrization only makes sense once you know why the base definition is directional (one graph fixed as ground truth, the other supplying adjustment sets) [§sec_2_4_4].

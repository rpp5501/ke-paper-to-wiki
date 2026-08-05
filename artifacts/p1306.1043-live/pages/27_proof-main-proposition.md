# Proof: Equivalence of Definitions

## TL;DR {#tldr}
This concept is the proof that closes the gap between how SID is originally defined and the graphical criterion actually used to compute it. The Definition asks a distributional question — does intervening on variable *i* in the true graph change the distribution of *j* in a way that graph *H*'s adjustment fails to reproduce? The Proposition replaces that with a purely graphical test that can be checked by looking at ancestors and parent sets, no probability calculus required. The proof shows these two tests never disagree: the set of pairs flagged as "mismatched" is exactly the same either way, which is what licenses computing SID graphically instead of by simulating interventions.

## Intuition {#intuition}
The proof is a set-equality argument, and set equality always splits into two halves: everything the Definition flags must also be flagged by the Proposition, and vice versa. Rather than proving this in one sweep, the argument case-splits on a single fact — whether *j* is an ancestor of *i* — because that fact alone decides whether intervening on *i* can possibly move *j*'s distribution at all.

When *j* isn't downstream of the intervened node, there's a clean reason the distributions can't differ: you can integrate away everything that isn't feeding into *j*, and what's left doesn't care whether *i* was intervened on. When *j* is downstream, the two definitions are shown to agree by producing an actual example — a concrete causal model — where the mismatch demonstrably occurs, rather than arguing it abstractly. That mix of "clean invariance" for one case and "explicit witness" for the other is what makes the proof work in both directions.

## Mechanics {#mechanics}
**The proof strategy is double inclusion.** Writing the pair-set from the Definition and the pair-set from the Proposition, the proof shows each is a subset of the other, so they coincide as sets of index pairs $(i,j)$ [§sec_8].

**Each direction case-splits on the ancestor relation between $i$ and $j$.** In the forward direction, taking a pair from the Definition's set: if $j$ is not an ancestor of $i$ (equivalently $i$ is upstream of $j$, since one of the two must hold), an invariance argument shows the interventional and observational distributions of $x_j$ coincide, which places the pair in the Proposition's set via eq_11 [eq_11]. If instead the ancestor relation goes the other way, a separate lemma is invoked directly to show the Proposition's criterion is violated, again placing the pair in the target set [§sec_8].

**The invariance step relies on a closure property of ancestor sets.** The equality in eq_11 holds because parents of ancestors of $j$ are themselves ancestors of $j$ — the ancestor set of $j$ is closed under taking parents. This closure is exactly what licenses integrating out every non-ancestor variable one at a time, starting from the sink nodes and working inward, without ever needing to touch a variable inside the ancestor set [eq_11].

**The reverse direction mirrors the structure but needs a constructive witness.** Taking a pair from the Proposition's set, the case where the ancestor relation matches again falls out of the same invariance fact. The other case is handled not by a general argument but by exhibiting a specific linear Gaussian structural equation model — unit error variances, linear structural equations matching the graph — for which the interventional distributions are shown explicitly to differ, which is what forces the pair into the Definition's set [§sec_8].

**Both halves land in the same place: "in both cases we have" membership in the target set.** Because each of the four cases (two per direction) independently establishes membership, and the two directions together give both inclusions, the two pair-sets are proven identical [§sec_8].

## The Math {#the-math}

The workhorse identity is the interventional-equals-observational equality for non-descendants, introduced to justify why $j$ not being an ancestor-relevant target means the intervention on $i$ leaves $x_j$'s distribution untouched, ending in the equation reproduced below [eq_11]:

```derivation
shape: Show the interventional distribution of x_j collapses to its observational marginal when j is not affected by intervening on i.
steps:
  - latex: "p_{\\G}(x_j \\given \\doo(X_i = \\hat x_i)) = \\int_{\\text{anc}(j)} \\int_{\\text{non-anc}(j)} p(x_1, \\ldots, x_p \\given \\hat x_i) \\;d\\B{x}_{\\text{non-anc}(j)} \\;d\\B{x}_{\\text{anc}(j)}"
    why: "Split the joint post-intervention density into the ancestor block that can causally depend on x_j's causes and everything else, so the intervention's effect is localized to one factor [eq_11]"
  - latex: "= \\int_{\\text{anc}(j)} \\prod_{k \\in \\text{anc}(j)} p(x_k \\given x_{\\text{pa}(k)}) \\;d\\B{x}_{\\text{anc}(j)}"
    why: "Because parents of ancestors of j are themselves ancestors of j, the ancestor set is closed under taking parents, so non-ancestors can be integrated out from the sink nodes inward without leaving a dangling dependency on the intervened value [eq_11]"
  - latex: "= \\int_{\\text{anc}(j)} \\int_{\\text{non-anc}(j)} p(x_1, \\ldots, x_p) \\;d\\B{x}_{\\text{non-anc}(j)} \\;d\\B{x}_{\\text{anc}(j)} = p(x_j)"
    why: "The intervention value \\hat x_i has dropped out entirely, so what remains is exactly the observational marginal of x_j — the two definitions cannot disagree on this pair [eq_11]"
```

$$\begin{aligned}
p_{\G}(x_j \given \doo(X_i = \hat x_i)) &= \int_{\text{anc}(j)} \int_{\text{non-anc}(j)} p(x_1, \ldots, x_p \given \hat x_i) \;d\B{x}_{\text{non-anc}(j)} \;d\B{x}_{\text{anc}(j)}\\
&\overset{(\dagger)}{=} \int_{\text{anc}(j)} \prod_{k \in \text{anc}(j)} p(x_k \given x_{\text{pa}(k)}) \;d\B{x}_{\text{anc}(j)}\\
&= \int_{\text{anc}(j)} \int_{\text{non-anc}(j)} p(x_1, \ldots, x_p) \;d\B{x}_{\text{non-anc}(j)} \;d\B{x}_{\text{anc}(j)}
= p(x_j)
\end{aligned}$$ [eq_11]

**Why the $(\dagger)$ step is the load-bearing move:** it silently changes which variable the density is conditioned on — from "given $\hat x_i$" to an unconditional product over ancestors — and that swap is only valid because every ancestor's parents are already inside the integration domain, so no ancestor's conditional density secretly still depends on the clamped value of $x_i$ once its own upstream ancestors have been accounted for [eq_11].

**Where the proof needs more than the invariance identity:** eq_11 only handles the case where $j$ sits outside $i$'s downstream reach. When $j$ is a genuine descendant, no algebraic identity forces the distributions to differ in general — differing is a property of specific structural equations, not of the graph alone. That is why the reverse-direction case for descendants is closed with an explicit linear Gaussian SEM (unit error variances, equations linear in the parents, matching the graph's edge structure) rather than another identity: it is a minimal sufficient witness proving the mismatch is achievable, which is exactly what the direction of the proof needs to show membership in the Definition's pair set [§sec_8].

**The two remaining cases are handled by citation, not derivation:** whenever the ancestor relation fails to hold in the direction eq_11 needs, the proof falls back on a separate lemma to show the Proposition's graphical condition is violated. This is a genuine asymmetry in the proof's structure — one direction is closed algebraically, the other by an external result — worth noting if the surrounding claim in Proposition prop:main is being reused elsewhere [§sec_8].

## Go Deeper {#go-deeper}
- **Equivalent Graphical Formulation** — the parent concept this proof discharges; it states Proposition prop:main, i.e., the graphical criterion whose equivalence to the original intervention-distribution Definition is exactly what this proof establishes.

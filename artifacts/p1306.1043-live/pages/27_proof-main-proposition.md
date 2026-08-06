# Proof: Equivalence of Definitions

## TL;DR {#tldr}
This proof connects SID's distributional definition with its graphical computation criterion.

The Definition asks whether an intervention distribution is reproduced. The Proposition tests ancestors and parent sets instead.

The proof shows both flag exactly the same mismatched pairs, licensing graphical SID computation.

## Intuition {#intuition}
The proof is double inclusion: every Definition pair is a Proposition pair, and conversely.

Each direction splits on whether $j$ is an ancestor of $i$. That fact decides whether intervention on $i$ can move $j$'s distribution.

If $j$ is not downstream, integrate away variables that do not feed into $j$; intervention on $i$ disappears from its distribution.

For descendants, the proof uses an explicit causal-model witness with a mismatch. Invariance handles one case and a witness handles the other.

**Worked example:** for $(C,D)$ in shared truth $H$, candidate set $\{A\}$ leaves $C\leftarrow B\to D$ open. The graphical criterion rejects the pair, and the proof guarantees a distribution Markov to $H$ on which the corresponding intervention formulas disagree [§sec_8; eq_6].

## Mechanics {#mechanics}
**The proof strategy is double inclusion.** Writing the pair-set from the Definition and the pair-set from the Proposition, the proof shows each is a subset of the other, so they coincide as sets of index pairs $(i,j)$ [§sec_8].

**Each direction splits on ancestry.** In the forward direction, non-ancestry gives equality of interventional and observational $x_j$ distributions by eq. 11 [eq_11].

The other ancestry case invokes a separate lemma to show the Proposition's criterion fails [§sec_8].

**Invariance uses ancestor-set closure.** Parents of $j$'s ancestors are themselves ancestors of $j$ [eq_11].

That allows integration of non-ancestors from sink nodes inward without touching ancestor-set variables [eq_11].

**The reverse direction needs a witness.** One case again follows from invariance.

The other constructs a linear Gaussian SEM with unit error variances and graph-matching equations whose intervention distributions differ. This places the pair in the Definition's set [§sec_8].

**Both halves reach the same target.** The four cases establish membership, and the two inclusions prove the pair-sets identical [§sec_8].

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

**Why $(\dagger)$ is load-bearing:** it changes conditioning on $\hat x_i$ to an unconditional product over ancestors [eq_11].

That is valid because each ancestor's parents are already integrated. No remaining ancestor density depends on the clamped $x_i$ [eq_11].

**Why descendants need more than invariance:** eq. 11 handles targets outside $i$'s downstream reach [eq_11].

For descendants, distributional difference depends on structural equations, not graph shape alone. The proof therefore uses a linear Gaussian witness with unit error variances and graph-matching equations [§sec_8].

The witness proves mismatch is achievable, which is sufficient for Definition-set membership [§sec_8].

**Two cases are cited rather than derived.** When ancestry does not support eq. 11, a separate lemma shows the graphical condition fails [§sec_8].

The proof is intentionally asymmetric: one direction is algebraic and the other relies on an external result.

## Go Deeper {#go-deeper}
- **Equivalent Graphical Formulation** — the parent concept this proof discharges; it states Proposition prop:main, i.e., the graphical criterion whose equivalence to the original intervention-distribution Definition is exactly what this proof establishes.

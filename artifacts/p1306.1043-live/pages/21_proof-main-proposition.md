# Proof: Equivalence of Definitions

## TL;DR {#tldr}
This note walks through the proof that the interventional (Definition-based) characterization of a "mistake" in a causal graph and the purely graphical (Proposition-based) characterization pick out exactly the same set of ordered pairs. In other words, checking whether an intervention changes a variable's distribution is provably interchangeable with checking a graphical ancestry condition, which is what lets Structural Intervention Distance be computed efficiently from graph structure alone rather than by simulating interventions.

## Intuition {#intuition}
The proof is a two-way "sandwich" argument: take a pair flagged as a mistake under one definition and show it must also be flagged under the other, then do the same in reverse. The key intuitive move is that intervening on a variable only disturbs the distributions of its descendants downstream of the intervention point in a specific structural sense — everything that isn't causally "reachable" through ancestry can be integrated away without changing the answer. When that reachability condition fails, a concrete example (a simple linear Gaussian model) is used to certify that the graphical and interventional notions genuinely diverge unless the graphical condition is met, closing the loop between the two formulations referenced in this concept's neighborhood, the Equivalent Graphical Formulation.

## Mechanics {#mechanics}
The proof (Proposition, sec_8) fixes two sets of pairs — the set arising from Definition and the set arising from the Proposition — and shows one is a subset of the other, then the reverse containment, to conclude equality [§sec_8]. It proceeds by cases on whether the target node is an ancestor of the intervened node in the graph, since this ancestry relationship is exactly what controls whether integrating out non-ancestors is valid [§sec_8]. In the case where the ancestry condition fails, the proof invokes a Lemma to show the pair cannot satisfy the graphical-side condition either, matching set membership from that direction [§sec_8]. In the reverse direction, when the pair does satisfy the ancestry condition, the same integration argument is reused to show it lands in the Definition-based set, and when it does not, the Lemma is invoked again together with an explicit linear Gaussian structural equation model (unit error variances) used as a witness that the two distributions genuinely differ, forcing consistent case-by-case membership in both sets [§sec_8].

## The Math {#the-math}
The central computation shows that intervening on $X_i$ and marginalizing appropriately reduces to integrating only over the ancestors of $x_j$, because parents of ancestors are themselves ancestors — this is the step that licenses integrating out all non-ancestors starting from the sink nodes [eq_11]:

$$
p_{\G}(x_j \given \doo(X_i = \hat x_i)) &= \int_{\text{anc}(j)} \int_{\text{non-anc}(j)} p(x_1, \ldots, x_p \given \hat x_i) \;d\B{x}_{\text{non-anc}(j)} \;d\B{x}_{\text{anc}(j)}\\
&\overset{(\dagger)}{=} \int_{\text{anc}(j)} \prod_{k \in \text{anc}(j)} p(x_k \given x_{\text{pa}(k)}) \;d\B{x}_{\text{anc}(j)}\\
&= \int_{\text{anc}(j)} \int_{\text{non-anc}(j)} p(x_1, \ldots, x_p) \;d\B{x}_{\text{non-anc}(j)} \;d\B{x}_{\text{anc}(j)}
= p(x_j)
$$ [eq_11]

The final equality $p_{\G}(x_j \given \doo(X_i=\hat x_i)) = p(x_j)$ is exactly the interventional-invariance condition used to certify membership in the Definition-based set whenever the graphical ancestry condition holds, tying the two directions of the proof together through this one identity [eq_11].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here beyond the paper section itself — the primary source for further depth is sec_8 (Proof of Proposition) in the paper on Structural Intervention Distance.

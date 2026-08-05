# Proof: Equivalence of Definitions

## TL;DR {#tldr}
This proof shows that two ways of defining Structural Intervention Distance land on exactly the same count of pairs. The original Definition gives an operational, interventional characterization built from do-distributions; the Proposition restates it purely in graphical terms — ancestor/descendant relations and adjustment sets. Establishing that they agree means the practical, DAG-only algorithm for computing SID is not an approximation of the interventional definition, it *is* the definition, just read off the graph instead of off probability distributions.

## Intuition {#intuition}
Picture the two definitions as two witnesses answering the same question about a pair of nodes i and j: "does using the estimated parent set of i as an adjustment set still recover j's distribution correctly after intervening on i?" One witness reasons about interventional distributions and do-operators directly; the other only looks at the shape of the graph — who is whose ancestor, who is whose descendant. The proof walks every possible relationship between i and j and shows both witnesses reach the same verdict each time, so consulting the graphical witness is a matter of convenience, not a different question.

## Mechanics {#mechanics}
The proof establishes set equality between the pair-set from the Definition and the pair-set from the Proposition by showing each is a subset of the other, and each direction is split into the same two cases according to whether j is a descendant of i in the estimated graph. This double-inclusion, case-by-case structure is what lets a single lemma and a single integration argument cover both directions of the equivalence [§sec_8].

**Case where j is not a descendant of i** is handled by direct computation: the proof shows the interventional distribution of j collapses to its plain observational marginal whenever i is not an ancestor of j, using the truncated factorization of the joint density [§sec_8]. **Case where j is a descendant of i** is handled by appeal to a separate Lemma, which rules out the estimated parent set as a valid adjustment set whenever j sits downstream of i — no distributional computation is needed, membership follows structurally [§sec_8].

The integration argument behind the first case relies on a closure property: parents of ancestors of j are themselves ancestors of j. That closure means the non-ancestors of j can be integrated out one at a time starting from the sink nodes of the graph, each such integral collapsing to 1, without ever needing to touch the factors belonging to ancestors of j [§sec_8].

For the reverse inclusion, the non-descendant case is not settled by computation alone — the proof exhibits a specific linear Gaussian structural equation model, with unit error variances, realizing the graph structure in question [§sec_8]. Because the Definition is stated existentially over structural equation models, one explicit, closed-form instance is enough to witness that the graphical criterion's failure actually produces a distributional mismatch, closing the loop between the graphical and interventional sides [§sec_8].

## The Math {#the-math}
The workhorse identity is the truncated-factorization computation showing that intervening on X_i leaves j's marginal untouched whenever i is not an ancestor of j [eq_11]:

$$\begin{aligned}
p_{\G}(x_j \given \doo(X_i = \hat x_i)) &= \int_{\text{anc}(j)} \int_{\text{non-anc}(j)} p(x_1, \ldots, x_p \given \hat x_i) \;d\B{x}_{\text{non-anc}(j)} \;d\B{x}_{\text{anc}(j)}\\
&\overset{(\dagger)}{=} \int_{\text{anc}(j)} \prod_{k \in \text{anc}(j)} p(x_k \given x_{\text{pa}(k)}) \;d\B{x}_{\text{anc}(j)}\\
&= \int_{\text{anc}(j)} \int_{\text{non-anc}(j)} p(x_1, \ldots, x_p) \;d\B{x}_{\text{non-anc}(j)} \;d\B{x}_{\text{anc}(j)}
= p(x_j)
\end{aligned}$$ [eq_11]

The three-line chain is a controlled telescoping of the joint density, and the middle step (†) is where the graph structure — not just calculus — does the work [eq_11].

```derivation
shape: Show the post-intervention marginal of x_j collapses to the plain observational marginal when i is not an ancestor of j.
steps:
  - latex: "p_{\\G}(x_j \\given \\doo(X_i = \\hat x_i)) = \\int_{\\text{anc}(j)} \\int_{\\text{non-anc}(j)} p(x_1, \\ldots, x_p \\given \\hat x_i) \\;d\\B{x}_{\\text{non-anc}(j)} \\;d\\B{x}_{\\text{anc}(j)}"
    why: "Split the post-intervention joint density into an integral over ancestors of j and one over everything else, purely as bookkeeping [eq_11]"
  - latex: "= \\int_{\\text{anc}(j)} \\prod_{k \\in \\text{anc}(j)} p(x_k \\given x_{\\text{pa}(k)}) \\;d\\B{x}_{\\text{anc}(j)}"
    why: "Parents of ancestors of j are themselves ancestors of j, so no factor for a non-ancestor conditions on an ancestor; each non-ancestor factor is a complete conditional density and integrates to exactly 1, leaving only the ancestor product [eq_11]"
  - latex: "= \\int_{\\text{anc}(j)} \\int_{\\text{non-anc}(j)} p(x_1, \\ldots, x_p) \\;d\\B{x}_{\\text{non-anc}(j)} \\;d\\B{x}_{\\text{anc}(j)} = p(x_j)"
    why: "Since i is not an ancestor of j, the intervened factor was one of the ones absorbed to 1 either way, so re-running the same telescoping without the intervention gives an identical result: the true observational marginal of x_j [eq_11]"
```

This is the entire distributional content the proof needs for the non-descendant case: it never has to reason about the interventional distribution in general, only about this one collapse. The descendant case sidesteps distributions altogether and is settled by the Lemma directly, and the converse direction's non-descendant case is settled not by a general argument but by exhibiting one concrete linear Gaussian instance where the collapse provably fails [§sec_8].

## Go Deeper {#go-deeper}
- **Equivalent Graphical Formulation** — the Proposition this proof validates; read it first, since this page only makes sense as a check that it matches the original Definition.
- **Definition of SID** — supplies the existential-over-SEMs quantifier structure that makes a single linear Gaussian witness sufficient in the converse direction.
- **Lemma (adjustment-set failure under descendance)** — the shortcut invoked in both descendant-case branches; worth reading to see why descendance alone rules out a valid adjustment set without any distributional computation.

# Intervention Distributions
## TL;DR {#tldr}
An intervention distribution is the distribution a variable $Y$ would have if some other variable $X$ were forcibly *set* to a value, rather than merely observed to take that value. This is the object SID actually compares between the true and estimated graph: not correlations, but the outcome of a hypothetical experiment. Because it is defined for every pair of nodes in a DAG, it gives SID a well-defined, causally meaningful unit to check graph by graph.

## Intuition {#intuition}
Conditioning on $X=x$ asks "what does $Y$ look like among the cases where $X$ happened to equal $x$?" — it lets information flow backward through $X$'s parents. Intervening asks "what does $Y$ look like if we reach in and force $X=x$?" — that severs $X$ from its usual causes, so any path from $Y$ back through $X$'s parents is cut. The two coincide only when $X$ has no parents worth cutting from $Y$'s point of view; otherwise the intervention distribution strips out confounding that plain conditioning would leave in.

## Mechanics {#mechanics}
The intervention distribution $p_\mathcal{G}(y \mid do(X=\hat x))$ is built from the graph's Markov factorization with $X$'s own factor replaced by a point mass at $\hat x$; since it remains a genuine probability distribution, it can be marginalized or have expectations taken over it just like any other density [§sec_1_2].

**Two structurally different cases determine how it simplifies.** If $Y$ is a parent — or more generally a non-descendant — of $X$, the intervention on $X$ cannot propagate to $Y$ at all, so the interventional and observational distributions of $Y$ coincide [eq_2]. If instead $X$ is a parent of $Y$, the intervention distribution is not just equal to something observational, but *computable* from observational quantities by summing over $X$'s parents [eq_3].

Whenever a marginalized intervention distribution can be obtained this way, the set summed over is called an **adjustment set** for the intervention; $\mathrm{pa}(X)$ is always a valid one and, notably, the smallest such set [§sec_1_2]. Adjustment sets are not unique — a graph can admit several valid sets besides $\mathrm{pa}(X)$, but a Lemma rules out certain supersets of $\mathrm{pa}(X)$ from being valid at all, so validity is not simply "bigger is safer" [§sec_1_2].

## The Math {#the-math}
When $Y$ is a parent or non-descendant of $X$, intervening leaves $Y$'s marginal untouched, so the interventional distribution collapses to the plain observational one, with no adjustment needed [eq_2].

$$p_{\G}(y \given \doo(X = \hat x)) = p(y) \,.$$ [eq_2]

When $X$ is a parent of $Y$, the interventional distribution instead becomes an average of $Y$'s conditional over $X$'s parent configurations, weighted by how likely each configuration is to occur naturally [eq_3].

$$p_{\G}(y \given \doo(X = \hat x)) = \sum_{\pa{}{X}} p(y \given \hat x, \pa{}{X}) \, p(\pa{}{X}) \,.$$ [eq_3]

```annotated-eq
latex: "p_{\\G}(y \\given \\doo(X = \\hat x)) = \\sum_{\\pa{}{X}} p(y \\given \\hat x, \\pa{}{X}) \\, p(\\pa{}{X})"
terms:
  - tex: "p_{\\G}(y \\given \\doo(X = \\hat x))"
    role: 1
    words: "The target quantity — Y's distribution under a forced setting of X, computed entirely from observational pieces on the right [eq_3]"
  - tex: "\\sum_{\\pa{}{X}}"
    role: 2
    words: "Sums out X's parents, the adjustment set that stands in for everything the do-operator would otherwise sever [§sec_1_2]"
  - tex: "p(y \\given \\hat x, \\pa{}{X})"
    role: 3
    words: "An ordinary observational conditional — no do-operator needed once the parents are fixed [eq_3]"
  - tex: "p(\\pa{}{X})"
    role: 4
    words: "Reweights each parent configuration by its natural (observational) probability of occurring [eq_3]"
```

Because $\mathrm{pa}(X)$ is only the *smallest* valid adjustment set, not the only one, this identity is one instance of a broader adjustment-formula family that a supporting Proposition guarantees is valid for any node $X$ [§sec_1_2].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the prerequisite concept this page feeds: SID's per-pair comparisons are built by checking whether the estimated graph's adjustment sets reproduce these true intervention distributions.

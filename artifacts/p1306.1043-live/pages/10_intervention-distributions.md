# Intervention Distributions
## TL;DR {#tldr}

An intervention distribution asks a counterfactual question: if we forced a variable to take a specific value, what would the rest of the system look like? It is the object SID actually compares between two graphs — not correlations, but the outcome of hypothetically setting a variable by hand.

Because SID measures whether a graph gets the *causal* structure right, it needs a notion of "effect of an action," not just a joint density. Intervention distributions are that notion, and they are the prerequisite for defining SID at all.

## Intuition {#intuition}

Ordinary conditioning asks "what do we observe about Y among cases where X happened to equal x?" An intervention asks something stronger: "what would Y look like if we reached in and *set* X to x, overriding whatever normally determines it?" These two questions coincide only when X has no confounded relationship with Y — otherwise they can give different answers.

A graph encodes, for every variable, which other variables are its direct causes. Once you accept the graph, the intervention distribution is fully determined: you keep every other mechanism in the system exactly as it was, and just clip out the mechanism that used to generate X, replacing it with a constant. Two candidate graphs can therefore be compared by asking whether they predict the same effect of the same intervention — this comparison is exactly what SID is built on.

## Mechanics {#mechanics}

**When intervening on a non-cause does nothing:** if X is a parent — or more generally a non-descendant — of Y, setting X by hand cannot change Y's distribution at all, because nothing about Y's generating mechanism depended on X in the first place [§sec_1_2]. This is the degenerate case, and it collapses the intervention distribution back to the plain marginal of Y [eq_2].

$$p_{\G}(y \given \doo(X = \hat x)) = p(y) \,.$$ [eq_2]

**Why the general case needs a specific set:** when X is not a parent of Y, the intervention distribution is generally *not* just p(y) — X does have downstream effects — but it can still be computed from purely observational quantities by summing over the right set of variables rather than over the whole graph [§sec_1_2]. The graph tells you which set that is: it must contain the parents of X, since those are exactly the variables that would otherwise confound the observed association between X and Y [§sec_1_2].

**What makes a set "valid":** any set Z for which the marginalized formula reproduces the true intervention distribution is called a valid adjustment set for the pair (X, Y) — this is stated as a proposition, and the parents of X are one such set that always works [§sec_1_2]. Crucially, a valid adjustment set is not unique: a given graph can admit several different sets that all yield the correct intervention distribution, some smaller than others, while other candidate sets fail outright (adding certain nodes to an otherwise-valid set can break validity, as shown by a companion lemma) [§sec_1_2].

## The Math {#the-math}

The general adjustment formula replaces the intractable "reach in and set X" operation with an expression built entirely from the observational joint density [eq_3]:

$$p_{\G}(y \given \doo(X = \hat x)) = \sum_{\pa{}{X}} p(y \given \hat x, \pa{}{X}) \, p(\pa{}{X}) \,.$$ [eq_3]

```annotated-eq
latex: "p_{\\G}(y \\given \\doo(X = \\hat x)) = \\sum_{\\pa{}{X}} p(y \\given \\hat x, \\pa{}{X}) \\, p(\\pa{}{X})"
terms:
  - tex: "\\doo(X = \\hat x)"
    role: 1
    words: "The intervention itself: X is forced to the fixed value x, not merely observed to equal x [§sec_1_2]"
  - tex: "\\pa{}{X}"
    role: 2
    words: "The adjustment set — here, the parents of X in graph G — chosen because it blocks the confounding path between X and Y [§sec_1_2]"
  - tex: "p(y \\given \\hat x, \\pa{}{X})"
    role: 3
    words: "An ordinary conditional density, computable from observational data since it conditions rather than intervenes [§sec_1_2]"
  - tex: "p(\\pa{}{X})"
    role: 4
    words: "The marginal distribution of the adjustment variables, reweighting each conditional slice by how often that parent configuration actually occurs [§sec_1_2]"
```

**Why summing over the parents suffices:** the formula replaces an operation the data cannot directly show you — forcing X — with a weighted average of things the data *can* show you, conditionals and marginals, and this substitution is only licensed because the parent set screens off every other path by which X's assignment could correlate with Y [§sec_1_2]. Drop the sum, or adjust over the wrong set, and the right-hand side answers a different, purely associational question instead.

**Why this matters for SID specifically:** SID's whole comparison hinges on treating the parent sets that graph G implies as the correct adjustment sets, then asking whether an estimated graph H recovers the same intervention distributions using its own (possibly wrong) parent sets [§sec_1_2]. Equation [eq_2] is the boundary check — if H claims X is not even an ancestor of Y, the predicted intervention distribution must reduce to the marginal p(y); if it instead uses [eq_3] with the wrong adjustment set, the mismatch is exactly the kind of error SID is designed to count.

## Go Deeper {#go-deeper}

- No research note is attached to this concept — the primary source for intervention distributions and their role in SID is the paper's own §sec_1_2, including the proposition establishing valid adjustment sets and the lemma on sets that fail.

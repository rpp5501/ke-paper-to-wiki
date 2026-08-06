# Intervention Distributions
## TL;DR {#tldr}

An intervention distribution asks a counterfactual question: if we forced a variable to take a specific value, what would the rest of the system look like? It is the object SID actually compares between two graphs — not correlations, but the outcome of hypothetically setting a variable by hand.

Because SID measures whether a graph gets the *causal* structure right, it needs a notion of "effect of an action," not just a joint density. Intervention distributions are that notion, and they are the prerequisite for defining SID at all.

## Intuition {#intuition}

| Operation | Question |
|---|---|
| Conditioning | What do we observe about $Y$ when $X$ happened to equal $x$? |
| Intervention | What would $Y$ be if we set $X$ to $x$? |

The answers coincide only when $X$ has no confounded relationship with $Y$.

A graph encodes each variable's direct causes. An intervention preserves every mechanism except the one that generated $X$, which it replaces with a constant.

Two candidate graphs can then be compared by whether they predict the same effect of the same intervention. SID is built on that comparison.

### Running four-node example

Return to $G: A\to B, A\to C, B\to D, C\to D$ and $H=G+(B\to C)$.

For the ordered intervention $C\to D$, $G$ adjusts for $\mathrm{PA}_G(C)=\{A\}$. Estimate $H$ instead adjusts for $\mathrm{PA}_H(C)=\{A,B\}$.

**Worked example:** $B$ is not a descendant of $C$ in true graph $G$. Adding it does not place a mediator or its descendant in the adjustment set, and the set still blocks every non-causal $C$--$D$ path [eq_6]. Both parent adjustments therefore recover the same $p_G(d\mid\mathrm{do}(C=c))$ [§sec_2_3].

## Mechanics {#mechanics}

**When an intervention does nothing:** if $X$ is a non-descendant of $Y$, setting $X$ cannot change $Y$'s generating mechanism [§sec_1_2].

This degenerate case reduces the intervention distribution to the marginal of $Y$ [eq_2].

$$p_{\G}(y \given \doo(X = \hat x)) = p(y) \,.$$ [eq_2]

**Why the general case needs a set:** when $X$ has downstream effects on $Y$, the intervention distribution is not simply $p(y)$ [§sec_1_2].

It can still be computed from observational quantities by summing over the right variables. That set must include parents of $X$, which otherwise confound the observed $X$--$Y$ association [§sec_1_2].

**What makes a set valid:** $Z$ is valid for $(X,Y)$ when the marginalized formula reproduces the true intervention distribution. The parents of $X$ are always one such set [§sec_1_2].

Validity is not unique. Several sets may work, some smaller than others; adding a node can also make an otherwise-valid set fail [§sec_1_2].

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

**Why summing over parents suffices:** the formula replaces forcing $X$, which data cannot directly show, with a weighted average of observable conditionals and marginals [§sec_1_2].

That substitution works because the parent set blocks every other path that could correlate $X$'s assignment with $Y$. Dropping the sum or using the wrong set instead answers an associational question.

**Why this matters for SID:** graph $G$ supplies the correct parent-set adjustment, while estimate $H$ may use a wrong one. SID asks whether their intervention distributions agree [§sec_1_2].

Equation [eq_2] is the boundary case: if $H$ says $X$ is not an ancestor of $Y$, its prediction must be $p(y)$. Using [eq_3] with the wrong set creates the error SID counts.

## Go Deeper {#go-deeper}

- No research note is attached to this concept — the primary source for intervention distributions and their role in SID is the paper's own §sec_1_2, including the proposition establishing valid adjustment sets and the lemma on sets that fail.

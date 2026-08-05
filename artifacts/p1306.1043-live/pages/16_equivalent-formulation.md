# Equivalent Graphical Formulation

## TL;DR {#tldr}
The original definition of SID compares interventional distributions across two graphs, which is not something you can compute directly from graph structure alone. This concept replaces that comparison with a purely graphical test: for each ordered pair of variables, check whether the parent set assigned by the estimated graph would be a *valid adjustment set* in the true graph. That single yes/no test, repeated over all pairs, turns an analytically intractable definition into something a computer can actually evaluate.

## Intuition {#intuition}
An adjustment set is a set of variables you can condition on to recover the causal effect of X on Y without needing to actually intervene. The parent set of X is the obvious candidate — adjusting for a variable's direct causes is the textbook move — but it is not the only one that works, and it is not always sufficient on its own. The reformulation asks a sharper question: given the graph the estimator produced, does its guess for "what to adjust for" happen to be valid in the true underlying graph?

This reframing also explains why SID is forgiving in ways a naive parent-set comparison would not be. You are allowed to adjust for some children of X, as long as they don't sit on a directed path from X to Y — adjusting for a genuine mediator would block the very effect you're trying to measure. You are also allowed to drop parents of X whose only routes to Y are already blocked by other variables in the adjustment set. Both are cases where the estimated graph's parent set can diverge from the true parents yet still yield the correct interventional answer.

## Mechanics {#mechanics}
The reformulation rests on a two-way characterization of when a candidate set **Z** is a valid adjustment set for the effect of X on Y in a DAG G. **If Z satisfies condition (\*)** with respect to (G, X, Y), then Z is guaranteed valid for every structural equation model that is Markov with respect to G — the graphical test is sufficient, not just a heuristic [§sec_2_2]. **If Z fails (\*)**, the characterization is tight in the other direction too: there exists some SEM compatible with G's Markov structure for which adjusting by Z gives the wrong answer, so failing the test is not a false negative but a genuine counterexample [§sec_2_2].

This two-sidedness is what licenses using (\*) as SID's actual computational criterion rather than an approximation of it. When Z is taken to be the parent set PA(X), condition (\*) collapses to a slight extension of the classical back-door criterion, and the tight direction recovers the earlier proposition that PA(X) is always valid in its own graph [§sec_2_2]. That special case is the anchor: it confirms the general test agrees with the known-good baseline before it is applied to a mismatched graph H's guess at PA(X).

## The Math {#the-math}
Condition (\*) is the graphical test applied to a candidate adjustment set **Z** for the pair (X, Y) in graph G, and it has two clauses that must both hold [eq_6]:

$$
(*) \left \{
\begin{array}{c}
\text{In } \G \text{, no } Z \in \B{Z} \text{ is a descendant of any } W \text{ which lies on a directed}\\
\text{path from } X \text{ to } Y \text{ and } \B{Z} \text{ blocks all non-directed paths from } X \text{ to } Y.
\end{array}
\right.
$$ [eq_6]

The first clause forbids adjusting for anything downstream of a mediator, since conditioning on a collider or a mediator's descendant can open spurious paths or close the real one. The second clause is the classical back-door requirement — every non-causal route from X to Y must be blocked. Together they are necessary and sufficient by the Lemma described above, which is what lets SID be redefined without ever touching an interventional distribution [eq_6].

```annotated-eq
latex: "\\SID(\\G,\\HH) = \\# \\left\\{\\,(i,j), i \\neq j\\,|\\, \\begin{array}{cl} j \\in \\DE{\\G}{i} & \\text{if } j \\in \\PA{\\HH}{i}\\\\ \\PA{\\HH}{i} \\text{ does not satisfy } (*) \\text{ for } (\\G,i,j) & \\text{if } j \\not \\in \\PA{\\HH}{i} \\end{array}\\right\\}"
terms:
  - tex: "\\SID(\\G,\\HH)"
    role: 1
    words: "The count being defined, now purely graphical: it tallies ordered pairs where H's parent-set guess fails as an adjustment set in G [eq_7]"
  - tex: "j \\in \\DE{\\G}{i}"
    role: 2
    words: "First failure mode — H says j is a parent of i, but in the true graph j is actually a descendant of i, so adjusting by it would block the real effect or worse [eq_7]"
  - tex: "\\PA{\\HH}{i} \\text{ does not satisfy } (*)"
    role: 3
    words: "Second failure mode — j is not among H's claimed parents of i, so PA_H(i) is tested directly against condition (*) as a candidate adjustment set in G [eq_7]"
```
[eq_7]

The two branches of the formula correspond exactly to why a pair (i, j) can go wrong: either H's parent set includes something that is causally downstream in G, or H's parent set omits a variable in a way that leaves a back-door path unblocked. Every pair not caught by either branch contributes zero to the count, which is why SID is a count of graphical adjustment failures rather than a numerical distance between distributions [eq_7].

## Go Deeper {#go-deeper}
- **Motivation and Definition of SID** — the interventional-distribution definition this formulation replaces; read it first to see what problem the graphical test is solving.
- **Proof: Equivalence of Definitions** — the appendix proof (built on the Lemma referenced above) that formally establishes the two definitions coincide.
- **Metric Properties of SID** — builds on this graphical formulation to derive SID's pre-metric properties, since those proofs work directly with condition (\*) rather than distributions.

# Structural Intervention Distance (SID)
## TL;DR {#tldr}
SID(G, H) is a pre-metric for comparing a true causal DAG G against an estimated graph H by counting how many of the p(p−1) ordered pairs of variables get the wrong prediction for "what happens to Y_j if we intervene on X_i?" Unlike Structural Hamming Distance, which just tallies mismatched edges, SID asks a causal question of the graph: does the parent-adjustment formula computed from H reproduce the true intervention distribution computed from G? Two estimates can look equally wrong under SHD yet be worlds apart under SID.

## Intuition {#intuition}
Consider a true graph where X causes Y, and Y causes three further variables Z1, Z2, Z3. Two flawed estimates are built from it: one adds a spurious edge between Z1 and Z2; the other reverses the X→Y edge into Y→X. Both estimates differ from the truth by exactly one edge, so SHD scores them identically. But intervening on the graph reveals a sharp asymmetry between the two mistakes.

The spurious extra edge barely matters: for almost every pair of variables, the parent-adjustment formula computed in the flawed graph still recovers the correct interventional distribution, because the extra parent it adjusts for turns out to be conditionally irrelevant. The reversed edge is far more damaging: it silently deletes a confounder from the adjustment set (X no longer appears as a parent of Y), so predictions computed from that graph go wrong for many pairs at once — not just the one edge that changed. SID is built to notice this difference where SHD cannot.

## Mechanics {#mechanics}
**The naive definition needs a way to avoid depending on one arbitrary distribution.** For a fixed true DAG G, an intervention distribution predicted from H (via parent adjustment) can be checked against the one predicted from G for a chosen observational law P. But if P happens to factorize into independent variables, G and H agree on every intervention regardless of how different their structures are — the comparison would be vacuous. SID sidesteps this by requiring agreement for *every* distribution P that is Markov with respect to G, turning the comparison into a purely graph-based property rather than a statistical one [§sec_2_1].

A pair (i, j) is counted as an error exactly when some Markov-respecting P makes the two intervention distributions diverge; SID is the total count of such error pairs across all ordered pairs [eq_5].

**Checking "for every distribution" directly is infeasible, so the definition is restated as a graphical adjustment-validity test.** A set of variables is a valid adjustment set for the effect of X on Y precisely when it satisfies an extended back-door-style condition: no variable in the set is a descendant of anything on a directed path from X to Y, and the set blocks every non-directed path between them. This condition is denoted (*) [eq_6]. Testing whether the parent set that H proposes satisfies (*) in G replaces the impossible "for all distributions" check with a finite, graph-local test [§sec_2_2].

Applying this test pair-by-pair gives an equivalent, purely graphical form of SID, and it splits into two cases depending on whether H marks j as a parent of i [eq_7]:

- If **j is a parent of i in H**, the prediction is correct only if j is genuinely a descendant of i in the true graph G — otherwise H is adjusting for a variable that plays the wrong causal role, and the effect estimate is corrupted [eq_7].
- If **j is not a parent of i in H**, the prediction is correct only if H's proposed parent set for i satisfies condition (*) with respect to (G, i, j) — i.e., it would have worked as a valid back-door adjustment set had it been computed from the truth [eq_7].

**These graphical checks give SID real, non-obvious structural properties.** It is a pre-metric (zero on the diagonal, non-negative) but not symmetric: comparing a non-empty graph against the empty graph gives SID zero in one direction (the empty adjustment set is trivially valid when H has no edges) but not the other [§sec_2_3]. More strikingly, an estimate H can contain strictly more edges than G — even many more — and still score a perfect SID of zero, because a superset of the true parents can still satisfy (*); this is the formal counterpart to the "harmless extra edge" seen in the motivating example [§sec_2_3].

## The Math {#the-math}
The pre-metric is defined as a map from pairs of DAGs to a count of falsely estimated ordered pairs, quantified over all distributions Markov with respect to G rather than tied to one [eq_5].

$$
\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\G,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{ the intervention distribution from } i \text{ to } j\\
&& \qquad \qquad \qquad \quad \text{ is falsely estimated by } \HH \text{ with respect to } \G \}
\end{array}
$$ [eq_5]

The adjustment-validity condition (*) is what makes the definition computable without enumerating distributions: it requires no member of the candidate set to be a descendant of a mediator on a causal path, and requires the set to block every remaining confounding path [eq_6].

$$
(*) \left \{
\begin{array}{c}
\text{In } \G \text{, no } Z \in \B{Z} \text{ is a descendant of any } W \text{ which lies on a directed}\\
\text{path from } X \text{ to } Y \text{ and } \B{Z} \text{ blocks all non-directed paths from } X \text{ to } Y.
\end{array}
\right.
$$ [eq_6]

Substituting H's parent sets into (*) yields the equivalent, entirely graph-based reformulation of SID used for computation, with the two-case split by whether j is already listed as a parent of i in H [eq_7].

$$
\SID(\G,\HH) = \# \left\{\,(i,j), i \neq j\,|\, 
\begin{array}{cl}
j \in \DE{\G}{i} & \text{if } j \in \PA{\HH}{i}\\
\PA{\HH}{i} \text{ does not satisfy } (*) \text{ for } (\G,i,j) & \text{if } j \not \in \PA{\HH}{i}
\end{array}
\right\}
$$ [eq_7]

The worked example behind the "harmless extra edge" intuition can be checked algebraically: adjusting for an extra, spurious parent in the estimated graph still collapses back to the true parent-adjustment formula [eq_4].

```derivation
shape: Verify that adjusting for the extra parent X1 in the flawed graph H1 does not corrupt the intervention distribution from Y2 to Y3, compared to adjusting for the true parent set in G.
steps:
  - latex: "p_{H_1}(y_3 \\mid \\doo(Y_2 = \\hat y_2)) = \\sum_{x_1,x_2,y_1} p(y_3\\mid x_1,x_2,y_1,\\hat y_2)\\, p(x_1,x_2,y_1)"
    why: "Parent adjustment in H1 sums over all of Y2's parents there, which now additionally include X1 [eq_4]"
  - latex: "= \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2 \\mid x_1,x_2,y_1)} = \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2 \\mid x_1,x_2)}"
    why: "Rewriting the conditional as a ratio and dropping Y1 from the denominator is valid because Y1 is not a parent of Y2 in the true graph G, so it carries no information about Y2 beyond X1, X2 [eq_4]"
  - latex: "= \\sum_{x_1,x_2} p(y_3\\mid x_1,x_2,\\hat y_2)\\, p(x_1,x_2) = p_{\\G}(y_3\\mid \\doo(Y_2=\\hat y_2))"
    why: "Summing out Y1 leaves exactly the parent-adjustment formula computed from G itself, showing the spurious parent X1 introduced no error for this pair [eq_4]"
```

This is the graph-level mechanism behind the "extra edges are (statistically) forgivable, reversed edges are not" asymmetry: a superset of the true parent set can still satisfy condition (*), so G ⊆ H forces SID(G, H) = 0, while removing or misdirecting a true parent — as the reversed edge does — tends to break (*) for many pairs at once, since the missing confounder can lie on multiple unblocked paths simultaneously [§sec_2_3].

## Go Deeper {#go-deeper}
- **Comparing Estimated and True Causal Graphs** — the general evaluation problem SID is built to solve; explains why a purely edge-counting metric is insufficient.
- **Intervention Distributions** — defines the do-operator quantities SID checks for agreement, and the parent-adjustment formula used throughout.
- **DAG Terminology** — supplies the descendant/parent/path notation (DE, PA) that condition (*) and eq_7 depend on.
- **Structural Hamming Distance (SHD)** — the contrasting edge-count metric; the X/Y/Z1/Z2/Z3 example exists specifically to separate SID from it.
- **Motivation and Definition of SID** — the fuller derivation of why quantifying over all Markov-respecting distributions is necessary.
- **SID between a DAG and a CPDAG** — extends SID to Markov equivalence classes via lower/upper bounds, needed for PC-algorithm or GES output.
- **Penalizing Additional Edges** — addresses the "extra edges score zero" property when a stricter comparison is wanted.
- **Symmetrization of SID** — builds a symmetric distance for cases where neither graph is privileged as the estimate.
- **Hidden Variables (Future Work)** — sketches extending SID to ADMGs/MAGs when some variables are unobserved.
- **Multiple Interventions (Future Work)** — sketches extending single-node interventions to intervention sets.
- **SID versus SHD Simulation** — the empirical comparison showing how differently the two metrics behave in practice.
- **Implementation of SID** — the practical algorithm and code for computing the graphical criterion in eq_7.

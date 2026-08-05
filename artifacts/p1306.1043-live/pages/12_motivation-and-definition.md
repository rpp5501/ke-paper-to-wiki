# Motivation and Definition of SID

## TL;DR {#tldr}
The Structural Intervention Distance (SID) is a pre-metric for comparing two DAGs that scores them by whether they support the *same interventional predictions*, not by how many edges differ. Where the Structural Hamming Distance (SHD) counts edge mismatches and treats every mismatch as equally bad, SID counts the ordered pairs of variables for which the estimated graph would compute the wrong interventional distribution $p(y \mid do(x))$ if the true graph is the one actually generating the data. A single missing or extra edge can leave every intervention prediction intact, while a single reversed edge can corrupt many of them — SHD cannot tell these apart, which is the entire reason SID exists.

## Intuition {#intuition}
Think of the estimated graph not as a picture to be graded for resemblance, but as a *recipe*: for each variable, its parents in the estimate tell you which other variables to condition on if you want to simulate "what happens to some other variable if I intervene here." SHD grades the picture. SID grades the recipe by checking, for every ordered pair of variables, whether following that recipe on the true underlying distribution gives the right answer.

Because interventions are directional — intervening on X and asking about Y is a different question from intervening on Y and asking about X — SID has to examine ordered pairs $(i,j)$ with $i \neq j$, not unordered edges. That directionality is also why SID itself ends up asymmetric: an estimate can get "X causes Y" right while getting "Y causes X" wrong, so swapping the arguments to SID changes the count. This is the property that lets it separate two estimates that look equally wrong to SHD but are not equally wrong for the purpose the graph is actually used for.

## Mechanics {#mechanics}
SID fixes a specific procedure for turning graph structure into a predicted intervention distribution: **parent adjustment**, i.e. adjusting for the direct parents of the intervened-on node. This is a deliberate simplification — other adjustment sets are possible and are treated separately as a refinement of this same idea — but fixing it is what makes SID computable directly from graph structure, with no distributional assumptions beyond Markovianity to the true DAG [§sec_2_1].

Given that choice, a pair $(i,j)$ is **correctly estimated** if the parent-adjustment formula built from the estimate's parent sets returns the same interventional distribution as the one built from the true graph, for *every* distribution Markov to the true DAG — not just one convenient distribution, since a single factorized (fully independent) distribution would trivially make any two graphs agree [§sec_2_1]. Otherwise the pair is **falsely estimated**, and SID is the count of falsely estimated ordered pairs [§sec_2_1].

The paper's own worked comparison shows why edge-counting and intervention-counting diverge:

| Mistake in estimate | Change vs. true DAG | Effect on parent sets | Effect on intervention distributions |
|---|---|---|---|
| Extra edge $Z_1 \to Y$ added | +1 edge (SHD = 1) | Only $Y$'s parent set changes, gains $Z_1$ | All pairs still correct — $Z_1$ is conditionally irrelevant given $Y$'s true parents, so the extra adjustment variable cancels out [§sec_2_1] |
| Edge $X \to Y$ reversed to $Y \to X$ | 1 edge changed (SHD = 1) | $X$ loses its only parent | Several pairs become wrong, since interventions through $X$ now have no confounder to adjust for; the paper reports eight erroneous predictions for many observational distributions [§sec_2_1] |

Both mistakes cost SHD exactly one point, but only one of them costs anything under SID — which is the whole motivation for introducing it [§sec_2_1].

The implementation mirrors this logic at the level of ordered pairs rather than distributions, using reachability on the true graph and the estimate's parent sets to decide correctness directly from structure:

```algorithm
title: _sid_matrix — per-source pass over ordered pairs
lines:
  - code: "path_matrix = _compute_path_matrix(true_graph)"
    intent: "Precompute reachability once on the true DAG; every source's check reuses it [sid.py:L183]"
  - code: "if true_parents == est_parents: continue"
    intent: "Matching parent sets make the estimate's adjustment set the true back-door set for every target, so the whole source is trivially correct and skipped [sid.py:L183]"
  - code: "graph_without_conditioned_tails = true_graph; zero out rows of est_parents"
    intent: "Removing the outgoing edges of the adjustment set isolates which directed paths survive conditioning, needed to test the generalized adjustment criterion [sid.py:L183]"
  - code: "reachable_on_non_directed_path = _reachable_on_non_directed_path(...)"
    intent: "One traversal per source answers, for every target at once, whether the adjustment set blocks all non-causal paths [sid.py:L183]"
  - code: "if est_parents[target]: incorrect = not path_matrix[source, target]"
    intent: "If the target is itself in the adjustment set, the estimate predicts no effect; that is correct only when the true graph agrees there is none [sid.py:L183]"
```

## The Math {#the-math}
The definition packages the pairwise correctness check above into a single map from a pair of DAGs to a natural number [§sec_2_1]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\G,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{ the intervention distribution from } i \text{ to } j\\
&& \qquad \qquad \qquad \quad \text{ is falsely estimated by } \HH \text{ with respect to } \G \}
\end{array}$$ [eq_5]

```annotated-eq
latex: "\\mathrm{SID}: \\mathbb{G} \\times \\mathbb{G} \\rightarrow \\mathbb{N}"
terms:
  - tex: "\\mathrm{SID}"
    role: 1
    words: "A pre-metric, not a metric: it can be asymmetric and the argument order (true graph first) matters [§sec_2_1]"
  - tex: "\\mathbb{G}"
    role: 2
    words: "The space of DAGs over p variables — both arguments live here, but they play different roles [§sec_2_1]"
  - tex: "\\mathbb{N}"
    role: 3
    words: "The codomain is a plain count of ordered pairs, so it is bounded by p(p-1), the number of ordered pairs available [§sec_2_1]"
```

The extra-edge row of the table above is not a coincidence; it is a small instance of a general containment result, and the derivation shows exactly why the added parent $Z_1$ washes out algebraically instead of biasing the estimate:

```derivation
shape: Why adjusting for a superfluous extra parent still yields the correct interventional distribution
steps:
  - latex: "p_{\\HH_1}(y_3\\given \\doo(Y_2 = \\hat y_2)) = \\sum_{x_1,x_2,y_1} p(y_3\\given x_1,x_2,y_1,\\hat y_2)\\, p(x_1,x_2,y_1)"
    why: "Start from parent adjustment computed on the estimate H1, which conditions on Y1's full (over-complete) parent set including the extra edge [eq_4]"
  - latex: "= \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2 \\given x_1,x_2,y_1)} = \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2 \\given x_1,x_2)}"
    why: "Rewrite as a ratio of joint densities, then drop y1 from the conditioning of the denominator because y1 is not actually a parent of Y2 in the true DAG — this is where the extra edge's irrelevance enters [eq_4]"
  - latex: "= \\sum_{x_1,x_2} p(y_3\\given x_1,x_2,\\hat y_2)\\, p(x_1,x_2) = p_{\\G}(y_3\\given \\doo(Y_2 = \\hat y_2))"
    why: "Summing out y1 collapses the expression back to the true graph's own parent-adjustment formula, so the two intervention distributions coincide exactly, not approximately [eq_4]"
```

**Why this generalizes, and why the reversed edge doesn't get the same escape:** the algebra above only closes because the true DAG's edges are a subset of the estimate's — every path the extra adjustment could open is already accounted for by the true parent set, so summing it out is free. A reversed edge instead *deletes* a true parent (the confounder) from the adjustment set rather than adding a superfluous one, and there is no symmetric cancellation available: the missing conditioning variable stays missing throughout the sum, so the two distributions generally disagree [§sec_2_1].

**Cost of computing it:** because the implementation reruns a transitive-closure reachability computation for every source node, the running time scales roughly with the fourth power of the number of variables — practical for on the order of 100 nodes (seconds) but already reaching a minute around 200 nodes, which matters when SID is used to score simulation studies over many DAGs [sid.py:L256].

## Go Deeper {#go-deeper}
- **Equivalent Graphical Formulation** — turns the distributional definition above into a condition checkable purely from graph structure (the generalized adjustment criterion), which is what the `_sid_matrix` implementation actually runs instead of manipulating distributions directly.
- **Alternative Adjustment Sets** — this page fixes parent adjustment as *the* rule; that page examines what changes if a different valid adjustment set is used instead.
- **`SID` class / `_sid_matrix()` (sid.py)** — the concrete algorithm implementing this definition, worth reading alongside Mechanics above to see the pairwise correctness check turned into matrix operations.

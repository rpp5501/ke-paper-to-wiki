# Structural Intervention Distance (SID)
## TL;DR {#tldr}
The Structural Intervention Distance (SID) is a pre-metric for comparing an estimated causal DAG against a true one, built specifically for settings where the graph will be used to predict the effect of interventions. Instead of counting edge edits like the Structural Hamming Distance (SHD), it counts how many pairwise intervention distributions the estimate would get wrong if you used it to compute do-effects via parent adjustment. Because two graphs can look equally "close" under an edit-distance yet differ enormously in how trustworthy their causal predictions are, SID is designed to separate structural mistakes that matter for intervention from those that don't. It extends beyond DAG-vs-DAG comparison to DAGs-vs-CPDAGs, has a symmetrized variant, and can be combined with an edge-count penalty when extra edges are unwanted.

## Intuition {#intuition}
Picture a true causal graph and two flawed estimates that happen to have the exact same SHD to it — one estimate adds a single spurious edge, the other reverses a single edge. Edit-distance treats these mistakes as identical in severity. But they are not: adding a spurious edge among nodes that are already correctly connected barely disturbs the parent sets used for adjustment, so most intervention predictions still come out right. Reversing an edge, by contrast, can silently delete a confounder from the graph — the adjustment set computed from the flawed graph then misses a variable it needed, and several downstream intervention predictions become systematically wrong.

SID is built to notice this asymmetry. Rather than asking "how many edges differ," it asks "for every ordered pair of variables, would this estimated graph tell me the correct answer if I asked it what happens when I intervene here?" A metric defined that way naturally counts the reversed-edge mistake as far more damaging than the added-edge mistake, even when both cost exactly one point of SHD.

## Mechanics {#mechanics}
**Correctness is defined per ordered pair, against every compatible distribution:** for nodes $i \neq j$, the intervention distribution from $i$ to $j$ computed in the estimate $H$ is called correctly estimated only if it matches the one computed in the true DAG $G$ for *every* observational distribution that is Markov with respect to $G$ — not just one. This is deliberate: a fully factorized (independent) distribution would trivially make almost any two DAGs agree on all interventions, which would make the distance blind to real structural error. Quantifying over the whole Markov-compatible family instead yields a distance that depends only on graph structure, never on which particular distribution happens to hold [§sec_2_1].

**The count itself is a map into the naturals:** SID takes an ordered pair of DAGs and returns the number of ordered pairs $(i,j)$ for which $H$'s intervention prediction is false with respect to $G$. Because the roles of $G$ (truth) and $H$ (estimate) are not interchangeable, this count is not symmetric in its two arguments [§sec_2_1].

**Checking correctness graphically instead of distributionally:** the naïve definition above would require testing infinitely many distributions. A graphical adjustment-validity criterion collapses this to a single structural check: a set $\mathbf{Z}$ is a valid adjustment set for $(X,Y)$ in $G$ iff no $Z \in \mathbf{Z}$ is a descendant (in $G$) of any mediator on a directed path from $X$ to $Y$, and $\mathbf{Z}$ blocks every non-directed path between them [eq_6]. Because parent adjustment is used throughout, the object actually being tested at each pair $(i,j)$ is whether $\mathrm{PA}_H(i)$ satisfies this criterion for $(G,i,j)$ [§sec_2_2].

**This yields a purely graph-based reformulation of SID:** a pair $(i,j)$ counts as an error either when $j$ is claimed to be a child of $i$ in $H$ (i.e. $j \in \mathrm{PA}_H(i)$) while $j$ is actually a descendant of $i$ in $G$ — an outright reversal of causal direction that adjustment cannot repair — or, when $j \notin \mathrm{PA}_H(i)$, whenever $H$'s parent set fails the adjustment-validity criterion for that pair in $G$ [eq_7]. This is what makes SID computable without ever touching numerical data: both branches are graph queries [§sec_2_2].

**Extra edges are (structurally) free, missing or misdirected ones are not:** whenever the true DAG $G$ is a subgraph of the estimate $H$ (same or more edges, same orientations on shared edges), SID is exactly zero — parent adjustment in an over-connected $H$ still recovers the correct interventions, since the additional conditioning variables satisfy the criterion automatically. The converse failure mode — a missing edge or a reversed one — is what actually damages the count [§sec_2_3].

| Aspect | SHD | SID |
|---|---|---|
| Symmetric? | Yes, by construction | No — e.g. an empty estimate vs. a non-empty truth gives $\mathrm{SID}(G,H) \neq \mathrm{SID}(H,G)$ [§sec_2_3] |
| What one unit counts | One edge insertion/deletion/reversal | One ordered pair whose intervention prediction is wrong [§sec_2_1] |
| Effect of adding a superfluous (correct-direction) edge | Always costs at least 1 | Can cost 0 exactly when $G \subseteq H$ [§sec_2_3] |
| Effect of reversing one edge | Costs exactly 1 | Can cost up to $\mathcal{O}(p)$ falsely-estimated pairs if a confounder is lost [§sec_2_1] |
| Relationship when SHD = 0 | — | SID = 0 too, but the converse bound is loose and can be tight at the maximal possible SID for constant SHD [§sec_2_3] |

**Extending beyond DAG-vs-DAG:** when the estimate is a CPDAG (as output by PC or GES), individual DAGs in its Markov equivalence class can disagree on intervention predictions for a pair $(i,j)$. Rather than enumerating the whole equivalence class — infeasible for large graphs — each chain component (guaranteed chordal in a valid CPDAG) is extended to DAGs *locally*, and a lower/upper bound on SID is assembled from the best- and worst-case extension per component [§sec_2_4_1]:

```algorithm
title: Lower/upper SID bounds for a DAG-vs-CPDAG comparison
lines:
  - code: "for each chain component C_k of the CPDAG H:"
    intent: "Only chain components need enumeration — the CPDAG's directed edges are already fixed across the whole equivalence class [§sec_2_4_1]"
  - code: "    enumerate all DAG extensions D_1..D_m of C_k, leaving other components undirected"
    intent: "Chordality of C_k guarantees every one of these local extensions corresponds to a valid member DAG of the equivalence class [§sec_2_4_1]"
  - code: "    for each extension D_l and each vertex i in C_k: score_l += errors(i, D_l)"
    intent: "Reuses the graph-only error test from eq_7, applied vertex-by-vertex within the component [§sec_2_4_1]"
  - code: "    lower_k, upper_k = min(scores), max(scores)"
    intent: "The best- and worst-case orientation of this component bound how wrong H can be, independent of how other components are oriented [§sec_2_4_1]"
  - code: "SID_lower = sum(lower_k); SID_upper = sum(upper_k)"
    intent: "Summing per-component extremes over all components gives bounds that are each attained by some actual DAG member of the CPDAG's class [eq_8]"
```

**What the bounds mean operationally:** the lower bound counts intervention distributions that are identifiable in $H$ with respect to $G$ and are inferred falsely, while $p(p-1)$ minus the upper bound counts those identifiable and inferred correctly — so a large gap between the two bounds signals that many pairs' correctness depends on which member of the equivalence class turns out to be true, not on a graphical fact you can settle from $H$ alone [eq_9].

**Three further extensions build on the same machinery:** penalizing additional edges adds a simple edge-count term on top of SID so that a graph with strictly more edges than $G$ no longer gets a free pass to zero distance [§sec_2_4_3]; symmetrization defines $\mathrm{SID}(G,H) + \mathrm{SID}(H,G)$ (or a stricter variant requiring agreement under distributions Markov to *both* graphs) for settings where neither graph is privileged as ground truth [§sec_2_4_4]; and swapping the parent set for a minimal adjustment set changes the conditioning-set size but empirically changes the resulting SID value on only a small fraction of randomly generated dense graphs [§sec_2_4_5].

## The Math {#the-math}
The formal object being defined is a map from pairs of DAGs to a natural number, counting falsely-estimated ordered pairs, and its lead-in claim above is anchored here [eq_5]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\G,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{ the intervention distribution from } i \text{ to } j\\
&& \qquad \qquad \qquad \quad \text{ is falsely estimated by } \HH \text{ with respect to } \G \}
\end{array}$$ [eq_5]

```annotated-eq
latex: "\\mathrm{SID}: \\; \\mathbb{G} \\times \\mathbb{G} \\rightarrow \\mathbb{N}"
terms:
  - tex: "\\mathrm{SID}"
    role: 1
    words: "The pre-metric being defined; note the domain is an ordered pair, so the map need not agree with itself when the arguments swap [eq_5]"
  - tex: "\\mathbb{G} \\times \\mathbb{G}"
    role: 2
    words: "Both slots range over the full DAG space — the first argument plays the role of ground truth, the second the estimate under test [eq_5]"
  - tex: "\\mathbb{N}"
    role: 3
    words: "The codomain is a plain count, at most p(p-1), not a probability or a weighted score — every wrong pair contributes exactly one unit regardless of how wrong it is [eq_5]"
```

The graphical adjustment-validity criterion that lets this count be computed without touching any actual distribution is condition $(*)$ [eq_6]:

$$(*) \left \{
\begin{array}{c}
\text{In } \G \text{, no } Z \in \B{Z} \text{ is a descendant of any } W \text{ which lies on a directed}\\
\text{path from } X \text{ to } Y \text{ and } \B{Z} \text{ blocks all non-directed paths from } X \text{ to } Y.
\end{array}
\right.$$ [eq_6]

Substituting parent sets for $\mathbf{Z}$ throughout turns the distributional definition of eq_5 into the purely graph-based formula actually used for computation [eq_7]:

$$\SID(\G,\HH) = \# \left\{\,(i,j), i \neq j\,|\, 
\begin{array}{cl}
j \in \DE{\G}{i} & \text{if } j \in \PA{\HH}{i}\\
\PA{\HH}{i} \text{ does not satisfy } (*) \text{ for } (\G,i,j) & \text{if } j \not \in \PA{\HH}{i}
\end{array}
\right\}$$ [eq_7]

**Why an extra parent doesn't break correctness — worked calculation:** the claim that $H \supseteq G$ implies zero SID rests on a concrete computation of what happens when the adjustment set gains one superfluous member. In the motivating example, $H_1$ adjusts for $\{X_1,X_2,Y_1\}$ where $G$ only needed $\{X_1,X_2\}$, and the extra variable $Y_1$ cancels out of the estimate exactly [eq_4]:

```derivation
shape: Show that adjusting for an unnecessary extra parent Y1 still recovers G's true intervention distribution.
steps:
  - latex: "p_{H_1}(y_3\\mid \\mathrm{do}(Y_2=\\hat y_2)) = \\sum_{x_1,x_2,y_1} p(y_3\\mid x_1,x_2,y_1,\\hat y_2)\\,p(x_1,x_2,y_1)"
    why: "Parent adjustment applied literally in H1, which lists Y1 as a parent of Y2 even though G does not [eq_4]"
  - latex: "= \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2\\mid x_1,x_2,y_1)} = \\sum_{x_1,x_2,y_1} \\frac{p(x_1,x_2,y_1,\\hat y_2,y_3)}{p(\\hat y_2\\mid x_1,x_2)}"
    why: "The denominator simplifies because {X1,X2} already satisfies criterion (*) for this pair in G, so conditioning further on Y1 cannot change p(y2 | ...) [eq_6]"
  - latex: "= \\sum_{x_1,x_2} p(y_3\\mid x_1,x_2,\\hat y_2)\\,p(x_1,x_2) = p_{\\G}(y_3\\mid \\mathrm{do}(Y_2=\\hat y_2))"
    why: "Summing y1 out of the joint collapses the expression back to exactly G's own parent-adjustment formula, so H1's extra edge cost nothing [eq_4]"
```

**Bounding a DAG-vs-CPDAG comparison:** since a CPDAG $\CC$ represents a whole equivalence class, SID against it is not a single number but a pair of bounds, formalized as a map into $\mathbb{N} \times \mathbb{N}$ [eq_8]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{C} &\rightarrow& \mathbb{N} \times \mathbb{N}\\
(\G,\CC)& \mapsto & \big({\SID}_{\mathrm{lower}}(\G,\CC), {\SID}_{\mathrm{upper}}(\G,\CC)\big)
\end{array}$$ [eq_8]

These bounds have an exact identifiability-theoretic reading: the lower bound counts pairs that are identifiable in $\CC$ and inferred falsely, while $p(p-1)$ minus the upper bound counts pairs identifiable and inferred correctly, with the strictly-identifiable versions of both counts merely bounded rather than pinned down [eq_9]:

$$\begin{aligned}
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ identifiable in }\CC \text{ wrt } \G \text{ and}\\
\text{ inferred falsely by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;= \;{\SID}_{\mathrm{lower}}(\G,\CC)  \\
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ identifiable in }\CC \text{ wrt } \G \text{ and}\\
\text{ inferred correctly by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;= \;p \cdot (p-1) - {\SID}_{\mathrm{upper}}(\G,\CC)\\
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ strictly identifiable in }\CC \text{ and}\\
\text{ inferred falsely by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;\leq \;{\SID}_{\mathrm{lower}}(\G,\CC)  \\
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ strictly identifiable in }\CC \text{ and}\\
\text{ inferred correctly by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;\leq \;p \cdot (p-1) - {\SID}_{\mathrm{upper}}(\G,\CC)\,.
\end{aligned}$$ [eq_9]

**Why identifiability is the load-bearing concept when the roles flip:** comparing an *estimated* structure against a *true* CPDAG (rather than a true DAG) requires restricting attention to pairs whose intervention effect is identifiable in $\CC$ at all — otherwise the comparison would be scoring $H$ against a quantity that isn't even well-defined — and the resulting map again lands in the naturals rather than a bound pair, since only one graph ($H$) is uncertain here [eq_10]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{C} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\CC,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{the interv. distr from $i$ to $j$ is identif. in $\CC$}\\
&& \qquad \qquad \qquad \quad \text{and } \exists \lawX \text{ that is Markov wrt } \CC_1 \in \CC \text{ such that}\\
&& \qquad \qquad \qquad \quad p_{\CC_1}(x_j\given \doo(X_i = \hat x_i)) \neq p_{\HH}(x_j\given \doo(X_i = \hat x_i)) \}
\end{array}$$ [eq_10]

## Go Deeper {#go-deeper}
- **Motivation and Definition of SID** — the source of the reversed-edge-vs-extra-edge example that motivates the whole design; read it for the fully worked contrast this page's Intuition compresses.
- **DAG Terminology** and **Intervention Distributions** — prerequisites defining descendants, adjustment sets, and $p(\cdot \mid \mathrm{do}(\cdot))$ that the graphical criterion $(*)$ [eq_6] and eq_7 both lean on.
- **Structural Hamming Distance (SHD)** — the contrasting edit-distance metric; the comparison table above is a compressed version of the fuller SID-vs-SHD analysis there.
- **SID between a DAG and a CPDAG** — expands the lower/upper-bound algorithm sketched here into the full chordal-extension procedure and its worst-case behavior on long chains.
- **Penalizing Additional Edges** and **Symmetrization of SID** — the two extensions that patch SID's two best-known blind spots (free extra edges, asymmetry).
- **Hidden Variables (Future Work)** and **Multiple Interventions (Future Work)** — open directions toward ADMGs/MAGs and joint interventions on node sets, both currently unresolved.
- **SID versus SHD Simulation** and **Implementation of SID** — the empirical validation and the actual computational recipe for everything defined above.

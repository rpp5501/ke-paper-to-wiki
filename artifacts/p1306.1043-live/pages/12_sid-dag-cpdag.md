# SID between a DAG and a CPDAG
## TL;DR {#tldr}
Many causal discovery algorithms (e.g., the PC-algorithm, Greedy Equivalence Search) don't return a single DAG — they return a CPDAG representing a whole Markov equivalence class of DAGs. To score such an estimate against a true DAG, SID is extended to compare a DAG against a CPDAG by reporting a *pair* of numbers — a lower and an upper bound — rather than a single distance, capturing the best-case and worst-case DAG hiding inside the equivalence class. This extension builds directly on the base pairwise SID between two DAGs, and is itself a building block for comparing two CPDAGs to each other.

## Intuition {#intuition}
A CPDAG leaves some edges undirected because the data (or the equivalence class) simply can't tell you which way they point. Naively, you could enumerate every DAG consistent with the CPDAG, compute the DAG-to-DAG SID for each, and get a spread of possible distances. The extended SID keeps that spirit but avoids the combinatorial blowup: instead of enumerating full DAGs, it works locally, per undirected substructure, and stitches together a best-possible and worst-possible score. The lower bound is optimistic — it corresponds to the DAG in the class that gets the most intervention effects right; the upper bound is pessimistic — it corresponds to the DAG that gets the most wrong. The gap between them tells you how much the CPDAG's remaining uncertainty actually matters for causal effect estimation, with the extreme case being a fully unoriented chain, where the class contains both the perfectly correct DAG and its total reversal.

## Mechanics {#mechanics}
A CPDAG only represents a genuine Markov equivalence class of DAGs if each of its chain components (maximal undirected connected subgraphs) is chordal; the method exploits this by extending each chordal chain component locally to all of its possible DAG orientations while leaving the other chain components untouched [§sec_2_4_1].

For every such local extension, and for every vertex inside the chain component, the relevant quantity is evaluated, producing — per chain component — a set of vectors, each with as many entries as there are extensions; each vector is collapsed to its sum, and the minimum and maximum of these sums are retained as the best-case and worst-case values for that component [§sec_2_4_1].

Summing the per-component minima gives the overall lower bound and summing the per-component maxima gives the overall upper bound, and this construction guarantees that the neighborhood orientations chosen for the lower and upper bound never contradict each other across components, so both bounds are actually achieved by some single DAG member of the CPDAG's equivalence class [§sec_2_4_1].

The gap between these bounds can be large: for a true DAG that is a Markov chain, the equivalence class contains both the correct DAG (SID = 0, the lower bound) and its full reversal (the maximal possible SID, the upper bound) [§sec_2_4_1].

To make the bounds interpretable, they are related to which intervention distributions are *identifiable* versus *strictly identifiable* within the equivalence class represented by the CPDAG — the lower/upper bound choice is deliberately conservative, matching identifiable (not merely strictly identifiable) distributions, so that candidate interventions with a genuinely strong causal effect are not missed when using the CPDAG to propose experiments [§sec_2_4_1].

The procedure assumes the estimated object is a proper CPDAG; if it isn't — which can happen with some PC-algorithm variants under finite data or hidden variables — the method falls back to considering, for each node, all subsets of undirected neighbors as candidate parent sets (and does the same when a chain component exceeds eight nodes), again reporting lower and upper bounds [§sec_2_4_1].

## The Math {#the-math}
The extended SID is formalized as a mapping from a DAG–CPDAG pair to a pair of natural numbers, the lower and upper bound [eq_8], stated as:

$$
\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{C} &\rightarrow& \mathbb{N} \times \mathbb{N}\\
(\G,\CC)& \mapsto & \big({\SID}_{\mathrm{lower}}(\G,\CC), {\SID}_{\mathrm{upper}}(\G,\CC)\big)
\end{array}
$$ [eq_8]

The bounds are then tied to counts of correctly/falsely inferred intervention distributions, distinguishing distributions that are identifiable in the CPDAG from those that are strictly identifiable, with equalities for the identifiable case and inequalities bounding the strictly identifiable case [eq_9]:

$$
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
$$ [eq_9]

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to summarize here; the relevant background is the base [[Structural Intervention Distance (SID)]] concept it builds on, and it in turn feeds into the [[SID between a CPDAG and a DAG or CPDAG]] extension for comparing two estimated CPDAGs.

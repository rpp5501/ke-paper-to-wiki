# Metric Properties of SID

## TL;DR {#tldr}

SID is non-negative and zero on a graph compared with itself, but it is not symmetric. Swapping truth and estimate can change the score.

This section characterizes the large zero-SID set: an estimate can add extra edges and still be flawless.

It also contrasts SID with SHD, whose edge count can disagree sharply with causal accuracy.

## Intuition {#intuition}

SID scores whether an estimate answers every intervention question correctly, not whether it looks identical to truth.

Harmless extra edges do not hurt when the parent set still blocks true-graph confounding paths. Missing or misdirected edges can corrupt adjustment, so SID punishes absent structure more than surplus structure.

SID is asymmetric because $G$ supplies true intervention distributions while $H$ supplies the adjustment sets under test. Reversing the roles asks a different question.

SHD counts insertions, deletions, and reversals without asking whether they affect adjustment. One edge change can leave SHD tiny while making SID maximal.

**Boundary case:** for the shared pair $G\subseteq H=G+(B\to C)$, $\mathrm{SID}(G,H)=0$ although the graphs differ. Swapping them yields two errors, demonstrating both the large zero set and asymmetry [§sec_2_3; sid.py:L183-L253].

## Mechanics {#mechanics}

**Pre-metric, not metric:** SID is non-negative and vanishes when a graph is compared to itself, which is enough to qualify as a *pre-metric*, but it drops the symmetry requirement of a true metric [§sec_2_3].

**Why symmetry fails:** an empty graph as truth makes every node set trivially satisfy adjustment validity [§sec_2_3].

The same empty graph as an estimate supplies no adjustment information for a non-empty truth. The two directions therefore differ [§sec_2_3].

**Same distributions in both directions are not enough:** equal parent-adjustment distributions for one pair do not force both $\mathrm{SID}(G,H)$ and $\mathrm{SID}(H,G)$ to be zero [§sec_2_3].

That equality concerns one argument order, not every consequence of swapping the graphs [§sec_2_3].

**Characterizing zero SID:** a Proposition gives SID zero whenever true $G$ is a subgraph of the estimate [§sec_2_3].

This generalized $G\subseteq H$ condition is weaker than $G=H$: $H$ may add edges while keeping all of $G$'s [§sec_2_3].

**Why supersets are free:** extra edges add non-confounding covariates without removing or reversing any true edge [§sec_2_3].

Parent adjustment remains valid, so the superset's intervention distributions equal $G$'s. SID rewards at least as much structure as truth, not exact structure [§sec_2_3].

**Finite-sample checking is regression, not graph matching.** Intervention prediction conditions on estimated parents, so zero SID asks whether selected predictors reproduce the true conditional expectation [§sec_2_3].

Its empirical success depends on the regression method, not graph structure alone [§sec_2_3].

**Fixing SID's generosity:** SID alone cannot distinguish $G$ from strict supergraphs [§sec_2_3].

The paper proposes combining it with a second measure so only identical graphs receive zero [§sec_2_3].

## The Math {#the-math}

The zero-SID characterization is a subgraph containment statement between the true DAG and the estimate rather than an equality, which is exactly why the zero set is large [§sec_2_3]:

$$G \subseteq H \implies \mathrm{SID}(G, H) = 0$$ [§sec_2_3]

Here $G\subseteq H$ means each true edge also occurs in $H$; $H$ may carry additional edges [§sec_2_3].

This one-directional containment, not equality, is necessary and sufficient for every intervention answer to be correct [§sec_2_3].

The relationship to SHD is stated as a pair of bounds rather than a single formula, and each direction of the inequality carries different content [§sec_2_3]:

$$\mathrm{SHD}(G,H) = 0 \implies \mathrm{SID}(G,H) = 0$$ [§sec_2_3]

This first bound is a sanity check. Identical graphs have identical adjustment sets and therefore correct intervention answers [§sec_2_3].

SHD zero is stronger than containment because equality implies containment in both directions [§sec_2_3].

The sharp result reverses the perspective: some $G,H$ have $\mathrm{SHD}(G,H)=1$ while $\mathrm{SID}(G,H)$ is maximal [§sec_2_3].

One misplaced edge can invalidate parent adjustment for every downstream pair, not merely nearby ones [§sec_2_3].

**Why SID cannot bound SHD:** one SHD unit can already saturate SID [§sec_2_3].

A supergraph can have perfect SID and large edit distance, while one edit can produce near-worst SID. The measures are not commensurable in either direction [§sec_2_3].

## Go Deeper {#go-deeper}

- **Equivalent Graphical Formulation** (builds-on) — this concept's subgraph/superset characterization of the zero-SID set relies on the graphical (adjustment-set) restatement of SID developed there; read it first if the "why supersets are free" argument feels unmotivated.
- **Proof: SID for Superset Estimates** (defined-in) — supplies the formal argument behind the claim that $G \subseteq H$ implies SID zero, including the generalized subgraph relation used across DAGs.
- **Proof: SID and SHD Relationship** (defined-in) — proves both halves of the SHD/SID bound stated above, including the explicit construction achieving the sharp, maximal-SID single-edit example.

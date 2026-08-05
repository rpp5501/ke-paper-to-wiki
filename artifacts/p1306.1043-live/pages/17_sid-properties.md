# Metric Properties of SID

## TL;DR {#tldr}

SID behaves like a distance but isn't quite one: it's non-negative and zero when compared to itself, yet it isn't symmetric, so swapping the "true" and "estimated" graph can change the score. This section pins down exactly which DAGs get a perfect SID of zero relative to a ground truth, and shows that this set is much larger than "the same graph" — an estimate can pile on extra edges and still be judged flawless. It also compares SID against the more familiar Structural Hamming Distance (SHD), showing the two measures can disagree sharply, which is the paper's argument for why edge-counting metrics like SHD are the wrong tool for causal accuracy.

## Intuition {#intuition}

Think of SID as scoring an estimated graph by whether it gives the *right answer* to every possible intervention question, not by whether it looks structurally identical to the truth. That's why adding harmless extra edges doesn't hurt: if the estimated parent set for a node still blocks all the confounding paths in the true graph, the intervention effect computed from it is correct regardless of whatever superfluous edges are floating around elsewhere. Removing or misdirecting even one edge, by contrast, can corrupt an adjustment set and make the intervention answer wrong — which is why SID punishes missing structure far more than surplus structure.

This asymmetry is also why SID can't be symmetric: judging "how wrong is H if G is true" is a different question from "how wrong is G if H is true," because the two graphs don't play symmetric roles — one supplies the ground-truth interventional distributions, the other supplies the adjustment sets being tested against them. The comparison to SHD makes the same point from a different angle: SHD only counts edge insertions/deletions/reversals, blind to whether those edges matter for adjustment, so a single edge change can leave SHD tiny while SID swings to its maximum — meaning a graph can look almost right and still get every intervention wrong.

## Mechanics {#mechanics}

**Pre-metric, not metric:** SID is non-negative and vanishes when a graph is compared to itself, which is enough to qualify as a *pre-metric*, but it drops the symmetry requirement of a true metric [§sec_2_3].

**Why symmetry fails:** comparing a non-empty graph to the empty graph in one direction versus the other gives different scores, because in the empty DAG every set of nodes trivially satisfies the adjustment criterion, so the empty graph, treated as the truth, makes almost any adjustment set "valid" — but the same empty graph as the estimate provides no adjustment information at all when compared against a non-empty truth [§sec_2_3].

**Same distributions in both directions still isn't enough:** even if parent adjustment happens to yield identical intervention distributions when computed from G and from H, that does not force SID(G,H) and SID(H,G) to both be zero — the equality of distributions is a fact about that specific pair, not a guarantee that swaps the argument order [§sec_2_3].

**Characterizing the zero-SID set:** the paper's Proposition pins down exactly which DAGs achieve SID zero relative to a true DAG G — namely, whenever G is a subgraph of the estimate (every edge of G also appears in the tested graph, in some suitably generalized ⊆ sense across DAGs and their equivalence classes) [§sec_2_3]. This is a much weaker condition than G = H, since the estimate is free to add edges as long as it keeps all of G's [§sec_2_3].

**Why supersets are "free":** if the estimated graph has strictly more edges than G but no edge of G is missing or reversed, the extra edges can only add nodes into the conditioning set in a way that doesn't reintroduce confounding — parent-set adjustment is unaffected by adding non-confounding covariates, so intervention distributions computed from the superset agree exactly with those from G [§sec_2_3]. This is the mechanism behind the claim that SID rewards "at least as much structure as the truth" rather than exact structure.

**Estimating this in practice is regression, not graph-matching:** because computing the intervention distribution reduces to conditioning on the estimated parent set, checking whether the "SID = 0" equality holds from finite samples is really a feature-selection/regression question — whether a chosen predictor set reproduces the true conditional expectation — so how well this equality holds in practice depends on the regression method used, not on graph structure alone [§sec_2_3].

**Fixing the "too generous" behavior:** because a strict superset of G still scores zero, SID alone cannot distinguish G from any of its supergraphs; the paper notes this defect can be patched by combining SID with a second measure, so that the combined score is zero if and only if the two graphs are exactly identical [§sec_2_3].

## The Math {#the-math}

The zero-SID characterization is a subgraph containment statement between the true DAG and the estimate rather than an equality, which is exactly why the zero set is large [§sec_2_3]:

$$G \subseteq H \implies \mathrm{SID}(G, H) = 0$$ [§sec_2_3]

Here $G \subseteq H$ means every edge present in the true graph $G$ is also present in $H$ — $H$ is permitted to carry additional edges beyond $G$'s — and this one-directional containment, not full equality, is the necessary and sufficient condition for the estimate to answer every intervention question correctly [§sec_2_3].

The relationship to SHD is stated as a pair of bounds rather than a single formula, and each direction of the inequality carries different content [§sec_2_3]:

$$\mathrm{SHD}(G,H) = 0 \implies \mathrm{SID}(G,H) = 0$$ [§sec_2_3]

This first bound is the "sanity check" direction: if the two graphs are edge-for-edge identical, every adjustment set computed from H matches G exactly, so of course every intervention answer is correct — SHD zero is a strictly stronger condition than the subgraph criterion above, since equality trivially implies containment in both directions [§sec_2_3].

The sharp bound goes the other way and is the one that does real work: there exist graphs $G$ and $H$ with $\mathrm{SHD}(G,H) = 1$ — a single edge insertion, deletion, or reversal — for which $\mathrm{SID}(G,H)$ attains its maximal possible value [§sec_2_3]. Concretely, flipping or misplacing one edge can break the adjustment-set validity for *every* remaining pair of nodes downstream of that edge, since a single wrong edge in the wrong place can turn a valid parent set into an invalid one across the whole graph, not just locally [§sec_2_3].

**Why this blocks bounding SHD from SID:** because a single unit of SHD can already saturate SID, no upper bound on SID can be turned into an upper bound on SHD — a graph can score perfectly on SID while still being far in edit distance (the superset case above), and a graph can score near-worst on SID while being one edit away in SHD, so the two measures are, in the paper's words, simply not commensurable in either direction [§sec_2_3].

## Go Deeper {#go-deeper}

- **Equivalent Graphical Formulation** (builds-on) — this concept's subgraph/superset characterization of the zero-SID set relies on the graphical (adjustment-set) restatement of SID developed there; read it first if the "why supersets are free" argument feels unmotivated.
- **Proof: SID for Superset Estimates** (defined-in) — supplies the formal argument behind the claim that $G \subseteq H$ implies SID zero, including the generalized subgraph relation used across DAGs.
- **Proof: SID and SHD Relationship** (defined-in) — proves both halves of the SHD/SID bound stated above, including the explicit construction achieving the sharp, maximal-SID single-edit example.

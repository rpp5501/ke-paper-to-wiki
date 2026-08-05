# Penalizing Additional Edges

## TL;DR {#tldr}

SID can score a graph as perfect — SID = 0 — even when that graph has strictly more edges than the truth. This is a deliberate blind spot: SID only checks whether every intervention effect computed from the estimated graph matches the truth, not whether the graph is otherwise parsimonious. A companion edge-count distance is introduced to catch the cases where SID's silence would otherwise be mistaken for structural correctness.

## Intuition {#intuition}

SID asks a narrow, causal question for every ordered pair of variables: "if I intervened on one and adjusted using the estimated parent set, would I get the true interventional distribution?" An extra edge that happens to sit on top of an already-valid adjustment set never breaks that check — it's redundant information, not wrong information. So a denser graph can pass every single one of SID's pairwise tests.

That's fine for the purpose SID was built for: it isn't lying about causal effects. But a graph with superfluous edges is still a worse *model* — it has more parameters to estimate, is harder to interpret, and in finite samples the extra edges translate into higher variance when the adjustment sets are actually put to use. SID doesn't see that cost because it evaluates population-level distributions, not estimation difficulty. The fix isn't to change SID — it's to report a second, orthogonal number alongside it: how many edges got added.

## Mechanics {#mechanics}

**Why SID alone can't flag this:** the zero-SID result for edge-inflated graphs is a direct consequence of the proposition characterizing when SID vanishes — it holds whenever every pairwise adjustment set implied by the estimated graph remains valid in the true graph, and adding edges consistent with the true topological order can preserve that validity for every pair simultaneously [§sec_2_4_3].

**What the extra measure counts:** a directed or undirected edge each count as exactly one unit, so the measure is a simple cardinality difference between the edge sets of the true DAG and the estimate — it does not care about edge orientation, only about whether an edge is present at all [§sec_2_4_3].

**Where it plugs in:** the same edge-count comparison is defined for both the DAG-vs-DAG case and the DAG-vs-CPDAG case, so it can be reported next to SID regardless of which type of graph the estimation procedure produces [§sec_2_4_3].

**What it's for:** the passage is explicit that in most practical settings the extra-edges phenomenon is a statistical problem that shrinks as sample size grows, not a correctness problem — the edge-count distance exists only for the practical situations where a user cares about parsimony independently of causal-effect accuracy [§sec_2_4_3].

## The Math {#the-math}

No new estimator or bound is derived here beyond the edge-cardinality count itself, so the useful thing to make concrete is *how* SID = 0 coexists with strictly more edges — a worked boundary case.

Take true DAG $G: X \to Y \to Z$ (2 edges) and estimate $H: X \to Y \to Z,\ X \to Z$ (3 edges) — $H$ adds one edge but keeps the same topological order [§sec_2_4_3].

- For the pair $(X, Z)$: in $G$, $X$ has no parents, so the true causal effect of $X$ on $Z$ is identified by the unconditional distribution $p(z \mid x)$. In $H$, $X$ still has no parents, so the adjustment set $H$ implies for this pair is also empty — the extra edge changes the graph's picture of *how* $X$ reaches $Z$ but not *which variables must be adjusted for*, so the estimated intervention distribution still matches [§sec_2_4_3].
- Every other ordered pair's adjustment set is unaffected by the new edge, so the pairwise indicator SID sums over is 0 for all of them too, giving $\mathrm{SID}(G,H) = 0$ [§sec_2_4_3].
- Meanwhile the edge-count distance between $G$ and $H$ is $|3-2| = 1$: the two graphs are causal-effect-equivalent under SID but not identical as models, and that difference is exactly what the extra measure is built to surface [§sec_2_4_3].

This is the general mechanism behind the proposition referenced in the text: any edge added between a node and a descendant that doesn't sit on the minimal path needed for identification is "free" from SID's perspective, however many of them accumulate [§sec_2_4_3].

## Go Deeper {#go-deeper}

- **Structural Intervention Distance (SID)** — the parent concept this measure is a companion to; read it first to see the pairwise adjustment-set check that the extra-edges case exploits.

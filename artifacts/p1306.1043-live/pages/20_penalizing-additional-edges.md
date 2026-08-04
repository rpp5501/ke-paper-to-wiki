# Penalizing Additional Edges
## TL;DR {#tldr}
Structural Intervention Distance (SID) can score an estimated causal graph as perfect (SID = 0) even when that graph contains extra edges beyond the true DAG, because SID only checks whether every pairwise interventional distribution is correctly identifiable, not whether the graph is minimal. This extension adds a companion distance that explicitly counts the difference in edge count between the estimated and true graphs, so that "too many edges" is no longer invisible to evaluation.

## Intuition {#intuition}
SID builds on the idea that a graph is "good" if it lets you read off the right causal effects, but a graph can achieve that by being overly generous with edges — throwing in extra connections costs nothing in SID as long as the true interventional relationships still come through correctly. That's fine in an idealized, infinite-data setting, but in practice extra edges mean wasted degrees of freedom and noisier estimates, so practitioners may still want to penalize them. The fix is conceptually simple: keep SID for correctness of intervention distributions, and separately tally how many edges the estimate has beyond what's needed, giving a second, complementary score.

## Mechanics {#mechanics}
The starting observation is that an estimated DAG can have strictly more edges than the true DAG while still receiving an SID of zero, a fact established by an earlier proposition in the paper [§sec_2_4_3]. This is not treated as a flaw of SID itself: the paper had already argued that for causal inference purposes, such superfluous edges only introduce statistical inefficiencies that shrink as sample size grows, rather than genuine identification errors [§sec_2_4_3]. Even so, the authors note that in some practical situations this insensitivity to extra edges may be regarded as an unwanted side effect worth measuring directly [§sec_2_4_3]. Their proposed remedy is an additional distance that measures the difference in the number of edges between the estimated and true graphs, where a directed or undirected edge each count as one edge [§sec_2_4_3].

## The Math {#the-math}
The local context describes the edge-count distance and its relationship to the earlier proposition in prose, but the specific equations are not reproduced in the supplied excerpt, so no display equations can be given here honestly [§sec_2_4_3]. What is stated is that the result holds directly as a consequence of the proposition for any DAG compared against another DAG, and analogously for a DAG compared against a CPDAG, establishing that the edge-count penalty is well-defined across both graph representations used elsewhere in the SID framework [§sec_2_4_3].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list beyond the parent paper itself; see [[Structural Intervention Distance (SID)]] for the base distance this extension penalizes edges alongside.

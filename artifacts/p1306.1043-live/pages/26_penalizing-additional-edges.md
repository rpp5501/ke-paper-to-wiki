# Penalizing Additional Edges
## TL;DR {#tldr}
SID can score a graph as flawless — zero errors on every intervention — even when that graph carries strictly more edges than the truth. Because that gap is a real blind spot in practice, it is common to pair SID with a second, simpler distance that just counts the extra edges.

## Intuition {#intuition}
SID asks a narrow question: does every parent set the estimated graph implies still work as a valid adjustment set in the true model? A graph can pad itself with harmless extra edges — ones that never corrupt an adjustment — and still answer that question perfectly. Those extra edges aren't free, though: they mean adjusting on more variables than necessary, which is a data-efficiency cost even when it isn't a correctness cost. An edge-count distance is the natural complement, since it flags exactly the sparsity that SID is structurally blind to.

## Mechanics {#mechanics}
The starting fact is a **Proposition**: an estimated DAG can have strictly more edges than the true DAG and still receive SID equal to zero [§sec_2_4_3]. Nothing in SID's definition rules this out, because SID only checks whether implied adjustments succeed, not whether the graph is minimal [§sec_2_4_3].

For causal inference itself, this is framed as a **statistical rather than a structural problem** — extra covariates in an adjustment set cost variance, and that cost shrinks as sample size grows, so it is not treated as a correctness failure [§sec_2_4_3]. The paper is explicit, though, that in some practical settings this is "nevertheless... seen as an unwanted side effect," which is the motivation for a second measure [§sec_2_4_3].

The fix is an **additional distance that counts edges directly**: the difference in edge count between the estimated and true graph, with the convention that a directed edge and an undirected edge each count as exactly one edge [§sec_2_4_3]. This keeps the edge tally comparable whether the estimate is a fully-oriented DAG or a partially-oriented CPDAG [§sec_2_4_3].

The same construction is stated **twice, for two comparison settings**: once for a true DAG against an estimated DAG, and analogously for a true DAG against an estimated CPDAG [§sec_2_4_3]. Both follow directly from the same Proposition, since neither the DAG-vs-DAG nor the DAG-vs-CPDAG version of SID bounds the estimate's edge count [§sec_2_4_3].

## The Math {#the-math}
No display equation is given for this measure in the source text, but its logic can be made explicit. The Proposition's content is that zero SID and edge inflation can coexist — formalizing that relationship is what motivates the edge-count distance [§sec_2_4_3].

```derivation
shape: Formalizing why zero SID does not bound the edge count.
steps:
  - latex: "\\mathrm{SID}(G,H) = 0"
    why: "Every parent set H implies yields a valid adjustment in G for every ordered pair — that is all SID checks [§sec_2_4_3]"
  - latex: "|E(H)| > |E(G)|"
    why: "The Proposition places no upper bound on H's edge count once every adjustment succeeds, so H can carry strictly more edges than G [§sec_2_4_3]"
  - latex: "\\mathrm{ED}(G,H) = \\big|\\,|E(H)| - |E(G)|\\,\\big|"
    why: "A second distance, counting only the edge-count gap, recovers the sparsity signal SID discards — directed and undirected edges weighted equally [§sec_2_4_3]"
```

This is a genuine **complement, not a replacement**: SID(G,H) = 0 says every causal query answerable from H matches G; ED(G,H) > 0 says H is doing that with unnecessary machinery [§sec_2_4_3]. The two numbers can move independently — a graph can be SID-perfect and edge-heavy, or edge-light and SID-imperfect — which is exactly why the paper reports them side by side rather than folding one into the other [§sec_2_4_3].

The **DAG-vs-CPDAG case** uses the identical count, not a reweighted one: the "one edge" convention applies whether an edge in H is drawn as directed (a DAG) or undirected (a CPDAG edge left unoriented), so ED stays comparable across both settings without a separate scale [§sec_2_4_3].

## Go Deeper {#go-deeper}
- No dedicated research note is attached to this concept.
- See **Structural Intervention Distance (SID)** — the parent concept this edge-count measure supplements; understanding what SID does and does not check is the prerequisite for seeing why this gap matters.

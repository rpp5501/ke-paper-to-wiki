# Scalability of the SID
## TL;DR {#tldr}
Computing the SID gets slower as graphs grow, but the rate depends on density: for sparse graphs runtime grows roughly with the square of the node count, for dense graphs roughly with the cube. This was measured empirically by timing the reference implementation on random graphs of increasing size, not derived as a formal bound, and it directly characterizes the cost of the procedure introduced for computing SID.

## Intuition {#intuition}
Picture SID checking, for every pair of variables, whether the estimated graph's parent set still recovers the true causal effect. In a sparse graph each such check is cheap — few parents, few competing paths to rule out. In a dense graph the same check has to reckon with many more potential parents and alternative paths, so each individual check gets more expensive as the graph grows, not just more numerous. Stack that per-check slowdown on top of a check count that already grows with the graph, and quadratic growth in the sparse regime becomes cubic in the dense one.

## Mechanics {#mechanics}
The experiment times SID computation between two random graphs on nodes, sweeping across a range of values and repeating the measurement for both a sparse and a dense random-graph setting — the same generative setup used to characterize the SID implementation elsewhere. Processor time is recorded per pair of graphs and summarized with box plots so that the spread across repeated draws, not just the average, is visible at each graph size [§sec_3_3].

Results are averaged over 100 independently sampled graph pairs at each node count, which is what lets the box plots separate a genuine trend in with sampling noise from any one unlucky pair of random graphs. The resulting curves are then read off visually for their approximate growth rate rather than fit to a closed-form model [§sec_3_3].

| Setting | Observed scaling in | What drives it |
|---|---|---|
| Sparse random graphs | Roughly quadratic | Each pairwise check stays cheap as grows [§sec_3_3] |
| Dense random graphs | Roughly cubic | Each pairwise check gets costlier as grows [§sec_3_3] |

## The Math {#the-math}
No closed-form runtime bound is stated in this section — the quadratic and cubic rates are read off the timing curves, not proved — but the shape of the result follows from how SID is built. Evaluating SID between two -node graphs requires examining relationships across the node pairs, so the number of checks performed scales as regardless of density [§sec_3_3]. What separates sparse from dense is the cost of each individual check: in a sparse graph, parent sets stay small and roughly constant in size as grows, so per-pair cost is , giving an total that matches the observed quadratic curve [§sec_3_3].

In a dense graph, parent-set size grows along with the graph itself, so per-pair cost scales as rather than staying flat; multiplying that by the pairs gives an total, matching the observed cubic curve [§sec_3_3]. A quick sanity check: doubling under this account should roughly quadruple runtime for sparse graphs () and roughly octuple it for dense graphs () — the qualitative gap the box plots are built to show [§sec_3_3].

## Go Deeper {#go-deeper}
- **Implementation of SID** — the algorithm whose runtime this section is measuring; read it first to see what a single SID evaluation actually computes before judging why its cost scales the way it does.

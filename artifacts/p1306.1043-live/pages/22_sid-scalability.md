# Scalability of the SID
## TL;DR {#tldr}
Computing the SID between two graphs gets more expensive as the number of nodes grows, and the rate depends on how dense the graphs are: roughly quadratic time for sparse graphs, roughly cubic for dense ones. This matters because it sets a practical ceiling on how large a causal-discovery benchmark can be before scoring the output graphs becomes the bottleneck rather than learning them.

## Intuition {#intuition}
SID scores a graph by checking, for every pair of variables, whether the estimated graph's implied adjustment set would correctly identify the causal effect. More nodes means more pairs to check, and denser graphs mean each individual check has more to look at — bigger parent sets, more paths to trace. The empirical study behind this concept just runs the SID computation across a range of graph sizes and times it, for both sparse and dense random graphs, to see how those two effects combine in practice.

## Mechanics {#mechanics}
**The experimental setup:** for a sequence of node counts, random sparse and dense graph pairs are generated using the same graph-generation setting used elsewhere in the evaluation, and the wall-clock/processor time to compute SID on one pair is recorded [§sec_3_3].

**Why box plots over repeated pairs:** each node count is evaluated on 100 independently sampled graph pairs rather than a single pair, and the spread is shown as a box plot — this exposes how much timing varies across random instances of the same size, not just the average trend [§sec_3_3].

**The observed trend:** across the range of node counts tested, processor time grows approximately quadratically with the number of nodes for sparse graphs, and approximately cubically for dense graphs [§sec_3_3].

## The Math {#the-math}
No cost formula is stated directly in this section, but the quadratic/cubic split follows from counting what SID has to check. SID evaluates every ordered pair of distinct nodes, and the cost of each pair's check scales with how much of the graph that check has to touch — which is exactly where sparsity vs. density enters.

```derivation
shape: Account for why runtime is quadratic on sparse graphs and cubic on dense graphs.
steps:
  - latex: "|\\{(i,j) : i \\neq j\\}| = n(n-1) = O(n^2)"
    why: "SID makes one adjustment-set check per ordered node pair, so the number of checks alone is already quadratic in the node count before any per-check cost is added [§sec_3_3]"
  - latex: "T_{\\text{sparse}}(n) = O(n^2) \\cdot O(1) = O(n^2)"
    why: "A sparse graph keeps each node's neighborhood bounded, so a single adjustment-set check costs roughly constant work, leaving the pair count as the dominant term [§sec_3_3]"
  - latex: "T_{\\text{dense}}(n) = O(n^2) \\cdot O(n) = O(n^3)"
    why: "A dense graph gives nodes parent/adjustment sets that can grow with n, so each check now costs O(n) work, multiplying the O(n^2) pair count into an O(n^3) total — matching the cubic trend seen in the dense-graph box plots [§sec_3_3]"
```

This is why the two curves separate as n grows: the pair-counting term is identical for sparse and dense graphs, and the entire gap between quadratic and cubic scaling traces back to how much work a single adjustment-set check does in a denser neighborhood [§sec_3_3].

## Go Deeper {#go-deeper}
- **Implementation of SID** — the algorithm being timed here; read it first to see what a single adjustment-set check actually does, which is what drives the per-pair cost term in the complexity account above.

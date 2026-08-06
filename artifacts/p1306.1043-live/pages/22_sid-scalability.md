# Scalability of the SID
## TL;DR {#tldr}
SID becomes more expensive as node count grows. Empirical runtime is roughly quadratic for sparse graphs and cubic for dense graphs.

This sets the benchmark size at which scoring, rather than learning, becomes the bottleneck.

## Intuition {#intuition}
SID checks whether each pair's estimated adjustment set identifies the causal effect.

More nodes create more pairs. Denser graphs create larger parent sets and more paths per check.

The study times SID across graph sizes for sparse and dense random graphs.

**Worked example:** doubling $p$ multiplies $p(p-1)$ by about four, while a dense quartic worst case permits about sixteen times the work. An observed factor between those values describes sampled behavior, not a new worst-case bound [§sec_3_3; §sec_4].

## Mechanics {#mechanics}
**The experimental setup:** for a sequence of node counts, random sparse and dense graph pairs are generated using the same graph-generation setting used elsewhere in the evaluation, and the wall-clock/processor time to compute SID on one pair is recorded [§sec_3_3].

**Why box plots over repeated pairs:** each node count is evaluated on 100 independently sampled graph pairs rather than a single pair, and the spread is shown as a box plot — this exposes how much timing varies across random instances of the same size, not just the average trend [§sec_3_3].

**The observed trend:** across the range of node counts tested, processor time grows approximately quadratically with the number of nodes for sparse graphs, and approximately cubically for dense graphs [§sec_3_3].

**Observed scaling is not a worst-case proof:** the implementation section gives a dense-matrix worst-case upper bound of $O(p^4)$. The empirical quadratic/cubic trends do not contradict that bound: they describe average timings for the sampled graph families and tested sizes, where sparsity and graph structure avoid some worst-case work [§sec_3_3; §sec_4].

## The Math {#the-math}
No cost formula is proved here. The following count is intuition for the empirical split, not a replacement for the implementation's worst-case analysis.

SID evaluates every ordered pair. Per-pair work depends on how much graph structure the check touches.

```derivation
shape: Account for why runtime is quadratic on sparse graphs and cubic on dense graphs.
steps:
  - latex: "|\\{(i,j) : i \\neq j\\}| = n(n-1) = O(n^2)"
    why: "SID makes one adjustment-set check per ordered node pair, so the number of checks alone is already quadratic in the node count before any per-check cost is added [§sec_3_3]"
  - latex: "T_{\\text{sparse}}(n) = O(n^2) \\cdot O(1) = O(n^2)"
    why: "If sampled sparse graphs keep effective per-pair work roughly bounded, the quadratic pair count can dominate; this explains the observed curve but is not a universal asymptotic guarantee [§sec_3_3]"
  - latex: "T_{\\text{dense}}(n) = O(n^2) \\cdot O(n) = O(n^3)"
    why: "If effective per-pair work grows roughly linearly on the sampled dense graphs, the result is a cubic empirical trend; worst-case instances may still exercise the quartic upper bound [§sec_3_3; §sec_4]"
```

The pair count is identical for sparse and dense graphs. Their separation comes from work per adjustment-set check in a denser neighborhood [§sec_3_3].

## Go Deeper {#go-deeper}
- **Implementation of SID** — the algorithm being timed here; read it first to see what a single adjustment-set check actually does, which is what drives the per-pair cost term in the complexity account above.

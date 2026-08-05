# SID versus SHD Simulation
## TL;DR {#tldr}
This simulation study puts SID and SHD side by side on the same random DAGs and shows they are not interchangeable: two graphs that look almost identical under SHD can have wildly different SID, because SHD only tallies edge-level disagreements while SID tallies disagreements in the causal conclusions those edges license. When the true data-generating process is a linear Gaussian model, SID turns out to count exactly the number of pairs of variables whose estimated causal effect is wrong — making it a much more direct proxy for "how much causal inference actually goes wrong" than SHD.

## Intuition {#intuition}
Think of SHD as a proofreader who counts typos in a causal graph, and SID as a fact-checker who asks whether the story the graph tells about cause and effect still holds up. A single misplaced edge (one typo) can silently break several causal claims at once, so a graph with SHD of one or two can still have a large SID; conversely, edges that don't sit on any relevant path can be wrong without disturbing the causal effects anyone cares about. Because this concept builds on the broader project of comparing causal inference methods, the simulation is really asking which distance metric a method-comparison should optimize against — and the answer favors SID whenever the downstream goal is estimating effects, not just recovering edges.

## Mechanics {#mechanics}
The experiment samples random DAG pairs $(G, H)$ over $p \in \{10, 20\}$ nodes under two edge-density regimes — sparse and dense — using i.i.d. Bernoulli edge inclusion with probability chosen so the expected edge count matches each regime, with variable order drawn from a uniform permutation each time. Plotting SID against SHD as a 2D histogram shows the two measures diverge sharply: at a fixed low SHD (one or two edge edits, especially in the dense setting) SID still ranges over many different values, meaning small structural edits can correspond to large or small causal disagreement depending on which edges moved [§sec_3_1].

To turn this into a ground-truth check rather than just a shape comparison, each DAG $G$ is paired with a linear structural equation model that is Markov with respect to $G$: coefficients drawn uniformly, noise Gaussian with mean 0 and variance 1, and equal error variances across variables — a condition that makes $G$ identifiable from the observational distribution alone [§sec_3_1]. Comparing $G$ and $H$'s implied causal effects then gives an actual count of "how many pairs got the causal effect wrong," which the right-hand histograms in the figure compare directly against SID [§sec_3_1].

## The Math {#the-math}
Because the SEM is linear and Gaussian, the entire interventional distribution collapses to a single scalar per ordered pair — the total causal effect, i.e. how much the expectation of $X_j$ shifts per unit change in an intervened $X_i$ — so two distributions can be compared just by comparing that number instead of full densities [§sec_3_1].

```derivation
shape: Recover the total causal effect from a linear Gaussian SEM in the simulation.
steps:
  - latex: "X_j = \\sum_{k \\in \\mathrm{pa}(j)} \\beta_{jk} X_k + \\varepsilon_j, \\quad \\varepsilon_j \\sim \\mathcal{N}(0,1)"
    why: "Each candidate graph is fitted with coefficients drawn uniformly and errors of equal variance, which is precisely what makes the DAG identifiable from the observed distribution [§sec_3_1]"
  - latex: "\\mathrm{effect}(X_i \\to X_j) = \\frac{\\partial}{\\partial x_i}\\, \\mathbb{E}\\big[X_j \\mid \\mathrm{do}(X_i = x_i)\\big]"
    why: "This derivative is constant in a linear model, so the whole intervention distribution for the pair is summarized by one number [§sec_3_1]"
  - latex: "\\big|\\,\\mathrm{effect}_G(X_i \\to X_j) - \\mathrm{effect}_H(X_i \\to X_j)\\,\\big| > 10^{-2}"
    why: "Two effects only count as genuinely different past this tolerance, filtering out numerical noise so the count of 'wrong' effects is well-defined [§sec_3_1]"
  - latex: "\\#\\{(i,j) : \\text{effect differs}\\} = \\mathrm{SID}(G,H)"
    why: "The empirical result: across every tested setting this count coincides exactly with SID, even though the definition of SID never guaranteed equality, only that some discriminating distribution exists [§sec_3_1]"
  - latex: "P(\\text{undetected difference}) ,\\ P(\\text{coefficient} \\to 0) \\approx 0"
    why: "The two mechanisms that could make SID overcount — a real effect difference smaller than the 10^-2 threshold, or a coefficient vanishing by chance and breaking faithfulness — both have negligible probability under i.i.d. continuous sampling, explaining why the match is exact rather than approximate [§sec_3_1]"
```

The exactness result is stronger than what the definition of SID promises: Definition of SID only requires that *some* distribution exists that discriminates the two intervention distributions for a mismatched pair, not that the count of such mismatches under an arbitrary linear Gaussian instantiation equals SID [§sec_3_1]. That the simulation nonetheless hits this count exactly, in every dense and sparse setting tested, is empirical evidence that generic linear Gaussian distributions are "generic enough" — almost surely faithful and almost surely not landing exactly on the detection threshold — for SID's worst-case guarantee to become a typical-case equality [§sec_3_1].

| Axis | SHD | SID |
|---|---|---|
| Counts | edge insertions / deletions / reversals [§sec_3_1] | pairs with a wrongly estimated total causal effect [§sec_3_1] |
| Behavior at SHD ≈ 1–2 (dense) | by construction, small | can still range widely [§sec_3_1] |
| Grounding | purely structural, distribution-free | tied to a concrete intervention distribution via the linear SEM [§sec_3_1] |
| Interpretation in this study | a proofreading count of graph edits | an (empirically exact) causal-error count [§sec_3_1] |

## Go Deeper {#go-deeper}
- Section on the main proposition — read this for the analytic bounds relating SID and SHD that the histograms in this simulation are shown to be "in par with" [§sec_3_1].
- The appendix derivation of the total causal effect for linear Gaussian SEMs — needed to see exactly how the derivative-based effect formula used here is obtained.
- The formal Definition of SID — worth revisiting alongside this page, since the simulation's exact-match result is notably stronger than what that definition alone guarantees.

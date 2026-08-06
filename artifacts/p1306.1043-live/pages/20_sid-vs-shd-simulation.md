# SID versus SHD Simulation
## TL;DR {#tldr}
This simulation tests whether SID is a different, more causally meaningful error measure than SHD.

The two scores are nearly uncorrelated: graphs with SHD about 1--2 can have very different SID.

A second experiment shows that SID exactly matches the number of wrongly estimated causal effects.

## Intuition {#intuition}
SHD counts edge mistakes; SID counts consequence mistakes.

One missing or reversed edge can break adjustment for many downstream pairs and yield large SID with little SHD. Several irrelevant edge errors can leave SID untouched.

The simulation shows this difference changes which graph looks better.

SID is abstractly defined through the existence of a discriminating distribution, not as a literal wrong-effect count.

The simulation tests that practical count, which causal-method comparison needs. The two quantities coincide almost perfectly.

**Prediction check:** hold SHD near one and increase the number of downstream targets behind a misoriented source. SID can spread across more ordered pairs even though SHD stays fixed; the simulation tests precisely that divergence [§sec_3_1].

## Mechanics {#mechanics}
**Generating comparison pairs:** two regimes use small dense and larger sparse random DAGs [§sec_3_1].

Edges are sampled i.i.d. with low or high $p$ to target expected edge counts. A uniform random variable order fixes the possible directions [§sec_3_1].

SID and SHD are computed for every pair and binned into a 2D histogram [§sec_3_1].

**Why this isolates the signal:** separately randomizing topological order prevents a favored causal shape from explaining the SID/SHD divergence [§sec_3_1].

At fixed low SHD, especially in dense graphs, SID spans a wide range. That is consistent with Proposition's loose SID/SHD bounds [§sec_3_1].

**Testing causal effects needs a distribution.** Each DAG receives a linear SEM with uniformly drawn coefficients and independent $\mathcal{N}(0,1)$ noise [§sec_3_1].

Equal error variances identify each DAG from its distribution, making a true-versus-estimated test possible [§sec_3_1].

In this linear-Gaussian model, each intervention distribution becomes one total-effect derivative [§sec_3_1].

**The counting comparison:** effects for $(i,j)$ differ only beyond $10^{-3}$, absorbing floating-point noise [§sec_3_1].

Across every tested setting, the resulting disagreeing-pair count equals SID exactly [§sec_3_1].

## The Math {#the-math}
The identification-then-linearization step is what turns SID's abstract discrimination condition into a countable quantity, and it's worth walking through why each piece is necessary.

```derivation
shape: Reducing "some distribution discriminates the intervention distributions" to a single comparable number per pair.
steps:
  - latex: "X_j = \\sum_{k \\in \\mathrm{pa}(j)} \\beta_{jk} X_k + \\epsilon_j, \\quad \\epsilon_j \\sim \\mathcal{N}(0,1)"
    why: "Fixing a linear-Gaussian SEM on each DAG gives a concrete distribution Markov to that graph, as required to instantiate SID's existential definition [§sec_3_1]"
  - latex: "\\mathrm{Var}(\\epsilon_j) = 1 \\ \\forall j"
    why: "Equal error variances make the DAG identifiable from the observational distribution, so 'the estimated graph's effect' is a well-defined number to compare against rather than one of several consistent alternatives [§sec_3_1]"
  - latex: "\\Delta_{ij} = \\frac{\\partial \\, \\mathbb{E}[X_j \\mid do(X_i = x)]}{\\partial x}"
    why: "Linearity collapses the entire interventional distribution p(X_j \\mid do(X_i=x)) to one scalar, the total causal effect — this is the number SID's abstract test is implicitly discriminating on [§sec_3_1]"
  - latex: "\\#\\{(i,j) : |\\Delta_{ij}^{G} - \\Delta_{ij}^{H}| > 10^{-3}\\}"
    why: "Thresholding turns floating-point-exact disagreement into a robust count, and this count is what the simulation shows equals SID(G,H) in every configuration tested [§sec_3_1]"
```

The equality is surprising because SID promises only some discriminating distribution, not a matching count under this particular linear-Gaussian instance.

It could fail through a true difference below $10^{-3}$ or a vanishing coefficient that violates faithfulness. Under i.i.d. uniform coefficients, exact cancellation has measure zero, so both are unlikely [§sec_3_1].

| Setting | Graph size | Edge probability $p$ | Purpose |
|---|---|---|---|
| Dense | small | higher $p$ (denser expected edge count) | stress-tests SID vs. SHD when many adjustment sets overlap [§sec_3_1] |
| Sparse | larger | lower $p$ (sparser expected edge count) | tests the same divergence at scale, where SHD=1–2 still spans a wide SID range [§sec_3_1] |

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the parent concept this simulation validates; read it for the formal discrimination definition being tested here.
- **Comparing Causal Inference Methods** — the broader motivation this simulation feeds into: why an evaluation metric needs to track wrong causal effects, not just wrong edges.
- **Proposition (SID/SHD bounds)** — the theoretical bounds this simulation's histograms are shown to be consistent with; worth reading alongside the dense-regime SHD=1–2 result.
- **Appendix derivation of the total causal effect** — referenced directly in [§sec_3_1] as the source of the derivative formula used to reduce each intervention distribution to one number.

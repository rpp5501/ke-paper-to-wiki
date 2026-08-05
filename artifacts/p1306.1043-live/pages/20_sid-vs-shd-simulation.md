# SID versus SHD Simulation
## TL;DR {#tldr}
This is the empirical check that justifies treating SID as a genuinely different — and more causally meaningful — error measure than SHD. Random pairs of DAGs are scored both ways, and the two scores turn out to be nearly uncorrelated: graphs that are almost identical edge-for-edge (SHD ≈ 1–2) can have wildly different SID. A second experiment then asks whether SID's abstract definition (does *some* distribution discriminate the two intervention distributions?) actually tracks something concrete — the number of wrongly estimated causal effects — and finds that it does, exactly.

## Intuition {#intuition}
SHD counts edge mistakes; SID counts *consequence* mistakes. A single missing or reversed edge can silently break the adjustment set used to compute a causal effect for many downstream variable pairs, so one small structural slip can produce a large SID while barely moving SHD. Conversely, several edge errors that don't disturb any relevant adjustment set leave SID untouched. This gap is the whole motivation for SID as a companion metric within Structural Intervention Distance (SID): it's asking a different question than SHD, and this simulation is the evidence that the difference isn't cosmetic — it changes which graph looks "better."

The second half of the experiment pushes further: SID is defined abstractly, via the *existence* of a discriminating distribution, not via a literal count of wrong effects. The simulation tests whether that abstract guarantee coincides with the intuitive one in practice — comparing causal inference methods should care about the latter, and it turns out the two coincide almost perfectly.

## Mechanics {#mechanics}
**Generating the comparison pairs.** For each of two regimes — small dense graphs and larger sparse graphs — random DAG pairs are drawn by sampling edges i.i.d. with probability $p$ (a low $p$ for the sparse setting, a higher $p$ for the dense one, each chosen to target a specific expected edge count) and by drawing the variable order from a uniform random permutation, which fixes which edge directions are even possible [§sec_3_1]. Both SID and SHD are computed on every sampled pair, and the results are binned into a 2D histogram of SID against SHD [§sec_3_1].

**Why this design isolates the right thing.** Randomizing the topological order separately from the edge draws prevents the sampler from favoring graphs with a particular causal shape (e.g., all hubs near the source), so the SID/SHD divergence observed can't be explained by some artifact of how the DAGs were built [§sec_3_1]. The headline finding — that a fixed low SHD (one or two edge edits) maps to a spread of SID values, especially in the dense regime — is exactly what Proposition's bounds predict, since those bounds relate SID to SHD only loosely, not tightly [§sec_3_1].

**Attaching a distribution to test the causal-effect interpretation.** For every graph pair, a linear structural equation model is built on top of each DAG: coefficients drawn uniformly, noise terms independent $\mathcal{N}(0,1)$ [§sec_3_1]. Equal error variances make each DAG identifiable from its induced distribution — this isn't incidental, it's what lets the simulation know which graph is "true" in a way that can be checked against the estimated one [§sec_3_1]. Because the model is linear-Gaussian, each intervention distribution collapses to one number per variable pair: the total causal effect, the derivative of $\mathbb{E}[X_j]$ with respect to $do(X_i = x)$ [§sec_3_1].

**The counting comparison.** For every pair $(i,j)$, the true and estimated total causal effects are compared, treating them as different only if they disagree by more than a fixed numerical threshold ($10^{-3}$, to absorb floating-point noise) [§sec_3_1]. The count of disagreeing pairs is then plotted against SID, and across every setting tested, SID equals that count exactly [§sec_3_1].

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

That last line is the empirical surprise: Definition of SID only promises that *some* distribution can tell the two graphs' intervention behavior apart, not that the count of literally-wrong effects under *this* linear-Gaussian instance will match. The two failure modes that could break the equality are informative about why it holds anyway: a true difference smaller than the $10^{-3}$ threshold, or a coefficient that happens to vanish and thereby violates faithfulness — and the text notes both occur with small probability under i.i.d. uniform coefficient draws, since the set of coefficient values producing an exact cancellation has measure zero [§sec_3_1].

| Setting | Graph size | Edge probability $p$ | Purpose |
|---|---|---|---|
| Dense | small | higher $p$ (denser expected edge count) | stress-tests SID vs. SHD when many adjustment sets overlap [§sec_3_1] |
| Sparse | larger | lower $p$ (sparser expected edge count) | tests the same divergence at scale, where SHD=1–2 still spans a wide SID range [§sec_3_1] |

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the parent concept this simulation validates; read it for the formal discrimination definition being tested here.
- **Comparing Causal Inference Methods** — the broader motivation this simulation feeds into: why an evaluation metric needs to track wrong causal effects, not just wrong edges.
- **Proposition (SID/SHD bounds)** — the theoretical bounds this simulation's histograms are shown to be consistent with; worth reading alongside the dense-regime SHD=1–2 result.
- **Appendix derivation of the total causal effect** — referenced directly in [§sec_3_1] as the source of the derivative formula used to reduce each intervention distribution to one number.

# Hidden Variables (Future Work)

## TL;DR {#tldr}
With hidden variables, the true structure may not be a fully identifiable DAG, so original SID cannot be computed outright.

This roadmap uses ADMGs or MAGs, excludes non-identifiable effects, and bounds PAG estimates as CPDAG estimates are bounded.

A looser alternative scores whether a method correctly reports identifiability itself.

## Intuition {#intuition}
SID assumes true-DAG parent sets give the intervention distributions used to check an estimate.

Hidden confounders can make $p(y\mid do(x))$ unrecoverable from every observed adjustment set. Such pairs are unanswerable, not wrong, and should not affect the score.

As with equivalence classes, exclude what cannot be judged and count what can.

Hidden variables make identifiability itself harder because the true-graph surrogate is less informative than a DAG.

**Boundary case:** with an unobserved common cause $U\to X$ and $U\to Y$, no observed parent set containing $U$ is available. A pair whose effect cannot otherwise be identified must be excluded, not scored as an SID mistake [§sec_2_4_6].

## Mechanics {#mechanics}
**Candidate truth objects grow harder:**

| Object | What it represents | SID consequence |
|---|---|---|
| ADMG | Confounders marked by bidirected edges | Existing work identifies effects; exclude non-identifiable pairs |
| MAG | Coarser ancestral/separation representation without a confounder marker | Identifiability is harder |
| PAG | Equivalence class of MAGs returned by FCI-type methods | Bound over member MAGs, as CPDAGs bound over DAGs [§sec_2_4_6] |

**Estimated PAG versus true MAG reuses CPDAG machinery.** A PAG does not select one MAG, so enumerate its MAGs and take SID lower and upper bounds [§sec_2_4_6].

Making that enumeration efficient remains open [§sec_2_4_6].

```algorithm
title: Roadmap — comparing an estimated PAG to the true MAG
lines:
  - code: "for each ordered pair (i, j):"
    intent: "SID is still scored pointwise per intervention target/effect pair, as in the DAG and CPDAG cases [§sec_2_4_6]"
  - code: "    if effect of i on j is non-identifiable under the true structure:"
    intent: "Hidden confounders can make an intervention distribution unrecoverable from the graph alone [§sec_2_4_6]"
  - code: "        exclude (i, j) from the count"
    intent: "Mirrors how CPDAG-SID drops pairs whose orientation is undetermined by the equivalence class [§sec_2_4_6]"
  - code: "    else:"
    intent: "Only identifiable effects can meaningfully be checked against the estimate [§sec_2_4_6]"
  - code: "        enumerate every MAG consistent with the estimated PAG"
    intent: "A PAG stands for a class of MAGs just as a CPDAG stands for a class of DAGs [§sec_2_4_6]"
  - code: "        compute lower and upper bound of the mismatch over that class"
    intent: "Reuses the bracketing already built for CPDAG-vs-DAG, since no single representative MAG can be singled out [§sec_2_4_6]"
```

**A looser method-agnostic alternative avoids graph comparison.** A method can report a usable adjustment set or "not identifiable" for each pair [§sec_2_4_6].

Score the fraction correctly identified as identifiable and correctly solved. This trades structural precision for applicability beyond DAG/CPDAG estimators [§sec_2_4_6].

## The Math {#the-math}
**The obstacle is identifiability:** with latent confounding, two compatible causal models can agree observationally while assigning different values to the same intervention distribution. A distance cannot score that pair as simply right or wrong without first specifying which effects are identifiable [§sec_2_4_6].

**Why ADMG identifiability is easier than MAG identifiability:** a DAG has one graph-determined $\mathrm{pa}(X)$ adjustment set [§sec_2_4_6].

An ADMG preserves confounder markers through bidirected edges, permitting an existing edge-by-edge characterization. A MAG discards those markers [§sec_2_4_6].

A MAG retains ancestral and separation relations but not the latent structure itself. Identifiability must range over its compressed family, so the characterization is harder [§sec_2_4_6].

**Why PAG enumeration compounds CPDAG cost:** an undirected CPDAG edge has two resolutions, so each doubles member-DAG count [§sec_2_4_6].

A PAG edge has independently resolved endpoint marks. It permits at least as many resolutions, typically more, so its class grows at least as fast [§sec_2_4_6].

This motivates lower/upper bounds rather than exact counts and leaves efficiency open [§sec_2_4_6].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — this section is explicitly framed as extending SID's machinery (exclusion of non-identifiable pairs, lower/upper bounding over an equivalence class) to settings with hidden variables; read it first to see the CPDAG version of the same bounding trick this roadmap reuses.

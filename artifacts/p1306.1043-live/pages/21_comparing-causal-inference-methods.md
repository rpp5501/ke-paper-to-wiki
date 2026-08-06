# Comparing Causal Inference Methods

## TL;DR {#tldr}
SID and SHD can rank causal-discovery methods differently on the same simulated data.

A method may recover the skeleton yet orient edges badly, looking strong under SHD and mediocre under SID.

Structural and causal closeness differ. Extra identifiability assumptions can drive SID toward zero.

## Intuition {#intuition}
Methods differ by assumptions:

- PC, CPC, and GES return CPDAGs because observational data alone leaves some directions undetermined.
- Greedy DAG search adds equal error variances, identifying the full DAG.
- RAND ignores data and returns a DAG with a random edge count.

Skeleton and orientation accuracy matter differently to the metrics. SHD assigns one point to a missing, extra, or reversed edge.

SID counts broken causal-effect predictions. One bad root orientation can invalidate every descendant effect while costing SHD one point.

A method can therefore look reasonable by SHD while its causal claims are barely better than a coin flip.

Assumptions buy identifiability, which collapses a CPDAG to one DAG.

GDS exploits equal-variance linear Gaussian SEMs, an assumption PC, CPC, and GES do not use. That removes its orientation-ambiguity band.

**Counterexample:** a CPDAG can recover the correct skeleton and look close under SHD while its worst member orients a root badly and scores poorly under SID. Correct adjacency alone is therefore not evidence of reliable intervention predictions [§sec_3_2].

## Mechanics {#mechanics}
The pipeline draws a sparse true DAG, samples an equal-variance linear Gaussian SEM with uniform coefficients, then scores each method against truth [§sec_3_2].

Repeated runs and averages prevent one lucky graph or data set from determining the comparison [§sec_3_2].

```algorithm
title: Simulation protocol for comparing causal discovery methods
lines:
  - code: "for each (n, p) setting:"
    intent: "n is the sample size and p the number of nodes; performance is compared across a grid of both [§sec_3_2]"
  - code: "  repeat 100 times:"
    intent: "Averaging over 100 independent DAGs and datasets keeps the reported SID/SHD from being an artifact of one graph [§sec_3_2]"
  - code: "    G_true = random sparse DAG()"
    intent: "The ground truth is unknown to every method being scored, mimicking a real discovery setting [§sec_3_2]"
  - code: "    data = sample linear-Gaussian SEM(G_true, equal error variances)"
    intent: "Equal error variances is a deliberate modeling choice: it is the extra structure GDS alone is built to exploit [§sec_3_2]"
  - code: "    for method in {PC, CPC, GES, GDS, RAND}:"
    intent: "PC/CPC/GES only assume a linear Gaussian SEM; GDS additionally assumes equal variances; RAND uses no data at all [§sec_3_2]"
  - code: "      out = method(data)"
    intent: "GDS returns a single DAG because equal-variance identifiability pins down orientations that PC/CPC/GES cannot [§sec_3_2]"
  - code: "      if out is a CPDAG: score = (SID_lower(out, G_true), SID_upper(out, G_true))"
    intent: "For an equivalence class, report the best- and worst-case member DAG rather than pretending there is one answer [§sec_3_2]"
  - code: "      else: score = SID(out, G_true)"
    intent: "GDS and RAND already output a single DAG, so no bound is needed [§sec_3_2]"
  - code: "  average and report SID, SHD across the 100 repeats"
    intent: "Reporting both metrics side by side is what lets a method's ranking flip between them become visible [§sec_3_2]"
```

PC, CPC, and GES receive two SID rows because each returns a CPDAG. One member DAG can be near zero SID and another near worst-case [§sec_3_2].

Equivalence-class SID supplies the lower/upper pair. GDS and RAND output one DAG: GDS through identifiability and RAND through arbitrary orientation [§sec_3_2].

## The Math {#the-math}
The ranking divergence is sharpest at small sample sizes. RAND non-negligibly often beat PC's *upper-bound* DAG under SID, but rarely beat it under SHD [§sec_3_2].

Same data and PC output yield opposite conclusions, evidence that PC's failure is orientation rather than skeleton recovery [§sec_3_2].

| Method | Output | Extra assumption used | SID bound behavior at small n |
|---|---|---|---|
| PC | CPDAG | Linear Gaussian SEM, faithfulness | Upper bound can be no better than RAND [§sec_3_2] |
| CPC | CPDAG | + conservative orientation rule | Same lower/upper structure as PC, more edges left unoriented [§sec_3_2] |
| GES | CPDAG | Score-based search, linear Gaussian SEM | Same lower/upper structure as PC [§sec_3_2] |
| GDS | single DAG | + equal error variances (identifiability) | No bound needed; SID collapses toward the identified DAG [§sec_3_2] |
| RAND | single DAG | none — ignores the data | Baseline; the yardstick the others must beat [§sec_3_2] |

Small samples leave orientation unresolved. PC's worst member DAG can differ from truth on nearly every direction, matching RAND's constructed failure and converging to its SID [§sec_3_2].

SHD charges one per wrong orientation, so a CPDAG with correct skeleton can still look close. PC can thus be best by SHD and worst by SID in one $(n,p)$ cell [§sec_3_2].

Equal error variances identify the DAG, not just its class. GDS therefore carries no orientation ambiguity into its score [§sec_3_2].

## Go Deeper {#go-deeper}
- **SID versus SHD Simulation** (builds on this page) — the single-DAG-output version of this same experiment (GDS only), before CPDAG-outputting methods and their lower/upper bounds are introduced.
- The Markov-equivalence-class extension of SID referenced here (turning one CPDAG into a lower and an upper bound) is worth reading in full where SID is extended from DAG-vs-DAG to DAG-vs-CPDAG comparisons — it's the mechanism that makes PC, CPC, and GES scoreable at all in this table.
- The equal-error-variance identifiability result that GDS relies on is the reason it alone escapes the bound machinery — worth tracing back to where that identifiability claim is established.

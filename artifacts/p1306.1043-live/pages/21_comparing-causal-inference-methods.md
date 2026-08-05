# Comparing Causal Inference Methods

## TL;DR {#tldr}
When several causal discovery algorithms are run on the same simulated data and scored against the true DAG, SID and SHD frequently disagree about which method won — a method that reconstructs the causal skeleton well but gets edge directions wrong can look strong under SHD and mediocre-to-random under SID. The comparison exposes that "structurally close" and "causally close" are different properties, and that exploiting extra identifiability assumptions (rather than just more data) is what lets a method's SID collapse toward zero.

## Intuition {#intuition}
Think of the methods on a spectrum of how much they assume. PC and its conservative variant (CPC) and GES search only for a Markov equivalence class — a CPDAG — because that's all the observational distribution can tell them without further assumptions; some edges are left undirected. Greedy DAG search adds one more assumption, equal error variances, which happens to make the full DAG identifiable, not just its equivalence class. RAND adds nothing: it ignores the data entirely and returns a DAG with a random edge count.

The punchline of the comparison is that skeleton accuracy and orientation accuracy matter very differently to the two metrics. SHD counts edges: a missing edge, an extra edge, and a reversed edge all cost the same, one point. SID counts broken causal-effect predictions, and a single wrong orientation near the root of the graph can invalidate the predicted intervention effect for every descendant, while the same reversal contributes only one unit to SHD. A method can therefore look reasonable by SHD's bookkeeping while its causal claims are barely better than a coin flip.

The other intuition worth carrying forward is that assumptions are what buy identifiability, and identifiability is what collapses the CPDAG down to a single DAG. GDS isn't "smarter" in a generic sense — it's exploiting a fact about equal-variance linear Gaussian SEMs that PC, CPC, and GES don't use, and that's exactly what removes the ambiguity band that plagues the other methods' evaluation.

## Mechanics {#mechanics}
The experiment repeats a fixed pipeline: draw a sparse random ground-truth DAG, generate data from a linear Gaussian structural equation model with equal error variances and uniformly-drawn coefficients, then hand that same data to each competing method and score its output against the known DAG [§sec_3_2]. Repeating this many times per configuration and averaging is what turns a single lucky or unlucky run into a comparison that means something [§sec_3_2].

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

The reason PC, CPC, and GES each get two rows instead of one is that they only ever commit to a CPDAG, and the same equivalence class can contain a DAG whose SID to the truth is near zero and one whose SID is close to the worst possible — the earlier extension of SID to equivalence classes is what supplies this lower/upper bound pair [§sec_3_2]. GDS and RAND need no such bound since both output one concrete DAG per run, though for opposite reasons: GDS earns identifiability from its assumption, RAND simply commits to an arbitrary orientation [§sec_3_2].

## The Math {#the-math}
The central empirical claim is a divergence between two rankings, and it's sharpest at small sample size: for small n and p, the number of simulation runs where a random DAG (RAND) actually beat PC's own *upper-bound* DAG under SID was reported as non-negligible, whereas under SHD, RAND beat PC in far fewer of the same runs [§sec_3_2]. That single contrast — same data, same PC output, opposite conclusion depending on which metric is applied — is the paper's evidence that PC's failure mode is orientation, not skeleton recovery [§sec_3_2].

| Method | Output | Extra assumption used | SID bound behavior at small n |
|---|---|---|---|
| PC | CPDAG | Linear Gaussian SEM, faithfulness | Upper bound can be no better than RAND [§sec_3_2] |
| CPC | CPDAG | + conservative orientation rule | Same lower/upper structure as PC, more edges left unoriented [§sec_3_2] |
| GES | CPDAG | Score-based search, linear Gaussian SEM | Same lower/upper structure as PC [§sec_3_2] |
| GDS | single DAG | + equal error variances (identifiability) | No bound needed; SID collapses toward the identified DAG [§sec_3_2] |
| RAND | single DAG | none — ignores the data | Baseline; the yardstick the others must beat [§sec_3_2] |

Why the upper bound degrades to random performance is a direct consequence of what the CPDAG leaves unresolved: when the sample size is too small to pin down orientation, the true DAG and the worst member of PC's returned equivalence class can differ on essentially every edge direction, which is the same failure mode RAND exhibits by construction, so their SID values converge [§sec_3_2]. Under SHD this convergence does not happen, because SHD only ever penalizes each wrong orientation by one, so a CPDAG that gets the skeleton right and the orientations wrong still scores close to the truth on SHD even in its worst-case member — which is exactly why PC can be reported as best by SHD and worst by SID in the same (n, p) cell [§sec_3_2]. The gap between GDS and the CPDAG-based methods is the identifiability argument made quantitative: equal error variances is enough extra structure to determine the DAG (not just its equivalence class) from the observational distribution, so GDS carries no orientation ambiguity into its score at all [§sec_3_2].

## Go Deeper {#go-deeper}
- **SID versus SHD Simulation** (builds on this page) — the single-DAG-output version of this same experiment (GDS only), before CPDAG-outputting methods and their lower/upper bounds are introduced.
- The Markov-equivalence-class extension of SID referenced here (turning one CPDAG into a lower and an upper bound) is worth reading in full where SID is extended from DAG-vs-DAG to DAG-vs-CPDAG comparisons — it's the mechanism that makes PC, CPC, and GES scoreable at all in this table.
- The equal-error-variance identifiability result that GDS relies on is the reason it alone escapes the bound machinery — worth tracing back to where that identifiability claim is established.

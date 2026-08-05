# SID between a DAG and a CPDAG

## TL;DR {#tldr}
When an estimation method returns not a single DAG but a Markov equivalence class — a CPDAG, as produced by the PC-algorithm or Greedy Equivalence Search — there is no single "estimated graph" to compare against the truth. Structural Intervention Distance (SID) handles this by refusing to collapse the class to one representative: instead it returns an interval, a lower and an upper bound on the SID that any DAG in the equivalence class could have achieved. The interval's width is itself informative — a narrow interval means the equivalence class is nearly unanimous about which interventions the estimate gets right, a wide one means the class contains members that disagree sharply, from perfect to worst-case.

## Intuition {#intuition}
The naive fix would be to enumerate every DAG consistent with the CPDAG, compute the ordinary DAG-vs-DAG SID for each, and report the resulting spread of numbers. That is exactly right in spirit, but the equivalence class can be exponentially large, so exhaustive enumeration is only a fallback for small graphs. The extension used here instead reasons locally: it exploits the fact that within a CPDAG, only the chain components (the undirected blocks) carry the ambiguity, and works out the best- and worst-case orientation of each block separately before combining them. That local decomposition is what keeps the computation tractable on graphs where full enumeration would not finish.

## Mechanics {#mechanics}
The starting point is the ideal but expensive procedure: enumerate every DAG in the Markov equivalence class the CPDAG represents, compute the SID against the true DAG for each, and read off the resulting vector of distances as lower and upper bounds. Because enumeration explodes with graph size, the method instead extends the CPDAG locally, one chain component at a time, which for sparse graphs is considerably cheaper [§sec_2_4_1].

```algorithm
title: Local extension procedure for SID(G, C)
lines:
  - code: "for each chain component of C (chain components of a valid CPDAG are chordal):"
    intent: "Only chain components carry orientation ambiguity; everything already directed in C is fixed, so only these blocks need to be resolved [§sec_2_4_1]"
  - code: "    enumerate all DAG orientations of that component, leaving other components undirected"
    intent: "Chordality guarantees every one of these local orientations is a valid member of the equivalence class, so none of them can be ruled out a priori [§sec_2_4_1]"
  - code: "    for each orientation, for each vertex in the component, evaluate the SID-relevant comparison to G"
    intent: "Produces one length-vector per orientation, mirroring what a full DAG-vs-DAG SID would compute for that vertex [§sec_2_4_1]"
  - code: "    reduce each orientation's vector to its sum, then track the min and max sum seen"
    intent: "The min and max over orientations are exactly the best-case and worst-case DAG completions of that component [§sec_2_4_1]"
  - code: "SID_lower(G,C) = sum of per-component minima; SID_upper(G,C) = sum of per-component maxima"
    intent: "Summing minima (resp. maxima) independently across components is valid because the construction guarantees neighboring components' orientations never contradict each other, so the best-case (worst-case) choices can be made component-by-component and still correspond to one real DAG in the class [§sec_2_4_1]"
```

Both resulting bounds are therefore tight in the strong sense that each is attained by an actual DAG member of the equivalence class of the CPDAG, not just by an infeasible combination of per-component extremes [§sec_2_4_1].

The interval can be wide. If the true DAG is a Markov chain, its equivalence class contains the correct DAG itself — giving a lower bound of zero — but also contains the fully reversed chain, which gets every intervention distribution wrong and pushes the upper bound toward the maximum possible value, on the scale of the total number of ordered vertex pairs the metric counts over [§sec_2_4_1].

The local-extension trick assumes the input actually is a valid CPDAG, i.e. that every chain component is chordal. That assumption can fail — for instance for PC-algorithm output learned from finite data or in the presence of hidden variables — in which case the procedure falls back to treating, for each vertex, every subset of its undirected neighbors as a candidate parent set and again reporting lower and upper bounds; the same fallback is used when a chain component is too large (more than eight nodes) for full local enumeration to be practical [§sec_2_4_1].

## The Math {#the-math}
The comparison is redefined as a map into a pair of naturals rather than a single number, reflecting that a CPDAG stands for a whole class of DAGs rather than one fixed structure [eq_8]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{C} &\rightarrow& \mathbb{N} \times \mathbb{N}\\
(\G,\CC)& \mapsto & \big({\SID}_{\mathrm{lower}}(\G,\CC), {\SID}_{\mathrm{upper}}(\G,\CC)\big)
\end{array}$$ [eq_8]

```annotated-eq
latex: "\\mathrm{SID}: \\; \\mathbb{G} \\times \\mathbb{C} \\rightarrow \\mathbb{N} \\times \\mathbb{N}, \\quad (\\G,\\CC) \\mapsto \\big({\\SID}_{\\mathrm{lower}}(\\G,\\CC), {\\SID}_{\\mathrm{upper}}(\\G,\\CC)\\big)"
terms:
  - tex: "\\mathbb{G} \\times \\mathbb{C}"
    role: 1
    words: "Domain: a true DAG paired with an estimated CPDAG, not two DAGs — the reason a single output number no longer suffices [eq_8]"
  - tex: "\\mathbb{N} \\times \\mathbb{N}"
    role: 2
    words: "Codomain is a pair, not a scalar: SID becomes interval-valued precisely because the CPDAG represents many DAGs at once [eq_8]"
  - tex: "{\\SID}_{\\mathrm{lower}}(\\G,\\CC)"
    role: 3
    words: "Best case over the equivalence class — attained by whichever member DAG happens to match the truth most closely on identifiable interventions [eq_8]"
  - tex: "{\\SID}_{\\mathrm{upper}}(\\G,\\CC)"
    role: 4
    words: "Worst case over the equivalence class — attained by the member that gets the most identifiable interventions wrong [eq_8]"
```

The bounds are not arbitrary summary statistics; they have an exact combinatorial reading in terms of which intervention distributions the CPDAG can even pin down. The lower bound counts distributions that are identifiable from the CPDAG and that it identifies incorrectly, while the upper bound's complement counts distributions identifiable and identified correctly — and both statements loosen to inequalities once "identifiable" is tightened to "strictly identifiable," since strict identifiability is the harder condition to satisfy [eq_9]:

$$\begin{aligned}
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ identifiable in }\CC \text{ wrt } \G \text{ and}\\
\text{ inferred falsely by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;= \;{\SID}_{\mathrm{lower}}(\G,\CC)  \\
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ identifiable in }\CC \text{ wrt } \G \text{ and}\\
\text{ inferred correctly by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;= \;p \cdot (p-1) - {\SID}_{\mathrm{upper}}(\G,\CC)\\
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ strictly identifiable in }\CC \text{ and}\\
\text{ inferred falsely by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;\leq \;{\SID}_{\mathrm{lower}}(\G,\CC)  \\
\# \left\{ \text{interv. distr. that are } 
\begin{array}{c}
\text{ strictly identifiable in }\CC \text{ and}\\
\text{ inferred correctly by }\CC \text{ wrt } \G
\end{array}
\right\}
&\;\leq \;p \cdot (p-1) - {\SID}_{\mathrm{upper}}(\G,\CC)\,.
\end{aligned}$$ [eq_9]

```derivation
shape: Why the bounds are pinned to identifiable-in-C rather than strictly-identifiable distributions.
steps:
  - latex: "\\text{intervention distr. is \\emph{identifiable in } } \\CC \\text{ wrt } \\G"
    why: "Holds if the effect is the same across every distribution Markov to G that happens to lie in C's equivalence class — a property of this particular class, not of C's DAG structure in isolation [§sec_2_4_1]"
  - latex: "\\text{intervention distr. is \\emph{strictly identifiable} in } \\CC"
    why: "The stronger condition: the effect is fixed for every distribution Markov to C itself, independent of which true DAG generated the data — strict identifiability implies identifiability-in-C but not conversely, which is why the strict counts only bound (\\leq) the lower/upper terms rather than equal them [§sec_2_4_1]"
  - latex: "{\\SID}_{\\mathrm{lower}}(\\G,\\CC), \\; p(p-1) - {\\SID}_{\\mathrm{upper}}(\\G,\\CC)"
    why: "Using the weaker, identifiable-in-C notion for the bound is deliberately conservative: if the CPDAG is meant to nominate candidate experiments worth running, discarding a distribution just because it fails the stricter test risks throwing away a genuinely good candidate [§sec_2_4_1]"
```

Read together, eq_8 and eq_9 say the same thing at two levels: eq_8 fixes the *shape* of the answer (a pair, not a scalar), and eq_9 explains *why* that pair is meaningful — each bound is literally a count of correctly- or incorrectly-inferred intervention effects, not just an optimization artifact of the local-extension algorithm [eq_9].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the DAG-vs-DAG base metric this concept generalizes; understanding its single-number definition is the prerequisite for seeing why a CPDAG forces a pair of bounds instead.
- **SID between a CPDAG and a DAG or CPDAG** — the further generalization that reuses this same lower/upper-bound machinery when the *true* graph is itself only known up to Markov equivalence.
- **R implementation (first author's homepage)** — the reference code implementing both the local chordal-component extension and the subset-of-neighbors fallback for non-CPDAG or oversized chain-component inputs [§sec_2_4_1].

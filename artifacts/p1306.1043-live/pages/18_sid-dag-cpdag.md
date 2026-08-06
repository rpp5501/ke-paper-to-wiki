# SID between a DAG and a CPDAG

## TL;DR {#tldr}
A CPDAG is a Markov equivalence class, not one estimated DAG. PC and Greedy Equivalence Search can return this form.

SID returns a lower and upper bound instead of choosing one representative. Any member DAG's SID lies in that interval.

A narrow interval means near agreement about correct interventions. A wide interval means members disagree, potentially from perfect to worst-case.

## Intuition {#intuition}
Enumerating every DAG in the CPDAG and reporting their SID range is conceptually right. Its exponential class size makes it feasible only for small graphs.

The extension instead resolves each ambiguous chain component locally. It combines each block's best and worst orientation, which keeps the calculation tractable.

**Boundary case:** if a CPDAG's class contains the true DAG, its SID lower bound is zero. The upper bound can still be positive because another member may orient the same skeleton differently [§sec_2_4_1].

## Mechanics {#mechanics}
The ideal procedure enumerates member DAGs, computes SID against truth, and takes the minimum and maximum. Its graph-size explosion motivates local chain-component extension [§sec_2_4_1].

For sparse graphs, local extension is considerably cheaper [§sec_2_4_1].

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

The interval can be wide. A true Markov chain's equivalence class contains the correct DAG, giving lower bound zero [§sec_2_4_1].

It can also contain the fully reversed chain, which gets every intervention distribution wrong and drives the upper bound toward the ordered-pair maximum [§sec_2_4_1].

Local extension assumes a valid CPDAG, so each chain component is chordal [§sec_2_4_1].

Finite-data PC output and hidden variables can violate that assumption. The fallback tries every subset of a vertex's undirected neighbors as candidate parents and still returns bounds [§sec_2_4_1].

The same fallback applies when a chain component exceeds eight nodes [§sec_2_4_1].

## The Math {#the-math}
The comparison is redefined as a map into a pair of naturals rather than a single number, reflecting that a CPDAG stands for a whole class of DAGs rather than one fixed structure [eq_8]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{C} &\rightarrow& \mathbb{N} \times \mathbb{N}\\
(\G,\CC)& \mapsto & \big({\SID}_{\mathrm{lower}}(\G,\CC), {\SID}_{\mathrm{upper}}(\G,\CC)\big)
\end{array}
$$ [eq_8]

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

The bounds have an exact combinatorial meaning, not merely a summary-statistic role [eq_9].

The lower bound counts identifiable distributions inferred incorrectly. The upper bound's complement counts identifiable distributions inferred correctly [eq_9].

With the stricter notion of strict identifiability, both equalities become inequalities [eq_9]:

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
\end{aligned}
$$ [eq_9]

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

Eq. 8 fixes the answer's shape: a pair rather than a scalar. Eq. 9 gives that pair its interpretation [eq_9].

Each bound is a count of correctly or incorrectly inferred intervention effects, not an optimization artifact [eq_9].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — the DAG-vs-DAG base metric this concept generalizes; understanding its single-number definition is the prerequisite for seeing why a CPDAG forces a pair of bounds instead.
- **SID between a CPDAG and a DAG or CPDAG** — the further generalization that reuses this same lower/upper-bound machinery when the *true* graph is itself only known up to Markov equivalence.
- **R implementation (first author's homepage)** — the reference code implementing both the local chordal-component extension and the subset-of-neighbors fallback for non-CPDAG or oversized chain-component inputs [§sec_2_4_1].

# SID between a DAG and a CPDAG

## TL;DR {#tldr}

When the estimated graph is a CPDAG rather than a single DAG, it stands for a whole Markov equivalence class of DAGs at once, so a single SID number no longer makes sense — instead SID reports a lower and an upper bound, the scores of the best-case and worst-case DAG the CPDAG could represent. Rather than enumerating every DAG in the class (infeasible for large graphs), the extension is computed locally, chain component by chain component, which is the key trick that keeps this practical for sparse graphs.

## Intuition {#intuition}

Methods like the PC-algorithm or Greedy Equivalence Search don't commit to edge directions they can't identify from data — they output a CPDAG, leaving some edges undirected wherever the data is compatible with either orientation. Every full orientation consistent with those constraints is an equally valid DAG member of the same equivalence class, and different members can have wildly different structural intervention distances to the truth. So instead of pretending the CPDAG picks out one graph, this extension asks two honest questions: how good is the best DAG in that class, and how bad is the worst one? The interval between those answers is the fair way to score an equivalence-class estimate, and it also tells you how much the undirectedness itself is costing you — a narrow interval means orientation ambiguity barely matters here, a wide one means it matters a lot.

## Mechanics {#mechanics}

A CPDAG only represents a genuine Markov equivalence class when each of its chain components (maximal sets of nodes connected by undirected edges) is chordal, which is what licenses treating "all DAG orientations of a chain component" as a well-defined, enumerable object rather than an arbitrary guess [§sec_2_4_1]. The extension therefore works component by component: fix everything outside a chain component, enumerate every DAG orientation of that component alone, leave every other component undirected, and score each local extension — this is strictly cheaper than enumerating full-graph DAG members because the combinatorics are confined to one chordal component at a time [§sec_2_4_1].

```algorithm
title: Lower/upper bound extension of a DAG–CPDAG SID
lines:
  - code: "for each chain component K of the CPDAG C:"
    intent: "Only chordal components admit a well-defined set of DAG orientations, so the extension must be done component-wise [§sec_2_4_1]"
  - code: "    enumerate all DAG orientations of K, leaving other components undirected"
    intent: "Restricting enumeration to one component keeps the blow-up local instead of global, which is the source of the speed-up for sparse graphs [§sec_2_4_1]"
  - code: "    for each orientation and each vertex in K, compute the per-vertex SID contribution vector"
    intent: "Building per-vertex vectors lets the min and max be taken coordinate-wise before summing, rather than re-scoring whole DAGs [§sec_2_4_1]"
  - code: "    record min(sum) and max(sum) over these vectors"
    intent: "The minimum and maximum correspond to the best- and worst-case DAG extensions achievable within this component [§sec_2_4_1]"
  - code: "SID_lower = sum of per-component minima; SID_upper = sum of per-component maxima"
    intent: "Summing minima/maxima across components (rather than mixing orientations arbitrarily) guarantees the bounds are still achieved by a single consistent DAG in the equivalence class [§sec_2_4_1]"
```

The reason summing per-component minima (or maxima) still gives an achievable bound, and not just a loose combination, is that the definition enforces that neighborhood orientations at shared nodes never contradict each other across components — so both the lower and upper bound are each realized by some actual DAG member of the equivalence class of the CPDAG, not by an inconsistent patchwork [§sec_2_4_1]. This bound can be very loose: if the true DAG is a chain of length p, its equivalence class contains that exact chain (SID = 0, the lower bound) but also the fully reversed chain, which attains the maximal possible SID (the upper bound) — so a single equivalence class can span the entire range from perfect to worst-case [§sec_2_4_1]. When the CPDAG assumption itself breaks — output from finite-sample PC-algorithm runs or from settings with hidden variables, where the graph may not represent a true equivalence class, or where a chain component exceeds eight nodes — the same lower/upper bound machinery is kept but the enumeration is replaced by considering all subsets of a node's undirected neighbors as candidate parent sets, a fallback shipped in the authors' R implementation [§sec_2_4_1].

## The Math {#the-math}

SID on a DAG against a CPDAG is redefined as a pair rather than a scalar, mapping into two natural numbers instead of one [eq_8]:

$$\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{C} &\rightarrow& \mathbb{N} \times \mathbb{N}\\
(\G,\CC)& \mapsto & \big({\SID}_{\mathrm{lower}}(\G,\CC), {\SID}_{\mathrm{upper}}(\G,\CC)\big)
\end{array}$$ [eq_8]

```annotated-eq
latex: "\\mathrm{SID}: \\; \\mathbb{G} \\times \\mathbb{C} \\rightarrow \\mathbb{N} \\times \\mathbb{N}"
terms:
  - tex: "\\mathbb{G}"
    role: 1
    words: "The space of true DAGs — SID still needs a single ground-truth DAG, only the estimate side becomes an equivalence class [eq_8]"
  - tex: "\\mathbb{C}"
    role: 2
    words: "The space of CPDAGs, each standing in for potentially many DAGs that share the same conditional independencies [eq_8]"
  - tex: "\\mathbb{N} \\times \\mathbb{N}"
    role: 3
    words: "The codomain is a pair, not a scalar: a single number cannot represent 'best case and worst case' at once [eq_8]"
```

The bounds are not an arbitrary min/max convenience — the remark ties them exactly to counts of identifiable intervention distributions, which is what justifies calling them a *lower* and *upper* bound rather than just two numbers [eq_9]:

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
shape: Why the bounds land where they do, from identifiability to inequality.
steps:
  - latex: "\\text{identifiable in } \\CC \\text{ wrt } \\G"
    why: "A weaker requirement than strict identifiability: the effect only needs to agree across DAGs consistent with C and this particular G, not across every distribution Markov to C [§sec_2_4_1]"
  - latex: "\\#\\{\\text{identifiable, inferred falsely}\\} = \\SID_{\\mathrm{lower}}(\\G,\\CC)"
    why: "Equality (not inequality) holds here because identifiable-wrt-G is exactly the notion the lower bound was built to count — this is the equation that gives the bound its meaning, not just a name [eq_9]"
  - latex: "\\#\\{\\text{strictly identifiable, inferred falsely}\\} \\leq \\SID_{\\mathrm{lower}}(\\G,\\CC)"
    why: "Strict identifiability is a stronger, G-independent condition, so its count of false inferences can only be smaller or equal — the equality above becomes an inequality once the reference set shrinks [eq_9]"
  - latex: "\\text{choosing identifiable-wrt-}\\G \\text{ over strictly identifiable}"
    why: "This is a deliberate conservative choice: using the weaker notion for the bounds means no genuinely good candidate experiment for detecting strong causal effects gets excluded from consideration [§sec_2_4_1]"
```

## Go Deeper {#go-deeper}

- **[[Structural Intervention Distance (SID)]]** — the base DAG-to-DAG definition this concept extends; read it first since the lower/upper bounds here are built from per-vertex SID contributions defined there.
- **[[SID between a CPDAG and a DAG or CPDAG]]** — the further generalization that builds on this page's local chain-component extension when the *true* graph is also uncertain, not just the estimate.
- **Authors' R implementation** — the paper notes the chordal chain-component extension, the >8-node fallback, and the hidden-variable/finite-sample fallback (subsets of undirected neighbors as candidate parent sets) are all implemented in code on the first author's homepage, useful if you need to see the enumeration and bounding logic concretely rather than reconstruct it from the prose [§sec_2_4_1].

# Structural Hamming Distance (SHD)
## TL;DR {#tldr}
SHD counts how many edges two graphs disagree on — a simple edit-distance between an estimated causal graph and the true one. This paper uses it purely as a baseline: something to contrast against the Structural Intervention Distance (SID), which measures whether graph errors actually change causal predictions rather than just whether edges are drawn differently.

## Intuition {#intuition}
Think of SHD as a proofreading count: line up the two graphs edge by edge and tally every place they disagree — an edge present in one but not the other, or drawn in a different direction. It treats every disagreement as a graph-editing problem, with no regard for what the edges are *for*.

That's exactly what makes it a useful foil for SID. Two graphs can have a small SHD yet make wildly different causal predictions, or a large SHD yet agree on every intervention effect that matters. SHD answers "how different do these graphs look?"; SID answers "how different do these graphs behave, causally?" — the two are deliberately pitted against each other throughout the paper.

## Mechanics {#mechanics}
**What it's defined over:** SHD is a function on pairs of PDAGs (partially directed acyclic graphs) — graphs that may mix directed and undirected edges, the natural output of algorithms that only estimate a Markov equivalence class rather than a single DAG. Since a DAG is just a PDAG with no undirected edges, the same definition gives a DAG-to-DAG distance for free, as a special case rather than a separate formula [§sec_1_1].

**What counts as a disagreement:** for every ordered pair of variables $(i,j)$, SHD checks whether the two graphs draw the *same type* of edge between $i$ and $j$ — no edge, $i\to j$, $j \to i$, or the undirected $i-j$ — and counts the pairs where they don't [§sec_1_1].

**Why ordered pairs, not unordered ones:** running the count over $\mathcal{V}^2$ rather than over unordered pairs $\{i,j\}$ is what makes SHD penalize a *reversed* edge more heavily than a *missing* one. An edge orientation is really encoded by two slots — "is there an arrowhead at $j$" and "is there an arrowhead at $i$" — and a reversal flips both slots while an outright addition or deletion flips only one. The ordered-pair formulation bakes that asymmetry directly into the count instead of needing a separate rule for it [eq_1].

**Role in this paper:** SHD isn't proposed as a contribution here — it's the incumbent measure the paper compares its own metric against, and the point of introducing it early is to give SID something concrete to disagree with later [§sec_1_1].

## The Math {#the-math}
The formal definition maps a pair of PDAGs to a natural number by counting type-mismatched ordered pairs [eq_1]:

$$\begin{array}{rcll}
\mathrm{SHD}: \; \mathbb{P} \times \mathbb{P} &\rightarrow& \mathbb{N}&\\
(\G,\HH)& \mapsto & \# \{\,(i,j) \in \B{V}^2 \,\given \, \G \text{ and } \HH \text{ do not have the same type}\\
&& \qquad \qquad \qquad \;\; \text{ of edge between } i \text{ and } j\}\,,
\end{array}$$ [eq_1]

```annotated-eq
latex: "\\mathrm{SHD}(\\G,\\HH) = \\#\\{(i,j) \\in \\B{V}^2 \\mid \\G, \\HH \\text{ disagree on the edge type at } (i,j)\\}"
terms:
  - tex: "\\mathbb{P} \\times \\mathbb{P} \\rightarrow \\mathbb{N}"
    role: 1
    words: "SHD is a symmetric count, not a probability or an effect size — the same two graphs in either order give the same number, unlike SID [§sec_1_1]"
  - tex: "(i,j) \\in \\B{V}^2"
    role: 2
    words: "Ordered pairs, not unordered ones — the two slots per variable-pair are what let a reversal cost twice as much as a missing edge [eq_1]"
  - tex: "\\text{same type of edge}"
    role: 3
    words: "Edge type is categorical: none, i→j, j→i, or i–j, taken from the PDAG edge-type definitions in the appendix [§sec_1_1]"
```

**The symmetric-difference reformulation.** The note restates the same count as a symmetric difference of edge sets rather than a per-pair type check — the same quantity, viewed as set arithmetic instead of enumeration [§sec_1_1]:

```derivation
shape: Show that counting mismatched ordered pairs is the same as counting the symmetric difference of the two edge sets.
steps:
  - latex: "\\mathrm{SHD}(\\G,\\HH) = \\#\\{(i,j) \\in \\B{V}^2 : \\G, \\HH \\text{ disagree at } (i,j)\\}"
    why: "Definition as given — a per-pair type comparison [eq_1]"
  - latex: "= \\#\\big(E(\\G) \\,\\Delta\\, E(\\HH)\\big)"
    why: "A pair (i,j) is a mismatch exactly when the directed-edge-slot it represents is in exactly one of the two edge sets, i.e. in their symmetric difference Δ [§sec_1_1]"
```

**Worked example — why reversal costs double a deletion.** Take truth $G: A\to B \to C$ and two candidate estimates. If $H_1$ reverses the first edge ($B \to A$, $B \to C$), the ordered-pair slots $(A,B)$ and $(B,A)$ *both* flip relative to $G$, giving $\mathrm{SHD}(G,H_1) = 2$. If $H_2$ instead just drops the edge ($B\to C$ only, no edge between $A,B$), only the $(A,B)$ slot flips — the $(B,A)$ slot stays $0$ in both graphs — giving $\mathrm{SHD}(G,H_2)=1$ [eq_1]. The two errors look intuitively different in severity, and the ordered-pair count is what produces that difference automatically rather than by special-casing edge reversal.

**Cost of computing it.** Because the count runs over $\mathcal{V}^2$, evaluating SHD is a single $O(p^2)$ pass comparing edge types — no search over adjustment sets, no intervention queries, just a table lookup per pair. That cheapness is precisely what SID gives up in exchange for causal relevance [eq_1].

## Go Deeper {#go-deeper}
- **Appendix edge-type definitions** — needed to pin down what "same type of edge" means for the four PDAG categories used in the count [§sec_1_1].
- **Structural Intervention Distance (SID)** — the paper's main proposal, introduced specifically to contrast with SHD's purely structural counting.
- **Companion comparison of counting-based distances** referenced in the note (e.g. metrics that count only missing edges) — cited as being "of similar type as SHD," useful if a reader wants the space of edit-distance alternatives rather than the causal alternative [§sec_1_1].

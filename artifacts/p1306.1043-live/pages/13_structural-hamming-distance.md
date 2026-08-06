# Structural Hamming Distance (SHD)
## TL;DR {#tldr}
SHD is an edit-distance: it counts edges on which an estimated causal graph and the truth disagree.

This paper uses it as SID's baseline. SID asks whether those graph errors change causal predictions.

## Intuition {#intuition}
Think of SHD as proofreading: line up the graphs and tally every missing, extra, or differently directed edge.

It treats each disagreement as a graph-editing problem, not a causal one.

This makes SHD a useful foil for SID. A small SHD can hide very different causal predictions, while a large SHD can preserve every relevant intervention effect.

SHD asks how different graphs look. SID asks how differently they behave causally.

## Mechanics {#mechanics}
**What it is defined over:** SHD is a function on pairs of PDAGs, which can mix directed and undirected edges [§sec_1_1].

PDAGs are a natural output when an algorithm estimates a Markov equivalence class rather than one DAG. A DAG is the special PDAG with no undirected edges [§sec_1_1].

**What counts as a disagreement:** SHD compares the edge type for each ordered pair $(i,j)$ [§sec_1_1].

The four types are no edge, $i\to j$, $j\to i$, and undirected $i-j$. Mismatched types count [§sec_1_1].

**Why ordered pairs matter:** an orientation uses two slots: an arrowhead at $i$ and one at $j$ [eq_1].

A reversal flips both slots, while an addition or deletion flips one. Counting $\mathcal{V}^2$ therefore penalizes reversal more heavily without a separate rule [eq_1].

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

**Worked example: reversal costs double a deletion.** Let $G: A\to B \to C$. If $H_1$ reverses the first edge, $(A,B)$ and $(B,A)$ both flip, so $\mathrm{SHD}(G,H_1)=2$ [eq_1].

If $H_2$ drops that edge, only $(A,B)$ flips and $(B,A)$ remains $0$, so $\mathrm{SHD}(G,H_2)=1$ [eq_1]. Ordered pairs produce the distinction without special-casing reversal.

**Cost of computing it.** Because the count runs over $\mathcal{V}^2$, evaluating SHD is a single $O(p^2)$ pass comparing edge types — no search over adjustment sets, no intervention queries, just a table lookup per pair. That cheapness is precisely what SID gives up in exchange for causal relevance [eq_1].

## Go Deeper {#go-deeper}
- **Appendix edge-type definitions** — needed to pin down what "same type of edge" means for the four PDAG categories used in the count [§sec_1_1].
- **Structural Intervention Distance (SID)** — the paper's main proposal, introduced specifically to contrast with SHD's purely structural counting.
- **Companion comparison of counting-based distances** referenced in the note (e.g. metrics that count only missing edges) — cited as being "of similar type as SHD," useful if a reader wants the space of edit-distance alternatives rather than the causal alternative [§sec_1_1].

# Structural Hamming Distance (SHD)

## TL;DR {#tldr}
SHD is a baseline metric for scoring how well an estimated causal graph matches the truth: it counts edge-level disagreements between two graphs and does nothing more. It's the natural point of comparison for this paper's proposed metric, the Structural Intervention Distance (SID), which instead scores graphs by whether they'd give the right answer to interventional questions rather than by whether their edges literally match.

## Intuition {#intuition}
Think of two graphs as two strings of edge labels over the same vertex pairs, and SHD as ordinary Hamming distance applied to that string: for every pair of nodes, check whether the two graphs agree on what kind of edge (if any) connects them, and tally the mismatches. It treats every disagreement as equally bad, wherever it falls in the graph. That's exactly what SID pushes back on — two graphs can differ by the same number of edges yet imply very different causal effects, or differ by many edges yet imply the same effects, which is the gap this paper's metric is built to close.

## Mechanics {#mechanics}
SHD is defined over the space of **partially directed acyclic graphs (PDAGs)**, so it covers CPDAGs and, since DAGs are a special case of PDAGs, ordinary DAG-to-DAG comparison as well — one definition serves both settings [§sec_1_1]. For a pair of graphs $(\mathcal{G}, \mathcal{H})$, it looks at every ordered pair of vertices $(i,j)$ and asks a single yes/no question: do $\mathcal{G}$ and $\mathcal{H}$ have the same type of edge between $i$ and $j$ (none, directed one way, directed the other way, or undirected)? SHD is the count of pairs where the answer is no [§sec_1_1].

An equivalent way to compute the same count is via the **symmetric difference of the two graphs' edge sets**: a pair $(i,j)$ contributes to SHD exactly when it belongs to one graph's edge-type set but not the other's, which is what "symmetric difference" means [§sec_1_1]. This reformulation is useful operationally — it turns the metric into a set-difference computation rather than a pairwise type comparison, which is how it is typically implemented [§sec_1_1].

In this paper, SHD's role is specifically to serve as the **reference baseline** against which the new structural intervention distance is contrasted, rather than as an object being newly defined [§sec_1_1].

## The Math {#the-math}
SHD is formalized as a function from pairs of PDAGs to the natural numbers, defined by the count of mismatched-type vertex pairs [eq_1].

$$
\begin{array}{rcll}
\mathrm{SHD}: \; \mathbb{P} \times \mathbb{P} &\rightarrow& \mathbb{N}&\\
(\G,\HH)& \mapsto & \# \{\,(i,j) \in \B{V}^2 \,\given \, \G \text{ and } \HH \text{ do not have the same type}\\
&& \qquad \qquad \qquad \;\; \text{ of edge between } i \text{ and } j\}\,,
\end{array}
$$ [eq_1]

```annotated-eq
latex: "\\mathrm{SHD}: \\; \\mathbb{P} \\times \\mathbb{P} \\rightarrow \\mathbb{N}, \\quad (\\G,\\HH) \\mapsto \\#\\{(i,j) \\in \\B{V}^2 \\mid \\G \\text{ and } \\HH \\text{ do not have the same type of edge between } i \\text{ and } j\\}"
terms:
  - tex: "\\mathbb{P} \\times \\mathbb{P} \\rightarrow \\mathbb{N}"
    role: 1
    words: "SHD is a function on pairs of PDAGs returning a natural number — a count, not a normalized score, so its scale grows with the number of vertex pairs [eq_1]"
  - tex: "(\\G,\\HH)"
    role: 2
    words: "The two graphs being compared; unlike SID, the definition is symmetric in its arguments since it only checks agreement [§sec_1_1]"
  - tex: "(i,j) \\in \\B{V}^2"
    role: 3
    words: "Every ordered vertex pair is inspected independently — the metric has no notion of which edges matter more [§sec_1_1]"
  - tex: "\\text{do not have the same type of edge}"
    role: 4
    words: "The comparison predicate: edge type (none/directed either way/undirected) must match exactly, as fixed in the appendix's edge-type definitions [§sec_1_1]"
```

The same count can be reached by a set-based route rather than a pointwise predicate, which is the form used when the metric is actually computed [§sec_1_1].

```derivation
shape: Rewrite the pointwise mismatch count as a symmetric-difference count.
steps:
  - latex: "\\mathrm{SHD}(\\G,\\HH) = \\#\\{(i,j) \\in \\B{V}^2 : \\text{edge}_\\G(i,j) \\neq \\text{edge}_\\HH(i,j)\\}"
    why: "Direct restatement of the defining predicate — a pair counts once if the two graphs disagree on its edge type [eq_1]"
  - latex: "= \\#\\big(E(\\G) \\,\\triangle\\, E(\\HH)\\big)"
    why: "A pair with mismatched edge type is, by definition, in exactly one of the two edge-type sets, so the mismatch count equals the size of their symmetric difference [§sec_1_1]"
```

Because SHD is defined over all of PDAG space rather than only DAGs, it applies unchanged whether $\mathcal{G}$ and $\mathcal{H}$ are two DAGs, two CPDAGs, or one of each — no separate DAG-specific version is needed [§sec_1_1].

## Go Deeper {#go-deeper}
- **Appendix (edge-type definitions)** — SHD's predicate depends on a fixed taxonomy of PDAG edge types (directed, undirected, absent); read it before trusting a specific SHD count across tools, since implementations can disagree on borderline cases [§sec_1_1].
- **Structural Intervention Distance (SID)** — the paper's main contribution and SHD's explicit foil: read it to see why counting matching edges is a poor proxy for whether a graph gives correct causal-effect estimates.
- **Comparison to other structural distances** — the paper notes that other counting-based metrics (e.g., counting only missing edges) exist and behave similarly to SHD; useful context for why SHD, not a variant, was chosen as the baseline here [§sec_1_1].

# Structural Hamming Distance (SHD)
## TL;DR {#tldr}
Structural Hamming Distance (SHD) is a way of scoring how different two causal graph estimates are by counting the edges that disagree between them. It exists as the standard, simple baseline against which more refined comparisons — such as the Structural Intervention Distance (SID) — are contrasted.

## Intuition {#intuition}
Think of SHD as an edit-counting metric: given two graphs over the same set of variables, tally up how many variable pairs are connected differently — an edge present in one graph but missing (or oriented differently) in the other. It treats every such mismatch as equally costly, which makes it easy to compute and interpret, but also means it does not distinguish between a mismatch that changes what the graph implies about interventions and one that doesn't. This is precisely the gap that motivates comparing SHD against SID, since the latter is designed to be sensitive to differences that actually matter for causal reasoning rather than pure graph-edit counting.

## Mechanics {#mechanics}
SHD is defined over partially directed acyclic graphs (PDAGs), of which ordinary DAGs are a special case, so the same definition covers comparisons between two DAGs, two PDAGs, or a DAG and a PDAG [§sec_1_1]. Concretely, the distance counts the number of variable pairs (i, j) for which the two graphs do not have the same type of edge between i and j, where edge types are the categories defined in the paper's appendix (e.g., no edge, directed edge in either orientation, undirected edge) [§sec_1_1]. Equivalently, this can be seen as counting pairs whose edge relationships fall in the symmetric difference between the two graphs' edge sets [§sec_1_1]. In this work, SHD is used mainly as a reference measure alongside the newly proposed structural intervention distance, and the paper notes that other similar structural distances (e.g., ones counting only missing edges) are of the same general type as SHD [§sec_1_1].

## The Math {#the-math}
SHD is formalized as a function mapping a pair of PDAGs to a natural number, counting mismatched-edge-type pairs of vertices [eq_1]:

$$\begin{array}{rcll}
\mathrm{SHD}: \; \mathbb{P} \times \mathbb{P} &\rightarrow& \mathbb{N}&\\
(\G,\HH)& \mapsto & \# \{\,(i,j) \in \B{V}^2 \,\given \, \G \text{ and } \HH \text{ do not have the same type}\\
&& \qquad \qquad \qquad \;\; \text{ of edge between } i \text{ and } j\}\,,
\end{array}$$ [eq_1]

## Go Deeper {#go-deeper}
The local context provides no research note or resource list for this concept, so there is nothing further to cite here beyond the paper section already used above.

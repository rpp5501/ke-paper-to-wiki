# Graphical Formulation of SID

## TL;DR {#tldr}
The direct definition of SID needs distributions, which are hard to compute. The paper gives an equivalent definition using only graph reachability and a blocking criterion — so SID can be computed from adjacency matrices alone.

## Intuition {#intuition}
The first definition asks a probabilistic question ("do these two recipes give the same distribution?"). The equivalent formulation shows that question has a purely structural answer you can read off the graph: does a certain set of nodes *block* all the wrong paths, and does it accidentally block a needed one? No integrals required.

That is what makes SID practical: everything reduces to checking paths between $i$ and $j$.

## Mechanics {#mechanics}
For the pair $(i,j)$, the estimate's parent set $\operatorname{pa}_{\mathcal{H}}(i)$ is a valid adjustment in $\mathcal{G}$ exactly when, in $\mathcal{G}$, no adjustment node is a descendant of $i$ on a directed path to $j$, and the set blocks every non-causal ("back-door") path from $i$ to $j$ [§sec_2_2].

If either condition fails — an adjustment node sits on a directed path, or a back-door path stays open — the pair is counted [§sec_2_2].

## The Math {#the-math}
The validity condition $(*)$ for counting a pair is, informally,

$$ (*)\quad \begin{cases} \text{no } Z \in \mathbf{Z} \text{ lies on a directed path } i \to j \text{ in } \mathcal{G}, \\ \mathbf{Z} \text{ blocks every back-door path from } i \text{ to } j \text{ in } \mathcal{G}, \end{cases} $$

with $\mathbf{Z} = \operatorname{pa}_{\mathcal{H}}(i)$. SID then counts the descendant/blocking violations:

$$ \operatorname{SID}(\mathcal{G},\mathcal{H}) = \#\Big\{ (i,j),\ i \neq j \ :\ (*) \text{ fails} \Big\}. $$

Because $(*)$ is graphical, each pair is decided by reachability in $\mathcal{G}$ [eq_6] [eq_7] [§sec_2_2].

## Go Deeper {#go-deeper}
- The SID Algorithm turns this criterion into path/reachability-matrix operations [§sec_12].
- Valid Adjustment Set is the sub-concept doing the real work here.

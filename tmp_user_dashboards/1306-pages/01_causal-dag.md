# Causal DAG

## TL;DR {#tldr}
A causal DAG is a directed graph with no cycles whose arrows say "this variable directly causes that one." It is the object every claim in this paper is *about*: two DAGs can look almost identical yet make very different causal predictions.

## Intuition {#intuition}
Think of a wiring diagram for a system. Each variable is a box; an arrow from $A$ to $B$ means turning the knob on $A$ can change $B$ directly, not through some third box. "Acyclic" means you can never follow arrows in a loop and arrive back where you started — causes come before their effects.

The reason the whole paper needs this object: a learning algorithm hands you an *estimated* DAG and claims it is close to the truth. To judge "close," you first have to agree that the graph is not just a picture but a set of promises about what would happen if you intervened.

## Mechanics {#mechanics}
A DAG $\mathcal{G}$ over variables $X_1,\dots,X_p$ has a vertex per variable and directed edges with no directed cycle. For a node $X_j$, its parents $\operatorname{pa}(j)$ are the nodes with an arrow directly into it. The paper works with DAGs and, later, with equivalence classes of DAGs [§sec_1].

The graph is not just topology: it is tied to a distribution through the Markov factorization, so structural differences translate into differences in predicted distributions [§sec_1_2].

## The Math {#the-math}
A distribution $p$ is Markov with respect to $\mathcal{G}$ when its density factorizes over parents:

$$ p(x_1,\dots,x_p) = \prod_{j=1}^{p} p\!\left(x_j \mid x_{\operatorname{pa}(j)}\right). $$

This factorization is what lets a purely graphical object make probabilistic predictions; every intervention formula later in the paper is a modification of this product [§sec_1_2].

## Go Deeper {#go-deeper}
- Appendix terminology section formalizes paths, colliders, and d-separation used throughout [§sec_7].
- The parent set $\operatorname{pa}(j)$ becomes the adjustment set the SID checks — see the Parent Adjustment concept.

# SID between a CPDAG and a DAG or CPDAG (level L2)

## TL;DR {#tldr}
This concept extends the Structural Intervention Distance to the case where the *true* graph is only known up to Markov equivalence, i.e. represented as a CPDAG rather than a single DAG. It builds directly on the pairwise notion of [[SID between a DAG and a CPDAG]], generalizing the comparison from "one true DAG vs. one estimated CPDAG" to "one true CPDAG vs. an estimated DAG or CPDAG." The goal is still to count how many pairwise interventional predictions disagree, but now both the identifiability of the intervention and the comparison itself must account for the whole equivalence class represented by the true CPDAG.

## Intuition {#intuition}
Sometimes the data-generating process itself makes the true DAG unrecoverable — for instance, a linear Gaussian SEM with equal error variances lets you identify only the Markov equivalence class, not the unique DAG, even in the infinite-data limit. In that setting it is unfair (and pointless) to score an estimate against "the" true DAG, since no method could recover it; the honest comparison is against the true equivalence class as a whole. The natural fix is to only judge intervention predictions that are actually determined by the equivalence class — for pairs where every DAG consistent with the true CPDAG agrees on the interventional distribution — and to extend the DAG-to-CPDAG machinery so it works symmetrically when the ground truth itself is a CPDAG.

## Mechanics {#mechanics}
The setup mirrors the earlier definitions of SID on DAG-vs-DAG and DAG-vs-CPDAG comparisons, but now both the true structure $\mathcal{C}$ and the estimate $\mathcal{H}$ can range over the space of CPDAGs $\mathbb{C}$; since a CPDAG $\mathcal{C}$ represents a whole equivalence class of DAGs, each of which can imply a different interventional distribution from $i$ to $j$, the central idea is to restrict attention to pairs $(i,j)$ whose intervention distribution is actually identifiable from $\mathcal{C}$ alone [§sec_2_4_2]. Identifiability in a CPDAG is characterized using a generalized backdoor criterion, and a path in a partially directed graph is called *possibly causal* if no edge on it points backward toward the source; the key graphical result is that the intervention distribution from $i$ to $j$ fails to be identifiable in a CPDAG exactly when there exists a possibly-causal path from $i$ to $j$ that begins with an undirected edge [§sec_2_4_2]. When the true structure collapses to a single DAG, every intervention becomes identifiable and this definition reduces exactly to the earlier DAG-based SID definitions, confirming consistency across the hierarchy of comparisons [§sec_2_4_2]. For the general CPDAG-to-CPDAG case, the extension follows the same logic used for DAG-to-CPDAG: the score is computed as lower and upper bounds taken over all DAGs consistent with the estimated Markov equivalence class, now paired against the identifiability-restricted set of pairs from the true CPDAG [§sec_2_4_2].

## The Math {#the-math}
The resulting quantity is a map from a true CPDAG $\mathcal{C}$ and an estimated graph $\mathcal{H}$ (DAG or CPDAG) to a natural number, counting ordered pairs $(i,j)$ such that the intervention distribution from $i$ to $j$ is identifiable in $\mathcal{C}$ and there exists some DAG $\mathcal{C}_1$ in the equivalence class $\mathcal{C}$, Markov with respect to it, whose post-intervention conditional disagrees with the one implied by $\mathcal{H}$ [eq_10]:

$$
\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{C} \times \mathbb{G} &\rightarrow& \mathbb{N}\\
(\CC,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{the interv. distr from $i$ to $j$ is identif. in $\CC$}\\
&& \qquad \qquad \qquad \quad \text{and } \exists \lawX \text{ that is Markov wrt } \CC_1 \in \CC \text{ such that}\\
&& \qquad \qquad \qquad \quad p_{\CC_1}(x_j\given \doo(X_i = \hat x_i)) \neq p_{\HH}(x_j\given \doo(X_i = \hat x_i)) \}
\end{array}
$$ [eq_10]

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no additional resources to list here.

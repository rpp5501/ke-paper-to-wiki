# Motivation and Definition of SID
## TL;DR {#tldr}
The Structural Intervention Distance (SID) is a graph (pre-)metric for comparing a true DAG to an estimated DAG when the end goal is causal prediction rather than mere structural similarity. Instead of counting edge differences like the Structural Hamming Distance (SHD), SID counts how many pairwise intervention distributions — "what happens to variable j if I intervene on variable i" — are wrongly predicted by the estimated graph relative to the truth, across all observational distributions compatible with the true DAG.

## Intuition {#intuition}
Two estimated graphs can have the exact same SHD to the true graph yet be very different in how trustworthy their causal predictions are: adding a spurious edge that doesn't change any node's parent set is often harmless for intervention predictions, while reversing a single edge can silently break a whole cascade of interventional queries by adjusting for the wrong variables (e.g., failing to adjust for a real confounder, or adjusting for a variable that shouldn't be conditioned on). SHD treats both mistakes as costing "one edge," but they are not equally bad if your purpose is predicting interventions. SID is built to distinguish exactly this: it asks, for every ordered pair of variables, whether the estimated graph's parent-adjustment recipe would give the correct answer for every distribution that could plausibly have generated the data — and counts the pairs where it wouldn't.

## Mechanics {#mechanics}
The motivating example compares a true DAG to two candidate graphs that both have SHD = 1 from the truth: one candidate has an extra edge between two nodes that are both children of the same parent, and the other has a single reversed edge. Working through parent adjustment on the first candidate shows that, because every node's parent set is either unchanged or only gains a variable that is itself independent of the outcome given the existing adjustment set, all pairwise intervention distributions computed from the estimate still agree with the true ones [§sec_2_1]. The second candidate is worse in kind, not just degree: reversing an edge removes a node's true parent (a confounder), so the parent-adjustment formula on the estimate fails to condition on it, and this single reversal is shown to propagate into eight erroneous intervention predictions for generic observational distributions [§sec_2_1].

Because whether a given intervention prediction is "correct" or "wrong" depends on the actual observational distribution, and a fully independent distribution would trivially make any two graphs agree on all interventions, the definition instead quantifies over the whole family of distributions that are Markov with respect to the true DAG, so that the resulting count is a purely graphical property with no dependence on a specific distribution [§sec_2_1]. This is formalized by declaring the intervention distribution from i to j "correctly estimated" only if the estimate's parent-adjustment formula matches the truth's for every such Markov-compatible distribution, and "falsely estimated" otherwise [§sec_2_1].

## The Math {#the-math}
The worked example verifies correctness for one specific pair by manipulating the adjustment formula under the estimated graph and showing it collapses back to the true interventional query via the rules of probability and adjustment validity [eq_4].

$$
p_{\HH_1}(y_3\given \doo(Y_2 = \hat y_2)) &= \sum_{x_1,x_2,y_1} p(y_3\given x_1,x_2,y_1,\hat y_2) p(x_1,x_2,y_1)\\
& = \sum_{x_1,x_2,y_1} \frac{p(x_1,x_2,y_1,\hat y_2,y_3)}{p(\hat y_2 \given x_1,x_2,y_1)}
 = \sum_{x_1,x_2,y_1} \frac{p(x_1,x_2,y_1,\hat y_2,y_3)}{p(\hat y_2 \given x_1,x_2)}\\
& = \sum_{x_1,x_2} p(y_3\given x_1,x_2,\hat y_2) p(x_1,x_2)
 = p_{\G}(y_3\given \doo(Y_2 = \hat y_2))
$$ [eq_4]

The formal definition packages this pairwise correctness check into a single count: SID maps a pair of DAGs to the number of ordered node pairs whose intervention distribution is falsely estimated by the second graph relative to the first [eq_5].

$$
\label{eq:SIDdagdag}
\begin{array}{rcl}
\mathrm{SID}: \; \mathbb{G} \times \mathbb{G} &\rightarrow& \mathbb{N}\\



(\G,\HH)& \mapsto &\# \{\,(i,j), i \neq j\;|\;\text{ the intervention distribution from } i \text{ to } j\\
&& \qquad \qquad \qquad \quad \text{ is falsely estimated by } \HH \text{ with respect to } \G \}
\end{array}
$$ [eq_5]

Note that this definition is not symmetric in $(\G,\HH)$, so SID is a pre-metric rather than a full metric [§sec_2_1].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** (part-of) — the parent concept; this page covers only the motivating example and the formal definition that anchors the rest of the SID framework.
- **Equivalent Graphical Formulation** (builds-on) — shows how to compute SID directly from graph structure (e.g. via Proposition) without enumerating distributions, turning this definition into something practically calculable.
- **Alternative Adjustment Sets** (builds-on) — revisits the choice of parent adjustment used throughout this definition and discusses what changes if a different valid adjustment set is used instead.

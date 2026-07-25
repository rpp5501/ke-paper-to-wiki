# Structural Intervention Distance (SID)

## TL;DR {#tldr}
SID scores how wrong an estimated causal graph is by counting the ordered variable pairs for which the estimate would send you to the wrong adjustment set — and therefore predict the wrong interventional effect. It is the paper's central contribution.

## Intuition {#intuition}
Imagine grading a student's causal map not by how many edges they drew wrong, but by how many *cause-effect questions* their map would answer incorrectly. A single misplaced edge can corrupt many such questions, or none at all. SID grades on the questions, which is what an experimenter actually cares about.

Concretely: for every ordered pair $(i,j)$, ask "if I use the estimate's recipe to predict the effect of intervening on $i$ upon $j$, does the *true* graph say that recipe is valid?" Count the pairs where the answer is no.

## Mechanics {#mechanics}
Given a true DAG $\mathcal{G}$ and an estimate $\mathcal{H}$, SID looks at each ordered pair $(i,j)$ with $i \neq j$. It forms the estimate's parent-adjustment set for the effect of $i$ on $j$ using $\mathcal{H}$, then checks whether that set is a *valid* adjustment set in $\mathcal{G}$ [§sec_2_1].

Pairs whose estimated adjustment is invalid in the truth are counted as mistakes; pairs that happen to stay valid are not penalized even if edges differ. This is why SID and edge-counting can disagree sharply [§sec_2_1].

## The Math {#the-math}
SID is a map on ordered pairs of graphs,

$$ \operatorname{SID} : \mathbb{G} \times \mathbb{G} \to \{0, 1, \dots, p(p-1)\}, $$

defined by counting the offending pairs

$$ \operatorname{SID}(\mathcal{G}, \mathcal{H}) = \#\Big\{ (i,j),\ i \neq j \ :\ \text{the } \mathcal{H}\text{-parent adjustment for } i\to j \text{ is invalid in } \mathcal{G} \Big\}. $$

The maximum $p(p-1)$ is the number of ordered pairs, so SID is naturally comparable across problems of the same size [eq_5] [§sec_2_1].

## Go Deeper {#go-deeper}
- Graphical Formulation of SID replaces the distribution check with a pure adjustment-criterion check [§sec_2_2].
- Metric Properties of SID explains why it is only a pre-metric (asymmetric) [§sec_2_3].
- SHD is the edge-counting baseline SID is designed to improve on.

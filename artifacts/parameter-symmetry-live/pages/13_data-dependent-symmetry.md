# Data-Dependent Symmetry

## TL;DR {#tldr}
- Functional symmetry must preserve a network's output on *every* possible input. Data-dependent symmetry only has to preserve it on a fixed batch of $n$ data points, which strictly enlarges the group of behavior-preserving transformations [§sec_2_3_2].
- Model-merging methods that align two networks by matching activations on a training or validation set are implicitly searching this data-dependent group, not the exact functional one [S3].

## Intuition {#intuition}
Functional symmetry is a promise that holds for every input the network will ever see. Data-dependent symmetry is a weaker promise — it only has to hold for the inputs you actually checked.

That weaker promise is still useful. Two networks that were trained separately can look "the same" once you only ask them to agree on a shared batch of data, even though nothing forces them to agree everywhere else.

## Mechanics {#mechanics}

**Defining the group action.** A data-dependent group action of $G$ on parameters $\Par$ also takes a data batch $X \in \Data^n$ as an argument, but it acts trivially on $X$ itself — only $\theta$ moves [§sec_2_3_2].

**Group-action laws.** Writing the action as $g \cdot (\theta, X)$, it must satisfy $e \cdot (\theta, X) = \theta$ and $g \cdot (g' \cdot (\theta, X), X) = (gg') \cdot (\theta, X)$ for all $g, g' \in G$ — the usual identity and composition laws of a group action, carried along a fixed $X$ [§sec_2_3_2].

**What the symmetry preserves.** A data-dependent symmetry of $F$ is such an action that keeps $F$'s value fixed on the data batch $X$ used to define it, stated formally as an invariance condition [eq_5] — not on inputs outside that batch [§sec_2_3_2].

**Where this sits among symmetry groups.** Godfrey et al. formalize the resulting gap between three groups of parameter transformations, ordered by how much they're allowed to disturb the network:

| Symmetry type | Must preserve output on | Relative group size | Stable under resampling? |
|---|---|---|---|
| Functional | every input | smallest | not dataset-dependent [§sec_2_3_2] |
| Data-dependent | one fixed batch $X$ of size $n$ | strictly larger than functional | no — dataset-specific [S1][S3] |
| Arbitrary reparameterization | nothing required | largest | not applicable [S2] |

The data-dependent group sits strictly between the other two, not equal to either [S2].

**Concrete case: ReLU sign flips.** A ReLU unit's incoming and outgoing weight signs can be flipped only for units whose activation pattern happens to be constant across the dataset — a transformation that breaks functional equivalence on inputs outside that dataset [S1].

**Practical use: model merging.** Permutation-based model merging and linear-mode-connectivity methods align two independently trained networks by matching neuron activations on a fixed training or validation set, effectively searching a data-dependent symmetry rather than the exact functional one [S3].

**Instability under resampling.** Because the group is defined by finite-sample behavior, it is generally unstable under resampling: a transformation valid on one dataset or subset can fail on another, so equivalences found via activation matching are approximate and dataset-specific rather than exact invariances of the trained function [S1][S3].

## The Math {#the-math}

The defining condition of a data-dependent symmetry is an equality of $F$ at each data point in the batch, not everywhere:

$$
F(g \cdot (, X), x) = F(, x), \quad \forall g \in G,~ \forall  \in \Par,~ \forall X \in (\Data_{\text{input}})^n,~ \text{and }~ \forall x \in X.
$$
[eq_5]

```annotated-eq
latex: "F(g \cdot (, X), x) = F(, x), \quad \forall g \in G,~ \forall  \in \Par,~ \forall X \in (\Data_{\text{input}})^n,~ \text{and }~ \forall x \in X."
terms:
  - tex: "g \cdot (, X)"
    role: 1
    words: "The transformed parameters produced by acting with g on batch X — the blank marks where the parameter argument sits in this rendering of the equation [eq_5]"
  - tex: "F(, x)"
    role: 2
    words: "The network's output at a single point x under the original, untransformed parameters [eq_5]"
  - tex: "\forall x \in X"
    role: 3
    words: "Equality is only required pointwise across the finite batch X, not for inputs outside it — this restriction is exactly what makes the symmetry data-dependent rather than functional [eq_5]"
```

**Worked example: two-layer network setup.** Consider $f(W_2, W_1, X) = W_2 \sigma(W_1 X)$ with $(W_2, W_1) \in \R^{m\times h}\times \R^{h\times n}$; if $\sigma$ never outputs the zero vector, this architecture carries a data-dependent $\text{GL}_h(\R)$ symmetry [§sec_2_3_2].

**Worked example: the transformation.** The group acts by $g \cdot (W_2, W_1, x) = (W_2 R_{\sigma(W_1x)} R_{\sigma(gW_1x)}^{-1},\, gW_1)$, where $R_z$ is the matrix built from $z$ defined in the section. The correction factor $R_{\sigma(W_1x)}R_{\sigma(gW_1x)}^{-1}$ is constructed exactly to undo the change $g$ makes to the hidden activation, but only at the single point $x$ it is built from [§sec_2_3_2].

**Boundary case: why it is not functional.** Because $R_{\sigma(W_1x)}$ is rebuilt from $x$ itself, the transformation is data-dependent: reusing the same $g$ and $W_1$ but swapping in a different point $x'$ changes $R_{\sigma(W_1x')}$, so the correction no longer cancels and output equality breaks [§sec_2_3_2].

## Go Deeper {#go-deeper}

- [On the Symmetries of Deep Learning Models and their Internal Representations](https://arxiv.org/abs/2205.14258) — directly names and formalizes data-dependent symmetry as a group nested between parameter-space and functional symmetry; read this first for the formal picture behind this page.
- [Geometry of the Loss Landscape in Overparameterized Neural Networks: Symmetries and Invariances](https://arxiv.org/abs/2105.12221) — a formal treatment separating exact functional symmetry from symmetries that only hold conditional on a dataset.
- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — a concrete, practical use of data-dependent symmetry to align and merge independently trained networks.
- [samuela/git-re-basin](https://github.com/samuela/git-re-basin) — visualizes the effect of applying a data-derived permutation symmetry on the loss landscape between two models.

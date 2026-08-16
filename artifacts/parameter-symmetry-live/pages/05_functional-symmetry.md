# Functional Neural Network Symmetry

## TL;DR {#tldr}

Functional symmetry is the strictest form of parameter-space symmetry: a group of parameter transformations that leaves the network's input-output function exactly unchanged for every possible input, not just on average or on some subset of data. Permutation of hidden units is the universal instance; sign-flips and rescalings are extra symmetries specific to certain activation functions [§sec_2_2].

## Intuition {#intuition}

Think of a hidden layer as a set of interchangeable units, not an ordered list. Swap two neurons' incoming and outgoing weights together, and the layer computes the same sum over the same set of features — the ordering was never part of the computation [S1].

This reordering is a permutation symmetry: it changes the parameter vector but leaves the function the network computes untouched, so a hidden layer with $M$ units carries at least $M!$ such relabelings [S1].

Some activations allow more than relabeling. A tanh unit is odd, meaning $\tanh(-z) = -\tanh(z)$, so flipping the sign of everything feeding into a unit and everything it feeds out to cancels perfectly and reproduces the original function [S1].

Each hidden unit can be sign-flipped independently of the others, which multiplies the permutation count by $2^M$ and gives the full symmetry group order $M! \cdot 2^M$ for a single tanh hidden layer [S1].

## Mechanics {#mechanics}

**Functional symmetry is defined as a group action** on the parameter space $\Par$ that leaves the network's function $f\colon \Par \times \Data_{\text{input}} \to \Data_{\text{target}}$ invariant for every input in $\Data_{\text{input}}$, not just a subset or a particular data distribution [§sec_2_2].

This makes it the strictest of the parameter-space symmetry definitions, and the group $G$ that realizes this invariance is called a symmetry group of $f$ [§sec_2_2].

Permutation is the base case that appears in every over-parameterized architecture. An MLP's hidden units, a CNN's channels, and a ResNet's blocks can each be permuted consistently across layers without changing the function computed [S2].

This generalization is what makes it possible to align and merge two independently trained networks, by finding the permutation that lines up their hidden representations before averaging weights [S2].

Which extra symmetries exist beyond permutation depends on the activation function, not on the architecture:

| Activation | Extra symmetry beyond permutation | Group structure |
|---|---|---|
| tanh (odd, sign-symmetric) | sign-flip per hidden unit | finite, order $M!\cdot 2^M$ [S1] |
| ReLU (positively homogeneous) | positive rescale of fan-in, inverse rescale of fan-out | continuous, one scale factor per unit [S3] |
| Generic activation | none beyond permutation, unless odd or homogeneous | architecture- and activation-specific [S3] |

## The Math {#the-math}

The formal definition is the invariance equation itself:

$$f(g \cdot \theta, x) = f(\theta, x), \quad \forall g \in G, \quad \forall \theta \in \Par, \quad \forall x \in \Data_{\text{input}}.$$
[eq_1]

```annotated-eq
latex: "f(g \\cdot \\theta, x) = f(\\theta, x), \\quad \\forall g \\in G, \\quad \\forall \\theta \\in \\Par, \\quad \\forall x \\in \\Data_{\\text{input}}"
terms:
  - tex: "g \\cdot \\theta"
    role: 1
    words: "The group action applied to a parameter setting — a possibly nonlinear transformation, such as permuting or sign-flipping weights [§sec_2_2]"
  - tex: "f(\\cdot, x)"
    role: 2
    words: "The network's feedforward function evaluated at a fixed input; the object required to be unchanged [§sec_2_2]"
  - tex: "\\forall x \\in \\Data_{\\text{input}}"
    role: 3
    words: "The universal quantifier over every input, not a subset or a distribution, which is what makes this the strictest symmetry definition [§sec_2_2]"
```

The quantifiers in [eq_1] give a concrete way to count a symmetry group. For a single tanh hidden layer with $M$ units, every one of the $M!$ orderings of the units combined with every one of the $2^M$ independent sign choices satisfies the equation, and no other transformation does, so $|G| = M! \cdot 2^M$ exactly [S1].

Swap in ReLU and the sign-flip term vanishes, because $\mathrm{ReLU}(-z) \neq -\mathrm{ReLU}(z)$: flipping a sign changes the function, so it cannot be a member of $G$. What survives instead is positive homogeneity, $\mathrm{ReLU}(cz) = c\cdot\mathrm{ReLU}(z)$ for $c > 0$, which lets a unit's fan-in weights be scaled by $c$ and its fan-out weights by $1/c$ with [eq_1] still holding — a continuous one-parameter family per unit in place of a finite sign choice [S3].

## Go Deeper {#go-deeper}

- [Pattern Recognition and Machine Learning (Bishop, 2006)](https://www.microsoft.com/en-us/research/uploads/prod/2006/01/Bishop-Pattern-Recognition-and-Machine-Learning-2006.pdf) — derives the exact $M!\cdot 2^M$ permutation-and-sign-flip group for a single-hidden-layer tanh MLP; start here for the canonical worked example.
- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — extends permutation symmetry from toy MLPs to deep, convolutional, and residual networks, showing which symmetries persist across architectures.
- [git-re-basin (reference implementation)](https://github.com/samuela/git-re-basin) — runnable code that explicitly constructs permutation matrices realizing functional symmetry and visualizes function-preserving weight permutations.
- [Sharp Minima Can Generalize For Deep Nets](https://arxiv.org/abs/1703.04933) — introduces the continuous positive-rescaling symmetry specific to positively homogeneous activations like ReLU, contrasting it with permutation and sign-flip symmetry.

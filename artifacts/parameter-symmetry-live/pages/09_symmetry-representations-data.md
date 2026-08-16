# Symmetry in Parameters, Internal Representations, and Data
## TL;DR {#tldr}
Parameter-space symmetry, symmetry in a network's internal representations, and symmetry in the data distribution are three faces of the same phenomenon: an activation function's equivariance group (the intertwiner group) transports symmetry from parameters into representations, while symmetry present in training data is inherited by learned parameters and preserved throughout gradient descent.

## Intuition {#intuition}
If you rotate a photograph before feeding it to a convolutional network, the hidden feature maps rotate along with it — the network doesn't need to relearn rotated features from scratch, because the same weight pattern already produces a rotated answer.

That transport only pays off because natural images really are approximately symmetric under translation and rotation; building the symmetry into the weights is a bet on a property the data actually has, not a free lunch.

The same logic runs in reverse during training: if the data is symmetric, gradient descent has no mechanism to break that symmetry in the weights, so a network initialized symmetrically stays symmetric at every step.

## Mechanics {#mechanics}
Many parameter-space symmetries trace back to the equivariance of the network's activation function: $\sigma$ is equivariant to a group $G$ when $\sigma \circ g = g \circ \sigma$ for every $g \in G$, and the set of transformations satisfying this condition is called the intertwiner group [§sec_6_1].

```annotated-eq
latex: "\\sigma \\circ g = g \\circ \\sigma"
terms:
  - tex: "\\sigma"
    role: 1
    words: "The activation function whose equivariance generates the symmetry — the property being tested, not assumed [§sec_6_1]"
  - tex: "g"
    role: 2
    words: "A candidate group element; it belongs to the intertwiner group only if it satisfies this commuting condition [§sec_6_1]"
  - tex: "\\circ"
    role: 3
    words: "Function composition on either side of $\\sigma$ — applying $g$ before or after the nonlinearity must give the same map [§sec_6_1]"
```

Because the intertwiner group acts identically on parameters and on internal representations, it can be used to stitch two functionally equivalent networks together: writing the two networks as $f_1 \circ \sigma \circ f_2$ and $\tilde f_1 \circ \sigma \circ \tilde f_2$, an element $g \in G$ realigns the first into $\tilde f_1 \circ g \circ \sigma \circ f_2$ without changing the output [§sec_6_1].

This shared symmetry also reframes how hidden activations should be compared: internal representations are equivalent only up to intertwiner-group transformations, which motivates similarity metrics invariant to that group and justifies reading ReLU networks neuron-by-neuron rather than through arbitrary linear combinations that can hide this structure [§sec_6_1].

Symmetry can also flow the other direction, from data into parameters: if a dataset $X$ is invariant under $G$ (so $g \cdot X = X$), the loss $L(\theta, g\cdot X) = L(\theta; X)$ is unchanged, which makes the gradient equivariant and lets a symmetric initialization stay symmetric throughout gradient descent [§sec_6_1].

Symmetry can also be defined jointly across data and parameter space rather than on either alone; using such a joint group action, together with Schur's lemma, one can show the ridgelet transform is a right inverse of a neural network's integral representation, giving a symmetry-based constructive proof of the universal approximation theorem [§sec_6_1].

Weight-tying a layer to be invariant under a group action makes the resulting map provably equivariant, so the group acts on the layer's feature maps exactly as it acts on the input — parameter-space symmetry is transported directly into representation-space symmetry [S1][S2].

This transport is only useful when the data itself carries the symmetry being built in: convolutional weight-sharing pays off because natural images are approximately translation-symmetric, and G-convolutions generalize the same idea to whatever symmetry group structures the input domain [S2][S3].

Representation-learning work makes this link definitional: a representation counts as disentangled with respect to a task exactly when it decomposes into subspaces on which the data's generative symmetry group acts independently [S4].

The resulting design principle — identify the data domain's symmetry group first, then constrain the architecture to be equivariant or invariant to it — is formalized as the geometric deep learning blueprint, and operationalized concretely by libraries such as e3nn, which fix hidden-layer representations to match the O(3) symmetry of 3D input [S3][S5].

## The Math {#the-math}
The intertwiner group of $\sigma$ is the set $\{g \in G : \sigma \circ g = g \circ \sigma\}$, defined purely by requiring $\sigma$ to commute with the group action [§sec_6_1].

Commuting means the same $g$ can be applied either before or after $\sigma$ without changing the result, which is exactly the property stitching exploits to move a correction $g$ across the nonlinearity untouched [§sec_6_1].

Consider the one-layer linear network $f(W, b, X) = WX + b$ with joint group action $g \cdot (W, X) = (Wg^{-1}, gX)$ applied to parameters and data together [§sec_6_1].

$$f(Wg^{-1}, b, gX) = Wg^{-1}gX + b = WX + b = f(W,b,X)$$
[§sec_6_1]

The $g^{-1}$ on the weight and the $g$ on the data cancel inside the product, so the joint transformation leaves the network's output exactly unchanged — this is the joint-space symmetry the ridgelet-transform argument for universal approximation builds on [§sec_6_1].

```derivation
shape: Show that a G-invariant dataset keeps a G-symmetric initialization G-symmetric at every step of gradient descent.
steps:
  - latex: "L(\\theta, g\\cdot X) = L(\\theta; X)"
    why: "The dataset is G-invariant ($g\\cdot X = X$), so the loss cannot distinguish $X$ from its transformed copy [§sec_6_1]"
  - latex: "\\nabla_W L(g\\cdot W; X) = g \\cdot \\nabla_W L(W; X)"
    why: "Differentiating the invariant loss makes the gradient itself equivariant to $G$ [§sec_6_1]"
  - latex: "g W_0 = W_0 \\implies g W_t = W_t \\ \\text{for all } t"
    why: "An equivariant gradient can only move a symmetric $W_t$ to another symmetric point, so the symmetry present at initialization is never broken by gradient descent [§sec_6_1]"
```

## Go Deeper {#go-deeper}
- [Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges](https://geometricdeeplearning.com/) — the clearest single picture of the blueprint this whole page follows: pick the data's symmetry group first, then build the representation to match it.
- [Equivariance Through Parameter-Sharing](https://arxiv.org/abs/1702.08389) (Ravanbakhsh, Schneider, Poczos, 2017) — the explicit theorem behind the Mechanics claim that weight-tying a layer's parameters provably forces its representation to be equivariant.
- [Group Equivariant Convolutional Networks](https://arxiv.org/abs/1602.07576) (Cohen & Welling, 2016) — the canonical worked construction of a G-convolution, showing concretely how a symmetry group gets encoded into a layer.
- [e3nn: Euclidean neural networks](https://docs.e3nn.org/en/latest/) — a working library where a data domain's O(3) symmetry directly fixes the hidden-layer representations, making the parameter–representation–data link concrete in code.

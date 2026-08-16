# Role of Symmetry in Loss Landscapes

## TL;DR {#tldr}
Every minimum of a neural network's loss function sits inside a family of equivalent minima produced by parameter symmetries. These symmetries turn single points into connected manifolds or into scattered but equal-quality clusters, which explains much of the loss landscape's apparent size and complexity [§sec_3].

## Intuition {#intuition}

Picture a hidden layer as interchangeable workers. Swap two workers and swap their wiring to match — the network computes the same function as before. That is a discrete symmetry: it creates a separate, equally good copy of the minimum elsewhere in parameter space [S1].

Now picture stretching one worker's incoming weights while shrinking their outgoing weights by the same factor. A ReLU layer passes scale straight through, so the output stays fixed across a whole continuous range of stretch factors. That is a continuous symmetry, and it sweeps out a connected surface of equally good minima rather than an isolated twin [S1].

Both kinds of symmetry mean that "how many minima does this network have" is the wrong question. The right question is how many orbits — equivalence classes under these symmetries — exist, since every point in an orbit computes the identical function [§sec_3].

## Mechanics {#mechanics}

Take the two-layer linear network $f_{linear}(W_2, W_1) = W_2 W_1 X$ over fixed input $X$. If $(W_2^*, W_1^*)$ is a global minimum, then so is $(W_2^* g^{-1}, g W_1^*)$ for any invertible $g \in \mathrm{GL}_h(\mathbb{R})$, because the $g^{-1}$ and $g$ cancel inside the product [§sec_3].

This is not a fluke of this toy model: $\mathrm{GL}_h(\mathbb{R})$ is a continuous group, so its orbit through $(W_2^*, W_1^*)$ is a positive-dimensional manifold, not a finite set of points. Every point on that manifold has exactly the same loss [§sec_3].

```figure
id: fig_5
caption: The zero-loss set around a minimum is not a point — every $g\cdot\theta$ in the symmetry group's orbit sits on it too [§sec_3]
```

Simsek et al. show the two symmetry types shape this landscape differently. Continuous rescaling symmetries — like the $\mathrm{GL}_h$ action above — sweep out connected, positive-dimensional manifolds of equal loss [S1].

Discrete permutation symmetries — reordering hidden units — instead produce combinatorially many separated basins that are all equally good but not path-connected to each other. The two symmetry types even act differently on the local curvature around a minimum [S1].

Freeman & Bruna study how the permutation and rescaling group actions on ReLU network weights structure the connectivity of sublevel sets — the region of parameter space where loss stays below some threshold [S2].

Their analysis explains why many apparently distinct minima found by different training runs are secretly the same point up to a symmetry transformation, rather than genuinely different solutions [S2].

Li et al.'s filter-normalized visualizations turn this abstract picture into something visible: 2D and 3D renderings of real networks' loss surfaces show concrete basins and barriers, making the effect of symmetry-related minima tangible rather than purely algebraic [S3].

Git Re-Basin demonstrates the practical payoff of understanding this structure: explicitly matching and re-aligning hidden units between two independently trained networks — quotienting out the permutation symmetry — collapses what looked like a disconnected landscape into a single connected basin [S4].

## The Math {#the-math}

The symmetry group acting on this network's minima is $\mathrm{GL}_h(\mathbb{R})$, the invertible $h\times h$ matrices, where $h$ is the hidden width. It acts on a global minimum $(W_2^*, W_1^*)$ by:

$$(W_2^*, W_1^*) \mapsto (W_2^* g^{-1},\ g W_1^*), \quad g \in \mathrm{GL}_h(\mathbb{R})$$
[§sec_3]

```derivation
shape: Show the reparameterized weights compute the identical function.
steps:
  - latex: "f_{linear}(W_2^* g^{-1}, g W_1^*) = (W_2^* g^{-1})(g W_1^*) X"
    why: "Substitute the symmetry action directly into the network's definition [§sec_3]"
  - latex: "= W_2^* (g^{-1} g) W_1^* X"
    why: "Matrix multiplication is associative, so the $g^{-1}$ and $g$ sit next to each other [§sec_3]"
  - latex: "= W_2^* W_1^* X = f_{linear}(W_2^*, W_1^*)"
    why: "$g^{-1}g$ is the identity matrix for any invertible $g$, so the output — and therefore the loss — is unchanged [§sec_3]"
```

Take $h = 1$, so $g$ is just a nonzero scalar $c$. If $W_1^* = [2]$ and $W_2^* = [3]$ multiply to weight $6$, then $g = 2$ gives $W_1 = [4]$, $W_2 = [1.5]$, and $1.5 \times 4 = 6$ again — same product, same loss, different weights [§sec_3].

Contrast this with a permutation: swapping the roles of two hidden units also preserves the loss, but the set of valid permutations is finite (there are $h!$ of them for $h$ units), so it produces isolated equal-loss points rather than a continuous manifold [§sec_3].

## Go Deeper {#go-deeper}

- [Visualizing the Loss Landscape of Neural Nets (project page)](https://www.cs.umd.edu/~tomg/projects/landscapes/) — Interactive filter-normalized 2D/3D renderings let you see the bumpy loss surface and its basins directly; start here to build visual intuition before the algebra.
- [Geometry of the Loss Landscape in Overparameterized Neural Networks: Symmetries and Invariances](https://arxiv.org/abs/2105.12221) — Works out in detail how continuous (scaling) and discrete (permutation) symmetry groups shape the geometry of minima differently.
- [Topology and Geometry of Half-Rectified Network Optimization](https://arxiv.org/abs/1611.01540) — Shows how the permutation and rescaling group actions on ReLU weights structure the connectivity of loss sublevel sets.
- [Git Re-Basin: Merging Models modulo Permutation Symmetries](https://arxiv.org/abs/2209.04836) — Demonstrates concretely that quotienting out permutation symmetry collapses a seemingly disconnected landscape into one connected basin.

# Related Work: Residual Representations & Shortcuts
## TL;DR {#tldr}

Two independent traditions anticipated residual learning before this paper: shallow vision representations that encode residual vectors instead of raw values, and a decades-long line of shortcut-connection tricks for training deep networks [§sec_2].

The closest contemporary is Highway Networks, whose gated shortcuts carry parameters and can close; ResNet's identity shortcuts are parameter-free and never close [§sec_2].

## Intuition {#intuition}

A residual is easier to represent well than the full quantity it comes from. VLAD encodes images as residual vectors against a dictionary rather than the raw descriptors, and vector quantization is known to work better on residuals than on originals [§sec_2].

Multigrid solvers apply the same idea to PDEs: each scale solves only the residual between a coarse and a fine approximation, and this converges far faster than solving the full system at one scale [§sec_2].

Shortcut connections pursue a different goal — not a better representation, but an easier path for gradients and signal to reach early layers of a deep network [§sec_2].

## Mechanics {#mechanics}

**Residual encoding in shallow vision models.** VLAD and Fisher Vector, a probabilistic generalization of VLAD, are both built on residual vectors relative to a dictionary rather than on the original descriptors, and both are strong representations for image retrieval and classification [§sec_2].

**Residual reformulation in numerical solvers.** The Multigrid method splits a PDE system into subproblems at multiple scales, where each subproblem solves the residual between a coarser and a finer solution; hierarchical basis preconditioning uses the same residual-between-scales idea instead of the multiscale subproblem structure [§sec_2].

Both solvers converge much faster than standard methods unaware of the residual structure, which suggests that reformulating a problem around its residual — rather than changing the optimizer — can make optimization itself easier [§sec_2].

**Early shortcut connections for optimization.** Before Highway Networks, shortcut connections already served several distinct optimization purposes [§sec_2]:

- Training multi-layer perceptrons with a linear layer connected directly from the network input to the output [§sec_2]
- Connecting a few intermediate layers directly to auxiliary classifiers to address vanishing and exploding gradients [§sec_2]
- Centering layer responses, gradients, and propagated errors, implemented via shortcut connections [§sec_2]
- Composing an inception layer from a shortcut branch alongside a few deeper branches [§sec_2]

**Highway Networks: the closest contemporary.** Highway Networks, developed concurrently with this paper, also use shortcut connections, but gate them with a learned, data-dependent function rather than leaving them fixed [§sec_2].

When a highway gate closes — approaches zero — the layer stops passing the identity signal and instead represents a plain, non-residual function; ResNet's identity shortcuts carry no gate and never close [§sec_2].

Highway Networks have not been shown to gain accuracy from extreme depth, past roughly 100 layers; this paper's identity-shortcut formulation is what later sections show scaling past that point [§sec_2].

The comparison below lines up the two shortcut designs on the dimensions the paper contrasts them by [§sec_2]:

| Property | Highway Networks | ResNet (this paper) |
|---|---|---|
| Shortcut type | Data-dependent, gated, carries parameters [§sec_2] | Identity, parameter-free [§sec_2] |
| Behavior as gate → 0 | Represents a non-residual, learned function [§sec_2] | Not applicable — shortcut is never closed [§sec_2] |
| What is always learned | A residual function plus a gate function [§sec_2] | Only a residual function; all information always passes through [§sec_2] |
| Depth demonstrated | No accuracy gain shown past roughly 100 layers [§sec_2] | Addressed by this paper's own experiments, outside this section [§sec_2] |

## The Math {#the-math}

**A boundary case: what a closed gate represents.** Highway Networks compute a gated combination of a transform and the identity path, where a learned gate decides how much of each to pass through [§sec_2].

Take the gate at its two extremes. At the open extreme the gate passes the transform fully, so the layer behaves like an ordinary feedforward layer with no shortcut benefit [§sec_2].

At the closed extreme, near zero, the gate blocks the transform and passes close to the identity — but that identity path still required learning a gate function to reach it, and the gate itself is a function of the input, so it is never a literal identity map [§sec_2].

That gap is the structural argument against calling highway shortcuts identity shortcuts: closing the gate approximates identity but does not equal it, and reaching that approximation still spends learned parameters [§sec_2].

ResNet's shortcut has no such extreme to reason about, because it has no gate — every layer's output is a residual function added to an untouched identity term, so the identity path costs zero parameters at any point during training [§sec_2].

**Parameter-count consequence.** A highway layer must learn both a residual function and a gate function, while a ResNet layer with an identity shortcut learns only the residual function — the gate's parameters are pure overhead that a plain identity shortcut removes entirely [§sec_2].

## Go Deeper {#go-deeper}

Two open threads worth tracing from here: how identity shortcuts compare quantitatively to gated shortcuts at extreme depth, and whether shallow residual-encoding tricks like VLAD have any deep-learning analogue beyond shortcut connections.

The next concept, Residual Learning, works out the identity-shortcut formulation that this section only contrasts against Highway Networks and the earlier shortcut-connection tricks.

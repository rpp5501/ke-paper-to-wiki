# Symmetries in Common Neural Network Components

## TL;DR {#tldr}
Every layer built from weights times an activation inherits a symmetry group fixed by how that activation transforms under a group action. Linear layers admit the largest group, GL_h(R); nonlinear activations shrink it to whatever subgroup the activation itself commutes with — scaling, sign-flip, rotation, translation, or permutation.

## Intuition {#intuition}
Picture the hidden layer as a coordinate system for whatever the activation computes. If the activation doesn't notice a rotation, rescaling, or permutation of those coordinates — its output moves the same way — then that move can be undone on the way out, leaving the network's final output unchanged.

The group of moves an activation doesn't notice is exactly the group of parameter symmetries cataloged below: continuous groups like GL_h(R) or O(h) for continuous-valued activations, discrete groups like sign-flips or permutations for activations with only finite symmetry.

## Mechanics {#mechanics}

**Equivariant activations inherit a group action from their own equivariance.** If σ satisfies σ(gZ) = ρ(g)σ(Z), the network f = W2σ(W1X) admits g·(W2,W1) = (W2ρ(g^{-1}), gW1): rotating the pre-activation by g inside σ is exactly undone by ρ(g)^{-1} at the output [§sec_2_2_1].

```figure
id: fig_2
caption: Three symmetry shapes on the same computation graph — scaling an invariant activation's incoming weights (a), scaling an equivariant activation's incoming and outgoing weights together (b), and permuting neurons with their attached weights (c) [§sec_2_2_1]
```

**The linear case is where this mechanism is easiest to see.** Take σ to be the identity, so ρ(g)=g and G = GL_h(R): the general formula collapses to g·(W2,W1,b2,b1) = (W2g^{-1}, gW1, b2, gb1), the largest group in the table because no nonlinearity restricts which g commute with it [§sec_2_2_1].

**Homogeneous activations shrink the group to positive diagonal scaling.** ReLU, LeakyReLU, and monomials satisfy σ(cz)_i = c^{α_i}σ(z)_i, so only diagonal g∈R_{>0}^h — not the full GL_h(R) — commute with σ, giving the action (W2g^{-α}, gW1) [§sec_2_2_1].

**Tanh restricts the group further, to sign flips.** tanh is odd, tanh(-z) = -tanh(z), so only diagonal g∈Z_2^n with entries in {1,-1} commute with it, giving the action (W2g^{-1}, gW1) [§sec_2_2_1].

**Radial activations recover a continuous, non-diagonal group.** σ(z) = f(‖z‖)z is equivariant under any orthogonal g, since ‖gz‖ = ‖z‖, so the symmetry group grows back to O(h), with the same action form (W2g^{-1}, gW1) [§sec_2_2_1].

**A different pattern appears when the activation is invariant rather than equivariant.** If σ(gZ) = σ(Z) exactly (ρ trivial), the group acts only on the input weights of σ, with no compensating transformation needed on the output side [§sec_2_2_1].

**Batchnorm is invariant to positive row scaling.** Scaling a row of W by c>0 scales both the mean and standard deviation of that row's pre-activations by c, so the normalized ratio is unchanged; the symmetry group is R_{>0}^h acting by g·W = gW [§sec_2_2_1].

**Softmax is invariant to a shared additive shift.** Adding the same vector g to every row of W shifts every logit in a column by the same amount, and softmax's normalization cancels any constant shift; the group is the additive group (R^n,+) [§sec_2_2_1].

**Identical activations across coordinates admit permutation symmetry.** When every σ_i is the same scalar function, relabeling the h hidden units — permuting rows of W1 and matching columns of W2 by π∈S_h — leaves f unchanged, since a sum over hidden units doesn't care about their order [§sec_2_2_1].

**Radial basis function networks permute over components rather than neurons.** Relabeling the k centers c_i, widths b_i, and weights w_i by π∈S_k leaves Σw_iφ(‖x-c_i‖/b_i) unchanged, since it doesn't depend on the order of terms in a sum [§sec_2_2_1].

| Name | Architecture | Symmetry Group | Group Action |
|---|---|---|---|
| Linear | $W_2 W_1 X$ | $\mathrm{GL}_h(\mathbb{R})$ | $g\cdot(W_2,W_1)=(W_2g^{-1},gW_1)$ [tab_1] |
| Homogeneous | $W_2\sigma_{hom}(W_1X)$ | $\mathbb{R}_{>0}^h$ | $g\cdot(W_2,W_1)=(W_2g^{-\alpha},gW_1)$ [tab_1] |
| Tanh | $W_2\sigma_{\tanh}(W_1X)$ | $\mathbb{Z}_2^n$ | $g\cdot(W_2,W_1)=(W_2g^{-1},gW_1)$ [tab_1] |
| Radial rescaling | $W_2\sigma_{radial}(W_1X)$ | $O(h)$ | $g\cdot(W_2,W_1)=(W_2g^{-1},gW_1)$ [tab_1] |
| Batchnorm | $\frac{(WX)_i-E[(WX)_i]}{\sqrt{\mathrm{Var}[(WX)_i]}}$ | $\mathbb{R}_{>0}^h$ | $g\cdot W=gW$ [tab_1] |
| Softmax | $\mathrm{softmax}(WX)$ | $(\mathbb{R}^n,+)$ | $(g\cdot W)_i=W_i+g$ [tab_1] |
| Pointwise | $W_2\sigma_{pointwise}(W_1X)$ | $S_h$ | $g\cdot(W_2,W_1)=(W_2g^{-1},gW_1)$ [tab_1] |
| RBF | $\sum_i w_i\varphi(\|x-c_i\|/b_i)$ | $S_k$ | $\pi\cdot(w_i,b_i,c_i)=(w_{\pi^{-1}(i)},b_{\pi^{-1}(i)},c_{\pi^{-1}(i)})$ [tab_1] |

**Every example above extends to deeper networks.** Viewed as a computational graph, a network inherits the symmetries of each subnetwork, so any of these symmetries can be applied independently to any adjacent pair of layers, and modern architectures built from these same components admit the same symmetries on the corresponding subspace of their parameters [§sec_2_2_1].

## The Math {#the-math}

**The linear example makes the general cancellation mechanism concrete.** Substituting the group action into f_linear and expanding shows the g^{-1} introduced by the output layer and the g introduced by the hidden layer cancel exactly, term by term [eq_2].

```derivation
shape: Verify that the linear network's output is unchanged under the GL_h(R) action.
steps:
  - latex: "f_{linear}(g\\cdot(W_2,W_1,b_2,b_1), X) = W_2g^{-1}(gW_1X + gb_1) + b_2"
    why: "Substitute the group action (W_2g^{-1}, gW_1, b_2, gb_1) directly into f_{linear} [eq_2]"
  - latex: "= W_2(W_1X+b_1)+b_2"
    why: "g^{-1} and g cancel inside the parenthesis, since g^{-1}g = I for any g \\in \\mathrm{GL}_h(\\mathbb{R}) [eq_2]"
  - latex: "= f_{linear}(W_2,W_1,b_2,b_1,X)"
    why: "The result is the original, untransformed output, confirming the action leaves f_{linear} fixed [eq_2]"
```

**The same cancellation drives the homogeneous case, with one exponent tracking the nonlinearity.** Take α=1 (ReLU) and g=2: W1 doubles, so σ(2W1X) = 2σ(W1X) by degree-1 homogeneity, and W2 halves (g^{-α}=2^{-1}), exactly cancelling the factor of 2 introduced by σ [§sec_2_2_1].

**Tanh's boundary case uses oddness instead of homogeneity.** Take g=-1 on a single hidden unit: W1 flips sign, tanh(-W1X) = -tanh(W1X) since tanh is odd, and W2 also flips sign, so the two sign flips cancel and f is unchanged [§sec_2_2_1].

**Radial rescaling's boundary case is a rotation, not a sign flip or scale.** Take g to be a 90° rotation in a 2-dimensional hidden space: ‖gz‖ = ‖z‖ for any orthogonal g, so σ(gW1X) rotates with g, and the output layer's g^{-1} rotates it back [§sec_2_2_1].

**Batchnorm's invariance is exact, not approximate, at any scale.** Take a row of W scaled by c=10: both the row mean and the row standard deviation of WX scale by 10, so (WX-mean)/std is identical whether c=1 or c=10, for every c>0 [§sec_2_2_1].

**Softmax's boundary case is the two-logit case, where the cancellation is visible directly.** With two rows shifted by the same g, both logits gain the same additive term gX, so e^{z_i+gX} shares a factor e^{gX} in numerator and denominator that cancels, leaving softmax(z) unchanged [§sec_2_2_1].

## Go Deeper {#go-deeper}
No external resources were supplied for this concept. Two related pages extend this material: Symmetries in Transformers builds directly on the equivariant-activation pattern established here, and Functional Neural Network Symmetry gives the general definition of which these examples are instances.

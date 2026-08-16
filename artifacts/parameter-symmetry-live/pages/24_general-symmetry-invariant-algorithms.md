# General Symmetry Invariant Algorithms

## TL;DR {#tldr}
- Natural gradient descent preconditions by the inverse Fisher information metric, making its update direction invariant to any smooth reparameterization of the network, not just rescalings [S1][S5].
- Exact invariance breaks at finite step size; second-order ODE solvers recover it to second order [§sec_4_2_2].
- K-FAC makes the Fisher-based update tractable by approximating each layer's Fisher block as a Kronecker product [S3].
- Scale-free updates (invariance to gradient scaling alone) are hypothesized to explain why AdamW beats Adam+ℓ2 [§sec_4_2_2].

## Intuition {#intuition}
Plain gradient descent measures distance in the parameter coordinates you happen to have chosen, so it slows down or speeds up depending on how those coordinates are scaled or skewed [§sec_4_2_2].

Natural gradient descent instead measures distance on the manifold of probability distributions the model represents, using the Fisher metric — a notion of distance that does not care which coordinates label a given distribution [§sec_4_2_2].

That is the general-symmetry case promised by this concept's place in the page tree: [[Scaling Invariant Algorithms]] only cancel out rescalings of individual weights, while natural gradient descent is built to be invariant to any smooth change of parametrization, general symmetry included.

## Mechanics {#mechanics}
Natural gradient descent computes gradients using the Fisher metric on the manifold of distributions, and because that metric is defined on the distributions themselves rather than on the parameter coordinates, it is invariant to parametrization [§sec_4_2_2].

**In implementation, this invariance is not exact.** A single natural-gradient step approximates a geodesic step on the manifold using a finite step size, and that approximation is what introduces the invariance error [§sec_4_2_2].

Methods that instead use a second-order ODE solver together with a second-order approximation of the exponential map can reduce this invariance error to second order [§sec_4_2_2] — worked out quantitatively below.

Beyond the Fisher metric itself, more recent work shows gradient descent can be made invariant to parameter symmetry by explicitly including a metric in the gradient computation, and that metrics other than the Fisher metric can achieve the same invariance [§sec_4_2_2].

A related but weaker property is scale-free updates: updates invariant to gradient scaling rather than to general reparametrization. These are hypothesized to explain why AdamW outperforms plain Adam with ℓ2 regularization [§sec_4_2_2] — contrast with [[Scaling Invariant Algorithms]].

The Fisher metric coincides with the expected Gauss-Newton matrix for many losses [S2]. Computing and inverting it exactly costs O(n^3) for n parameters, which is intractable for deep networks [S2].

K-FAC approximates each layer's Fisher block as a Kronecker product of two much smaller matrices to cut this cost while keeping most of the invariance benefit [S3] — quantified below.

The same coordinate-invariant-preconditioning idea recurs outside natural gradient: general Riemannian and second-order trust-region methods, and mirror descent under Bregman divergences, both precondition by a metric rather than by raw coordinates [S4].

Even first-order SGD is shaped by this: recent work shows its noise settles into an equilibrium that depends on the network's parameter symmetries, which is part of why metric-aware methods matter [S4].

```algorithm
title: Natural gradient descent with a K-FAC-approximated Fisher metric
lines:
  - code: "g_t = grad(L, theta_t)"
    intent: "Ordinary loss gradient in the current parameter coordinates [§sec_4_2_2]"
  - code: "F_l ≈ A_l ⊗ B_l   for each layer l"
    intent: "K-FAC approximates each layer's Fisher block as a Kronecker product instead of forming the full matrix [S3]"
  - code: "F_l^{-1} ≈ A_l^{-1} ⊗ B_l^{-1}"
    intent: "Kronecker inverses factor, so inverting two small matrices stands in for inverting one huge one [S3]"
  - code: "theta_{t+1} = theta_t - eta * F^{-1} g_t"
    intent: "Preconditioning by the inverse Fisher makes the step direction covariant with reparametrization, unlike raw gradient descent [S1][S5]"
```

## The Math {#the-math}
**Why exact Fisher inversion doesn't scale.** Take one layer with input dimension 100 and output dimension 100, so its Fisher block has n = 100×100 = 10,000 parameters [S2]. Direct inversion of an n×n matrix costs O(n^3) ≈ 10^12 operations [S2].

K-FAC instead inverts the two 100×100 factors separately, costing O(100^3 + 100^3) ≈ 2×10^6 operations [S3].

That is roughly a 500,000× reduction for this one layer, which is why K-FAC is what makes Fisher-metric preconditioning usable on real networks rather than a theoretical curiosity [S3].

**Why finite steps aren't exactly invariant.** A first-order integrator's local error grows as O(h^2) in step size h, so one natural-gradient step deviates from the true geodesic by an amount that shrinks quadratically as h shrinks, but is never zero at any fixed h [§sec_4_2_2].

Swapping in a second-order ODE solver with the second-order exponential-map approximation raises the local accuracy by one order, to O(h^3) [§sec_4_2_2].

That is what "reduces the invariance error to second order" means: not zero error, but an error term that vanishes one power of h faster, so halving the step size cuts the residual invariance violation by roughly 8× instead of 4× [§sec_4_2_2].

## Go Deeper {#go-deeper}
- [Fisher information metric](https://en.wikipedia.org/wiki/Fisher_information_metric) — the Riemannian-manifold picture (geodesics, curvature) that explains why preconditioning by this metric makes descent invariant to reparameterization. Start here if the manifold framing feels unmotivated.
- [New insights and perspectives on the natural gradient method](https://arxiv.org/abs/1412.1193) — derives the Fisher metric, connects it to the Gauss-Newton matrix, and works through the cost of computing it exactly.
- [Optimizing Neural Networks with Kronecker-factored Approximate Curvature](https://arxiv.org/abs/1503.05671) — the concrete K-FAC algorithm that makes the natural-gradient metric affordable at scale.

# Scaling Invariant Algorithms

## TL;DR {#tldr}

ReLU networks have a rescaling symmetry — multiply a unit's incoming weights by α and its outgoing weights by 1/α — that leaves the function unchanged, but plain gradient descent is not invariant to it.

Two algorithm families restore invariance: Path-SGD regularizes updates with a path-based norm over input-to-output weight products, and a second family optimizes directly in a quotient or manifold space that has already divided out the scaling symmetry.

## Intuition {#intuition}

Two networks can compute the exact same function while looking completely different on paper, the way a recipe scaled by 2× ingredients and 0.5× serving size still tastes identical. Gradient descent doesn't know this — it reacts to the numbers in front of it, not the function they represent.

If one version of the network has huge incoming weights and tiny outgoing ones, gradient descent sees a badly distorted landscape and crawls or zig-zags, even though a differently-scaled twin of the same network would train fine.

Scaling-invariant algorithms fix this by measuring progress with a ruler that doesn't care about the choice of scale — either by regularizing something already invariant, or by working in a space where the redundant scaling directions have been removed entirely.

## Mechanics {#mechanics}

ReLU networks are positively rescale-invariant: multiplying a unit's incoming weights by α and its outgoing weights by 1/α leaves the function unchanged, but gradient descent on the raw parameters is not invariant to this reparameterization [§sec_4_2_1].

When incoming and outgoing weights are badly mismatched, gradient descent tends to perform poorly, and the resulting inconsistency in performance across parameters on the same orbit also makes the algorithm harder to analyze [§sec_4_2_1].

The extra effort needed to avoid these configurations motivates optimization algorithms that are invariant to rescaling by construction. Two families have been developed, contrasted below [§sec_4_2_1].

| Family | Invariant quantity used | Where it optimizes | Example |
|---|---|---|---|
| Path-SGD | Product of weights along each input-to-output path, π(θ) | Raw parameter space, with a path-based proximal penalty | ReLU networks [§sec_4_2_1] |
| Quotient / manifold methods | The scaling-equivalence class of a parameter setting | A lower-dimensional quotient space or manifold with the symmetry already divided out | 𝒢-SGD; batch-norm quotient methods [§sec_4_2_1] |

Path-SGD builds on one fact and two consequences [§sec_4_2_1]:

- The product of a ReLU unit's incoming and outgoing weights along any input-to-output path is itself invariant to rescaling, so the paper collects these products into a path vector π(θ) [§sec_4_2_1].
- Instead of penalizing distance in raw parameter space, ‖θ − θᵗ‖₂², Path-SGD's proximal step penalizes distance in this path vector, ‖π(θ) − π(θᵗ)‖ₚ², giving the update in Equation [eq_10] [eq_10].
- Because each entry of π(θ) is a product of several parameters, a parameter's step size ends up inversely proportional to the norm of a vector of the other parameters on its paths — larger parameters get proportionally larger updates, which is what compensates for a rescaled configuration [§sec_4_2_1].

The second family removes the symmetry by changing where the optimization happens, using two constructions [§sec_4_2_1]:

- 𝒢-SGD performs gradient descent directly in the rescale-invariant space spanned by the path vector of a set of basis paths, so the scaling redundancy is never part of the optimization variables [§sec_4_2_1].
- A related approach constrains each layer's incoming weights to stay unit-norm, computing a Riemannian gradient and projecting back onto the oblique manifold {W : diag(WWᵀ) = I} after every step [§sec_4_2_1].
- Batch-normalized networks have their own positive scaling symmetry, and quotienting it out the same way yields gradient descent on the quotient manifold, proven to converge faster than gradient descent in the original parameter space [§sec_4_2_1].

## The Math {#the-math}

$$
^{t+1} = \argmin_ \eta \left< \grad L(^t), \right> + \frac{1}{2} \left\| \pi() - \pi(^t) \right\|_p^2.
$$
[eq_10]

Some symbols were dropped from Equation [eq_10] by source extraction (the θ and Δ terms are missing). The derivation below reconstructs them to show the two structural changes Path-SGD makes on top of an ordinary proximal step [§sec_4_2_1].

```derivation
shape: From an ordinary proximal gradient step to Path-SGD's path-regularized version.
steps:
  - latex: "\theta^{t+1} = \operatorname*{argmin}_{\Delta}\ \eta\langle \nabla L(\theta^t), \Delta\rangle + \tfrac{1}{2}\|\Delta\|_2^2"
    why: "The ordinary proximal step: a linear model of the loss around θᵗ plus a quadratic penalty on how far Δ moves in raw parameter space [§sec_4_2_1]"
  - latex: "\theta^{t+1} = \operatorname*{argmin}_{\Delta}\ \eta\langle \nabla L(\theta^t), \Delta\rangle + \tfrac{1}{2}\|\pi(\theta+\Delta) - \pi(\theta^t)\|_p^2"
    why: "Path-SGD swaps the penalty on Δ for one on the path vector's displacement, so the same functional change costs the same regardless of which rescaled parameterization it's measured from [eq_10]"
```

A minimal case makes the imbalance concrete, for a single ReLU unit with one incoming weight w₁ and one outgoing weight w₂ [§sec_4_2_1]:

- Take w₁ = 10, w₂ = 0.1, computing the same function as w₁ = 1, w₂ = 1 — both give the same path product π = w₁w₂ = 1 [§sec_4_2_1].
- In raw parameter space, the two configurations sit at very different distances from any fixed point, so an ℓ2 penalty ‖θ − θᵗ‖₂² treats them completely differently despite computing the same function [§sec_4_2_1].
- In path space, both configurations map to the same π = 1, so a penalty on ‖π(θ) − π(θᵗ)‖ₚ² scores them identically — that is what "invariant to rescaling" means concretely [eq_10].
- The per-parameter step size is inversely proportional to the other parameter on the same path: w₁'s update scales with 1/w₂, and w₂'s scales with 1/w₁, so the larger of a mismatched pair gets a proportionally larger step [§sec_4_2_1].

## Go Deeper {#go-deeper}

- [Gradient Descent — Dive into Deep Learning](https://d2l.ai/chapter_optimization/gd.html) — an animated contour plot showing exactly why gradient descent struggles when a loss is scaled very differently along different directions, the core pathology these algorithms fix. Start here if the ill-conditioning argument above isn't clicking.
- [Path-SGD: Path-Normalized Optimization in Deep Neural Networks](https://arxiv.org/abs/1506.02617) — the original derivation of the steepest-descent update in a path-based norm, provably invariant to positive rescaling.
- [Weight Normalization: A Simple Reparameterization to Accelerate Training of Deep Neural Networks](https://arxiv.org/abs/1602.07868) — the reparameterization alternative, decoupling a weight vector's direction from its scale so gradient steps act only on direction.
- [Three Mechanisms of Weight Decay Regularization](https://arxiv.org/abs/1810.12281) — formalizes how ReLU + batch-norm scale invariance turns weight decay into an implicit effective-learning-rate controller.

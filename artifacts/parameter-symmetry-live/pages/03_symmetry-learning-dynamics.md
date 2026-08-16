# Implications of Symmetry for Learning Dynamics

## TL;DR {#tldr}

Continuous symmetries in a network's parameter space carry over Noether's theorem from physics: each one implies a quantity that stays constant along the continuous-time gradient-flow trajectory. These conserved quantities are invisible in the loss curve, but they couple parameters together and shape the geometry the optimizer actually moves through.

In real, discrete SGD the conservation is only approximate — its breaking, not just its presence, is a driver of learning dynamics.

## Intuition {#intuition}

In physics, a symmetry of the potential energy — say, spinning a system without changing its energy — buys you a conserved quantity, like angular momentum, that survives the whole trajectory.

Kunin et al.'s insight is that a neural network's loss plays the role of a potential, and gradient descent, in its continuous limit, plays the role of the dynamics.

So a symmetry direction in parameter space — a way of moving the weights that leaves the loss unchanged — buys the same thing: a quantity that gradient flow can't touch. Training doesn't erase it; training just moves along the surface it defines.

## Mechanics {#mechanics}

Noether's theorem states that every continuous symmetry of a physical system's Lagrangian corresponds to a conserved quantity under its dynamics. [S3]

Gradient flow — the continuous-time limit of gradient descent — plays the role of the physical dynamics, and treating the loss as the potential lets the same variational argument be applied to training trajectories. [S1][S3]

Kunin et al. show many common architectures possess parameter-space symmetries: rescaling symmetries in ReLU networks and rotational symmetries around normalization layers are both continuous families of weight transformations that leave the loss unchanged. [S1]

Each such symmetry implies a conserved quantity along the gradient-flow trajectory, analogous to a Noether charge — a scalar function of the parameters that gradient flow holds constant even as the weights themselves keep moving. [S1]

These conserved quantities constrain how parameters move relative to one another, coupling otherwise-independent weights and shaping the effective optimization geometry even though they are invisible in the loss value itself. [S1]

Tanaka and Kunin extend the analysis to the discrete, stochastic setting of real SGD, where the continuous conservation laws hold only approximately rather than exactly. [S2]

Momentum, weight decay, and finite learning rates each break the continuous conservation law at every update, though for different reasons. [S2]

- **Momentum** carries the trajectory past the level set the conserved quantity defines, since the update depends on past gradients rather than only the current symmetry-respecting direction. [S2]
- **Weight decay** actively shrinks the parameters along directions the symmetry would otherwise leave untouched, directly displacing the conserved quantity. [S2]
- **Finite learning rates** turn the exact continuous-time integral into a first-order discrete approximation, so the conserved quantity drifts by an amount that scales with step size. [S2]

This breaking is not a numerical artifact: Tanaka and Kunin show it actively drives learning dynamics, meaning the departure from the conserved quantity is doing real optimization work rather than merely eroding a theoretical bookkeeping device. [S2]

## The Math {#the-math}

Noether's counting is exact enough to state without a formula: a one-parameter continuous symmetry — the ReLU rescaling family, or the rotation angle around a normalization layer — contributes exactly one conserved scalar. [S1]

Moving along that symmetry direction confines the gradient-flow trajectory to one level set of that scalar, rather than letting it explore the full parameter space — the conserved quantity is a coordinate the optimizer cannot change. [S1]

The step-size dependence is itself a boundary case. As the discrete learning-rate step shrinks toward zero, the SGD update converges to the continuous gradient-flow trajectory, and the conserved quantity is held exactly in that limit. [S2]

At any finite step, the update is only a first-order approximation to that flow, so each step displaces the trajectory off the level set by an amount that does not vanish as training proceeds. [S2]

Momentum and weight decay are two more instances of the same boundary argument: both are extra terms absent from the pure gradient-flow update, so both are additional sources of departure from the level set — neither is a special case that happens to preserve it. [S2]

## Go Deeper {#go-deeper}

- [Noether's theorem](https://en.wikipedia.org/wiki/Noether%27s_theorem) — the general physics statement and diagrams of the symmetry–conservation correspondence; start here if the Lagrangian/conserved-quantity language above is unfamiliar.
- [Neural Mechanics: Symmetry and Broken Conservation Laws in Deep Learning Dynamics](https://arxiv.org/abs/2012.04728) — derives the Noether-style conserved quantities implied by common neural network symmetries under gradient flow; this is the paper behind the claims in Mechanics above.
- [Noether's Learning Dynamics: Role of Symmetry Breaking in Neural Networks](https://arxiv.org/abs/2105.02716) — extends the analogy to real, discrete, stochastic SGD and shows that symmetry breaking actively drives training.

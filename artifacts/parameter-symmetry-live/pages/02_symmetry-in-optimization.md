# Applications of Symmetry in Gradient-Based Optimization
## TL;DR {#tldr}
- Points on the same symmetry orbit have identical loss but can have very different gradients, so gradient descent from $\theta$ and $\theta' = g\cdot\theta$ can diverge even though $L(\theta) = L(\theta')$ [§sec_4].
- Two families of optimizers exploit this: **invariant algorithms** rebuild the update rule so it never depends on which orbit point you start from, and **teleportation** actively jumps to a better orbit point before taking a normal gradient step [§sec_4].

## Intuition {#intuition}
Gradient descent (eq_9) treats the raw coordinates of $\theta$ as if they carried meaning, but a continuous symmetry group can move $\theta$ along a flat direction — a path where the loss never changes while the gradient magnitude changes a lot [§sec_4].

ReLU rescaling is a concrete instance: scaling a unit's incoming weights up and its outgoing weights down by the same factor leaves the network's function untouched, yet changes how steep the loss looks in that direction [S2].

An optimizer walking blindly along raw coordinates can get stuck on a near-flat slope simply because of which point on the orbit it landed on, not because of the actual loss landscape [S1][S2].

Two responses follow from this: make the update rule itself blind to the symmetry, or actively choose a better point on the orbit before stepping, since the loss doesn't care where you are but the gradient does [S1][S2].

## Mechanics {#mechanics}
**Symmetry-invariant algorithms** redesign the update so its step size and direction do not depend on the arbitrary parameterization chosen within an orbit [S2].

Path-SGD is the concrete example: it derives an update for ReLU networks provably invariant to the positive-rescaling symmetry, so two networks related by $g\cdot\theta$ take equivalent steps rather than steps that differ only because of an arbitrary rescaling [S2].

**Teleportation** takes the opposite route: instead of changing the update rule, it changes the point before applying eq_9's ordinary rule [S1].

It moves $\theta$ along its own symmetry orbit to a location where $\nabla L$ has larger norm, then takes a standard gradient step from there — provably accelerating convergence in some settings [S1].

Both diverge from vanilla gradient descent, which applies eq_9's fixed step size $\eta_t$ directly to whatever coordinates $\theta_t$ happens to have, making its behavior sensitive to a symmetry that never shows up in the loss value itself [S1][S2].

| Approach | Mechanism | Where it acts | What it fixes |
|---|---|---|---|
| Invariant algorithms (Path-SGD) | Update rule built to be unaffected by the symmetry group | Every step | Removes the dependence of step size/direction on an arbitrary parameterization [S2] |
| Teleportation | Move along the orbit to a higher-gradient point, then take a standard step | Once, before the step | Exploits the gradient variation across the orbit to speed convergence [S1] |

## The Math {#the-math}
$$\theta_{t+1} = \theta_t - \eta_t \nabla L (\theta_t)$$
[eq_9]

```annotated-eq
latex: "\\theta_{t+1} = \\theta_t - \\eta_t \\nabla L (\\theta_t)"
terms:
  - tex: "\\theta_t"
    role: 1
    words: "The current point in parameter space — one specific member of whatever symmetry orbit the true function lives on [§sec_4]"
  - tex: "\\eta_t"
    role: 2
    words: "A scalar step size applied uniformly to every raw coordinate of theta, with no notion of which coordinates are 'flat' due to symmetry [§sec_4]"
  - tex: "\\nabla L(\\theta_t)"
    role: 3
    words: "The gradient at this exact point — the quantity that changes across an orbit even though L itself does not [§sec_4]"
```

The update rule takes only $\theta_t$, $\eta_t$, and $\nabla L(\theta_t)$ as inputs — it has no way to know that $\theta_t$ is one of many equally-good points related by the symmetry group $G$ [§sec_4].

Because $\eta_t$ scales every coordinate identically, a point on the orbit with a small gradient produces a small step, and a point with a large gradient produces a large step, even though both sit at the same loss value [S1][S2].

The two families close this gap from opposite ends. Invariant algorithms change what $\nabla L(\theta_t)$ means, replacing the raw Euclidean gradient with one built to ignore the symmetry direction [S2].

Teleportation instead changes what $\theta_t$ is before the update runs, picking the orbit member with the largest $\|\nabla L(\theta_t)\|$ so eq_9's fixed $\eta_t$ produces a more useful step [S1].

Neither modifies $L$ itself — both only change how eq_9 is applied against a landscape the symmetry has made structurally redundant [S1][S2].

The same phenomenon shows up in ordinary quadratic optimization without any group symmetry: decomposing a quadratic loss's Hessian into its eigenbasis separates directions where gradient descent converges quickly from directions where it converges slowly, as a function of curvature [S3].

Parameter symmetry is a more extreme version of the same idea — an entire orbit direction has zero curvature (flat loss) but nonzero, coordinate-dependent gradient, exactly the situation eq_9 handles worst [S3].

## Go Deeper {#go-deeper}
- [Symmetry Teleportation for Accelerated Optimization](https://arxiv.org/abs/2205.10637) — start here: the concrete teleportation algorithm this page describes, with a proof of its convergence-rate speedup.
- [Path-SGD: Path-Normalized Optimization in Deep Neural Networks](https://arxiv.org/abs/1506.02617) — derives the invariant update rule this page contrasts with vanilla gradient descent, and shows exactly why it diverges from eq_9.
- [Why Momentum Really Works](https://distill.pub/2017/momentum/) — interactive visualization of the eigenbasis decomposition behind the fast/slow-direction intuition used above.

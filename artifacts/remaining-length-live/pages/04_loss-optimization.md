# Loss and Optimization

## TL;DR {#tldr}
Each active probe trains against its own supervised loss on hidden states pulled from a frozen base model, and the base model's weights are never updated [§sec_3_5]. Per-probe gradients are computed, backpropagated into that probe's own parameters, and cleared before the next minibatch, so probes never interfere with each other's optimizer state [§sec_3_5].

## Intuition {#intuition}
Think of the frozen base model as a fixed camera and each probe as a small dial trying to read one number off the picture it already took. Training a probe never touches the camera — it only turns that probe's own dial until its reading matches the label, using its own gradient and its own optimizer state [§sec_3_5].

## Mechanics {#mechanics}
Training touches only the probes, never the base model. Each minibatch produces hidden states once, then every active probe in $\mathcal{P}$ computes its own loss, backpropagates, and steps its own optimizer against those same hidden states [§sec_3_5].

```algorithm
title: Per-minibatch probe training loop
lines:
  - code: "h = base_model(batch)  # frozen, no grad"
    intent: "Hidden states are computed once and shared across every probe in P; the base model's parameters are never updated by this step [§sec_3_5]"
  - code: "for p in P:"
    intent: "The loop runs independently over each active probe, one at a time [§sec_3_5]"
  - code: "    loss = L_p(theta_p; batch)"
    intent: "Each probe supervises its own head against its own labels, most commonly cross-entropy for a classification-style probe [S4]"
  - code: "    loss.backward()"
    intent: "Backprop runs only into theta_p — gradients stop at the frozen hidden states, so no probe's gradient touches another probe's parameters [§sec_3_5]"
  - code: "    optimizer_p.step()"
    intent: "Each probe keeps its own optimizer state (e.g. Adam moments), so a large-gradient probe cannot distort another probe's step size [S1]"
  - code: "    optimizer_p.zero_grad()"
    intent: "Clearing per-probe gradients after the step stops next minibatch's gradient from accumulating onto this one [§sec_3_5]"
```

Probes can be combined into training in two ways, and they trade off differently:

| Scheme | Gradient interaction | Optimizer | When it matters |
|---|---|---|---|
| Joint | Summed into one scalar, backprop shares the frozen backbone's forward pass | One optimizer over all $\theta_p$ | Standard hard-parameter-sharing multi-task setup [S1] |
| Independent | None between probes | Separate optimizer per probe | Avoids one probe's loss scale dominating another when task difficulty differs [S1] |

The paper's own loop steps each probe's optimizer separately [§sec_3_5], matching the independent row: no probe's gradient ever reaches another probe's parameters.

Whichever scheme is used, the per-probe loss is minimized with a first-order stochastic optimizer such as Adam, which adapts each parameter's step size from running estimates of the gradient's first and second moments rather than one global learning rate [S2][S3].

## The Math {#the-math}
Every active probe here is a single linear layer on frozen features, so its loss is convex in $\theta_p$: cross-entropy composed with an affine map has no local minima to trap gradient descent, unlike training the deep base model itself [S4].

The consequence for Adam's step size is worth tracing through actual numbers, since "adapts per-parameter step size" is otherwise just a phrase:

```derivation
shape: Track Adam's adaptive step size across two gradient updates for one probe weight ($\beta_1=0.9$, $\beta_2=0.999$, lr $=0.001$).
steps:
  - latex: "m_1 = 0.9(0)+0.1(0.8)=0.08,\\quad v_1=0.999(0)+0.001(0.8)^2=0.00064"
    why: "First- and second-moment running estimates after the first minibatch's gradient g_1=0.8 [S2][S3]"
  - latex: "\\hat m_1=0.08/(1-0.9^1)=0.8,\\quad \\hat v_1=0.00064/(1-0.999^1)=0.64"
    why: "Bias correction undoes the zero initialization of m and v, which would otherwise shrink early steps [S2][S3]"
  - latex: "\\Delta w_1 = -0.001\\cdot 0.8/(\\sqrt{0.64}+10^{-8}) \\approx -0.001"
    why: "The corrected moments combine into a step near the base learning rate because the gradient's sign has been consistent so far [S2][S3]"
  - latex: "m_2=0.9(0.08)+0.1(-0.2)=0.052,\\quad v_2=0.999(0.00064)+0.001(0.2)^2\\approx0.000679"
    why: "A sign-flipped, smaller gradient g_2=-0.2 pulls the first moment down while the second moment stays small [S2][S3]"
  - latex: "\\Delta w_2 \\approx -0.001\\cdot 0.274/0.583 \\approx -0.00047"
    why: "The step shrinks roughly in half once the gradient direction becomes less consistent — this per-parameter adaptation is what separates Adam from plain SGD with a fixed learning rate [S2][S3]"
```

Because hidden states are computed once per minibatch and shared across every probe, joint versus independent optimizers change wall-clock cost, not the minimum each probe reaches [S4].

Adding a probe only adds one shallow forward-backward pass on top of the shared frozen backbone, so training $|\mathcal{P}|$ probes costs roughly $|\mathcal{P}|$ single-probe steps rather than $|\mathcal{P}|$ full base-model passes [§sec_3_5][S4].

## Go Deeper {#go-deeper}
- [3Blue1Brown - Gradient descent, how neural networks learn](https://www.youtube.com/watch?v=IHZwWFHWa-w) — the intuitive picture of what minimizing $\mathcal{L}_p(\theta_p; \text{batch})$ via gradient descent is actually doing, before any probe-specific detail.
- [An Overview of Multi-Task Learning in Deep Neural Networks](http://ruder.io/multi-task/) — diagrams hard vs. soft parameter sharing, the exact pattern behind the joint-vs-independent probe training choice.
- [torch.optim.Adam](https://pytorch.org/docs/stable/generated/torch.optim.Adam.html) — the canonical reference implementation of the optimizer used to minimize each per-probe loss.
- [Understanding intermediate layers using linear classifier probes (Alain & Bengio)](https://arxiv.org/abs/1610.01644) — the paper that established linear probes on frozen activations and how their per-probe loss is set up and optimized.

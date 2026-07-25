# Per-Neuron Activation Upper Bounds

## TL;DR {#tldr}
MM-BM introduces a separate ceiling for every neuron in selected layers, suppressing abnormally large activations without pruning neurons or changing learned parameters.

## Intuition {#intuition}
A single dimmer switch would be too crude: some neurons naturally need high values while others carry the suspicious burst. Per-neuron ceilings let the repair tighten each channel independently.

## Mechanics {#mechanics}
The bounded network keeps the original layer functions and parameters but replaces each activation with its componentwise minimum against a bound vector [§sec_1]. The paper initializes bounds large enough to avoid initial saturation, then optimizes them downward while monitoring clean accuracy [§sec_1].

## The Math {#the-math}
For layers $l=2,\ldots,L$, the bound vectors are $\mathbf{z}_l$. The bounded logit is formed by composing clipped layers, with $$\bar{\sigma}_l(\mathbf{a};\mathbf{z}_l)=\min\{\sigma_l(\mathbf{a}),\mathbf{z}_l\}$$ [§sec_1].

## Go Deeper {#go-deeper}
- Activation-Bound Mitigation connects ceilings to the full repair.
- Accuracy-Preserving Lagrangian explains how ceilings are chosen.
- Empirical Scope and Failure Modes notes why tiny global perturbations are harder to suppress.

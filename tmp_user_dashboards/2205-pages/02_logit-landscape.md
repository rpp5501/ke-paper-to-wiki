# Logit Landscape

## TL;DR {#tldr}
The logit landscape is the classifier's pre-softmax output viewed as a surface over input space. A backdoor deforms this surface for the target class, and that deformation — not the trigger itself — is what the detector measures.

## Intuition {#intuition}
Forget the trigger's appearance for a moment. Whatever the trigger looks like, the network had to build an internal "shortcut" that lifts the target class's score sky-high whenever that pattern appears. That shortcut shows up as a suspiciously steep hill in the target class's logit surface: a small, common nudge to almost any image can climb it.

Clean classes have no such universal hill. So the *shape* of the logit surface — how easily a shared perturbation can inflate one class's score — betrays the backdoor without ever knowing the trigger.

## Mechanics {#mechanics}
For class $c$, the logit $g_c(\mathbf{x})$ is the network's output before softmax. A backdoor creates a direction in input space along which $g_t$ for the target class rises far more easily than any clean class allows [§sec_3_1].

Crucially this is independent of the specific trigger design: additive, patch, and blended triggers all leave the same signature — an unusually reachable margin for one class [§sec_3_1].

## The Math {#the-math}
The logit is the final linear read-out over the network's last-layer features,

$$ g_c(\mathbf{x}) = \mathbf{w}_c^{\top}\,\big(\sigma_L \circ \cdots \circ \sigma_1\big)(\mathbf{x}) + b_c, $$

where each $\sigma_\ell$ is a layer's nonlinearity. The detector studies how large the gap $g_t(\mathbf{x}) - \max_{c \neq t} g_c(\mathbf{x})$ can be driven for a candidate target $t$ [eq_4] [§sec_3_1].

## Go Deeper {#go-deeper}
- The Maximum Margin (MM) Statistic turns "how steep is the hill" into one number.
- Bounded-Logit Neuron Clipping later flattens the hill to mitigate the attack [§sec_3_3].

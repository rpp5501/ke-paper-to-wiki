# Maximum-Margin Backdoor Mitigation (MM-BM)

## TL;DR {#tldr}
MM-BM repairs a detected model by capping layer activations with optimized upper bounds, while trying to preserve clean predictions and leaving the learned weights unchanged.

## Intuition {#intuition}
A trigger can work because a small set of internal signals becomes unusually large. MM-BM puts a ceiling above every signal: high enough that ordinary examples still pass, but low enough to suppress the extreme activation pattern that carries the backdoor.

## Mechanics {#mechanics}
The method applies a separate upper-bound vector to each layer after the first. It optimizes these bounds on a small clean set, constrains clean accuracy to stay above a benchmark, and then applies softmax to the bounded logits [§sec_1]. The paper reports effective mitigation for most tested patterns, with weaker results for very small chessboard perturbations [§sec_1].

## The Math {#the-math}
For layer $l$, the bounded activation is $$\bar{\sigma}_l(\mathbf{a};\mathbf{z}_l)=\min\{\sigma_l(\mathbf{a}),\mathbf{z}_l\}$$ [§sec_1]. The min is componentwise, so $\mathbf{z}_l$ supplies one ceiling per neuron rather than one global clipping value [§sec_1].

## Go Deeper {#go-deeper}
- Per-Neuron Activation Upper Bounds gives the architecture-level operation.
- Accuracy-Preserving Lagrangian gives the optimization objective.
- Empirical Scope and Failure Modes records the mitigation caveats.

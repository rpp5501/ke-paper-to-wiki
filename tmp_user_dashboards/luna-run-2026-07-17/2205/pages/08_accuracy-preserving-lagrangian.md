# Accuracy-Preserving Lagrangian

## TL;DR {#tldr}
MM-BM minimizes activation-bound norms while penalizing changes between bounded and original logits on a small clean dataset.

## Intuition {#intuition}
The repair has a safety contract: shrink the internal dynamic range, but do not change ordinary decisions. A Lagrange multiplier acts like a negotiation knob between stronger suppression and fidelity to the original model.

## Mechanics {#mechanics}
The constrained problem requires clean accuracy to exceed a benchmark such as $\pi=0.95$. The practical algorithm minimizes a logit-matching loss plus a weighted sum of bound norms, adjusting the multiplier when the accuracy constraint is met or violated [§sec_1].

## The Math {#the-math}
The paper's constraint is $$\min_{Z}\sum_{l=2}^{L}\|\mathbf{z}_l\|_2\quad\text{subject to}\quad \frac{1}{|D|}\sum_{(\mathbf{x},y)\in D}\mathbf{1}[y=\arg\max_c\bar g_c(\mathbf{x};Z)]\ge\pi$$ [§sec_1]. Its Lagrangian adds $$\lambda\sum_{l=2}^{L}\|\mathbf{z}_l\|_2$$ [§sec_1].

## Go Deeper {#go-deeper}
- Per-Neuron Activation Upper Bounds describes $Z$.
- Activation-Bound Mitigation explains why clean samples are needed only here.
- Maximum-Margin Backdoor Mitigation (MM-BM) summarizes the algorithmic outcome.

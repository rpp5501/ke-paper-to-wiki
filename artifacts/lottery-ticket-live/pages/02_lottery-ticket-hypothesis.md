# The Lottery Ticket Hypothesis
## TL;DR {#tldr}

A dense, randomly-initialized network contains a much smaller subnetwork that, trained alone from the same starting weights, matches or beats the full network's accuracy in no more iterations. Finding that subnetwork by pruning after training, then resetting the survivors to their original values, is the paper's core empirical claim.

## Intuition {#intuition}

Think of a dense network's individual connections as lottery tickets: most are duds, but a few — combined with their specific starting values — are primed to learn quickly.

Pruning after training is how the paper finds the winning combination. Resetting those surviving weights to their original draw, rather than keeping their trained values, is what tests whether the initial values themselves were the lucky part.

This reframes why big networks train more easily than small ones: a bigger network holds many more ticket combinations, so it is more likely to already contain a winning one.

## Mechanics {#mechanics}

Randomly sampled sparse subnetworks are traditionally hard to train from scratch: as sparsity increases, they learn more slowly and settle for lower accuracy than the dense original [§sec_1].

```figure
id: fig_1
caption: Randomly sampled sparse subnetworks (dashed) get slower and less accurate as sparsity increases; the winning tickets this paper finds (solid) do not [§sec_1]
```

The hypothesis makes "a winning subnetwork exists" precise with three conditions on a mask $m$ applied to parameters $\theta_0$ of a network $f(x;\theta)$ [§sec_1]:

- **Equal or faster learning:** $j' \leq j$ — the winning ticket reaches minimum validation loss in no more iterations than the original network [§sec_1]
- **Equal or higher accuracy:** $a' \geq a$ — its test accuracy at that iteration is at least as good [§sec_1]
- **Genuine sparsity:** $\lVert m \rVert_0 \ll |\theta|$ — the surviving mask is a small fraction of the original parameter count [§sec_1]

```algorithm
title: Central experiment — identifying a winning ticket
lines:
  - code: "θ0 ~ D_θ; initialize f(x; θ0)"
    intent: "Draw the dense network's random starting weights [§sec_1]"
  - code: "train f(x; θ0) for j iterations → θ_j"
    intent: "Train the full dense network normally to obtain trained weights θ_j [§sec_1]"
  - code: "m = mask pruning the smallest-magnitude p% of θ_j"
    intent: "Magnitude pruning after training identifies which connections went unused, not which were luckiest at init [§sec_1]"
  - code: "return f(x; m ⊙ θ0)"
    intent: "Resetting survivors to θ0 rather than their trained values is what turns this into a test of the initialization, not just of the architecture [§sec_1]"
```

**One-shot pruning** runs this once: train, prune $p\%$, reset. **Iterative pruning** repeats it over $n$ rounds, each pruning $p^{1/n}\%$ of the weights still surviving the previous round, and finds winning tickets at smaller sizes than one-shot does for the same eventual sparsity [§sec_1].

Resetting survivors to $\theta_0$ is deliberate: a control that instead reinitializes the surviving mask to fresh random weights $\theta_0' \sim \mathcal{D}_\theta$ trains far worse, showing the mask alone does not explain a winning ticket's success [§sec_1].

The empirical claim is bounded to what was tested: fully-connected Lenet on MNIST, and convolutional Conv-2/4/6 on CIFAR10, across SGD, momentum, and Adam, with dropout, weight decay, batchnorm, and residual connections [§sec_1].

Within that scope, winning tickets run 10-20% of the original network's size or smaller, and deeper networks need learning-rate warmup for the pruning procedure to find them [§sec_1].

## The Math {#the-math}

The three inequalities above are the paper's only formal statement for this concept; the arithmetic worth doing is what the iterative rate $p^{1/n}$ implies about how much sparser iterative winning tickets end up than one-shot pruning at the same nominal $p$ [§sec_1].

```derivation
shape: Why the iterative per-round rate is more aggressive than the one-shot rate it is built from.
steps:
  - latex: "r_1 = p^{1/1} = p"
    why: "n = 1 recovers one-shot pruning exactly: the single round removes p of the weights [§sec_1]"
  - latex: "r_n = p^{1/n} > p \\quad (0 < p < 1,\\ n > 1)"
    why: "Raising a fraction between 0 and 1 to a power less than 1 makes it larger, so each iterative round removes a bigger share of survivors than the nominal one-shot rate p [§sec_1]"
  - latex: "(1 - r_n)^n < 1 - p"
    why: "Compounding n rounds of that larger per-round rate removes more weight in total than a single one-shot cut, leaving a sparser final network for the same p [§sec_1]"
```

A worked case makes the gap concrete:

- **Setup:** $p = 0.2$ (a one-shot cut that keeps 80% of weights), $n = 4$ rounds [§sec_1]
- **Per-round rate:** each round removes $0.2^{1/4} \approx 66.9\%$ of surviving weights — far more aggressive than the nominal 20% [§sec_1]
- **Compounded result:** after 4 rounds, $(1-0.669)^4 \approx 1.2\%$ of the original weights remain, versus 80% for a single one-shot cut at the same $p$ [§sec_1]

At $n=1$ the two rates coincide exactly, since one-shot pruning is iterative pruning's own single-round special case [§sec_1].

## Go Deeper {#go-deeper}

No research note or external resources were supplied for this concept. See the related concepts in this paper — Iterative Magnitude Pruning, Winning Ticket, and the Fully-Connected Lenet/MNIST Experiments — for the mechanics and evidence this page builds on.

# Iterative Magnitude Pruning
## TL;DR {#tldr}

Iterative Magnitude Pruning (IMP) finds a winning ticket by repeating a train-prune-rewind loop many times instead of cutting to the target sparsity in one shot. Each round trains the current subnetwork, removes a small fraction of its lowest-magnitude weights, and resets the survivors to their original initialization before the next round begins.

## Intuition {#intuition}

Think of IMP as sculpting rather than cutting: instead of removing most of the material in one strike and hoping the statue still stands, a sculptor chips away a little, steps back, reassesses what matters, and chips again.

Each round of retraining re-ranks which weights look important given everything the network has learned so far, so the pruning decision made in round five is informed by four earlier rounds of learning rather than by the raw magnitudes of an untrained network.

## Mechanics {#mechanics}

Both strategies examined in the appendix share the same outer loop of training, pruning, and re-masking; they differ only in where the weight values come from when retraining resumes after each cut [§sec_9].

```algorithm
title: Strategy 1 — iterative pruning with resetting
lines:
  - code: "θ = θ0; m = 1^|θ|"
    intent: "Start from the full network at its original random initialization [§sec_9]"
  - code: "for round in rounds:"
    intent: "Repeat the cut-and-retrain cycle instead of pruning to the target sparsity in one step [§sec_9]"
  - code: "    train f(x; m ⊙ θ) for j iterations"
    intent: "Retrain the current subnetwork so weight magnitudes reflect what this pruned structure has actually learned [§sec_9]"
  - code: "    prune s% of remaining weights, updating m → m'"
    intent: "Remove the lowest-magnitude survivors, shrinking the surviving fraction by s percentage points this round [§sec_9]"
  - code: "    θ = θ0; m = m'"
    intent: "Reset the surviving weights to their original values before the next round retrains them [§sec_9]"
```

Strategy 2 follows the identical outer loop but skips the reset: it retrains from the weights the previous round already learned, only rewinding to $\theta_0$ once after the final prune [§sec_9].

| Strategy | Retrain source after each prune | Empirical result on Lenet and Conv-2/4/6 |
|---|---|---|
| 1: Resetting | Original initialization $\theta_0$ [§sec_9] | Higher validation accuracy and faster early-stopping at smaller sizes [§sec_9] |
| 2: Continued training | Weights already trained in the previous round [§sec_9] | Lower validation accuracy and slower early-stopping at the same sizes [§sec_9] |

```figure
id: fig_9
caption: Early-stopping iteration and accuracy for Lenet under the two iterative strategies — Strategy 1's curve stays above Strategy 2's at every sparsity level shown [§sec_9]
```

In both strategies, once the network has been pruned to its target sparsity, the surviving weights are reset to $\theta_0$ one final time before the ticket is evaluated — this last reset is what makes the result a claim about the original initialization, not about the training run that found the mask [§sec_9].

## The Math {#the-math}

IMP's tunable knob is the per-round pruning rate $s\%$: the fraction of currently-surviving weights cut before the next retraining pass [§sec_9].

A common choice removes 20% of the surviving weights each round, so the fraction of the original network still present after $n$ rounds decays geometrically as $(1-s)^n = (0.8)^n$ [S1].

- Round 1: $(0.8)^1 = 80\%$ of weights remain [S1]
- Round 2: $(0.8)^2 = 64\%$ of weights remain [S1]
- Round 3: $(0.8)^3 \approx 51.2\%$ of weights remain [S1]
- Round 4: $(0.8)^4 \approx 41.0\%$ of weights remain [S1]
- Round 5: $(0.8)^5 \approx 32.8\%$ of weights remain [S1]

Only a handful of rounds are needed before the sparsest reliably-trainable ticket is reached; performance collapses once too much has been removed for the remaining sparse subnetwork to train at all [S1].

A one-shot schedule can reach that same 32.8% remaining in a single cut: prune about 67% of weights immediately, instead of removing 20% five times with four retraining passes in between [S1].

The two schedules differ in what informs the cut, not in where they end up. Iterative pruning's round-five magnitudes reflect four earlier rounds of learning on the already-shrunk network [S1].

One-shot pruning has no such feedback: it ranks all weights by their magnitude after a single training run, then removes 67% of them at once, so a weight that only becomes important after early rounds of retraining gets cut before that signal exists [S1].

Frankle and Carbin report that this collateral damage is exactly what separates the two schedules empirically: one-shot pruning at high sparsity degrades accuracy, while the iterative schedule with the same number of surviving weights keeps finding a trainable, better-performing ticket [S1].

## Go Deeper {#go-deeper}

- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask](https://www.uber.com/blog/deconstructing-lottery-tickets/) — animated figures showing how a weight's sign and mask status evolve across successive pruning rounds, the fastest way to build intuition for what "re-ranking" looks like round to round.
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the original paper defining Strategy 1 and Strategy 2 and comparing them directly (Appendix, Figures 9–10).
- [OpenLTH: A Framework for Lottery Ticket Style Experiments](https://github.com/facebookresearch/open_lth) — Frankle's own codebase implementing the prune-retrain-rewind loop end to end, useful for seeing the algorithm above as running code.

# Fully-Connected LeNet/MNIST Experiments

## TL;DR {#tldr}
Pruning LeNet-300-100 on MNIST to about a fifth of its weights, then resetting survivors to their original initial values, yields a subnetwork that trains faster and reaches higher test accuracy than the full network [§sec_2].

Randomly reinitializing the same pruned mask erases this advantage: the ticket needs its original initialization, not just its sparse structure, to win [§sec_2].

## Intuition {#intuition}
Think of the dense network as a lottery pool and pruning as picking a ticket: most connections are duplicates or noise, but a lucky few, paired with the initial values they started from, already sit close to a good solution.

Removing the losing connections and keeping only that lucky subset should make training slower, not faster — the fact that it doesn't is the paper's central surprise [§sec_2].

## Mechanics {#mechanics}
**Architecture and pruning rule:** LeNet-300-100 is a fully-connected network trained on MNIST [§sec_2].

Pruning removes the lowest-magnitude weights within each layer, layer by layer, and the output layer is pruned at half the rate of the rest of the network [§sec_2].

Sparsity is written $P_m$, the fraction of original weights the surviving mask keeps; smaller $P_m$ means more aggressive pruning [§sec_2].

The paper compares two pruning schedules: iterative pruning, which repeats prune-then-retrain in rounds of 20% per round, and one-shot pruning, which prunes to a target sparsity in a single pass [§sec_2].

| Condition | $P_m$ | Early-stopping iteration | Test accuracy |
|---|---|---|---|
| Original (unpruned) | 100% | baseline | baseline [§sec_2] |
| Winning ticket, fastest | 21.1% | 38% earlier than original | higher than original [§sec_2] |
| Winning ticket, peak accuracy | 13.5% | faster than original | +0.3 pp over original [§sec_2] |
| Winning ticket, regressed | 3.6% | back to original's pace | back to original's level [§sec_2] |
| Winning ticket at iteration 50,000 | ~21% | — | up to +0.35 pp despite ~100% train accuracy [§sec_2] |
| Random reinit, same mask | 21.1% | 2.51x slower than winning ticket | 0.5 pp less accurate than winning ticket [§sec_2] |

At early stopping the training-accuracy pattern tracks test accuracy, so pruning alone looked like better optimization rather than better generalization [§sec_2].

The iteration-50,000 comparison rules that out: training accuracy is already near 100% for almost every network, so the leftover test-accuracy gap has to come from a smaller train/test gap — genuine generalization, not just faster fitting [§sec_2].

Random reinitialization isolates what the mask alone contributes: keep the same sparse structure but redraw the surviving weights from the original distribution instead of resetting them to their original values [§sec_2].

Reinitialized tickets learn increasingly slower and lose accuracy after only modest pruning, unlike winning tickets, which keep improving down to single-digit $P_m$ — the mask is not sufficient without its paired initialization [§sec_2].

One-shot pruning — a single prune-to-target pass instead of repeated rounds — also finds winning tickets: early stopping is faster than the original for $67.5\% \geq P_m \geq 17.6\%$, and test accuracy is higher for $95.0\% \geq P_m \geq 5.17\%$ [§sec_2].

Iterative pruning still wins at smaller network sizes, reaching higher accuracy and faster early stopping than one-shot pruning finds at the same sparsity — the reason later experiments in the paper default to iterative pruning [§sec_2].

The network architectures compared across the paper — including LeNet-300-100 — are laid out in a reference figure; no image is available here, but the text describes LeNet as fully-connected with Gaussian Glorot initialization [fig_2].

```figure
id: fig_3
caption: The learning-speed and accuracy pattern this page describes: winning tickets pruned to around a fifth of their weights outpace the original network, and further pruning erodes that advantage [§sec_2]
```

```figure
id: fig_4
caption: Early-stopping iteration and test accuracy side by side across pruning levels and methods, showing where iterative pruning's advantage peaks and where it gives it back [§sec_2]
```

## The Math {#the-math}
$$P_m = \frac{\lVert m \rVert_0}{|\theta|}$$
[§sec_2]

This is the fraction of original weights the mask $m$ keeps out of the total count $|\theta|$ [§sec_2].

A concrete case: if a layer starts with 1,000 weights and pruning removes 750 of them, 250 survive, so $P_m = 250/1000 = 25\%$ — the paper's own example [§sec_2].

Worked comparison at the fastest winning ticket, $P_m = 21.1\%$: it reaches minimum validation loss 2.51x faster than the same mask with randomly reinitialized weights, and scores half a percentage point higher in test accuracy [§sec_2].

2.51x is a ratio, not an absolute count: for every iteration the winning ticket needs to reach minimum validation loss, the reinitialized network needs about 2.51 — the paper does not report the raw iteration counts here, only this ratio [§sec_2].

At $P_m = 3.6\%$, both the early-stopping speedup and the accuracy gain vanish: the winning ticket regresses to the original network's pace and accuracy, marking where too much pruning removes the structure the ticket needs [§sec_2].

The reinitialized control's accuracy drops off already at $P_m = 21.1\%$, while the same-mask winning ticket holds up until $P_m = 2.9\%$ — the paired initialization delays the collapse far longer than the mask alone would [§sec_2].

## Go Deeper {#go-deeper}
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635v5) — the original paper, with the exact FC LeNet-300-100 MNIST pruning experiments and the random-reinit control described above. Start here if anything above needs the full derivation.
- [google-research/lottery-ticket-hypothesis](https://github.com/google-research/lottery-ticket-hypothesis) — the official code release; run it to reproduce the sparsity-vs-accuracy curves yourself.
- [Stabilizing the Lottery Ticket Hypothesis](https://arxiv.org/abs/1903.01611v3) — shows this FC/MNIST result is comparatively easy to reproduce, and explains why deeper convolutional networks needed "rewinding" to find stable winning tickets.
- [Papers with Code: The Lottery Ticket Hypothesis](https://paperswithcode.com/paper/the-lottery-ticket-hypothesis-finding-sparse) — aggregates reported sparsity-vs-accuracy numbers so you can see the effect plotted without rerunning anything.

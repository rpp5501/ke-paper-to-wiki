# Convolutional CIFAR10 Experiments

## TL;DR {#tldr}
Conv-2, Conv-4, and Conv-6 — scaled-down VGG-style networks — extend the lottery ticket search from LeNet on MNIST to CIFAR10.

Pruned to roughly 9–15% of original weights, winning tickets learn 2.5–3.5x faster and beat the unpruned network's test accuracy by 3.3–3.5 percentage points.

## Intuition {#intuition}
On [[fc-lenet-mnist-experiments|LeNet/MNIST]], a winning ticket was a small, sparse subnetwork that trained as fast or faster than the full dense network once reset to its original initialization. This experiment asks whether that pattern survives when the network is convolutional and the task is harder.

Conv-2/4/6 form a ladder of increasing convolutional depth, from Conv-2 (under 1% of parameters in conv layers) to Conv-6 (nearly two-thirds). Moving up that ladder tests whether winning tickets are a fluke of small, dense networks or a property that holds as architectures grow more convolutional.

The headline finding repeats and sharpens: pruned networks don't just match the original, they learn faster and generalize better, and this holds even after adding dropout — a second, unrelated regularizer already known to implicitly train an ensemble of subnetworks.

Where the pattern breaks is the next step up in scale: pushing to full-depth [[vgg-resnet-cifar10-experiments|VGG-19 and ResNet-18]], the same reset-to-init procedure stops reliably finding winning tickets, which is why this concept sits below that one as a foundation rather than its final word.

## Mechanics {#mechanics}
Conv-2, Conv-4, and Conv-6 are scaled-down variants of the VGG family: two, four, or six convolutional layers followed by two fully-connected layers, with max-pooling after every pair of convolutional layers [§sec_3].

They span a deliberate range of convolutional-ness — under 1% of parameters sit in convolutional layers for Conv-2, versus nearly two-thirds for Conv-6 — so the experiment can check whether the effect depends on how convolutional the network is [§sec_3].

**Best-case speedup and accuracy gain, by network:** each network's fastest early-stopping time and its largest test-accuracy improvement occur at different pruning levels, both measured against the unpruned original [§sec_3].

| Network | Best early-stop speedup | $P_m$ at that speedup | Best test-accuracy gain | $P_m$ at that gain |
|---|---|---|---|---|
| Conv-2 | 3.5x | 8.8% | +3.4 pp | 4.6% [§sec_3] |
| Conv-4 | 3.5x | 9.2% | +3.5 pp | 11.1% [§sec_3] |
| Conv-6 | 2.5x | 15.1% | +3.3 pp | 26.4% [§sec_3] |

All three networks stay above their original average test accuracy for every pruning level once $P_m > 2\%$, so the table's gains are not isolated best-case points [§sec_3].

**The generalization gap shrinks, not just the headline accuracy:** at the iteration where the original dense network finishes training — 20,000 for Conv-2, 25,000 for Conv-4, 30,000 for Conv-6 — winning tickets with $P_m \geq 2\%$ reach 100% training accuracy while still holding higher test accuracy than the original [§sec_3].

That combination — perfect training accuracy plus a test-accuracy edge — means the gap between train and test performance is smaller for the pruned network, evidence it generalizes better rather than merely fitting faster [§sec_3].

**Random reinitialization breaks the ticket, but more slowly than expected:** repeating the reinitialization control from the LeNet experiment, randomly reinitialized subnetworks at the same sparsity take longer to learn and lose test accuracy faster as pruning continues, matching the earlier pattern [§sec_3].

Unlike LeNet, though, early-stopping test accuracy for reinitialized Conv-2 and Conv-4 stays flat or even improves at moderate pruning, suggesting the winning ticket's structure alone — separate from its specific initial weights — carries some of the benefit [§sec_3].

**Dropout and iterative pruning compound rather than conflict:** training Conv-2/4/6 with a dropout rate of 0.5 raises initial test accuracy over the no-dropout baseline, and iterative pruning on top of dropout raises it further still, for every network tested [§sec_3].

The two effects are additive and separable: dropout alone accounts for one gain, pruning on top of dropout accounts for a second, larger one [§sec_3].

| Network | Dropout-only gain (avg) | Further gain from pruning (avg, up to) |
|---|---|---|
| Conv-2 | +2.1 pp | +2.3 pp [§sec_3] |
| Conv-4 | +3.0 pp | +4.6 pp [§sec_3] |
| Conv-6 | +2.4 pp | +4.7 pp [§sec_3] |

```figure
id: fig_5
caption: Early-stopping iteration and accuracy for Conv-2/4/6, iteratively pruned (solid) versus randomly reinitialized (dashed) — the bottom-right panel is the same-iteration comparison behind the generalization-gap claim [§sec_3]
```

```figure
id: fig_6
caption: The same iterative-pruning curves repeated with a dropout rate of 0.5 (dashed lines show the no-dropout baseline), behind the additive dropout-plus-pruning gains above [§sec_3]
```

**The result does not survive unmodified at VGG/ResNet depth:** pushing this same procedure — prune, reset to iteration 0, retrain — to full VGG-19 and ResNet-18 on CIFAR10 no longer reliably finds winning tickets, a failure that grows with network depth and complexity [S1].

Later work fixes this by resetting weights to an early-training checkpoint instead of iteration 0, plus a short learning-rate warm-up, which stabilizes winning-ticket discovery at that larger scale [S3].

**Layers are not pruned uniformly:** wider fully-connected layers tolerate much higher sparsity before accuracy collapses than earlier convolutional layers, a difference that motivates pruning by a global ratio across all layers rather than the same per-layer rate everywhere, the question explored directly in [[hyperparameter-search-conv|hyperparameter search]] [S1].

## The Math {#the-math}
**Turning the reported percentages into fractions of training time:** a 3.5x early-stopping speedup means the winning ticket reaches minimum validation loss in about $1/3.5 \approx 29\%$ of the iterations the original dense network needed — true for both Conv-2 and Conv-4, though at different pruning levels ($P_m = 8.8\%$ and $9.2\%$) [§sec_3].

Conv-6's smaller 2.5x speedup ($1/2.5 = 40\%$ of original iterations) shows up at a higher $P_m = 15.1\%$, consistent with the more convolutional network needing to keep more weights before it shows the same relative speed-up [§sec_3].

The accuracy gains — +3.4, +3.5, +3.3 percentage points for Conv-2/4/6 — are nearly identical in absolute size across all three networks [§sec_3].

They occur at very different pruning levels, though: $P_m = 4.6\%$, $11.1\%$, and $26.4\%$ respectively [§sec_3].

That gap shows the sparsity budget a network can absorb before losing its accuracy edge grows with depth, even though the size of the edge itself does not [§sec_3].

Dropout's contribution decomposes into two additive pieces: an initial-accuracy gain from dropout alone (+2.1, +3.0, +2.4 pp for Conv-2/4/6) and a further gain from pruning on top of it (up to +2.3, +4.6, +4.7 pp) [§sec_3].

Summed, the largest combined improvement over the no-dropout, unpruned baseline reaches roughly +4.4 pp for Conv-2, +7.6 pp for Conv-4, and +7.1 pp for Conv-6 — larger than either regularizer's contribution alone [§sec_3].

## Go Deeper {#go-deeper}
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the source paper; Figure 4 has the Conv-2/4/6 accuracy-vs-remaining-weights curves with and without dropout, Figure 7 has the VGG-19/ResNet-18 results and the late-resetting comparison.
- [google-research/lottery-ticket-hypothesis](https://github.com/google-research/lottery-ticket-hypothesis) — the official TensorFlow implementation that produced these Conv-2/4/6 and VGG/ResNet CIFAR10 results, for readers who want to run the actual pruning loop.
- [Stabilizing the Lottery Ticket Hypothesis](https://arxiv.org/abs/1903.01611) — explains and fixes the VGG/ResNet-on-CIFAR10 failure case this page's Mechanics section leaves open, via late resetting and learning-rate warm-up.

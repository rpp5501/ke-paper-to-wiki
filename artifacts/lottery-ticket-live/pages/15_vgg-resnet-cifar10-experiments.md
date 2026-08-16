# VGG/ResNet CIFAR-10 Experiments

## TL;DR {#tldr}

Winning tickets exist for VGG-19 and ResNet-18 on CIFAR-10, but finding them takes two changes from the smaller experiments: pruning must be global across all convolutional layers, and training must use a lower learning rate or the original rate with linear warmup — plain iterative pruning at the standard learning rate fails outright.

## Intuition {#intuition}

Lenet and Conv-2/4/6 are small enough that pruning every layer at the same rate works, and matching the original accuracy is enough to call a subnetwork a winning ticket.

VGG-19 and ResNet-18 are much deeper, trained with batchnorm, weight decay, and augmented data — a harsher test of whether the lottery ticket pattern holds up in practice.

Two things break at this scale. Pruning every layer at the same rate starves small layers long before large ones feel it, so pruning has to be global instead. And the learning rate itself becomes load-bearing: pruning only finds winning tickets at a lower rate, or at the original rate cushioned by a warmup ramp.

## Mechanics {#mechanics}

VGG-19 and ResNet-18 add batchnorm, weight decay, learning-rate schedules, and data augmentation on top of the plain training used for Lenet and Conv-2/4/6, testing whether winning tickets survive a training recipe closer to practice. [§sec_4]

VGG-19 is a 20-million-parameter CIFAR-10 network trained for 160 epochs (112,480 iterations) with SGD, momentum 0.9, and the learning rate cut 10x at epochs 80 and 120. [§sec_4]

ResNet-18 has 271,000 parameters and trains for 30,000 iterations with the same momentum, cutting the learning rate 10x at 20,000 and 25,000 iterations. [§sec_4]

For these deeper networks, pruning switches from a fixed rate per layer to global pruning: weights are ranked and removed by magnitude across all convolutional layers at once, rather than layer by layer. [§sec_4]

| VGG-19 layer | Parameters |
|---|---|
| First convolutional layer | 1,728 [§sec_4] |
| Second convolutional layer | 36,864 [§sec_4] |
| Largest convolutional layer | ≈2.35 million [§sec_4] |

Pruning every layer at the same rate makes the 1,728-parameter layer hit a given sparsity target at the same pace as the 2.35-million-parameter layer, so the small layer becomes a bottleneck: most of its weights are gone before the large layer has lost much at all. [§sec_4]

Global pruning avoids this by letting large layers absorb most of the removed weights, and it finds smaller winning tickets for both VGG-19 and ResNet-18 than layer-wise pruning does. [§sec_4]

Iterative pruning is sensitive to learning rate at this depth: at VGG-19's original rate of 0.1, pruning never finds winning tickets, and pruned subnetworks perform no better than randomly reinitialized ones. [§sec_4]

At a lower learning rate, 0.01, the usual pattern reappears: VGG-19 subnetworks stay within one percentage point of the original accuracy while $P_m \geq 3.5\%$ of weights remain. [§sec_4]

These are not true winning tickets, since they fall short of the original accuracy rather than matching or exceeding it, but they clearly beat random reinitialization at the same sparsity. [§sec_4]

ResNet-18 shows the same pattern: iterative pruning finds winning tickets at learning rate 0.01 but not at the original rate of 0.1. [§sec_4]

At the lower learning rate, pruned subnetworks learn faster than the unpruned network early in training, but this lead erodes later because of the lower initial rate — though they still outlearn random reinitialization throughout. [§sec_4]

```figure
id: fig_7
caption: VGG-19 accuracy at 30K, 60K, and 112K iterations — the early lead of pruned subnetworks at the lower learning rate narrows by the final checkpoint [§sec_4]
```

ResNet-18 shows the same early-late pattern: the winning ticket at the lower learning rate leads early, then falls behind the unpruned network's higher-learning-rate accuracy later in training. [§sec_4]

```figure
id: fig_8
caption: ResNet-18 accuracy at 10K, 20K, and 30K iterations — pruned subnetworks lead early, then the unpruned network at higher learning rate catches up [§sec_4]
```

Linear learning-rate warmup ramps the rate from 0 up to its target value over $k$ iterations before training proceeds normally, letting both networks train at their original, higher learning rate while still producing winning tickets. [§sec_4]

For VGG-19, warmup with $k=10000$ at learning rate 0.1 raises the unpruned network's accuracy by about one percentage point over the same setup without warmup. [§sec_4]

With that warmup in place, iterative pruning exceeds this improved baseline for $P_m \geq 1.5\%$, so warmup is what makes winning tickets reachable at the original learning rate. [§sec_4]

For ResNet-18, warmup with $k=20000$ at learning rate 0.03 reaches 90.5% test accuracy at $P_m = 27.1\%$, matching the unpruned network's accuracy at the original higher learning rate. [§sec_4]

Winning tickets persist down to $P_m \geq 11.8\%$ under this schedule, though no tested hyperparameters recover winning tickets at the original learning rate of 0.1 itself. [§sec_4]

## The Math {#the-math}

VGG-19's layer-size disparity, spelled out: the first two convolutional layers hold 1,728 and 36,864 parameters, while the largest holds roughly 2.35 million — a ratio of about 1,360 to 1. [§sec_4]

A uniform per-layer pruning rate forces the 1,728-parameter layer through the same percentage cut as the 2.35-million-parameter layer, so a sparsity target that barely dents the largest layer can strip the smallest one almost bare. [§sec_4]

| Regime | Learning rate | Best accuracy | Winning-ticket sparsity |
|---|---|---|---|
| Original training | 0.1 | 90.5% (unpruned) | none found [§sec_4] |
| Lower learning rate | 0.01 | 89.5% | $41.7\% \geq P_m \geq 21.9\%$ [§sec_4] |
| Warmup ($k=20000$) | 0.03 | 90.5% at $P_m=27.1\%$ | down to $P_m \geq 11.8\%$ [§sec_4] |

Without warmup, the best winning ticket (89.5% at learning rate 0.01) falls 1.0 percentage point short of the original network's accuracy at the higher rate (90.5%) — exactly the gap warmup closes. [§sec_4]

Warmup also widens the sparsity range: winning tickets survive down to $P_m \geq 11.8\%$ with warmup versus $P_m \geq 21.9\%$ without, roughly $21.9/11.8 \approx 1.9\times$ sparser. [§sec_4]

VGG-19 shows the same widening: winning-ticket-like subnetworks appear down to $P_m \geq 3.5\%$ at the lower learning rate but down to $P_m \geq 1.5\%$ with warmup, roughly $3.5/1.5 \approx 2.3\times$ sparser. [§sec_4]

## Go Deeper {#go-deeper}

- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635v5) — the source of these VGG-19/ResNet-18 experiments; read it for the actual warmup and global-vs-layer-wise pruning plots this page describes numerically.
- [Stabilizing the Lottery Ticket Hypothesis](https://arxiv.org/abs/1903.01611v3) — shows that rewinding weights to iteration $k$ ("late resetting") instead of iteration 0 removes the need for learning-rate warmup, addressing why VGG-19/ResNet-18 needed it in the first place.
- [Linear Mode Connectivity and the Lottery Ticket Hypothesis](https://arxiv.org/abs/1912.05671v4) — explains why late-reset tickets stay trainable at this depth: they are linearly mode connected across independent SGD runs, unlike iteration-0 tickets.

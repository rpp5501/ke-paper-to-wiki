# Random Reinitialization Control

## TL;DR {#tldr}
- The random reinitialization control keeps the winning-ticket mask but replaces the surviving weights with fresh random values before retraining.
- It isolates whether a winning ticket's advantage comes from *which* weights survive pruning or from their *specific initial values*.
- Reinitialized networks train slower and end up less accurate than the true winning ticket, and the gap grows as the network gets sparser.

## Intuition {#intuition}
A winning ticket is a sparse subnetwork plus a specific set of starting weight values that together train as fast and as accurately as the full dense network. The random reinitialization control asks a narrower question: does the sparse connectivity pattern alone carry that advantage, or do the original weight values matter too?

To find out, the same mask is kept but the surviving weights are redrawn at random before retraining. If accuracy held up, sparsity would be doing all the work; since it degrades instead, the specific initialization pruning uncovered is doing part of the work too.

## Mechanics {#mechanics}
Frankle & Carbin's iterative magnitude pruning produces two things: a mask marking which weights survive, and a record of each surviving weight's value at initialization. The winning ticket resets survivors to that original value before retraining [S1].

The random reinitialization control changes only one input: it keeps the same mask but draws new random values for the surviving weights, using the same initialization distribution as the original network [S1].

```algorithm
title: Random reinitialization control
lines:
  - code: "mask = iterative_magnitude_pruning(net)"
    intent: "Iterative pruning finds which weights survive at the target sparsity level [§sec_12]"
  - code: "reinit_weights = sample(init_distribution)"
    intent: "Surviving weights get fresh random values instead of the ones logged at the original initialization [S1]"
  - code: "reinit_net = apply(mask, reinit_weights)"
    intent: "The sparse structure is identical to the winning ticket; only the weight values differ [S1]"
  - code: "retrain(reinit_net)"
    intent: "Training under the same schedule as the winning ticket isolates the effect of initial weight values from the effect of the mask [S1]"
```

Figure [fig_14] plots three networks against each other at every pruning level: the winning ticket, which resets survivors to their original values; the reinitialization control, which keeps the same mask but redraws survivor values at random; and a random sparse network, which uses a freshly random mask at matching parameter count [§sec_12].

```figure
id: fig_14
caption: The reinitialization control (orange) sits between the winning ticket (blue) and random sparsity (green) at every pruning level [§sec_12]
```

| Network | Mask | Weight values | Tests |
|---|---|---|---|
| Winning ticket | Found by iterative pruning | Original initialization | Baseline performance [§sec_12] |
| Reinit control | Same as winning ticket | Fresh random draw | Whether original values matter [S1] |
| Random sparse | Random, same parameter count | Fresh random draw | Whether the mask alone matters [§sec_12] |

Two independent factors are in play: which mask is used, and which weight values fill it. The reinit control changes only the weight values while holding the mask fixed [S1].

Any performance gap between the winning ticket and the reinit control must then come from the weight values, not the mask. This separates two hypotheses a single ticket-versus-random-sparsity comparison cannot: does sparsity help, or do the specific pruning-discovered values help, or both [S1]?

For the fully-connected LeNet on MNIST, the reinitialized network still beats random sparsity by a clear margin. For every convolutional architecture in the paper — VGG and ResNet on CIFAR-10 — the two are statistically indistinguishable [§sec_12].

The authors attribute this split to how information is distributed in the input. MNIST digits concentrate useful signal in specific pixel regions, so a fully-connected network's connections vary in value and pruning can find better ones to keep. Convolutional filters slide over the whole image, so no filter position is privileged the same way [§sec_12].

## The Math {#the-math}
The three-way comparison isolates two independent variables rather than one. Random sparsity changes the mask while randomizing weights; the reinit control holds the mask fixed while randomizing weights. Comparing the winning ticket against the reinit control is the one pairing that holds the mask constant, so it isolates weight values as a cause [§sec_12].

The gap between the winning ticket and the reinit control is small at low sparsity and widens as more weights are pruned [S1].

At mild sparsity, enough redundant good initializations exist for a random draw to land near one; at extreme sparsity, only a handful of surviving weights carry the signal, so their specific starting values matter far more [S1].

The condition that separates the two controls is architecture, not sparsity level: on fully-connected LeNet, the reinit control still beats random sparsity, but on every convolutional network tested it does not [§sec_12].

The authors' explanation is that fully-connected layers let pruning concentrate on the input pixels that actually carry class information, so which mask is kept matters even after reinitialization; convolution shares weights across every spatial position, erasing that advantage [§sec_12].

## Go Deeper {#go-deeper}
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the original source; Figure 4 directly plots the reinitialized-network curves against the true winning ticket, so start here to see the comparison this page describes.
- [open_lth](https://github.com/facebookresearch/open_lth) — Frankle's own codebase implementing the exact iterative-pruning-plus-reinit-control pipeline, useful if you want to reproduce or extend the experiment.
- [Linear Mode Connectivity and the Lottery Ticket Hypothesis](https://arxiv.org/abs/1912.05671) — extends the reinit-control logic into an instability analysis across random seeds, explaining why tickets found early versus late in training behave differently.

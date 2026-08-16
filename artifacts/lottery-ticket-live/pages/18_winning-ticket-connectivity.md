# Winning Ticket Connectivity

## TL;DR {#tldr}
- A winning ticket's mask ([[Winning Ticket]]) is not spread evenly at the level of individual connections, even though whole layers prune at a fixed rate.
- Incoming connectivity per unit tracks the layer's overall pruning rate closely, for both Adam- and SGD-trained networks.
- Outgoing connectivity is uneven: a minority of units become connectivity hubs that keep far more outgoing connections than their neighbors, most visibly in the input layer.

## Intuition {#intuition}
A winning ticket ([[Winning Ticket]]) is a sparse subnetwork that trains as well as the dense network it came from. This page asks whether the mask that defines it treats every unit the same way, or whether a handful of units end up doing most of the work.

The original lottery ticket paper's own connectivity study finds that pruning does not treat every unit alike: a subset of units in each layer keeps disproportionately more connections than the rest, acting as connectivity hubs [S1]. Mechanics below pins down exactly which kind of connection this hub effect shows up in.

Zhou et al.'s follow-up sign-and-magnitude analysis suggests these surviving units are not hubs by chance: the units that keep the most connections also tend to have a sign pattern that already encodes useful structure on its own [S2].

Neither paper tests whether hub formation is what makes winning tickets train fast — the paper's headline speed and accuracy results are reported separately from this connectivity analysis [§sec_13_6].

## Mechanics {#mechanics}
The section asks a direct question: does pruning concentrate on a few hidden units and leave others untouched, or does it spread evenly across all units in a layer? [§sec_13_6]

For incoming connections the answer is even spreading: in both Adam- and SGD-trained networks, each unit's fraction of surviving incoming connections tracks the pruning rate applied to its whole layer, rather than diverging unit by unit [§sec_13_6].

```figure
id: fig_21
caption: Incoming-connection survival by node, layer by layer, for the Adam-trained network — note how flat this is compared to the outgoing plot below [§sec_13_6]
```

```figure
id: fig_22
caption: The same incoming-connection plot for the SGD-trained network, showing the same even spread [§sec_13_6]
```

The output layer looks better connected than the rest only because it is pruned at half the rate applied elsewhere in the network, not because its units are treated specially [§sec_13_6].

Outgoing connections behave differently: in the Adam-trained network, some units keep far more outgoing connections than others, and the resulting per-node distributions are far less smooth than the incoming-connection distributions [§sec_13_6].

This unevenness suggests that some features matter more to the network than others, which is unsurprising for a fully connected network trained on centered MNIST digits [§sec_13_6].

Edge pixels in an MNIST image carry little information, so input-layer units near the edges have less reason to keep as many outgoing connections as units nearer the center [§sec_13_6].

The input layer's outgoing-connectivity distribution has two peaks: a larger peak of units that keep a high fraction of outgoing connections, and a smaller peak of units that keep very few [§sec_13_6].

```figure
id: fig_23
caption: Outgoing-connection survival by node for the Adam-trained network — the input layer's two peaks are the hub effect described above [§sec_13_6]
```

Adam-trained winning tickets develop a more uneven outgoing-connectivity distribution for the input layer than SGD-trained tickets do, meaning Adam concentrates outgoing connections onto fewer hub units [§sec_13_6].

```figure
id: fig_24
caption: The same outgoing-connection plot for SGD, flatter for the input layer than the Adam version above [§sec_13_6]
```

## The Math {#the-math}
Suppose a hidden layer keeps 20% of its weights after a pruning round, a typical per-round survival rate in iterative magnitude pruning. Incoming degree tracks that layer-wide rate rather than varying unit by unit [§sec_13_6].

A unit that started with 300 incoming connections keeps close to 60 after that round, and a neighboring unit that also started with 300 keeps a similarly close number — not one keeping 200 while another keeps 5 [§sec_13_6].

Outgoing connections break this pattern: two units in the same layer, at the same 20% survival rate, can land far apart. A hub unit keeps well above 60 outgoing connections while another keeps close to zero, because outgoing survival tracks which features the network finds useful, not the layer-wide rate [§sec_13_6].

The input layer's two peaks are the aggregate signature of this same split: most units cluster near the layer's average outgoing-survival rate, forming the larger peak [§sec_13_6].

A minority cluster near zero, forming the smaller peak, and the gap between the two clusters marks the boundary the network draws between informative center pixels and uninformative edge pixels [§sec_13_6].

## Go Deeper {#go-deeper}
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the source of the per-unit connectivity analysis and figures discussed on this page; start here to see the original incoming/outgoing plots.
- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask](https://arxiv.org/abs/1905.01067) — digs into why some units become hubs, via sign and magnitude analysis of the surviving weights.
- [google-research/lottery-ticket-hypothesis](https://github.com/google-research/lottery-ticket-hypothesis) — official code to reproduce Lenet-MNIST winning tickets and compute your own per-layer connectivity statistics.

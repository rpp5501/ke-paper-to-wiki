# Winning Ticket Initialization Distribution
## TL;DR {#tldr}
- At $P_m=100\%$ (no pruning), the surviving initializations exactly match the glorot distribution for each layer [§sec_13_1].
- As pruning tightens, the second hidden layer and output layer become bimodal, with survivors pushed away from 0 [§sec_13_1].
- The two bimodal peaks lean in opposite directions across those two layers [§sec_13_1].
- The input layer's distribution barely changes with pruning, unlike the two deeper layers [§sec_13_1].

## Intuition {#intuition}
Tag every connection with the random value it started at. Winning-ticket pruning keeps the highest-magnitude final weights in each layer, then asks what the survivors' tags looked like before training even began [§sec_13_1].

For the second hidden layer and the output layer, survivors mostly started far from zero — pruning by final magnitude is picking out connections whose initial magnitude already predicted their eventual strength [§sec_13_1].

The input layer breaks this pattern: it keeps its original glorot shape under pruning, so initialization there says little about which connections end up strong [§sec_13_1].

## Mechanics {#mechanics}
Winning tickets are produced by pruning, within each layer, the connections with the lowest-magnitude weights at the end of training. Figure 15 asks what the initializations of the surviving connections looked like before that training even started [§sec_13_1].

At $P_m=100\%$ (the leftmost plot, unpruned) the three per-layer curves match the network's glorot initialization exactly, since glorot assigns each layer its own standard deviation and no connections have yet been removed [§sec_13_1].

As $P_m$ shrinks (more pruning, moving rightward across the panels), the first hidden layer's blue curve keeps roughly the same shape it had at $P_m=100\%$ [§sec_13_1].

The second hidden layer (orange) and output layer (green) instead grow two humps straddling 0, and the humps grow taller and further apart the more aggressively the layer is pruned [§sec_13_1].

The two layers' humps lean opposite ways: the second hidden layer keeps more positive-initialized survivors than negative ones, while the output layer keeps more negative-initialized survivors than positive ones [§sec_13_1].

```figure
id: fig_15
caption: How the surviving connections' initializations spread out as pruning tightens, layer by layer [§sec_13_1]
```

Because pruning removes the lowest-magnitude final weights layer by layer, a bimodal survivor-initialization curve means initial magnitude and final magnitude are correlated in that layer; a flat, unchanged curve means they are not [§sec_13_1].

## The Math {#the-math}
Take the two extremes the figure spans. At $P_m=100\%$ nothing has been pruned, so the "surviving" set is the whole layer, and its initialization curve is just the glorot curve itself, layer by layer [§sec_13_1].

At the most-pruned $P_m$ shown, only the highest-final-magnitude connections in each layer remain. If a layer's initial and final magnitudes were uncorrelated, that surviving subset would be a random sample of the glorot curve, so the shape would stay glorot-like at every $P_m$ [§sec_13_1].

That is exactly the pattern the input layer shows, which is why the text reads its initialization as having little relation to its final weight [§sec_13_1].

The second hidden layer and output layer instead depart from glorot as $P_m$ drops, which is only possible if initial magnitude is informative about final magnitude in those layers, since surviving is decided purely by final magnitude [§sec_13_1].

That correlation constrains magnitude, not sign, so a symmetric relationship would still produce a symmetric bimodal curve. The observed left-right imbalance is therefore a separate fact: within each layer, one sign of initialization is more likely to end up high-magnitude than the other [§sec_13_1].

## Go Deeper {#go-deeper}
No resources were supplied for this concept.

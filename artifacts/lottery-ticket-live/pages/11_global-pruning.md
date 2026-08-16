# Global Pruning

## TL;DR {#tldr}

Global pruning ranks every convolutional weight across the whole network together and cuts a single bottom fraction, instead of cutting the same percentage out of each layer separately. On VGG-19 and Resnet-18 this finds smaller winning tickets than layer-wise pruning, because it lets parameter-poor layers keep more of their weights while parameter-rich layers absorb more of the cut [§sec_16_1].

## Intuition {#intuition}

Layer-wise pruning applies the same removal percentage to every layer on every round, so a layer that starts with very few parameters shrinks by the same proportion as a layer with millions of them.

In VGG-19 the layers vary enormously in size, and a thin layer can be pruned down to almost nothing well before the network as a whole reaches its smallest winning ticket [§sec_16_1].

Global pruning instead pools every convolutional weight into one ranked list and prunes a single fraction off the bottom of that list. A layer with few parameters is no longer required to give up the same share as a huge layer, so it is not forced to become a bottleneck [§sec_16_1].

## Mechanics {#mechanics}

On Lenet and the Conv-2/4/6 architectures, the paper prunes each layer separately at a fixed rate every round. On VGG-19 and Resnet-18, it instead pools all convolutional weights into a single collection and prunes a single fraction from that pool, without regard for which layer any weight came from [§sec_16_1].

```algorithm
title: Global pruning across convolutional layers
lines:
  - code: "pool = concatenate(weights from every conv layer)"
    intent: "Global pruning ignores layer boundaries and treats all convolutional weights as one collection to rank [§sec_16_1]"
  - code: "threshold = magnitude at percentile p in pool"
    intent: "A single percentile cutoff is computed over the whole pool rather than separately per layer [§sec_16_1]"
  - code: "mask = |pool| > threshold"
    intent: "Weights below the shared threshold are pruned regardless of which layer they came from, so a layer with few parameters is not forced to lose a fixed fraction [§sec_16_1]"
```

For VGG-19 trained at learning rate 0.1 with warmup to iteration 10,000, layer-wise pruning finds winning tickets only down to $P_m \geq 6.9\%$ of weights remaining, while global pruning keeps finding them down to $P_m \geq 1.5\%$ [§sec_16_1].

For other hyperparameter settings the same ordering holds — accuracy falls off at a higher $P_m$ under layer-wise pruning than under global pruning [§sec_16_1].

Layer-wise pruning must stop discarding weights sooner because its smallest layer hits a size floor before the whole network's overall fraction does, while global pruning lets large layers absorb more of the cut [§sec_16_1].

Global pruning also finds smaller winning tickets than layer-wise pruning for Resnet-18 [§sec_16_1].

The gap between the two schemes is less extreme for Resnet-18 than for VGG-19, and the paper does not report a specific $P_m$ threshold for Resnet-18 the way it does for VGG-19 [§sec_16_1].

The paper's own explanation is a bottleneck conjecture: the layers of these deep networks have very different parameter counts — VGG-19 especially so — and pruning every layer to the same fraction forces the smallest layers to become bottlenecks on how small the overall network can get [§sec_16_1].

Which pruning scheme is used does not change the learning-rate pattern established earlier for these networks [§sec_16_1]:

- At learning rate 0.1, iterative pruning finds no winning tickets for either network [§sec_16_1].
- At learning rate 0.01, the lottery ticket pattern reappears [§sec_16_1].
- With warmup to a higher learning rate, iterative pruning again finds winning tickets [§sec_16_1].

The layer-wise-pruning figures for VGG-19 and Resnet-18 show the same qualitative trends as their global-pruning counterparts, but every smallest winning ticket found under layer-wise pruning is larger than the smallest one global pruning finds [§sec_16_1].

## The Math {#the-math}

| Architecture (VGG-19, lr 0.1, warmup 10k) | Pruning scheme | Smallest winning-ticket $P_m$ | Weights removed at that threshold |
|---|---|---|---|
| VGG-19 | Layer-wise | ≥ 6.9% | 93.1% [§sec_16_1] |
| VGG-19 | Global | ≥ 1.5% | 98.5% [§sec_16_1] |

Global pruning's floor of 1.5% is about 4.6 times smaller than layer-wise pruning's floor of 6.9% ($6.9/1.5 \approx 4.6$), and at that boundary global pruning has removed roughly 5.4 percentage points more of the network's convolutional weights than layer-wise pruning has [§sec_16_1].

Consider a network where the smallest convolutional layer holds only 1% of all convolutional parameters. Layer-wise pruning cannot push the global fraction below roughly that layer's own floor once it has emptied out, whereas global pruning can keep removing weight from the far larger layers and push the whole-network fraction lower [§sec_16_1].

The paper reports the same direction for Resnet-18 without giving a matching pair of threshold numbers, so no equivalent ratio can be computed from the supplied evidence [§sec_16_1].

## Go Deeper {#go-deeper}

No external resource was supplied or verified for Global Pruning specifically. The full comparison this page draws on — including the matching layer-wise-pruning figures for VGG-19 and Resnet-18 — lives in the parent concept, **VGG/Resnet CIFAR10 Experiments**; start there for the complete set of graphs the paper reports [§sec_16_1].

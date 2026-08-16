# Pruning Convolutions vs. Fully-Connected Layers

## TL;DR {#tldr}
Pruning convolutional filters alone gives better accuracy and faster training than pruning fully-connected (FC) weights alone. But FC layers hold most of the parameters, so pruning convolutions alone barely shrinks the network — pruning both together is what actually compresses it while keeping most of the accuracy and speed benefit.

## Intuition {#intuition}
Think of a network's weights as two very different pools: convolutional filters that scan for local patterns, and fully-connected weights that combine those patterns into a decision.

The experiment asks two separate questions: which pool tolerates being trimmed better, and how much each pool actually weighs in the network's total parameter budget.

Those two questions have different answers. The pool that prunes best — convolutions — is often not the pool that is biggest — fully-connected layers — and that mismatch is why pruning only one layer type is a poor substitute for pruning both.

## Mechanics {#mechanics}

```figure
id: fig_37
caption: Pruning convolutions alone (green) beats pruning FC alone (orange) on accuracy and speed, but only pruning both (blue) meaningfully shrinks Conv-2, where FC holds 99% of the weights [§sec_15_6]
```

Pruning convolutional layers alone gives the best test accuracy and the fastest learning of the three settings compared, whether measured against pruning fully-connected layers alone or against pruning both together [§sec_15_6].

Pruning fully-connected layers alone has the opposite effect: test accuracy generally worsens and learning slows, a pattern that holds across Conv-2, Conv-4, and Conv-6 [§sec_15_6].

The experiment separates two questions that iterative magnitude pruning normally conflates: which layers benefit from having weights removed, and how much of the network's total parameter budget those layers actually hold [§sec_15_6].

[fig_37] plots early-stopping iteration and test accuracy against parameters remaining, so the convolutions-only and FC-only curves share an x-axis expressing the fraction of the whole network retained rather than the fraction of one layer type [§sec_15_6].

Fully-connected layers comprise 99%, 89%, and 35% of the parameters in Conv-2, Conv-4, and Conv-6 respectively, so most of each network's weight budget sits outside the convolutional layers that pruning-alone treats best [§sec_15_6].

That imbalance caps how much pruning convolutions alone can shrink the network: even removing every convolutional weight leaves the FC layers, and with them most of the parameter count, untouched [§sec_15_6].

| Network | FC share of params | Conv share of params | Evidence |
|---|---|---|---|
| Conv-2 | 99% | 1% | [§sec_15_6] |
| Conv-4 | 89% | 11% | [§sec_15_6] |
| Conv-6 | 35% | 65% | [§sec_15_6] |

Even pruning 100% of Conv-2's convolutional weights removes only about 1% of its total parameters, since convolutions hold so little of the budget there [§sec_15_6].

Pruning both layer types together is therefore needed to compress the network substantially, and it keeps most of the accuracy and speed benefit that pruning convolutions alone provides [§sec_15_6].

## The Math {#the-math}

Call $f$ the fraction of a network's parameters held by its fully-connected layers, so $1-f$ is the share held by convolutions. Pruning convolutions alone, even at full sparsity within that layer type, can remove at most $1-f$ of the network's total parameter count, since the FC weights stay untouched [§sec_15_6].

For Conv-2, $f = 0.99$, so that ceiling is 1% of the network — matching the near-flat conv-only curve in [fig_37]. For Conv-6, $f = 0.35$, so the same maneuver can remove up to 65% of the network, enough to matter for overall size and not just accuracy [§sec_15_6].

The boundary case is $f \to 0$, a network with almost no fully-connected weight. There, conv-only pruning and pruning-both would converge, since little FC budget remains to prune away [§sec_15_6].

Conv-2, Conv-4, and Conv-6 sit far from that boundary, which is why pruning both layer types stays necessary to compress them substantially even though convolutions alone win on accuracy per parameter removed [§sec_15_6].

## Go Deeper {#go-deeper}
No verified external resource was supplied for this concept. For how this pruning-type comparison fits into the broader convolutional hyperparameter sweep, see the parent concept, Hyperparameter Search (Convolutional).

# Limitations and Scope

## TL;DR {#tldr}

- The paper's claims are scoped to MNIST and CIFAR10 vision classification, magnitude-based iterative pruning, and networks shallow enough not to need warmup [§sec_6].
- Follow-up work has since tested the paper's own biggest open question — does the effect hold at ImageNet scale — and found it does, but only after the recipe itself was modified [S2][S3].

## Intuition {#intuition}

Every empirical claim in this paper holds inside a specific box: small vision datasets, one pruning method, and networks shallow enough not to need special tricks. The authors are explicit about that box's walls, listing four boundaries they have not yet tested past [§sec_6].

Nothing here implies the effect fails outside that box — only that, within this paper, nobody checked. That distinction matters: a scope limitation is a statement about what was tested, not a statement about what is true [§sec_6].

## Mechanics {#mechanics}

The paper restricts its experiments to vision classification on MNIST and CIFAR10. It does not test ImageNet, because iterative pruning requires training the network 15 or more times consecutively, and that cost repeats for every trial [§sec_6].

Magnitude pruning is the only method used to find winning tickets. The resulting sparse architectures are not optimized for current hardware or libraries, unlike structured pruning, which prunes whole units rather than individual weights and would produce hardware-friendly networks [§sec_6].

Winning tickets match the unpruned network's accuracy at sparsities where a randomly reinitialized network of the same size cannot. The paper does not explain what makes these particular initial weights, combined with the pruned architecture's inductive bias, easier to train [§sec_6].

On the deeper Resnet-18 and VGG-19 networks, iterative pruning only finds winning tickets when training uses learning-rate warmup. Without it the procedure fails outright, and the paper does not yet know why warmup is necessary [§sec_6].

Follow-up work has since resolved part of the paper's own open question about scale. A direct successor found that the plain rewind-to-initialization procedure fails to find winning tickets at ResNet-50/ImageNet scale on its own [S2].

It only succeeds once learning-rate warmup and other stabilizing changes are added — the same warmup dependency this paper already flags for ResNet-18 and VGG-19, now showing up at greater severity as depth and dataset size grow [S2].

A later paper found even those fixes break down at the largest scales, and instead rewinds weights to an early training iteration k rather than to initialization, keeping the pruned network inside a stable, linearly-connected optimization basin [S3].

Non-vision domains such as NLP and reinforcement learning were not addressed by either follow-up and remain a genuinely open extension of this paper's scope limitation [S1].

## The Math {#the-math}

**The 15x cost argument.** Iterative magnitude pruning trains a network, prunes a fraction of its weights, and retrains from the rewound initialization — repeated over 15 or more rounds to reach the sparsities the paper reports [§sec_6].

That means one full experiment costs roughly 15 times a single training run, before counting whatever multiple trials the paper runs per data point to control for variance — the total cost compounds multiplicatively, not additively, as sparsity targets increase [§sec_6].

That multiplier is exactly why the paper stops at MNIST and CIFAR10 instead of ImageNet: a cost that is merely inconvenient for a small network becomes prohibitive once each individual training run is itself large [§sec_6].

**Comparing the fixes that followed.** Each later paper changes one thing about where the rewind point sits, in response to the previous version breaking at larger scale:

| Approach | What it does | When needed / where it breaks |
|---|---|---|
| Original recipe (rewind to iteration 0) [S1] | Prune, then reset surviving weights to their original initialization | Works up to CIFAR10 / VGG-ResNet scale, only with warmup; not tested beyond |
| Warmup fix [S2] | Adds a learning-rate warmup schedule on top of rewind-to-0 | Needed to find winning tickets at ResNet-50/ImageNet scale; itself breaks down at the largest models |
| Late rewinding [S3] | Rewinds weights to an early training iteration k instead of to initialization | Keeps the pruned network in a stable, linearly-connected basin once warmup alone is no longer enough |

The dimension separating these three is how far into training the network is rewound before retraining: to iteration 0, to iteration 0 plus a warmup schedule, or to an early iteration k [S1][S2][S3].

Each fix is a response to the previous one failing at greater scale, which is itself evidence for the paper's limitation section: the original recipe was never claimed to survive unmodified past MNIST and CIFAR10 [§sec_6].

## Go Deeper {#go-deeper}

- [The Lottery Ticket Hypothesis at Scale](https://arxiv.org/abs/1903.01611) — directly tests whether winning tickets exist at ImageNet/ResNet-50 scale, the exact open question this brief raises.
- [Linear Mode Connectivity and the Lottery Ticket Hypothesis](https://arxiv.org/abs/1912.05671) — explains why the original rewind-to-iteration-0 procedure breaks down at scale and introduces late rewinding as the fix.

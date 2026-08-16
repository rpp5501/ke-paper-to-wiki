# Learning Rate Warmup

## TL;DR {#tldr}
Linearly ramping the learning rate up from zero over the first *k* iterations, instead of starting at the target rate immediately, lets VGG-19 and ResNet-18 train — and be pruned — at learning rates that would otherwise destroy the freshly reset winning ticket.

## Intuition {#intuition}
A winning ticket is a specific, small set of weights re-initialized to their original values. Right after pruning, before the network has had time to reshape its update directions around the surviving connections, a large learning-rate step can push those weights somewhere the training process can't recover from.

Warmup delays the big steps. It starts training with tiny updates and only reaches the intended learning rate once the network has had a chance to settle into a stable trajectory, after which training proceeds as normal.

This buys the ability to use a higher learning rate at all — the ceiling on achievable accuracy, not the accuracy itself. A winning ticket trained at a higher rate, once warmup makes that rate viable, reaches higher final accuracy than the same ticket trained at a lower, warmup-free rate.

## Mechanics {#mechanics}

Warmup is applied only where a network can't be pruned successfully at its target learning rate without it. VGG-19 needs warmup to train at its original rate of 0.1, and ResNet-18 needs it to move from 0.01 up to 0.03 — warmup pushes ResNet-18 no further than that [§sec_16_5].

Sweeping the learning rate directly, with no warmup, shows why this matters: accuracy falls off once the rate exceeds what each network can tolerate at initialization [fig_42][fig_43].

To measure how much warmup is enough, both networks are pruned iteratively while their warmup length *k* is swept, holding the learning rate fixed at the value warmup unlocks: 0.1 for VGG-19 and 0.03 for ResNet-18 [§sec_16_5].

```figure
id: fig_44
caption: The elbow at k≈5000 and ResNet-18's continued, smaller gains out to the chosen k=20000 [§sec_16_5]
```

```figure
id: fig_45
caption: The same elbow shape for VGG-19, flattening earlier so k=10000 is chosen [§sec_16_5]
```

Both networks show the same qualitative curve: accuracy rises quickly as *k* grows from 0 up to roughly 5000 iterations of warmup [§sec_16_5].

Past that point the curve flattens. Additional warmup still helps, but each extra iteration buys far less accuracy than it did below the elbow [§sec_16_5].

The two networks stop at different points along that flat region. ResNet-18 is pushed all the way to k=20000, the value giving the highest validation accuracy found in the sweep [§sec_16_5].

VGG-19 stops earlier, at k=10000, because the sweep found little further benefit from larger *k* for that network [§sec_16_5].

## The Math {#the-math}

The chosen *k* values look similar at first glance — 10000 for VGG-19, 20000 for ResNet-18 — until they're read against how long each network actually trains [§sec_16_5].

| Network | Learning rate unlocked by warmup | Warmup elbow | Chosen k | Total training iterations tracked | Warmup share of training |
|---|---|---|---|---|---|
| VGG-19 | 0.1 | ~5000 | 10000 | 112000 | 8.9% [fig_38] |
| ResNet-18 | 0.03 (from 0.01 without warmup) | ~5000 | 20000 | 30000 | 66.7% [fig_39] |

VGG-19 trains for up to 112000 iterations before its final checkpoint, so a 10000-iteration warmup is under 9% of the run — most of training happens at the full, stable learning rate [fig_38].

ResNet-18 trains for only 30000 iterations, so its 20000-iteration warmup consumes two-thirds of the entire run, leaving just 10000 iterations at the target learning rate before the final checkpoint [fig_39].

That split marks a boundary rather than a coincidence: push *k* close to the full iteration budget and there is no training left at the target rate to do the work pruning depends on. ResNet-18's 20000-of-30000 split sits close to that limit, consistent with the sweep finding diminishing returns rather than continued gains once *k* passes 5000 [§sec_16_5].

## Go Deeper {#go-deeper}

No research note is attached to this concept, so there's no external resource to link here. The most direct next step is the prerequisite concept, VGG/ResNet CIFAR10 Experiments, which lays out the full pruning-and-training setup that warmup is patched onto.

Looking directly at the four sweep figures — learning rate without warmup [fig_42][fig_43] and warmup length at the unlocked rate [fig_44][fig_45] — makes the elbow-and-plateau shape easier to see than the summary above.

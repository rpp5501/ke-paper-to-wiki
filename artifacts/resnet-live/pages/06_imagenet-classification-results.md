# ImageNet Classification Results
## TL;DR {#tldr}

On ImageNet-1k (1.28M training images, 50k validation, 1000 classes), plain networks get *worse* past 18 layers, but adding residual shortcuts flips this: ResNet-34 beats both plain-34 and ResNet-18, and stacking bottleneck blocks to 50/101/152 layers keeps improving accuracy with no degradation. The single 152-layer model alone (4.49% top-5 val, 3.57% test) outperforms every prior ensemble the paper compares against.

## Intuition {#intuition}

A deeper plain network should never be *worse* than a shallow one — you could always set the extra layers to the identity and match the shallow net's error exactly. In practice, plain nets don't find that solution: training error itself rises with depth, a symptom the paper calls the degradation problem, distinct from overfitting.

Residual learning sidesteps the search problem rather than solving it directly. Instead of asking each stack of layers to learn a full mapping from scratch, it asks them to learn a *residual* on top of the identity — a target that's trivially near-zero when extra depth isn't needed, and easy for the solver to find. Depth stops being a liability once "do nothing extra" is the network's default rather than something it has to discover.

## Mechanics {#mechanics}

An 18-layer plain net trains to lower validation error than a 34-layer plain net — the deeper network is strictly worse, not just no better, even though its solution space contains the shallow one's as a subspace [§sec_4_1].

Batch normalization keeps forward-signal variance non-zero and backward gradients healthy in both plain nets, ruling out simple vanishing gradients as the cause; the paper instead conjectures exponentially low convergence rates for very deep plain solvers [§sec_4_1].

Adding identity shortcuts (zero-padding for channel jumps, option A) reverses the trend: the 34-layer ResNet now beats the 18-layer ResNet by 2.8 points, and the degradation problem disappears — deeper trains to lower error and generalizes better [§sec_4_1].

Against its plain counterpart, ResNet-34 cuts top-1 error from 28.54% to 25.03%, a 3.5-point drop traced to lower training error rather than better generalization alone [tab_3].

| Model | Top-1 err. (%) | Top-5 err. (%) | Evidence |
|---|---|---|---|
| VGG-16 | 28.07 | 9.33 | [tab_3] |
| GoogLeNet | – | 9.15 | [tab_3] |
| PReLU-net | 24.27 | 7.38 | [tab_3] |
| plain-34 | 28.54 | 10.02 | [tab_3] |
| ResNet-34 A | 25.03 | 7.76 | [tab_3] |
| ResNet-34 B | 24.52 | 7.46 | [tab_3] |
| ResNet-34 C | 24.19 | 7.40 | [tab_3] |
| ResNet-50 | 22.85 | 6.71 | [tab_3] |
| ResNet-101 | 21.75 | 6.05 | [tab_3] |
| ResNet-152 | 21.43 | 5.71 | [tab_3] |

When depth is modest (18 layers), plain and residual nets reach similar final accuracy — SGD alone can already solve the shallower plain net — but the ResNet still converges faster early in training, showing residual learning eases optimization even before degradation would otherwise bite [§sec_4_1].

Three ways to handle shortcuts that must change dimension move the error down in small steps: zero-padding (A, 25.03/7.76), projection-only-where-dimensions-increase (B, 24.52/7.46), and all-projection (C, 24.19/7.40) [tab_3].

C's extra accuracy over B comes from thirteen additional projection shortcuts' parameters, not from solving degradation any more thoroughly than A does, so the paper keeps only option B going forward to hold down memory, time, and model size [§sec_4_1].

Stacking more 2-layer blocks to reach 50+ layers would be too costly, so each block becomes a 1×1→3×3→1×1 bottleneck: the two 1×1 convolutions shrink then restore channel depth, leaving the 3×3 convolution to run on fewer channels at similar time complexity [§sec_4_1].

```figure
id: fig_5
caption: The bottleneck block (right) used for ResNet-50/101/152 versus the plain building block (left) used for ResNet-34 — same time complexity, more depth [§sec_4_1]
```

Identity shortcuts matter even more here: swapping a bottleneck's identity shortcut for a projection would double both time complexity and parameter count, because that shortcut connects the block's two high-dimensional ends [§sec_4_1].

```algorithm
title: From the 34-layer 2-layer-block ResNet to 50/101/152-layer bottleneck ResNets
lines:
  - code: "block = [1x1 conv (reduce), 3x3 conv, 1x1 conv (restore)]"
    intent: "Replaces the 34-layer net's 2-layer block; the two 1x1 convs shrink then restore channel depth so the 3x3 convolution runs on fewer channels [§sec_4_1]"
  - code: "shortcut = identity, except projection where feature-map size changes (option B)"
    intent: "An identity shortcut on a bottleneck costs nothing extra; a projection shortcut here would double the block's time and parameter count because it touches the two high-dimensional ends [§sec_4_1]"
  - code: "stack bottleneck blocks: 50-layer, 101-layer, 152-layer variants"
    intent: "Substituting the bottleneck for the plain block and adding more of them buys depth (3.8B-11.3B FLOPs) without the degradation problem reappearing [§sec_4_1]"
```

Despite reaching 152 layers, this ResNet needs only 11.3 billion FLOPs — less than VGG-16 (15.3B) or VGG-19 (19.6B), which are 8-9x shallower [§sec_4_1].

The 50-, 101-, and 152-layer ResNets each beat the 34-layer one by a clear margin on every metric, with no degradation problem reappearing as depth grows [tab_3].

## The Math {#the-math}

Plain-34's 28.54% top-1 error falls to ResNet-34 A's 25.03%: a 3.51-point absolute drop, or 3.51/28.54 ≈ 12.3% relative [tab_3].

The same comparison in top-5 error: 10.02% → 7.76%, a 2.26-point absolute drop and 2.26/10.02 ≈ 22.6% relative — residual shortcuts help proportionally more on the harder top-5 metric [tab_3].

Moving from A to B saves 0.51 top-1 points (25.03→24.52); B to C saves only 0.33 more (24.52→24.19) despite C adding far more projection parameters — each extra dose of parameterized shortcuts buys less than the last [tab_3].

Top-5 error keeps falling as depth grows: 7.40% at 34 layers (option C), 6.71% at 50 (Δ −0.69 over +16 layers), 6.05% at 101 (Δ −0.66 over +51 layers), 5.71% at 152 (Δ −0.34 over +51 layers) — each added block yields a smaller marginal gain than the last [tab_3].

ResNet-152's 11.3 billion FLOPs is 11.3/15.3 ≈ 74% of VGG-16's budget and 11.3/19.6 ≈ 58% of VGG-19's, so the deepest ResNet is both more accurate and cheaper to run than either VGG variant [§sec_4_1].

ResNet-152 alone reaches 4.49% top-5 validation error as a single model — beating every previous ensemble the paper compares against, though the exact prior-ensemble numbers live on the Ensemble Results page rather than in this table [tab_4].

| Method | Top-1 err. (%, val) | Top-5 err. (%, val) | Evidence |
|---|---|---|---|
| VGG (ILSVRC'14) | – | 8.43† (test) | [tab_4] |
| GoogLeNet (ILSVRC'14) | – | 7.89 | [tab_4] |
| VGG v5 | 24.4 | 7.1 | [tab_4] |
| PReLU-net | 21.59 | 5.71 | [tab_4] |
| BN-inception | 21.99 | 5.81 | [tab_4] |
| ResNet-34 B | 21.84 | 5.71 | [tab_4] |
| ResNet-34 C | 21.53 | 5.60 | [tab_4] |
| ResNet-50 | 20.74 | 5.25 | [tab_4] |
| ResNet-101 | 19.87 | 4.60 | [tab_4] |
| ResNet-152 | 19.38 | 4.49 | [tab_4] |

| Method | Top-5 err. (test, %) | Evidence |
|---|---|---|
| VGG (ILSVRC'14) | 7.32 | [tab_4] |
| GoogLeNet (ILSVRC'14) | 6.66 | [tab_4] |
| VGG v5 | 6.8 | [tab_4] |
| PReLU-net | 4.94 | [tab_4] |
| BN-inception | 4.82 | [tab_4] |
| ResNet (ILSVRC'15) | 3.57 | [tab_4] |

On the test set, ResNet drops top-5 error to 3.57%, a (4.82−3.57)/4.82 ≈ 26% relative improvement over the next-best single method listed, BN-inception's 4.82% [tab_4].

## Go Deeper {#go-deeper}

The paper doesn't pin down *why* plain nets degrade — it conjectures exponentially low convergence rates and flags this as future work, so "BN rules out vanishing gradients" is elimination, not explanation [§sec_4_1].

The six-model ensemble's final test-set top-5 error isn't given in this evidence — the text refers to "the Table" without reproducing the number, so check the Ensemble Results page for it.

See Network Architectures for how the plain, residual, and bottleneck blocks are constructed, and ImageNet Localization for how these classification backbones carry over to localization.

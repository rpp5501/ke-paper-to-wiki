# Projection Shortcuts

## TL;DR {#tldr}
When a residual block's output has more channels than its input, the shortcut can't just add the two tensors — a projection shortcut is a 1×1 convolution that reshapes the input to match, used as Option (B) in the paper's dimension-matching scheme [§sec_3_3].

## Intuition {#intuition}
The identity shortcut just adds a block's input straight to its output, which is free but demands both live in the same-shaped tensor. Once a stage downsamples and doubles its channel count, that addition no longer type-checks — something has to reshape the input first.

A projection shortcut learns that reshape instead of hand-designing it. It is the same style of 1×1 convolution that appears elsewhere in the architecture, repurposed to carry the skip connection itself across a dimension change rather than leaving that connection literally an identity.

## Mechanics {#mechanics}

**Two ways to bridge a dimension change:** the paper considers two options wherever a shortcut crosses a change in feature-map size or channel count [§sec_3_3].

| Option | Mechanism | Extra parameters | Where used |
|---|---|---|---|
| A | Identity mapping with zero entries padded onto the new channels | None | Default when dimensions increase [§sec_3_3] |
| B | 1×1 convolution that learns the channel projection | Adds weights | Used to match dimensions in place of padding [§sec_3_3] |

**Where this happens in the network:** [tab_1] places the dimension change at the first block of conv3_x, conv4_x, and conv5_x, exactly where the channel count doubles and the stride is 2 [tab_1].

For both options, the shortcut is applied with a stride of 2 at these transitions, matching the stride used by the convolutional path so the two tensors still align spatially before they're summed [§sec_3_3].

## The Math {#the-math}

**A projection shortcut's cost:** a 1×1 convolution's multiply-adds equal (output height × output width) × (output channels) × (input channels), since each output channel needs one learned weight per input channel at each spatial position [§sec_3_3].

**The invariant this produces:** at each of the three transitions in the 18/34-layer network — 64→128, 128→256, 256→512 channels, with the feature map halving in each dimension — the projection shortcut costs the same ≈6.42×10⁶ multiply-adds [tab_1].

That invariance follows from design rule (ii): halving each spatial dimension divides the output positions by 4, while doubling the channel count multiplies the convolution's per-position cost by 4, so the two factors cancel exactly [§sec_3_3].

**The bottleneck architectures scale differently:** [tab_1] shows the 50/101/152-layer blocks project between 256, 512, 1024, and 2048 channels, not 64, 128, 256, and 512 [tab_1].

The same cancellation holds, but at ≈1.03×10⁸ multiply-adds per transition — 16× larger than the basic-block case, because the channel counts are 4× larger and enter the cost squared [tab_1].

**Option A as a boundary case:** if a 1×1 convolution's weights were forced into an identity-plus-zero-rows pattern instead of learned, projection shortcut (B) would degenerate exactly into zero-padding (A) — the same operation with fixed rather than trained weights [§sec_3_3].

## Go Deeper {#go-deeper}

```figure
id: fig_4
caption: The plain-vs-ResNet comparison here uses zero-padded identity shortcuts (Option A), not the projection shortcuts this page describes — the paper notes these residual nets have no extra parameters [§sec_3_3]
```

The paper's own comparison in [fig_4] isolates depth from the projection shortcut's added parameters: because it uses Option A throughout, any gap between the plain and residual curves can't be attributed to the projection's extra weights [§sec_3_3].

The supplied evidence covers only Options A and B for matching dimensions; a later all-projection variant is not described here, so this page does not establish its cost or accuracy trade-off.

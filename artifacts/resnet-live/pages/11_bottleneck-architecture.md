# Bottleneck Design

## TL;DR {#tldr}
The bottleneck block swaps a residual block's two same-width 3×3 layers for three layers where the middle layer runs narrower than the ones on either side. Table 1's block macros show it directly: two-argument blocks keep one channel count throughout, three-argument blocks give a separate inner count that's always a quarter of the output.

That narrowing is what lets 50-layer and deeper ResNets add far more layers for barely more compute than the 34-layer plain-block design.

## Intuition {#intuition}
Picture the bottleneck block as an hourglass built out of channel width. The block narrows to a smaller channel count in its middle layer, then widens back out to the count it started with, so the layer sandwiched in the middle runs cheaper than a same-width block would.

That's the whole trick behind stacking far more layers at 50, 101, and even 152 deep without the compute exploding the way it would if every layer stayed at full width.

## Mechanics {#mechanics}
Table 1 encodes the two block shapes through the arity of its own macros — two-argument blocks for the 18- and 34-layer nets, three-argument blocks for 50 layers and deeper [tab_1].

| Network depths | Block macro | Numbers given | What varies |
|---|---|---|---|
| 18, 34 | `blocka{channels}{count}` | 2 | one channel count for both layers in the block [tab_1] |
| 50, 101, 152 | `blockb{output}{inner}{count}` | 3 | inner channel count equals output ÷ 4 [tab_1] |

**The inner channel count is always a quarter of the output.** At conv2_x the bottleneck block is 64 inner / 256 output; at conv3_x it's 128/512; at conv4_x it's 256/1024; at conv5_x it's 512/2048 — the same 1:4 ratio at every stage, for every depth from 50 to 152 layers [tab_1].

**Depth in blocks, not just layers, matches between the 34-layer and 50-layer nets.** Both stack 3, 4, 6, and 3 blocks across conv2_x through conv5_x; the 50-layer net gets its extra depth by giving each of those blocks a third (bottleneck) layer, not by adding more blocks [tab_1].

**Every stage halves spatial size and doubles channel count from the one before it.** conv1 starts at 112×112 with 64 channels; conv2_x through conv5_x step down to 56², 28², 14², and 7² while the block's channel count goes 64→128→256→512 (or 256→512→1024→2048 for the bottleneck's output width) [tab_1].

That doubling follows the plain-network design rule the paper states directly: when feature-map size is halved, filter count doubles, to keep time complexity per layer roughly constant [§sec_3_3].

**Downsampling is done by the first block in each new stage, not by a separate pooling layer.** conv3_1, conv4_1, and conv5_1 each carry stride 2, and when a shortcut crosses that stride-2 boundary it uses either the zero-padded identity or the 1×1 projection to match the new size [tab_1].

- **Option A:** identity shortcut with extra zero-padded channels; adds no parameters, used across the stride-2 boundaries where dimensions increase [§sec_3_3].
- **Option B:** a 1×1 projection shortcut learns the channel-matching mapping instead of padding with zeros [§sec_3_3].

## The Math {#the-math}
**Table 1's own block counts, not an assumption, fix each net's total layers.** 16 blocks appear across conv2_x–conv5_x in both the 34-layer and 50-layer columns (3+4+6+3) [tab_1].

A 2-layer block gives the 34-layer net 16×2=32 block layers, plus conv1 and the fc layer, for 34 total; a 3-layer block gives the 50-layer net 16×3=48 block layers, plus conv1 and fc, for 50 total [tab_1].

**What the same +16 layers cost depends entirely on where they go.** 18-layer to 34-layer adds 16 layers by doubling block counts at full channel width; FLOPs go from 1.8×10⁹ to 3.6×10⁹, a 100% increase [tab_1].

34-layer to 50-layer adds the same 16 layers, but by giving each existing block a third, narrow-channel layer instead of adding blocks; FLOPs go from 3.6×10⁹ to 3.8×10⁹, only a 5.6% increase [tab_1].

The gap between a 100% FLOPs increase and a 5.6% increase for identical layer growth is the bottleneck design's payoff: depth added inside an already-narrow layer is nearly free, while depth added at full width is not [tab_1].

This is a measured cost for this specific architecture, not an asymptotic bound: 101-layer to 152-layer adds 39 more layers (conv4_x grows from 23 to 36 blocks) at the same 1:4 bottleneck ratio, and FLOPs rise from 7.6×10⁹ to 11.3×10⁹, a 48.7% increase [tab_1].

Because the bottleneck ratio never changes, this 48.7% cost is driven purely by adding 39 more narrow-middle blocks, the same mechanism that kept the 34-to-50 step cheap [tab_1].

## Go Deeper {#go-deeper}
Two threads worth chasing next: how the choice between identity padding (option A) and a learned 1×1 projection (option B) interacts with the bottleneck's own dimension-matching layers, and whether FLOPs tell the full efficiency story — a bottleneck block's parameter count drops even faster than its FLOPs, since the narrow middle layer touches far fewer weights per output pixel than a full-width 3×3 would.

Worth also tracing the same block-count-match trick used above (34-vs-50) forward to 101 and 152 layers, to see exactly which stage absorbs each depth increase.

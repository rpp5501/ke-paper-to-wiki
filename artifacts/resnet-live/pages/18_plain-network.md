# Plain Network
## TL;DR {#tldr}
A plain network is the residual network's ablation baseline: a stack of convolutional layers built with VGG-style filter rules, but with no shortcut connections carrying activations between layers [§sec_3_3]. Comparing the plain and residual versions of the same architecture is how the paper isolates what shortcuts contribute [§sec_3_3].

## Intuition {#intuition}
Think of the plain network as "ResNet with the shortcuts unplugged" — same layer count, same filter sizes, same channel counts at every stage, only the identity or projection paths that let a block skip its own transformation are removed [§sec_3_3]. That makes it the control condition: any accuracy or optimization difference between the plain and residual curves in training is attributable to the shortcuts themselves, not to a difference in capacity or depth [§sec_3_3][fig_4].

## Mechanics {#mechanics}
The 34-layer plain baseline is built from two filter design rules borrowed from VGG: layers producing the same output feature map size use the same number of filters, and when a layer halves the feature map size, the following layers double the filter count [§sec_3_3].

Downsampling is performed directly by convolutional layers with stride 2 rather than by separate pooling layers, and the network terminates in a global average pooling layer feeding a 1000-way fully connected layer with softmax [§sec_3_3].

Table 1 lays out the resulting stage structure: a 7×7, 64, stride-2 conv1, a stride-2 max pool, then four stages (conv2_x–conv5_x) whose 34-layer column stacks 3, 4, 6, and 3 two-layer blocks at 64, 128, 256, and 512 filters before the 1×1 average pool and 1000-d fc/softmax head [tab_1].

| Depth | FLOPs (billions) |
|---|---|
| 18-layer | 1.8 [tab_1] |
| 34-layer | 3.6 [tab_1] |
| 50-layer | 3.8 [tab_1] |
| 101-layer | 7.6 [tab_1] |
| 152-layer | 11.3 [tab_1] |

Despite reaching 34 weighted layers, this plain baseline costs 3.6 billion FLOPs, only about 18% of VGG-19's 19.6 billion FLOPs, because the filter-doubling rule trades depth for narrower feature maps rather than adding parameters at every scale [§sec_3_3][tab_1].

Figure 4's left panel plots this plain network's training and validation error against its 18-layer counterpart, isolating how depth alone affects a network with no shortcuts [fig_4].

```figure
id: fig_4
caption: Training-error curves that isolate depth's effect on a network with no shortcut connections [§sec_3_3]
```

## The Math {#the-math}
The paper's two design rules are chosen jointly so that computational cost per layer stays roughly constant as depth increases [§sec_3_3]. A convolutional layer's cost scales with output height × width × input channels × output channels, holding kernel size fixed [§sec_3_3].

Halving both spatial dimensions cuts the output feature-map area to one quarter, while doubling both the input and output channel counts multiplies the channel term by four — so the two changes cancel and the per-layer cost is preserved across stages [§sec_3_3].

**Worked check:** the paper reports the 34-layer plain baseline at "only 18" of VGG-19's FLOPs; dividing the table's own numbers confirms it: 3.6×10⁹ ÷ 19.6×10⁹ ≈ 0.184, about 18.4% [§sec_3_3][tab_1].

## Go Deeper {#go-deeper}
The plain network becomes the residual network by inserting a shortcut connection at every block: where input and output dimensions already match, the added shortcut is a parameter-free identity map, and where a block changes dimensions the paper compares zero-padded identity shortcuts (option A) against learned 1×1 projection shortcuts (option B) [§sec_3_3].

Because option A adds no parameters, the residual and plain networks in Figure 4 have identical parameter counts, which is what lets the paper attribute any error-curve difference to the shortcuts alone rather than to added capacity [fig_4].

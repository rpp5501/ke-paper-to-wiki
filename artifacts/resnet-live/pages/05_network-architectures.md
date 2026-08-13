# Network Architectures

## TL;DR {#tldr}
Section 3.3 fixes two concrete ImageNet networks — a VGG-style plain baseline and its residual counterpart made by adding shortcut connections — and Table 1 specifies five depths (18/34/50/101/152 layers) built from the same stage pattern.

## Intuition {#intuition}
Picture the plain network as a single corridor of convolutions: each stage shrinks the feature map and doubles the channel count, keeping the computational cost per layer roughly constant. VGG nets follow this same philosophy, so the plain baseline borrows its design directly.

The residual network is the identical corridor with footbridges added every couple of layers. A shortcut lets the signal skip a block outright, so the block only has to learn whatever the identity path doesn't already provide.

## Mechanics {#mechanics}
Section 3.3 describes two concrete instances built for discussion: a plain baseline and a residual network derived from it by inserting shortcuts [§sec_3_3].

The plain baseline's convolutional layers follow two rules, both aimed at keeping per-layer time complexity constant as the network deepens [§sec_3_3]:

- Same output feature-map size → same number of filters [§sec_3_3]
- Feature-map size halved → filter count doubled, so shrinking spatial extent is compensated by growing channel depth [§sec_3_3]

Downsampling is done directly by stride-2 convolutional layers rather than pooling, and the network ends with global average pooling feeding a 1000-way fully-connected softmax layer [§sec_3_3].

Table [tab_1] instantiates this stage pattern at five depths, scaling how many blocks are stacked per stage while keeping the same conv2_x–conv5_x layout [tab_1]:

| Depth | conv2_x | conv3_x | conv4_x | conv5_x | FLOPs |
|---|---|---|---|---|---|
| 18-layer | 2 | 2 | 2 | 2 | 1.8×10⁹ [tab_1] |
| 34-layer | 3 | 4 | 6 | 3 | 3.6×10⁹ [tab_1] |
| 50-layer | 3 | 4 | 6 | 3 | 3.8×10⁹ [tab_1] |
| 101-layer | 3 | 4 | 23 | 3 | 7.6×10⁹ [tab_1] |
| 152-layer | 3 | 8 | 36 | 3 | 11.3×10⁹ [tab_1] |

Once a plain network is defined, shortcut connections turn it into the residual counterpart. Identity shortcuts apply directly when a block's input and output dimensions match; when a stage boundary changes the channel count, the paper considers two options [§sec_3_3]:

- Option A: identity mapping, padding the extra channels with zeros — adds no extra parameters [§sec_3_3]
- Option B: a 1×1 projection convolution matches the dimensions with learned weights [§sec_3_3]

Both options use stride 2 whenever the shortcut crosses between two feature-map sizes, matching the stride the stage's own downsampling convolution uses so spatial dimensions stay aligned [§sec_3_3].

## The Math {#the-math}
The 34-layer plain baseline costs 3.6×10⁹ FLOPs against VGG-19's 19.6×10⁹: 3.6/19.6 ≈ 0.184, matching the paper's own claim that this is "only 18%" of VGG-19's cost despite comparable depth [§sec_3_3].

Depth names are literal layer counts. The 34-layer net stacks 3+4+6+3 = 16 basic blocks, each holding 2 conv layers (32 total), plus the conv1 stem and the final fc layer: 32+1+1 = 34 [tab_1].

The 50-layer net reuses the 34-layer's block counts (3+4+6+3=16) but swaps in 3-layer bottleneck blocks: 16×3+1+1 = 50 [tab_1].

The 101- and 152-layer nets keep the same bottleneck block but stack far more of them in conv4_x — 23 and 36 blocks respectively — which is where nearly all of the added depth and FLOPs come from [tab_1].

Option A's zero-padding shortcut adds exactly 0 parameters, since padding is not a learned operation; option B's 1×1 convolution adds C_in×C_out weights whenever a stage boundary changes channel count — matching conv2_x's 64 channels to conv3_x's 128 costs 64×128 = 8,192 extra weights for that single shortcut [§sec_3_3].

## Go Deeper {#go-deeper}
The architecture described here is what gets trained; the curves that motivated adding shortcuts in the first place come from the paper's own comparison of plain and residual training behavior.

```figure
id: fig_4
caption: Why extra depth alone doesn't help the plain nets, while the residual versions — same parameter count — improve with depth [§sec_3_3]
```

The full residual formulation (how the shortcut combines with the block's output) belongs to Residual Network; the block-level detail behind `blocka`/`blockb` in Table [tab_1] belongs to Implementation Details.

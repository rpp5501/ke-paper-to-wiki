That tool call was unnecessary — this task is just producing the corrected Markdown page directly, no file lookups needed. Here's the revised page:

# CIFAR-10 Depth Analysis

## TL;DR {#tldr}

On CIFAR-10, plain networks degrade as depth increases past 20 layers, while ResNets of the same depths train well and keep improving through 110 layers [S1]. Pushing further to 1202 layers still optimizes cleanly but generalizes worse, a gap the authors attribute to overfitting on a 50k-image dataset [S1].

## Intuition {#intuition}

CIFAR-10 lets the authors isolate the degradation problem from ImageNet-scale confounds. The architecture family and training recipe are held fixed across every depth, so any rise in training error as layers are added can only be attributed to depth itself, not to a change in data, compute, or model family.

The 1202-layer network is the intuition pushed to its limit: if identity shortcuts truly remove the optimization barrier, depth alone should stop being the bottleneck, and whatever failure remains has to come from somewhere else — here, too much capacity for too little data.

## Mechanics {#mechanics}

**Architecture.** The network opens with a single 3×3 convolution, then stacks three stages of 3×3 convolutions over 32×32, 16×16, and 8×8 feature maps, each stage holding 2n layers before global average pooling and a 10-way softmax [§sec_4_2].

| output map size | # layers | # filters | source |
|---|---|---|---|
| 32×32 | 1+2n | 16 | [§sec_4_2] |
| 16×16 | 2n | 32 | [§sec_4_2] |
| 8×8 | 2n | 64 | [§sec_4_2] |

**Depth variants.** Setting n = 3, 5, 7, 9, 18 gives 20-, 32-, 44-, 56-, and 110-layer networks. Shortcuts use identity mappings (option A) at every depth, so each residual model has exactly the same depth, width, and parameter count as its plain counterpart [§sec_4_2].

**Plain networks degrade with depth.** Training error rises as the plain nets get deeper across 20/32/44/56 layers, reproducing the same degradation seen on ImageNet and MNIST and pointing to an optimization difficulty rather than overfitting [§sec_4_2].

**ResNets do not.** The residual counterparts at matching depths train well and gain accuracy as depth increases, replicating the ImageNet result at CIFAR-10 scale [§sec_4_2].

**The 110-layer network needs a learning-rate warmup.** An initial rate of 0.1 is too large to start convergence, so training begins at 0.01 until training error drops below 80% (about 400 iterations), then switches to 0.1 for the rest of the schedule [§sec_4_2].

The network converges well and reaches 6.43% test error with fewer parameters than FitNet or Highway despite being deeper [§sec_4_2] [tab_5].

**Response magnitudes shrink with depth.** Standard deviations of layer outputs, measured after batch norm and before ReLU/addition, are smaller for ResNets than for plain nets, and shrink further from ResNet-20 to ResNet-56 to ResNet-110 [fig_7].

This supports the paper's motivation that residual functions are generally closer to zero than the functions a plain net must learn directly [§sec_4_2].

**The 1202-layer network trains but doesn't generalize.** At n = 200 the model reaches training error similar to the 110-layer network, below 0.1%, so optimization itself doesn't break down even at this depth [§sec_4_2].

Its test error is nonetheless worse than the 110-layer model's, 7.93% versus 6.43%, and the paper attributes the gap to overfitting since 19.4M parameters is large relative to CIFAR-10's 50k training images [tab_5] [§sec_4_2].

```figure
id: fig_7
caption: How response magnitude falls with depth — ResNets sit consistently below their plain counterparts, and ResNet-110 sits below ResNet-56 and ResNet-20 [§sec_4_2]
```

## The Math {#the-math}

**Capacity relative to data.** The 1202-layer network has 19.4M parameters trained on 50k images — about 388 parameters per training image. The 110-layer network has 1.7M parameters over the same 50k images, about 34 parameters per image [tab_5]. The deep network carries over 11× the capacity per training example, the concrete basis for the paper's "unnecessarily large" claim [§sec_4_2].

**Training error stays flat, test error does not.** Both networks reach training error below 0.1%, so optimization succeeds at both depths [§sec_4_2]. Test error is 6.43% at 110 layers versus 7.93% at 1202 layers — a gap of 1.50 percentage points, a 23% relative increase (1.50/6.43) with no matching change in training error [tab_5]. A widening test/train gap at constant train error is the numerical signature of overfitting, not of an optimization failure [§sec_4_2].

**What the comparison can't separate.** Going from 110 to 1202 layers changes both depth and capacity-per-example at once, and neither model uses dropout or maxout [§sec_4_2]. Isolating "extreme depth is hard to optimize" from "extreme depth overfits this dataset" would need matching regularization strength across both models — regularization the paper leaves to future work [§sec_4_2].

**A parameter-efficiency check elsewhere in the table.** ResNet-56 reaches 6.97% error with 0.85M parameters, beating Highway-32's 8.80% error despite Highway-32 using more parameters, 1.25M [tab_5]. Depth with identity shortcuts is buying accuracy that raw parameter count in a non-residual highway network isn't [§sec_4_2].

## Go Deeper {#go-deeper}

- **Section 4.2** of this paper is the primary source for the CIFAR-10 plain-vs-residual experiments and the 1202-layer overfitting result — https://arxiv.org/abs/1512.03385
- **Identity Mappings in Deep Residual Networks** follows up directly on the >1000-layer CIFAR-10 result, showing that reordering batch norm and ReLU before the convolutions (pre-activation units) eases optimization at extreme depth and narrows the train/test gap [S2] — https://arxiv.org/abs/1603.05027
- **pytorch_resnet_cifar10** reproduces the paper's exact CIFAR-10 configurations, including the deep n=200 variant, for hands-on inspection — https://github.com/akamaster/pytorch_resnet_cifar10

# Deep Residual Learning
## TL;DR {#tldr}
Deep networks should get more accurate as they get deeper, but plain stacks instead saturate and then degrade in training accuracy — a problem distinct from overfitting. [§sec_1]

Residual learning fixes this: each block learns a residual mapping instead of the full underlying mapping, added back through an identity shortcut connection that costs no extra parameters or computation. [§sec_1]

This lets networks over 100 layers train easily, and a 152-layer residual net achieves the best ImageNet result reported at the time while staying lower-complexity than VGG nets. [§sec_1]

## Intuition {#intuition}
The paper's core bet: if a block's optimal transformation is close to the identity, it should be easy to learn "add nothing" rather than forcing a stack of nonlinear layers to reconstruct identity from scratch. Pushing a residual toward zero is a much easier fitting problem than exactly reproducing the input through nonlinear transformations.

This concept sits at the top of a hub: the Degradation Problem motivates why the idea exists at all, Residual Learning and Network Architectures cover the mechanism and its concrete layer designs, and ImageNet, CIFAR-10, detection, and localization results test whether the idea pays off across tasks and depths.

## Mechanics {#mechanics}
Once normalized initialization and intermediate normalization layers made very deep networks trainable at all, a new failure mode appeared: as depth increases, accuracy saturates and then degrades rapidly, and this degradation shows up in training error itself, not just test error, ruling out overfitting as the cause. [§sec_1]

```figure
id: fig_1
caption: The degradation problem in a plain (non-residual) network — the 56-layer model has higher training error than the 20-layer model, even though it has strictly more representational capacity [§sec_1]
```

A constructive argument shows the degradation is not required by theory. Take a shallow network, build a deeper counterpart by copying its layers and setting every added layer to the identity mapping — this deeper model reproduces the shallow model's training error exactly. [§sec_1]

So a deeper network should never need to do worse in principle. Yet the solvers used in practice fail to find a solution this good, showing the difficulty is about optimization rather than representational capacity. [§sec_1]

Instead of asking a stack of layers to directly fit the desired underlying mapping, residual learning lets those layers fit the residual — the difference between the desired mapping and the input — and recovers the original mapping by adding the input back. [§sec_1]

The addition is implemented with an identity shortcut connection that skips one or more layers and adds its unmodified output to the stacked layers' output. Because the shortcut performs no operation beyond identity, it adds neither parameters nor computational cost, and the whole network still trains end-to-end with standard SGD and backpropagation in unmodified libraries. [§sec_1]

```figure
id: fig_2
caption: The residual building block this section describes — the stacked layers on the main path, and the identity shortcut that adds the input back in [§sec_1]
```

Three findings run through the rest of the paper:

- Extremely deep residual nets are easy to optimize, while plain nets of the same depth show higher training error as depth increases [§sec_1]
- Residual nets keep gaining accuracy as depth increases, well past where plain nets degrade [§sec_1]
- The same pattern holds on CIFAR-10, not just ImageNet, so it isn't an artifact of one dataset [§sec_1]

## The Math {#the-math}
The construction argument above is really a bound on achievable error, worth making precise:

- Let the shallow network's training error be $e_S$ [§sec_1]
- Copying the shallow network's layers and appending identity-mapping layers reproduces its function exactly, so this constructed deep network also achieves training error $e_S$ [§sec_1]
- Because construction shows a deep solution with error $e_S$ exists, the deep model's achievable error can never be theoretically worse than the shallow one's — depth alone cannot hurt what's representable [§sec_1]
- The degradation problem is the gap between this bound and what SGD actually finds: plain deep nets land at error above $e_S$, not because no better solution exists, but because the solver can't reach it [§sec_1]

The paper's extreme case isolates difficulty from capacity. If a block's optimal mapping actually is the identity, residual learning only needs to push its residual toward zero. A plain stack of nonlinear layers instead has to reconstruct the identity exactly through nonlinearities like ReLU — a much harder fitting target for the same solver. [§sec_1]

## Go Deeper {#go-deeper}
- **Degradation Problem** — the empirical failure this paper explains: training accuracy that gets worse with depth, not from overfitting.
- **Residual Learning** — the residual-mapping formulation and shortcut-connection design in mechanical detail.
- **Network Architectures** — how residual blocks are assembled into full networks at different depths.
- **ImageNet Classification Results** — the accuracy numbers and depth comparisons behind the ILSVRC results mentioned here.
- **CIFAR-10 Depth Analysis** — the 100+ and 1000+ layer experiments testing whether the effect holds at extreme depth.
- **Object Detection Generalization** — how these representations transfer to detection tasks.
- **ImageNet Localization** — the localization results from the same competitions.

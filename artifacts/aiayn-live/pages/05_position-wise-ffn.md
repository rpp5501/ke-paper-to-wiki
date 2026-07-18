# Position-wise Feed-Forward Networks
## TL;DR {#tldr}
Every layer in the Transformer's encoder and decoder stack contains a small feed-forward network applied independently to each position, sitting alongside the attention sub-layer as a core building block of the architecture.

## Intuition {#intuition}
Where attention lets positions exchange information with each other, this feed-forward step is the part of the layer where each position, on its own, gets to think. It runs the same transformation at every position, but that transformation differs from layer to layer, giving the model a per-position non-linear processing stage that complements attention's cross-position mixing. A related, more speculative framing treats these layers as performing attention over a fixed set of parameters rather than over the sequence itself.

## Mechanics {#mechanics}
Each layer of the encoder and decoder applies this feed-forward network identically and separately to every position, in addition to the attention sub-layer, meaning the same function is computed at each position but no information is shared across positions within this sub-layer [§sec_3_3]. Structurally it consists of two linear transformations with a ReLU activation in between; the linear transformations share the same form across positions but use different learned parameters at each layer [§sec_3_3]. The authors note this is equivalent to describing the network as two convolutions with kernel size 1, which is just another way of expressing the position-wise, parameter-sharing-within-layer nature of the operation [§sec_3_3]. The input and output dimensionality is fixed at the model dimension, while the inner layer expands to a larger intermediate dimensionality before being projected back down [§sec_3_3].

## The Math {#the-math}
The transformation applied at each position is the composition of two affine maps around a ReLU nonlinearity [eq_3]:

$$\mathrm{FFN}(x)=\max(0, xW_1 + b_1) W_2 + b_2$$ [eq_3]

## Go Deeper {#go-deeper}
No research note is attached to this concept, so no additional resources are available beyond the paper text itself [§sec_3_3].

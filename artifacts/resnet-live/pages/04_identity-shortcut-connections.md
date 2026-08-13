# Identity Mapping by Shortcuts

## TL;DR {#tldr}
A residual block learns a correction $\mathcal{F}(x)$ and adds it to the input through a shortcut: $y = \mathcal{F}(x, \{W_i\}) + x$. The shortcut adds no parameters and no extra computation, so plain and residual networks of the same depth cost the same to run.

## Intuition {#intuition}
Instead of asking a stack of layers to reproduce an entire desired mapping from scratch, the shortcut lets them work only on the leftover difference between input and target. If the ideal mapping is close to identity, the stacked layers just need to push their output toward zero — an easy target for gradient descent to find.

This reframing doesn't change what the network can represent, but it changes what's easy for the optimizer to find. That's why deeper stacks stop degrading once shortcuts are added.

## Mechanics {#mechanics}
In every building block, $x$ enters as the input and $y$ leaves as the output, while stacked weight layers compute the residual mapping $\mathcal{F}(x, \{W_i\})$ that the shortcut adds back on [eq_1].

The two-layer example in the paper uses $\mathcal{F} = W_2\sigma(W_1 x)$, with $\sigma$ denoting ReLU and biases omitted for clarity. The second nonlinearity is applied after the addition, not inside $\mathcal{F}$ [§sec_3_2].

The shortcut in eq_1 introduces neither extra parameters nor extra computation beyond the element-wise addition [eq_1]. This lets the paper compare plain and residual networks that share identical depth, width, and parameter count, isolating the shortcut as the only difference [§sec_3_2].

Eqn. (1) requires $x$ and $\mathcal{F}(x)$ to share the same dimensionality, since the addition is element-wise [eq_1]. When dimensions differ — for example when a block changes the number of channels — the shortcut instead applies a linear projection $W_s$ before adding [eq_2].

**Two shortcut forms:** the paper defines both an identity shortcut and a projection shortcut, differing in whether a projection matrix is needed to match dimensions [eq_1][eq_2].

| Form | Equation | When used |
|---|---|---|
| Identity shortcut | $y=\mathcal{F}(x,\{W_i\})+x$ | dimensions of $x$ and $\mathcal{F}(x)$ already match, so no parameters are added [eq_1] |
| Projection shortcut | $y=\mathcal{F}(x,\{W_i\})+W_s x$ | dimensions differ, e.g. when channel count changes [eq_2] |

A square $W_s$ could also be used when dimensions already match, but experiments show identity mapping is sufficient and more economical, so projection is used only to fix dimension mismatches [§sec_3_2].

$\mathcal{F}$ is flexible in depth: the paper's experiments use two- or three-layer residual functions, though more layers are possible [§sec_3_2]. A single-layer $\mathcal{F}$ collapses Eqn. (1) into $y = W_1 x + x$, resembling a plain linear layer, for which no advantage was observed [§sec_3_2].

Although the notation describes fully-connected layers, it applies equally to convolutional layers, where $\mathcal{F}$ represents multiple conv layers and addition happens channel-by-channel on feature maps [§sec_3_2].

## The Math {#the-math}
$$\ve{y}= \mathcal{F}(\ve{x}, \{W_{i}\}) + \ve{x}.$$
[eq_1]

```annotated-eq
latex: "\\ve{y}= \\mathcal{F}(\\ve{x}, \\{W_{i}\\}) + \\ve{x}"
terms:
  - tex: "\\ve{y}"
    role: 1
    words: "The block's output, the sum of the learned residual and the untouched input [eq_1]"
  - tex: "\\mathcal{F}(\\ve{x}, \\{W_i\\})"
    role: 2
    words: "The residual mapping learned by the stacked weight layers — what the block must add to reach the target [eq_1]"
  - tex: "\\ve{x}"
    role: 3
    words: "The block's input, carried forward unchanged by the shortcut connection [eq_1]"
```

$$\ve{y}= \mathcal{F}(\ve{x}, \{W_{i}\}) + W_{s}\ve{x}.$$
[eq_2]

Eqn. (2) replaces the identity shortcut with a linear projection $W_s$, needed only when $x$ and $\mathcal{F}(x)$ have different dimensions [eq_2].

```derivation
shape: What Eqn. (1) reduces to when F has only one layer.
steps:
  - latex: "\\ve{y} = \\mathcal{F}(\\ve{x}) + \\ve{x} = W_1\\ve{x} + \\ve{x}"
    why: "A single-layer residual function is just a linear map, so F(x) = W1 x [§sec_3_2]"
  - latex: "\\ve{y} = (W_1 + I)\\ve{x}"
    why: "Factoring shows the whole block collapses to one linear layer, which the paper reports gives no observed advantage [§sec_3_2]"
```

Figure 3 makes the zero-cost claim concrete: the 34-layer plain network and the 34-layer residual network both cost 3.6 billion FLOPs, against 19.6 billion for VGG-19, showing the shortcut adds no measurable computation [fig_3].

```figure
id: fig_3
caption: Plain and residual 34-layer networks share 3.6 billion FLOPs, the identity shortcut's cost showing up as effectively zero [fig_3]
```

## Go Deeper {#go-deeper}
This block is the unit that Residual Network stacks to build the full architecture, and Projection Shortcuts extends eq_2's $W_s$ to the specific rules the paper uses for downsampling blocks. The neighborhood also contrasts this design with prior work on residual representations and shortcut connections, which used shortcuts for different purposes than addressing the degradation problem this paper targets.

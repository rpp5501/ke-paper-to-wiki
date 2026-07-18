# Background: Reducing Sequential Computation
## TL;DR {#tldr}
Before the Transformer, models trying to avoid step-by-step recurrence turned to convolutions instead, but paying a price: relating two positions in a sequence still took more operations the farther apart they were. This background sets up the problem the Transformer's design is meant to solve.

## Intuition {#intuition}
Recurrent models process a sequence one step at a time, so relating a token to one far earlier means passing information through every intervening step. Convolutional alternatives like Extended Neural GPU, ByteNet, and ConvS2S process all positions in parallel instead, which helps with computation but doesn't fully solve the distance problem: stacking enough convolutional layers to connect two distant positions still means the number of operations needed grows with how far apart they are. That growth makes it harder for the model to learn dependencies between distant positions. The Transformer, which this concept builds on, was designed to cut that cost down to a constant, regardless of distance.

## Mechanics {#mechanics}
Extended Neural GPU, ByteNet, and ConvS2S all use convolutional neural networks as their basic building block, which lets them compute hidden representations for all input and output positions in parallel rather than sequentially [§sec_2]. However, relating signals from two arbitrary positions still requires a number of operations that grows with the distance between them: linearly for ConvS2S and logarithmically for ByteNet [§sec_2]. This growth makes learning dependencies between distant positions more difficult, since long-range signals must propagate through more computational steps to connect [§sec_2].

## The Math {#the-math}
The local context does not provide explicit equations or complexity formulas for these models — it states the scaling behavior in words only (linear for ConvS2S, logarithmic for ByteNet), without derivation [§sec_2]. The Transformer counters this by reducing the operation count needed to relate any two positions to a constant, though this comes at the cost of reduced effective resolution from averaging attention-weighted positions, an effect addressed separately by Multi-Head Attention [§sec_2].

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no additional resources to summarize beyond the paper's own background section [§sec_2].

# Encoder and Decoder Stacks
## TL;DR {#tldr}
The Transformer's encoder and decoder are each built by stacking identical layers, with the encoder mapping the input sequence into a continuous representation and the decoder generating the output sequence from it, one position at a time. Both stacks are assembled from the same building blocks — self-attention and position-wise feed-forward sublayers — wrapped in residual connections and layer normalization so information and gradients flow cleanly through many stacked layers.

## Intuition {#intuition}
Think of the encoder as reading the entire input sentence and refining its understanding layer by layer, where each layer lets every word look at every other word (via attention) and then processes that information locally (via the feed-forward network). The decoder does something similar for the output it's generating, but with two twists: it can only look at output words it has already produced (it can't peek ahead), and it also gets to consult the encoder's finished understanding of the input via an extra attention step. This stacked, layered design is what lets the Transformer build up increasingly rich representations without recurrence, relying instead on attention and feed-forward transformations repeated many times.

## Mechanics {#mechanics}
The encoder is composed of a stack of identical layers, and each layer has exactly two sub-layers: a multi-head self-attention mechanism, followed by a simple, position-wise fully connected feed-forward network [§sec_3_1]. Around each of these two sub-layers there is a residual connection followed by layer normalization, so the output of each sub-layer is LayerNorm(x + Sublayer(x)) [§sec_3_1]. To make these residual connections work, every sub-layer in the model, including the embedding layers, is constrained to produce outputs of the same dimension [§sec_3_1].

The decoder is also composed of a stack of identical layers, but each decoder layer inserts a third sub-layer in addition to the two found in the encoder: a multi-head attention sub-layer that attends over the output of the encoder stack, letting the decoder condition its generation on the encoded input [§sec_3_1]. As in the encoder, each of the decoder's three sub-layers is wrapped with a residual connection and followed by layer normalization [§sec_3_1]. The decoder's self-attention sub-layer is additionally modified with masking to prevent positions from attending to subsequent positions [§sec_3_1].

## The Math {#the-math}
Each sub-layer's output is defined as LayerNorm(x + Sublayer(x)), where Sublayer(x) is the function implemented by the sub-layer itself (self-attention, encoder-decoder attention, or the feed-forward network) [§sec_3_1]. This residual formulation is why every sub-layer output, and the embedding layers, must share the same dimension d_model — the addition x + Sublayer(x) only type-checks if both terms have matching shape [§sec_3_1]. The decoder combines this with output masking and a one-position offset of the output embeddings so that the prediction for position i depends only on known outputs at positions less than i, formalizing the auto-regressive property of generation [§sec_3_1].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so no external resources are available to cite here.

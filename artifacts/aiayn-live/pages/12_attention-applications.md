# Applications of Attention in the Model
## TL;DR {#tldr}
The Transformer doesn't use just one attention mechanism — it reuses multi-head attention in three distinct roles throughout the architecture: encoder-decoder attention, encoder self-attention, and decoder self-attention. Each role governs a different kind of information flow, and together they replace the recurrence and convolution used in prior sequence models.

## Intuition {#intuition}
Think of attention as a general-purpose "lookup and blend" operation, and the model as reusing that same operation in three different contexts depending on who is asking (the queries) and who is being consulted (the keys and values). When the decoder needs to consult the source sentence, it uses encoder-decoder attention. When any layer needs to relate different positions within its own sequence to build contextual representations, it uses self-attention. The decoder's version of self-attention has an extra constraint: since it generates output one token at a time, it must not be allowed to "peek" at future tokens it hasn't produced yet.

## Mechanics {#mechanics}
In encoder-decoder attention layers, the queries come from the previous decoder layer, while the keys and values come from the output of the encoder, letting every decoder position attend over all positions of the input sequence — this mirrors the typical encoder-decoder attention mechanisms found in earlier sequence-to-sequence models [§sec_3_2_3].

The encoder uses self-attention layers where the queries, keys, and values all originate from the same place: the output of the previous encoder layer. This means each position in the encoder can attend to all positions in the previous encoder layer, allowing full bidirectional context within the source sequence [§sec_3_2_3].

The decoder also uses self-attention, but restricted so that each position can only attend to positions up to and including itself, preventing leftward information flow to preserve the auto-regressive property needed for generation [§sec_3_2_3].

## The Math {#the-math}
The masking that enforces the decoder's auto-regressive constraint is implemented inside scaled dot-product attention itself, by setting all values in the softmax input that correspond to illegal (future) connections to negative infinity before the softmax is applied, so those positions receive zero attention weight [§sec_3_2_3].

## Go Deeper {#go-deeper}
No research note is available for this concept — the section above (sec_3_2_3) is the only local source used for this page.

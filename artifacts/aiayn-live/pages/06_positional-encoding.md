# Positional Encoding
## TL;DR {#tldr}
Since the Transformer has no recurrence or convolution, it has no built-in sense of token order — attention alone treats a sequence like a bag of tokens. Positional encoding fixes this by adding a vector that encodes each token's position directly into its embedding before it enters the encoder and decoder stacks, giving the model access to sequence order without any architectural change.

## Intuition {#intuition}
Because the Transformer is part of a larger architecture built entirely from attention and feed-forward layers, order has to be smuggled in through the data rather than through the network structure. The trick is to give every position in the sequence its own unique "fingerprint" vector, sized to match the token embeddings, and simply add the two together. As long as each position's fingerprint is distinct and consistent, the model can learn to use it to infer relative or absolute position when computing attention.

## Mechanics {#mechanics}
Positional encodings are added to the input embeddings at the bottom of both the encoder and decoder stacks, before any attention is computed, and share the same dimensionality as the embeddings so the two can simply be summed [§sec_3_5]. Many positional encoding schemes are possible, including learned embeddings, but this work uses a fixed, hand-designed function of sine and cosine waves at different frequencies [§sec_3_5]. The authors also trained a learned positional embedding variant and found it produced nearly identical results to the sinusoidal version, indicating the specific encoding scheme is not critical to performance [§sec_3_5].

## The Math {#the-math}
The encoding for a token at position `pos` and embedding dimension `2i` (even index) is `sin(pos / 10000^{2i/d_model})`, and for dimension `2i+1` (odd index) it is `cos(pos / 10000^{2i/d_model})`, so each dimension of the positional vector traces a sinusoid and the wavelengths across dimensions form a geometric progression [eq_4]. This sinusoidal form was chosen because for any fixed offset `k`, `PE_{pos+k}` can be expressed as a linear function of `PE_{pos}`, which was hypothesized to make it easy for the model to learn to attend by relative position [§sec_3_5]. The sinusoidal choice was also preferred over learned embeddings because it may let the model extrapolate to sequence lengths longer than those seen during training [§sec_3_5].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.

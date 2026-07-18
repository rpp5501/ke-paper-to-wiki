# Why Self-Attention {#why-self-attention}

## TL;DR {#tldr}
Self-attention was chosen over recurrent and convolutional layers because it connects every pair of positions in a sequence directly, making it cheaper to compute when sequences are shorter than the model's dimensionality, far more parallelizable, and much better at learning long-range dependencies. This is the core justification for building the Transformer entirely out of attention.

## Intuition {#intuition}
Recurrent networks process a sequence one step at a time, so information from the first word has to travel through every intermediate step before it can influence the last word — a long, sequential chain that makes long-range relationships hard to learn and impossible to parallelize across time. Self-attention instead lets every position look at every other position in a single step, collapsing that chain to a constant length. The tradeoff being weighed is essentially: how much work per layer, how much of that work can happen simultaneously, and how far a signal has to travel to connect two related words — self-attention wins on the latter two, which is why it replaces recurrence in the Transformer.

## Mechanics {#mechanics}
The comparison is organized around three desiderata: total computational complexity per layer, the amount of computation that can be parallelized (measured by the minimum number of sequential operations required), and the path length that forward and backward signals must traverse between any long-range dependency in the network — shorter paths make such dependencies easier to learn [§sec_4].

A self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires a number of sequential operations proportional to sequence length; this is the key parallelization advantage of self-attention [§sec_4].

For very long sequences, self-attention could be restricted to a neighborhood of size r around each output position to improve computational performance, at the cost of increasing the maximum path length between distant positions to O(n/r); this restricted variant was noted as future work rather than something evaluated in the paper [§sec_4].

A single convolutional layer with kernel width k < n does not connect all pairs of input and output positions, so a stack of O(n/k) contiguous convolutional layers (or O(log_k(n)) dilated convolutional layers) is required to do so, which lengthens the paths between positions compared to self-attention; convolutional layers are also generally more expensive than recurrent layers by a factor of k, though separable convolutions reduce this substantially [§sec_4].

As a side benefit, self-attention was also observed to yield more interpretable models: individual attention heads appear to learn distinct tasks, with some exhibiting behavior tied to the syntactic and semantic structure of sentences [§sec_4].

## The Math {#the-math}
Let n be the sequence length, d the representation dimension, k the kernel size of convolutions, and r the neighborhood size for restricted self-attention. The per-layer complexity, minimum sequential operations, and maximum path length for each layer type are: self-attention has complexity O(n²·d), O(1) sequential operations, and O(1) maximum path length; recurrent layers have complexity O(n·d²), O(n) sequential operations, and O(n) maximum path length; convolutional layers have complexity O(k·n·d²), O(1) sequential operations, and O(log_k(n)) maximum path length; restricted self-attention has complexity O(r·n·d), O(1) sequential operations, and O(n/r) maximum path length [§sec_4].

Self-attention layers are faster than recurrent layers whenever the sequence length n is smaller than the representation dimensionality d, which the paper notes is most often the case for sentence representations used by state-of-the-art machine translation models (e.g., word-piece and byte-pair representations) [§sec_4].

Even in the best case where k = n, a separable convolution's complexity is equal to the combination of a self-attention layer and a point-wise feed-forward layer — which is the approach the Transformer actually takes [§sec_4].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to summarize here — this page draws solely on the local section content (sec_4) and its comparison table. For broader context, see the neighboring concepts **Recurrent Model Limitations** (the contrasting baseline this section argues against) and **Transformer** (the architecture this justification builds on).

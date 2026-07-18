# Scaled Dot-Product Attention

## TL;DR {#tldr}
Scaled Dot-Product Attention is the core attention mechanism used in the Transformer: it scores how much each query should attend to each key via a dot product, scales that score down, and uses it to weight a sum of values. It is the fundamental building block that sits inside the broader Attention mechanism, and it is the specific function that Multi-Head Attention builds on by running many copies of it in parallel.

## Intuition {#intuition}
Think of each query as asking "which of these keys are relevant to me?" — the dot product measures similarity between the query and each key, producing a raw relevance score. Because these scores can grow very large when the vectors are high-dimensional, they are rescaled before being turned into a probability-like distribution over the values, so the mechanism reliably picks out the most relevant values without the scoring process becoming numerically unstable. This simple, matrix-multiplication-friendly design is what makes it a practical foundation for Attention, and why Multi-Head Attention can afford to stack many instances of it.

## Mechanics {#mechanics}
The inputs are queries and keys of dimension $d_k$ and values of dimension $d_v$; for each query, the dot products are computed against all keys, each is divided by $\sqrt{d_k}$, and a softmax is applied to obtain the weights placed on the values [§sec_3_2_1]. In practice this is computed for a whole set of queries at once by packing them into a matrix $Q$, with the keys and values likewise packed into matrices $K$ and $V$, so the entire operation reduces to matrix multiplications [§sec_3_2_1]. This is contrasted with additive attention, which computes the compatibility function using a feed-forward network with a single hidden layer, and with unscaled dot-product attention, which is identical except for the missing $\sqrt{d_k}$ scaling factor [§sec_3_2_1]. Dot-product attention is much faster and more space-efficient than additive attention in practice because it can be implemented with highly optimized matrix multiplication code, even though the two have similar theoretical complexity [§sec_3_2_1]. For large $d_k$, the dot products grow large in magnitude and push the softmax into regions with extremely small gradients, which is why the scaling by $\sqrt{d_k}$ is applied to counteract this effect [§sec_3_2_1].

## The Math {#the-math}
The output of the attention function over the packed matrices is given by [eq_1]:

$$\mathrm{Attention}(Q, K, V) = \mathrm{softmax}(\frac{QK^T}{\sqrt{d_k}})V$$ [eq_1]

## Go Deeper {#go-deeper}
There is no research note attached to this concept, so no external resources can be listed here.

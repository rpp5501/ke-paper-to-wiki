# Attention
## TL;DR {#tldr}
Attention is a mechanism that lets a model look up relevant information from a set of vectors by comparing a query against keys, then blending the associated values according to how well each key matches. It is the core building block that the Transformer's [[Encoder and Decoder Stacks]] rely on to move information between positions in a sequence.

## Intuition {#intuition}
Think of attention as a soft, differentiable lookup table: instead of retrieving a single exact match, the model retrieves a weighted average of everything in the table, where the weights reflect how relevant each entry is to the current query. This single idea underlies two concrete realizations used in the model — [[Scaled Dot-Product Attention]] as the specific compatibility function, and [[Multi-Head Attention]] as a way of running several such lookups in parallel — and is reused throughout the network in the [[Applications of Attention in the Model]].

## Mechanics {#mechanics}
An attention function maps a query and a set of key-value pairs to an output, where the query, keys, values, and output are all vectors [§sec_3_2]. The output is not a single retrieved value but a weighted sum of all the values, so every value contributes in proportion to its relevance rather than only the single best match [§sec_3_2].

The weight given to each value is not fixed — it is computed by a compatibility function that scores the query against the corresponding key [§sec_3_2]. This scoring step is what makes attention content-based: the same set of keys and values can produce very different outputs depending on what query is asked of them [§sec_3_2].

## The Math {#the-math}
The local context describes attention only at this functional, conceptual level (query/key/value vectors in, weighted-sum vector out, weights from a compatibility function) without specifying the exact compatibility function or its formula [§sec_3_2]; the concrete scoring function (scaled dot-product) and its equation belong to [[Scaled Dot-Product Attention]] rather than this general definition.

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no additional resources to list beyond the paper's own definition in §3.2.

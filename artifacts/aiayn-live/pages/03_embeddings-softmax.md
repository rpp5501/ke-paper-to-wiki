# Embeddings and Softmax
## TL;DR {#tldr}
This component turns discrete tokens into vectors the Transformer can compute with, and turns the model's final vectors back into a probability distribution over the vocabulary for predicting the next token. It's the "translation layer" at the entrance and exit of the Transformer.

## Intuition {#intuition}
Neural networks operate on continuous vectors, not words or symbols, so every token — whether it's an input word or an output word being generated — first needs to be mapped to a learned vector representation, called an embedding. At the other end of the model, after the decoder has produced its output, that vector needs to be converted back into a decision about which word comes next; a linear transformation followed by a softmax turns the decoder's output into a probability for every word in the vocabulary. This concept is the on-ramp and off-ramp for the whole Transformer architecture, sitting just outside the core attention machinery.

## Mechanics {#mechanics}
The model uses learned embedding layers — essentially lookup tables — to convert both the input tokens and the output tokens into vectors of a fixed dimension, rather than using any hand-crafted or fixed encoding scheme [§sec_3_4]. At the output side, the decoder's final vectors are passed through a learned linear transformation and then a softmax function, which converts them into predicted probabilities over the next possible token [§sec_3_4]. A notable design choice is that the same weight matrix is reused in three places: the input embedding layer, the output embedding layer, and the pre-softmax linear transformation, tying these representations together rather than learning them separately [§sec_3_4].

## The Math {#the-math}
In the embedding layers specifically, the shared weights are multiplied by a scaling factor before being used, a detail called out explicitly in this section though the precise constant depends on the model's embedding dimension [§sec_3_4]. Beyond this scaling step, the local text does not spell out the softmax formula itself or the loss computation that consumes these probabilities, so no further equations can be honestly attributed to this section.

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no external resources to list here.

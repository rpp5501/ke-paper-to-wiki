# Transformer

## TL;DR {#tldr}

The Transformer is a neural sequence-to-sequence architecture that throws out recurrence and convolution entirely, relying only on attention mechanisms and feed-forward layers to map an input sequence to an output sequence. It follows the standard encoder-decoder structure used by competitive translation models, but replaces the RNN or CNN layers inside the encoder and decoder with stacks of self-attention and point-wise fully connected sublayers. Because attention lets any two positions in a sequence interact directly, the model can be trained with far more parallelism than recurrent architectures, while still producing strong results on tasks like machine translation and English constituency parsing.

## Intuition {#intuition}

Recurrent models process a sequence one token at a time, so information about a distant word has to flow step by step through every position in between before it can influence another distant word — this is slow to train and hard to parallelize. The Transformer's core idea is to let every position look directly at every other position through attention, cutting that long chain of sequential steps down to a single step. This is the architecture's answer to the sequential-computation bottleneck that motivated the design, and it stands in direct contrast to the way recurrent models are limited by their step-by-step processing. Since attention alone has no built-in sense of word order, positional information is added separately so the model still knows which token came first. The result is a general building block — encoder stack, decoder stack, embeddings, and positional encoding all composing together — that turned out to generalize well beyond translation, later becoming the backbone for models like BERT.

## Mechanics {#mechanics}

Like other competitive sequence transduction models, the Transformer keeps the encoder-decoder shape: the encoder turns an input sequence of symbols into a sequence of continuous representations, and the decoder consumes those representations to generate an output sequence one symbol at a time, feeding each generated symbol back in as input for the next step (auto-regressive decoding) [§sec_3].

What distinguishes the Transformer is that both halves are built entirely from stacked self-attention and point-wise, fully connected layers, with no recurrence or convolution anywhere in the architecture [§sec_3]. Because self-attention has no inherent notion of sequence order, the model injects order information through fixed sinusoidal positional encodings added to the input embeddings, allowing it to infer relative and absolute position from the resulting phase relationships [S1][S2]. This design is also what gives the Transformer its parallelization advantage over RNNs: self-attention connects any two positions in a constant number of sequential operations rather than the linear number an RNN needs, so all positions can be processed simultaneously during training [S1][S3].

The encoder is a stack of 6 identical layers, each combining a multi-head self-attention sublayer with a position-wise feed-forward sublayer, both wrapped in residual connections and layer normalization [S1][S2]. The decoder mirrors this 6-layer structure but inserts a masked self-attention sublayer that prevents any position from attending to future tokens, plus a second multi-head attention sublayer that performs cross-attention over the encoder's output [S1][S2]. Multi-head attention itself works by running several scaled dot-product attention functions in parallel over projected subspaces, letting the model attend to different kinds of information at different positions simultaneously [S1][S3]. This encoder stack was later lifted directly as the backbone for bidirectional pretraining in BERT, showing the architecture's reach beyond the original translation task [S4].

## The Math {#the-math}

The local context for this concept describes the architecture at a structural level (encoder-decoder shape, sublayer composition, positional encoding, multi-head attention) but does not include any [eq_N] equation entries to reproduce here — the specific formulas for scaled dot-product attention, multi-head projections, and the sinusoidal positional encoding live in the child concepts that implement these pieces [§sec_3].

## Go Deeper {#go-deeper}

- **Attention Is All You Need (Vaswani et al., 2017)** — the original paper, for the full architecture diagram, equations, and ablation studies behind every claim above. https://arxiv.org/abs/1706.03762
- **The Illustrated Transformer** — best starting point for building visual intuition on Q/K/V, multi-head attention, and how the encoder-decoder stacks fit together. https://jalammar.github.io/illustrated-transformer/
- **The Annotated Transformer** — pairs a line-by-line PyTorch implementation with each paper equation, useful once you want to see the math turned into code. https://nlp.seas.harvard.edu/2018/04/03/attention.html
- **BERT: Pre-training of Deep Bidirectional Transformers (Devlin et al., 2018)** — shows how the encoder half of this architecture was repurposed for large-scale bidirectional pretraining. https://arxiv.org/abs/1810.04805

# Training Data and Batching
## TL;DR {#tldr}
This concept covers the raw material and packaging strategy behind Transformer training: which parallel corpora were used, how text was tokenized into subword units, and how sentences were grouped into batches. It sits under the paper's broader Training section, describing the data pipeline that feeds the model before any optimization happens.

## Intuition {#intuition}
Before a model can learn to translate, it needs a large aligned corpus of source-target sentence pairs and a way to turn open-ended vocabulary into a fixed, manageable set of tokens — subword schemes like byte-pair encoding solve the rare-word problem by splitting uncommon words into common sub-pieces. Batching by sentence length rather than by a fixed sentence count is a practical efficiency trick: it keeps the amount of padding low and the number of real (non-padding) tokens per batch roughly constant, so each training step does a similar amount of useful work regardless of whether the sentences in it happen to be short or long.

## Mechanics {#mechanics}
For English-German, training used the WMT 2014 English-German dataset (~4.5 million sentence pairs), encoded with byte-pair encoding over a vocabulary shared between source and target of about 37,000 tokens [§sec_5_1]. For English-French, a much larger corpus was used instead — the WMT 2014 English-French dataset with 36 million sentences — and tokens were split using a 32,000-token word-piece vocabulary rather than BPE [§sec_5_1]. Sentence pairs were not batched arbitrarily: they were grouped by approximate sequence length so that sentences of similar length end up in the same batch, and each training batch was sized to contain approximately 25,000 source tokens and approximately 25,000 target tokens, rather than a fixed number of sentences [§sec_5_1].

## The Math {#the-math}
The local context for this concept contains no formal equations — only dataset and configuration statistics (4.5M / 36M sentence pairs, ~37,000 / 32,000-token vocabularies, and ~25,000 source/target tokens per batch) [§sec_5_1].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.

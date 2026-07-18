# Recurrent Model Limitations
## TL;DR {#tldr}
Before the Transformer, state-of-the-art sequence models were recurrent — RNNs, LSTMs, and gated RNNs — which process a sequence one position at a time, carrying a hidden state forward from step to step. This step-by-step design is inherently sequential, so it cannot be parallelized within a single training example, and long sequences become expensive because memory limits how many examples can be batched together. The Transformer exists specifically to escape this constraint, replacing recurrence with an attention mechanism that draws global dependencies directly.

## Intuition {#intuition}
Imagine reading a sentence one word at a time, and being required to fully update your understanding after each word before you're allowed to look at the next one — you can never peek ahead or process two words simultaneously. That's the structural bottleneck of a recurrent model: computation is tied to position, and position *n* can't be computed until position *n-1* is done. It works, but it's slow to train, especially as sequences get longer, since you can't spread the work across a GPU's parallel cores within one example. This limitation is the direct motivation for the Transformer and for the broader case for self-attention as an alternative computational strategy.

## Mechanics {#mechanics}
Recurrent models factor computation along the symbol positions of the input and output sequences, aligning positions to steps in computation time: at each step they generate a hidden state as a function of the previous hidden state and the input at that position [§sec_1]. This recurrence relation is what makes the models sequential by construction — each hidden state depends on the one before it, so the chain of computation cannot be broken apart and run concurrently [§sec_1].

Because of this, the sequential nature "precludes parallelization within training examples," and the problem intensifies at longer sequence lengths, since memory constraints then limit how much batching across examples can compensate [§sec_1]. Prior work had chipped away at the cost side of this problem — factorization tricks and conditional computation improved computational efficiency, and conditional computation also improved model performance — but these were mitigations, not a fix: "the fundamental constraint of sequential computation, however, remains" [§sec_1].

Separately, attention mechanisms had already proven valuable for modeling dependencies regardless of their distance in a sequence, but in nearly all prior work they were used *bolted onto* a recurrent network rather than replacing it [§sec_1]. This sets up the Transformer's core move: keep the attention mechanism's ability to model long-range dependencies, but discard the recurrent backbone entirely [§sec_1].

## The Math {#the-math}
The local context describes the recurrent formulation only qualitatively — hidden state h_t as a function of h_{t-1} and the input at position t — without giving an explicit equation in this section [§sec_1]. No further mathematical detail on recurrent computation (e.g., specific LSTM/GRU gating equations) is present in this local context, so none is included here.

## Go Deeper {#go-deeper}
- No research note or additional resources are attached to this concept in the local context — none available beyond Section 1 of the paper itself.

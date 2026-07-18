# Model Variations

## TL;DR {#tldr}
To figure out which pieces of the Transformer actually matter, the authors ran a series of ablations on the base English-to-German model — tweaking one architectural knob at a time (number of attention heads, key/value dimensions, model size, dropout, and positional encoding scheme) and measuring the effect on translation quality. The results validate the core design choices behind the architecture: multi-head attention needs enough heads to be useful but not too many, richer key representations help, bigger models with proper regularization win, and the specific choice of sinusoidal vs. learned positional encodings barely matters. This builds directly on the main Machine Translation Results by explaining *why* the base and big configurations were chosen.

## Intuition {#intuition}
Think of this as the Transformer's sensitivity analysis: rather than just reporting one final score, the authors systematically dialed settings up and down to see what the model actually depends on. Some knobs turned out to be load-bearing (model size, dropout, attention key dimensionality), while others were largely cosmetic (the exact form of positional encoding). This kind of study is what separates a design choice that's "just what we tried first" from one that's actually justified by evidence.

## Mechanics {#mechanics}
The experiments hold total computation roughly constant while varying architecture, using beam search but no checkpoint averaging, and report per-wordpiece perplexity and BLEU on the newstest2013 development set [§sec_6_2].

Row group (A) varies the number of attention heads together with the per-head key/value dimensions so that total computation stays fixed; single-head attention scores 0.9 BLEU below the best multi-head setting, but performance also degrades when too many heads are used, indicating an interior optimum for the number of heads [§sec_6_2].

Row group (B) shrinks the attention key size specifically, and quality drops as a result — the authors interpret this as evidence that compatibility between queries and keys is not trivial to compute, and that a more expressive compatibility function than the simple dot product could improve results [§sec_6_2].

Row groups (C) and (D) confirm two expected trends: larger models (more layers/dimensions) consistently outperform smaller ones, and dropout is important for preventing overfitting, since removing it (dropout = 0.0) noticeably hurts perplexity and BLEU [§sec_6_2].

Row (E) swaps the fixed sinusoidal positional encoding for learned positional embeddings, and the resulting BLEU (25.7) and train perplexity (4.92) are nearly identical to the base model, showing that this particular design choice is not critical to performance [§sec_6_2].

## The Math {#the-math}
No new formulas are introduced here — this section is purely an empirical ablation table over the architecture defined elsewhere (base config: 6 layers, d_model=512, d_ff=2048, 8 heads, d_k=d_v=64, dropout=0.1, 100K training steps, ~65M params) [§sec_6_2]. The reported quantities are training perplexity per byte-pair-encoded wordpiece (not directly comparable to per-word perplexity) and BLEU on the dev set, alongside parameter counts, letting each row be read as a controlled trade-off between compute/capacity and translation quality [§sec_6_2].

## Go Deeper {#go-deeper}
No research note is attached to this concept; the only source material is the paper's own Section 6.2 (Model Variations) table and discussion, which is fully covered above [§sec_6_2].

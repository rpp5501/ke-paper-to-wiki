# Multi-Head Attention

## TL;DR {#tldr}
Multi-Head Attention runs several Scaled Dot-Product Attention operations in parallel, each on a different learned linear projection of the queries, keys, and values, then concatenates and re-projects the results. This lets the model attend to several kinds of relationships at once instead of averaging them into one view.

## Intuition {#intuition}
A single attention head produces one weighted average per query. If two different relationships matter for the same word — say, grammatical agreement and coreference — a single head must blend both into one average, which can cancel one signal in favor of the other.

Multiple heads give the model several independent subspaces to search in parallel, each free to specialize in a different kind of relationship, and the outputs are combined afterward rather than averaged during the lookup itself.

## Mechanics {#mechanics}
Each of the h heads gets its own learned projection matrices, W^Q_i, W^K_i, and W^V_i, which linearly project the d_model-dimensional queries, keys, and values down to d_k, d_k, and d_v dimensions before attention runs [§sec_3_2_2].

Attention then runs independently inside each of the h projected subspaces, in parallel, producing h separate d_v-dimensional output vectors — this is the same Scaled Dot-Product Attention computation, just applied h times with different projections instead of once [§sec_3_2_2].

The h outputs are concatenated into a single vector and passed through one more learned projection, W^O, to produce the final output — concatenation keeps every head's information distinct, and this last projection is what fuses the subspaces back into one representation [§sec_3_2_2].

With a single head, the attention weights form one probability distribution per query, so the output is one weighted average over all values — and averaging is exactly what stops the model from tracking more than one relationship at a position at once [§sec_3_2_2].

The paper uses h = 8 parallel heads, each with d_k = d_v = d_model/h = 64 — shrinking each head's dimension by the same factor that multiplies the head count, so the total computation across all heads is similar in cost to a single head running at the full model dimensionality [§sec_3_2_2].

```figure
id: fig_2
caption: The right-hand diagram — h parallel Scaled Dot-Product Attention blocks, each fed a different linear projection of Q, K, V, concatenated and projected once more into the final output [§sec_3_2_2]
```

## The Math {#the-math}
Multi-Head Attention concatenates the per-head outputs and projects the result once more, where each head first applies its own linear projections to Q, K, and V before running attention [eq_2].

$$
\begin{aligned}
\mathrm{MultiHead}(Q, K, V) &= \mathrm{Concat}(\mathrm{head_1}, ..., \mathrm{head_h})W^O\\
    \text{where}~\mathrm{head_i} &= \mathrm{Attention}(QW^Q_i, KW^K_i, VW^V_i)\\
\end{aligned}
$$
[eq_2]

```annotated-eq
latex: "\\mathrm{MultiHead}(Q, K, V) = \\mathrm{Concat}(\\mathrm{head_1}, ..., \\mathrm{head_h})W^O"
terms:
  - tex: "\\mathrm{head_i} = \\mathrm{Attention}(QW^Q_i, KW^K_i, VW^V_i)"
    role: 1
    words: "Head i's own attention computation, run entirely inside that head's projected subspace using its own W^Q_i, W^K_i, W^V_i [eq_2]"
  - tex: "\\mathrm{Concat}(\\mathrm{head_1}, ..., \\mathrm{head_h})"
    role: 2
    words: "Stacks all h heads' d_v-dimensional outputs side by side into one wide vector, keeping every head's information distinct rather than averaging [eq_2]"
  - tex: "W^O"
    role: 3
    words: "The single learned matrix that mixes the concatenated heads back into one output vector — the only point where information from different heads combines [eq_2]"
```

With d_model = 512 and h = 8, each head projects down to d_k = d_v = 64, so each head attends inside a 64-dimensional space instead of a 512-dimensional one; concatenating the 8 resulting 64-dimensional outputs reconstructs a 512-dimensional vector before W^O mixes them [§sec_3_2_2].

## Go Deeper {#go-deeper}
- Builds on [[Scaled Dot-Product Attention]], the single-head operation each head runs internally.
- Part of the broader [[Attention]] mechanism used throughout the encoder and decoder.
- See [[Attention Visualizations]] for what individual heads learn to attend to in practice.

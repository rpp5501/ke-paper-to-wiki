I made an unnecessary tool call — this task is just to return corrected Markdown text, no file or search tools needed. Here's the fixed page, with the flagged long paragraphs split at their claim boundaries and The Math tier rebuilt with a worked example instead of the placeholder.

# Sub-sequence Selection Procedure

## TL;DR {#tldr}

- Sample only a subsequence τ of the T forward-process indices instead of all of them, cutting the number of generative steps from T to S = |τ| [§sec_4_2]
- No retraining needed: the denoising objective only depends on q(x_t | x_0) for a fixed t, not on which forward process produced it [§sec_4_2]
- The tradeoff is speed for step density — a shorter τ means fewer, larger jumps through the latent chain [§sec_4_2]

## Intuition {#intuition}

The original DDPM forward process walks through every one of the T latent variables, so the reverse generative process is forced to take the same T steps to invert it [§sec_4_2].

Sub-sequence selection asks a different question: what if the model only needs the marginal distribution of each latent given x_0, not the exact chain that produced it? [§sec_4_2]

If the marginal is all that matters, a shorter forward process can be defined over a subset of indices τ that still matches the marginals the model was trained on [§sec_4_2]. The generative process then only has to invert this shorter chain, sampling S = |τ| latents instead of T [§sec_4_2].

## Mechanics {#mechanics}

The forward process is redefined not over all latent variables x_{1:T}, but over a subset {x_{τ_1}, …, x_{τ_S}}, where τ is an increasing sub-sequence of [1, …, T] of length S [§sec_4_2].

This sequential forward process q(x_τ | x_0) is constructed so it matches the same marginals q(x_{τ_i} | x_0) the model was trained on, even though it skips the indices outside τ [§sec_4_2].

The generative process mirrors this shortened schedule, sampling latents in the reverse order τ_S, τ_{S-1}, …, τ_1, which the paper calls the sampling trajectory [§sec_4_2].

The denoising objective only depends on q(x_t | x_0) for a fixed t, never on the full chain that produced it [§sec_4_2]. Skipping intermediate indices therefore does not violate any assumption the network was trained under [§sec_4_2].

When S is much smaller than T, the generative process needs far fewer iterative denoising steps, which is where the computational savings come from [§sec_4_2].

```figure
id: fig_2
caption: The shortened chain the generative process actually walks — here τ = [1, 3] skips index 2 entirely [§sec_4_2]
```

Only slight changes to the DDPM and DDIM update rules are needed to run them over τ instead of the full range [§sec_4_2]. The paper places the exact modified update equations in its appendix rather than in this section [§sec_4_2].

This separates training length from sampling length: a model could in principle be trained with an arbitrarily large or even continuous number of forward steps and sampled from only a small τ [§sec_4_2].

## The Math {#the-math}

The paper's own figure makes this concrete: τ = [1, 3] [fig_2]. Whatever the full range [1, …, T] contains, the sampling trajectory only visits the two indices in τ, in reverse order — x_3 first, then x_1 — skipping every other latent in between, such as x_2 [fig_2].

More generally, the speedup scales as T / S: the full chain costs T sequential network evaluations, while the shortened chain over τ costs only S, since each generative step still needs one denoising evaluation [§sec_4_2].

Two boundary cases bound the tradeoff. At S = T, τ = [1, …, T] contains every index, so the accelerated process collapses back to the original DDPM/DDIM generative process with no speedup [§sec_4_2].

As S shrinks toward the regime the paper targets — S much smaller than T — computational cost falls in proportion, which is the efficiency gain the paper attributes to the iterative nature of sampling [§sec_4_2].

## Go Deeper {#go-deeper}

- The same argument that lets training stay unchanged also applies uniformly across DDPM, DDIM, and every generative process the paper considers, not just one of them [§sec_4_2]
- The paper leaves the exact modified update equations to its appendix rather than restating them in the main accelerated-generation section [§sec_4_2]
- Future work the paper flags: train with an arbitrarily large or continuous number of forward steps, then sample from only a small τ at generation time [§sec_4_2]

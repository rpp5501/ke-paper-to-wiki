Sorry — that tool call was unnecessary for this task. Here's the corrected page, with the long paragraphs re-split at their claim boundaries and The Math tier rebuilt with real content instead of a no-equation notice.

# Accelerated Generation Processes

## TL;DR {#tldr}
A trained diffusion model doesn't have to sample every one of its $T$ forward steps at generation time. Picking a shorter increasing subsequence $\tau$ of length $S \ll T$ and running the generative process only on those indices produces samples in far fewer steps, using the exact same trained network.

## Intuition {#intuition}
Think of the forward process as a staircase from data to pure noise with $T$ steps. The model was trained to denoise at each individual step, not to climb the staircase one rung at a time.

As long as it still sees a clean version of each rung it visits, it can skip rungs entirely, jumping straight from a high-noise latent to a much less noisy one. Fewer rungs visited means fewer network evaluations — the entire cost of sampling.

## Mechanics {#mechanics}
The generative process in earlier sections samples all $T$ latent variables because the forward process is defined over the full index set $\{1,\dots,T\}$. Section 4.2 instead defines the forward process over a subset $x_{\tau_1},\dots,x_{\tau_S}$, where $\tau$ is an increasing sub-sequence of $\{1,\dots,T\}$ of length $S$ [§sec_4_2].

This sub-sequence forward process is built so that each $q(x_{\tau_i} \mid x_0)$ matches the corresponding marginal of the original $T$-step process, which is exactly what fig_2 depicts for $\tau = [1,3]$ [§sec_4_2].

```figure
id: fig_2
caption: The sub-sequence τ = [1,3] skips index 2 entirely — the generative process only ever conditions on x_1 and x_3 [§sec_4_2]
```

The generative process then runs in reverse over $\tau$ only, producing what the paper calls $q_\sigma(x_{\tau_{1:S}})$ — the object actually sampled, which visits $S$ latents instead of $T$ [§sec_4_2].

No retraining is required: the denoising objective at any step only depends on $q(x_t \mid x_0)$ being fixed, not on which other indices a sampling trajectory later visits, so one trained model serves every choice of $\tau$ [§sec_4_2].

The same slight modification to the update rule needed to accelerate sampling applies uniformly across the generative processes the paper considers [§sec_4_2]:

- DDPM [§sec_4_2]
- DDIM [§sec_4_2]
- every generalized non-Markovian process from the paper's earlier framework [§sec_4_2]

Because the trained network only ever needs $q(x_t\mid x_0)$ fixed, the paper notes it could in principle be trained on many more forward steps than any single sampling trajectory uses, even a continuous-time variable $t$, though it leaves that regime to future empirical work [§sec_4_2].

## The Math {#the-math}
The mechanism that licenses acceleration is an invariant, not a formula: the training loss at index $t$ only ever references $q(x_t \mid x_0)$, the marginal distribution of that single latent given the data. That quantity is fixed by $t$ alone, never by which other indices a later sampling trajectory $\tau$ happens to visit [§sec_4_2].

So a network trained once, over the full index set $\{1,\dots,T\}$, stays valid for every increasing sub-sequence $\tau$ simultaneously — accelerating generation is a choice made at sampling time, with no dependence on training [§sec_4_2].

Take the paper's own example, $\tau = [1,3]$, against a nearby full chain $x_0, x_1, x_2, x_3$. The unaccelerated process generates in three reverse steps: $x_3\to x_2$, $x_2\to x_1$, $x_1\to x_0$. The accelerated process generates in two: $x_3\to x_1$, $x_1\to x_0$ — index 2 is never visited, and no network evaluation is spent on it [§sec_4_2].

In general, if the full process has $T$ steps and the chosen sub-sequence has $S = |\tau|$ elements, the generative process performs exactly $S$ network evaluations rather than $T$. Sampling is iterative — each step's input is the previous step's output — so total cost scales linearly in $S$, and $S$ is a free choice made after training, independent of $T$ [§sec_4_2].

The boundary case $S = T$ with $\tau = [1,\dots,T]$ recovers the original, unaccelerated generative process exactly: the sub-sequence construction is a strict generalization of what earlier sections describe, not a separate mechanism [§sec_4_2].

## Go Deeper {#go-deeper}
This section builds on the non-Markovian, generalized forward processes defined earlier in the paper. Those constructions already decouple the forward process from a fixed-variance Markov chain [§sec_4_2].

Section 4.2 exploits that same freedom in a new direction: instead of changing the noise schedule's variance, it changes which indices the forward process is even defined over, keeping every visited marginal identical to the original [§sec_4_2].

The exact update rule for stepping between non-adjacent indices $\tau_{i-1}$ and $\tau_i$ is part of this concept — the paper reports it needs only a slight modification from the single-step update, with the derivation placed in an appendix not included here [§sec_4_2].

The paper leaves one implication as future work: a model could be trained on far more forward steps than any one sampling trajectory uses, including a continuous-time variable $t$, since the sub-sequence mechanism never constrains training itself [§sec_4_2].

# Related Work
## TL;DR {#tldr}

DDIM sits inside a family of methods that learn generative models as Markov-chain transition operators, alongside DDPMs and noise conditional score networks (NCSNs) [§sec_6].

Where DDPM and NCSN sample via a Langevin-like procedure that needs many steps, DDIM is an implicit generative model whose samples are fixed once the latent is fixed, letting it match or beat DDPM quality in far fewer iterations [§sec_6].

## Intuition {#intuition}

Think of DDPM and NCSN as hikers who must retrace a winding trail one short step at a time, because their update rule is a discretized random walk. DDIM instead teleports: once you know the starting point (the latent), the destination is fixed, so it can afford to skip most of the intermediate steps [§sec_6].

That fixed mapping from latent to sample is also why DDIM can produce meaningful interpolations, the way GANs and invertible flows do — moving smoothly in latent space moves smoothly in sample space [§sec_6].

## Mechanics {#mechanics}

DDPM, NCSN, and DDIM all belong to the same family: generative models built as transition operators of a Markov chain, trained with a denoising objective across many noise levels [§sec_6].

| Model | Training objective | Sampling procedure | Step count |
|---|---|---|---|
| DDPM | Variational lower bound on log-likelihood [§sec_6] | Langevin-like chain [§sec_6] | Many steps needed [§sec_6] |
| NCSN | Score matching over a nonparametric Parzen density estimator [§sec_6] | Langevin dynamics [§sec_6] | Many steps needed [§sec_6] |
| DDIM | Purely variational, no Langevin restriction [§sec_6] | Implicit deterministic mapping from latent [§sec_6] | Few iterations suffice [§sec_6] |

Despite this shared lineage, DDPM and NCSN start from different motivations. DDPM optimizes a variational lower bound to the log-likelihood, while NCSN optimizes a score-matching objective over a nonparametric Parzen density estimator of the data [§sec_6].

Yet both reduce to the same denoising autoencoder objective at each noise level, and both sample with a procedure similar to Langevin dynamics [§sec_6].

Langevin dynamics is a discretization of a gradient flow, so both DDPM and NCSN need many small steps to converge — which matches the empirical difficulty both families have generating high-quality samples in few iterations [§sec_6].

DDIM breaks from this pattern. It is an implicit generative model: samples are uniquely determined by the latent variables rather than accumulated through a long stochastic chain [§sec_6].

That determinism gives DDIM properties closer to GANs and invertible flows than to DDPM or NCSN, including the ability to produce semantically meaningful interpolations between samples [§sec_6].

## The Math {#the-math}

DDIM's derivation departs from Langevin dynamics entirely: it is built from a purely variational perspective, so the many-small-steps requirement that constrains DDPM and NCSN never enters the argument [§sec_6].

Consider sampling with very few iterations. For DDPM and NCSN, cutting steps means cutting the discretization that approximates Langevin dynamics, so error accumulates and sample quality drops sharply [§sec_6].

DDIM has no such discretization to cut: its sample is fixed by the latent rather than assembled step by step. The paper offers this as a partial explanation for why DDIM keeps higher sample quality than DDPM under fewer iterations [§sec_6].

The sampling trajectory itself gives a second boundary case. Two different sampling trajectories starting from the same latent variable produce samples with similar high-level visual features, which is the same behavior seen in neural networks with continuous depth [§sec_6].

## Go Deeper {#go-deeper}

This page draws only on the paper's own related-work section, so it doesn't derive the variational bound or score-matching objective in detail — those belong to the DDPM and NCSN pages themselves [§sec_6].

An open question the section leaves implicit: whether the continuous-depth resemblance is more than an analogy, i.e., whether DDIM's sampling ODE could be studied with the same tools used for neural ODEs [§sec_6].

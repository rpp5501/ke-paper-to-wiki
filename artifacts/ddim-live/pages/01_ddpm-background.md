# DDPM Background
## TL;DR {#tldr}

DDPMs are latent-variable generative models trained by maximizing a variational lower bound on the data log-likelihood. A **fixed** forward Markov chain adds Gaussian noise to data over $T$ steps; a **learned** reverse chain removes it step by step. Because each reverse step depends on the last, generating one sample needs $T$ sequential network evaluations — the bottleneck DDIM is built to remove.

## Intuition {#intuition}

Picture a drop of ink diffusing into water. The forward process is that dilution, run in small fixed increments until only diffuse noise remains — no learning involved, just a schedule.

The reverse process is a network trained to undo one increment at a time, walking backward from pure noise toward a clean image, one nudge per step.

Why so many small steps instead of one big jump? A single large denoising step is hard to approximate with a Gaussian, but a small step is not. Many small, well-approximated steps buy accuracy at the cost of a chain that can't be shortcut — each step needs the output of the one before it.

## Mechanics {#mechanics}

DDPMs define a joint distribution over the data and a sequence of latents living in the same space as the data, then marginalize the latents to get the model's density over $\vx_0$. Sampling draws $\vx_T$ from a fixed prior and runs the learned chain $p_\theta^{(t)}$ backward, one factor at a time. [eq_1]

The parameters $\theta$ are fit by maximizing a variational lower bound on this log-likelihood, using a fixed inference distribution $q$ over the latents as the variational posterior. Unlike a VAE, $q$ is never trained — it's specified analytically as a fixed noising process. [eq_2]

The forward process $q$ is a Markov chain of Gaussian transitions indexed by a decreasing sequence $\alpha_t$, so each step nudges $\vx_{t-1}$ toward noise; its covariance is built to keep positive diagonal entries so no transition ever collapses to a degenerate distribution. [eq_3]

The generative process $p_\theta$ mirrors this chain in reverse: it starts from the prior $\vx_T$ converges to as $\alpha_T$ is set near zero, then denoises iteratively down to $\vx_0$. [§sec_2]

```figure
id: fig_1
caption: The left half is the Markovian forward/reverse chain described on this page; the right half previews the non-Markovian inference model DDIM replaces it with [§sec_2]
```

A special property of the forward chain is that $\vx_t$ can be drawn directly from $\vx_0$ in one closed-form Gaussian step, skipping the $t$ intermediate transitions — this is what makes training on a random timestep tractable. [eq_4]

Modeling every reverse conditional as Gaussian with a trainable mean and fixed variance simplifies the variational bound to a sum of per-timestep noise-prediction losses, weighted by coefficients $\gamma_t$. [eq_5]

```algorithm
title: DDPM ancestral sampling
lines:
  - code: "x_T ~ N(0, I)"
    intent: "Start from the prior that x_T converges to when alpha_T is set close to 0 [§sec_2]"
  - code: "for t = T, ..., 1:"
    intent: "The reverse chain must be walked step by step, since x_{t-1} is only defined conditional on x_t [eq_1]"
  - code: "    x_{t-1} ~ p_theta^{(t)}(x_{t-1} | x_t)"
    intent: "Each step samples the learned Gaussian conditional, denoising one increment [eq_1]"
```

The chain length $T$ trades off two things: a longer chain keeps each reverse step closer to Gaussian, which motivates large $T$ (e.g., a thousand steps), but every step must run sequentially to produce one sample, since $\vx_{t-1}$ depends on $\vx_t$. [§sec_2]

## The Math {#the-math}

$$
p_(\vx_0) = \int p_(\vx_{0:T}) \diff \vx_{1:T}, \quad \text{where} \quad  p_(\vx_{0:T}) := p_(\vx_T) \prod_{t=1}^{T} p^{(t)}_(\vx_{t-1} | \vx_t)
$$
[eq_1]

This is the model DDPM fits: a prior over $\vx_T$ times $T$ learned reverse transitions, integrated over every latent to recover a density on $\vx_0$ alone. [eq_1]

$$
\max_ \bb{E}_{q(\vx_0)}[\log p_(\vx_0)] \leq \max_ \bb{E}_{q(\vx_0, \vx_1, \ldots, \vx_T)}\left[\log p_(\vx_{0:T}) - \log q(\vx_{1:T} | \vx_0) \right]
$$
[eq_2]

Maximizing the right side maximizes a lower bound on the true log-likelihood on the left, because Jensen's inequality applied to $p_\theta(\vx_{0:T})/q(\vx_{1:T}|\vx_0)$ can only underestimate $\log p_\theta(\vx_0)$; the gap it leaves is a KL divergence between $q$ and the true posterior. [eq_2]

$$
q(\vx_{1:T} | \vx_0) := \prod_{t=1}^{T} q(\vx_t | \vx_{t-1}), \text{where} \ q(\vx_t | \vx_{t-1}) := \gN\left(\sqrt{\frac{\alpha_t}{\alpha_{t-1}}} \vx_{t-1}, \left(1 - \frac{\alpha_t}{\alpha_{t-1}}\right) \mI\right)
$$
[eq_3]

Each transition shrinks $\vx_{t-1}$ by the ratio $\sqrt{\alpha_t/\alpha_{t-1}} < 1$ while its variance adds back exactly enough noise to hold the marginal variance steady — this balance is why the single sequence $\alpha_t$ suffices to parameterize the whole schedule. [eq_3]

```derivation
shape: Collapse the T-step forward chain into one closed-form step from x_0 to x_t.
steps:
  - latex: "\vx_t = \sqrt{\alpha_t/\alpha_{t-1}}\,\vx_{t-1} + \sqrt{1-\alpha_t/\alpha_{t-1}}\,\epsilon_{t-1}"
    why: "Each forward transition is Gaussian with the mean and variance given above, so it can be rewritten as a reparameterized sample [eq_3]"
  - latex: "\vx_t = \sqrt{\alpha_t/\alpha_{t-2}}\,\vx_{t-2} + \sqrt{1-\alpha_t/\alpha_{t-2}}\,\bar\epsilon"
    why: "Two independent Gaussian noise terms combine into one Gaussian, and the scale ratios telescope: (alpha_t/alpha_{t-1})(alpha_{t-1}/alpha_{t-2}) = alpha_t/alpha_{t-2} [eq_3]"
  - latex: "\vx_t = \sqrt{\alpha_t}\,\vx_0 + \sqrt{1-\alpha_t}\,\epsilon"
    why: "Repeating the merge down to x_0 (with alpha_0 := 1) collapses all t steps into one sample, so training never has to simulate the intermediate chain [eq_4]"
```

$$
\vx_t = \sqrt{\alpha_t} \vx_0 + \sqrt{1 - \alpha_t} \epsilon, \quad \text{where} \quad \epsilon \sim \gN(\vzero, \mI).
$$
[eq_4]

```annotated-eq
latex: "\vx_t = \sqrt{\alpha_t} \vx_0 + \sqrt{1 - \alpha_t} \epsilon"
terms:
  - tex: "\sqrt{\alpha_t}"
    role: 1
    words: "Shrinks the clean signal's contribution as t grows and alpha_t falls toward 0 [eq_4]"
  - tex: "\vx_0"
    role: 2
    words: "The original data point — the only place the actual image enters this formula [eq_4]"
  - tex: "\sqrt{1-\alpha_t}"
    role: 3
    words: "Grows as alpha_t falls, so noise dominates at large t [eq_4]"
  - tex: "\epsilon"
    role: 4
    words: "A single fixed standard Gaussian draw, independent of t — one noise sample scaled differently at every timestep [eq_4]"
```

At $t=0$ (with $\alpha_0 := 1$), this reduces to $\vx_0 = \vx_0$ exactly. As $t \to T$ with $\alpha_T$ near 0, $\vx_t \to \epsilon$, pure noise — the two boundary cases the schedule interpolates between. [eq_4]

$$
\begin{aligned}
L_\gamma(\epsilon_) & := \sum_{t=1}^{T}\gamma_t\bb{E}_{\vx_0 \sim q(\vx_0), \epsilon_t \sim \gN(\vzero, \mI)}\left[  \norm{\epsilon_{}^{(t)}(\sqrt{\alpha_t} \vx_0 + \sqrt{1 - \alpha_t} \epsilon_t) - \epsilon_t}_2^2 \right]
\end{aligned}
$$
[eq_5]

Because $\vx_t$ has the closed form derived above, this loss compares a network's prediction $\epsilon_\theta^{(t)}$ of the noise added to $\vx_0$ against the true $\epsilon_t$, turning generative training into $T$ coupled regression problems trained jointly on randomly sampled timesteps. [eq_5]

## Go Deeper {#go-deeper}

The sequential bottleneck named above — one network call per reverse step, $T$ steps deep — is exactly what DDIM is built to remove: it keeps the same trained $\epsilon_\theta$ but replaces this Markovian forward process with a non-Markovian one whose reverse chain can be traversed in far fewer steps. This concept page is a direct prerequisite for reading the DDIM concept page, which contrasts with the construction here.

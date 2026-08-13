# q_sigma(x_1:T|x_0) Construction

## TL;DR {#tldr}

$q_\sigma(\vx_{1:T}|\vx_0)$ is a family of joint inference distributions, one for every choice of the vector $\sigma$, each built to keep the same per-step marginals $q(\vx_t|\vx_0)$ that DDPM uses but to drop the requirement that $\vx_t$ depend only on $\vx_{t-1}$. [§sec_3_1]

## Intuition {#intuition}

DDPM fixes one Markov chain and one noise schedule. DDIM instead asks: what other joint distributions over $\vx_0,\dots,\vx_T$ reproduce the exact same marginals $q(\vx_t|\vx_0)$, so the same denoising network — trained only to predict $\vx_0$ from $\vx_t$ — still applies? [§sec_3_1]

The construction works backward from $\vx_0$: pick a variance $\sigma_t^2$ for each step, define $\vx_{t-1}$ as a Gaussian centered near $\vx_0$ and $\vx_t$ with that variance, and chain these steps together to reach $\vx_T$. [§sec_3_1]

## Mechanics {#mechanics}

The family is defined directly, not derived: fix $q_\sigma(\vx_T|\vx_0)$ to match DDPM's own marginal, then chain $t=2,\dots,T$ Gaussian kernels $q_\sigma(\vx_{t-1}|\vx_t,\vx_0)$ backward to build the full joint $q_\sigma(\vx_{1:T}|\vx_0)$. [§sec_3_1]

DDPM's forward process is a single fixed Markov chain: one $\sigma$, one factorization of $q(\vx_{1:T}|\vx_0)$. DDIM instead treats $\sigma$ as a free parameter, so every choice defines a distinct joint distribution over the same latent variables. [§sec_3_1]

Each kernel's mean is chosen so that $q_\sigma(\vx_t|\vx_0)=\mathcal N(\sqrt{\alpha_t}\vx_0,(1-\alpha_t)\mathbf I)$ holds for every $t$, the same marginal DDPM guarantees by construction — proved by induction in the paper's appendix lemma. [§sec_3_1]

Because each $q_\sigma(\vx_{t-1}|\vx_t,\vx_0)$ conditions on $\vx_0$ directly rather than only on $\vx_t$, the chain is no longer Markovian: $\vx_{t-1}$ can depend on $\vx_0$ in ways not mediated by $\vx_t$ alone. [§sec_3_1]

Every factor $q_\sigma(\vx_{t-1}|\vx_t,\vx_0)$ is Gaussian with variance $\sigma_t^2$ and a mean built from $\vx_0$ and $\vx_t$, chosen so the marginal-matching property above holds exactly. [§sec_3_1]

The scalar $\sigma_t$ controls how stochastic that step is. As $\sigma_t\to 0$, observing $\vx_t$ and $\vx_0$ pins $\vx_{t-1}$ down almost exactly, collapsing the sampling step to a deterministic map — the limit DDIM's fast sampler exploits. [§sec_3_1]

## The Math {#the-math}

$$q_\sigma(\vx_{t} | \vx_{t-1}, \vx_0) = \frac{q_\sigma(\vx_{t-1} | \vx_{t}, \vx_0) q_\sigma(\vx_{t} | \vx_0)}{q_\sigma(\vx_{t-1} | \vx_0)}$$
[eq_6]

This recovers the actual forward transition $q_\sigma(\vx_t|\vx_{t-1},\vx_0)$ by applying Bayes' rule to the reverse kernel and the marginal, rather than defining it directly the way DDPM does. [eq_6]

The result is still Gaussian, since a ratio of Gaussians in $\vx_t$ stays Gaussian in $\vx_t$, but the paper does not need this closed form for anything downstream — only $q_\sigma(\vx_{t-1}|\vx_t,\vx_0)$ and $q_\sigma(\vx_t|\vx_0)$ get used later. [§sec_3_1]

```annotated-eq
latex: "q_\\sigma(\\vx_{t} | \\vx_{t-1}, \\vx_0) = \\frac{q_\\sigma(\\vx_{t-1} | \\vx_{t}, \\vx_0) q_\\sigma(\\vx_{t} | \\vx_0)}{q_\\sigma(\\vx_{t-1} | \\vx_0)}"
terms:
  - tex: "q_\\sigma(\\vx_{t} | \\vx_{t-1}, \\vx_0)"
    role: 1
    words: "The quantity being solved for — the forward step, which the construction never defines directly [eq_6]"
  - tex: "q_\\sigma(\\vx_{t-1} | \\vx_{t}, \\vx_0)"
    role: 2
    words: "The reverse kernel that is defined directly, supplying the numerator [eq_6]"
  - tex: "q_\\sigma(\\vx_{t} | \\vx_0)"
    role: 3
    words: "The marginal fixed to match DDPM, the other numerator factor [eq_6]"
  - tex: "q_\\sigma(\\vx_{t-1} | \\vx_0)"
    role: 4
    words: "The marginal one step earlier, normalizing the ratio [eq_6]"
```

## Go Deeper {#go-deeper}

The marginal-matching claim used above is proved as a lemma in the paper's appendix, by induction over $t$ using the same Gaussian-composition identity as eq_6. [§sec_3_1]

This construction is the definition that **Non-Markovian Forward Processes** builds on, and the marginal-matching and $\sigma\to0$ limit claims used here are established formally in **Proofs of q_sigma Properties**.

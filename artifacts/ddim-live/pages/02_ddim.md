# Denoising Diffusion Implicit Models (DDIM)

## TL;DR {#tldr}
- DDIM replaces DDPM's fixed Markov-chain sampler with a family of non-Markovian generative processes that all reuse the same trained network, so no retraining is needed to switch between them.
- Setting the noise coefficient $\sigma_t$ to zero collapses the sampler into a deterministic map from a latent $\vx_T$ to a sample $\vx_0$ — this deterministic limit is what the paper calls DDIM.

## Intuition {#intuition}
DDPM's reverse process is a noisy, step-by-step walk: at every point it re-injects fresh randomness, so two runs starting from the same latent land in different places. DDIM asks a simple question about that walk — how much of the noise at each step is actually required for the model to have been trained correctly?

The answer is: none of it. The training objective only constrains what the network predicts about the underlying clean image, not how much extra randomness the sampler adds afterward. That freedom is what lets DDIM dial the noise down to zero and turn generation into a fixed trajectory instead of a random one, without touching the weights at all.

## Mechanics {#mechanics}

**The same trained network drives many samplers.** Given a sample $\vx_t$, the update produces $\vx_{t-1}$ using the model's noise prediction $\epsilon_\theta^{(t)}(\vx_t)$ through a formula that holds for any choice of the coefficients $\sigma_t$ [§sec_4_1].

Because $\epsilon_\theta$ is the same object trained under the DDPM objective and the update only changes how its output is combined, switching between the resulting generative processes requires no retraining [§sec_4_1].

**Two named endpoints of the same family:**
- Setting $\sigma_t$ to the value that makes the reverse process match the original Markovian forward process for every $t$ recovers ordinary DDPM sampling [§sec_4_1].
- Setting $\sigma_t = 0$ for every $t$ removes the random-noise term entirely, so $\vx_{t-1}$ becomes a deterministic function of $\vx_t$ and the model output — this is DDIM [§sec_4_1].

**Determinism turns the sampler into an implicit model.** With $\sigma_t=0$, the only randomness entering generation is the initial draw of $\vx_T$; every subsequent step down to $\vx_0$ is a fixed procedure, which is what "implicit probabilistic model" means here [§sec_4_1].

The paper names this case DDIM because it is trained with the ordinary DDPM objective even though its generative process is no longer a diffusion in the stochastic sense [§sec_4_1].

```algorithm
title: Sampling with the generalized DDIM update
lines:
  - code: "x = x_T ~ N(0, I)"
    intent: "Start from the same prior DDPM uses; only the steps after this differ [§sec_4_1]"
  - code: "for t = T, ..., 1:"
    intent: "The generative process still visits every latent index, just not necessarily as a Markov chain [§sec_4_1]"
  - code: "    pred_x0 = (x - sqrt(1-alpha_t) * eps_theta(x)) / sqrt(alpha_t)"
    intent: "Recover an estimate of the clean sample from the current noisy x_t and the model's noise prediction [eq_10]"
  - code: "    x = sqrt(alpha_{t-1}) * pred_x0 + sqrt(1-alpha_{t-1}-sigma_t^2) * eps_theta(x) + sigma_t * eps_t"
    intent: "Recombine the predicted x0, a direction term back toward x_t, and optional fresh noise scaled by sigma_t [eq_10]"
```

## The Math {#the-math}

$$\begin{aligned}
\vx_{t-1} & = \sqrt{\alpha_{t-1}} \underbrace{\left(\frac{\vx_t - \sqrt{1 - \alpha_t} \epsilon_^{(t)}(\vx_t)}{\sqrt{\alpha_t}}\right)}_{\text{`` predicted } \vx_0 \text{''}} + \underbrace{\sqrt{1 - \alpha_{t-1} - \sigma_t^2} \cdot \epsilon_^{(t)}(\vx_t)}_{\text{``direction pointing to } \vx_t \text{''}} + \underbrace{\sigma_t \epsilon_t}_{\text{random noise}}
\end{aligned}$$
[eq_10]

**The update decomposes into three independent pieces.** The first bracket inverts the forward marginal to reconstruct a clean-image estimate from $\vx_t$; the second bracket reuses the same noise prediction, rescaled, as a step back toward $\vx_t$; the third adds fresh noise scaled by $\sigma_t$ [eq_10].

```annotated-eq
latex: "\\vx_{t-1} = \\sqrt{\\alpha_{t-1}} \\left(\\frac{\\vx_t - \\sqrt{1 - \\alpha_t} \\epsilon_^{(t)}(\\vx_t)}{\\sqrt{\\alpha_t}}\\right) + \\sqrt{1 - \\alpha_{t-1} - \\sigma_t^2} \\cdot \\epsilon_^{(t)}(\\vx_t) + \\sigma_t \\epsilon_t"
terms:
  - tex: "\\left(\\frac{\\vx_t - \\sqrt{1 - \\alpha_t} \\epsilon_^{(t)}(\\vx_t)}{\\sqrt{\\alpha_t}}\\right)"
    role: 1
    words: "Predicted x0: solves the forward marginal for the clean sample the model believes produced x_t [eq_10]"
  - tex: "\\sqrt{1 - \\alpha_{t-1} - \\sigma_t^2} \\cdot \\epsilon_^{(t)}(\\vx_t)"
    role: 2
    words: "Direction pointing to x_t: reuses the same noise prediction, rescaled to land the step at variance 1-alpha_{t-1}-sigma_t^2 [eq_10]"
  - tex: "\\sigma_t \\epsilon_t"
    role: 3
    words: "Random noise: the only term with a free coefficient, and the one that determines how stochastic the step is [eq_10]"
```

**Worked boundary case: $\sigma_t = 0$.** The random-noise term vanishes, so $\vx_{t-1}$ is a deterministic combination of the predicted $\vx_0$ and the direction term; running this from $t=T$ down to $t=1$ defines a fixed map from $\vx_T$ to $\vx_0$, which is the implicit model the paper calls DDIM [§sec_4_1] [eq_10].

**Worked boundary case: matching the DDPM variance.** Choosing $\sigma_t$ so the reverse process satisfies the same one-step conditional as the original Markovian forward process recovers ordinary DDPM sampling from the identical trained $\epsilon_\theta$, with no change to training [§sec_4_1].

## Go Deeper {#go-deeper}
- **DDPM Background** is the prerequisite this page assumes: the Markovian special case above is exactly that model.
- **Non-Markovian Forward Processes**, **Unified Variational Inference Objective**, and **Generalized Generative Processes** build the machinery — a whole family sharing one $\epsilon_\theta$ — that this page's update rule is drawn from.
- **Accelerated Generation Processes** and **Relevance to Neural ODEs** extend the deterministic $\sigma_t=0$ case above toward faster sampling and a continuous-time view.
- **Sample Quality and Efficiency**, **Sample Consistency in DDIMs**, **Interpolation in Latent Space**, and **Reconstruction from Latent Space** are the empirical consequences of making generation deterministic, covered as their own pages.

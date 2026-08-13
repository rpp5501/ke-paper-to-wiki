# DDIM Sampling Update Equation

## TL;DR {#tldr}

DDIM replaces one reverse-diffusion step with a formula: predict the clean image from the current noisy sample, then rebuild the previous step from that prediction plus a tunable amount of fresh noise.

## Intuition {#intuition}

Think of denoising as aiming, not stepping blindly. A DDPM step nudges $\vx_t$ toward $\vx_{t-1}$ using only local information about the current noise level.

DDIM instead uses the network's noise prediction to guess the fully denoised image first, then walks back toward $\vx_{t-1}$ from that guess. The guess anchors the step; the noise term left over is optional, not required.

Because the same network $\epsilon_\theta$ produces this guess at every $t$, the guess gets sharper as $t$ shrinks, even though the underlying model is unchanged from DDPM.

## Mechanics {#mechanics}

The update splits into three named pieces: a predicted clean sample $\vx_0$, a direction pointing back toward $\vx_t$, and an independent noise term scaled by $\sigma_t$ [eq_10].

The predicted-$\vx_0$ term rearranges the forward-process relation to solve for $\vx_0$ given the network's noise estimate $\epsilon_\theta^{(t)}(\vx_t)$ [§sec_4_1].

Rescaling that estimate by $\sqrt{\alpha_{t-1}}$ moves it onto the noise schedule for step $t-1$ instead of $t$, which is why the whole term carries that prefactor [eq_10].

The second term supplies exactly enough noise-direction, scaled by $\sqrt{1-\alpha_{t-1}-\sigma_t^2}$, to keep the marginal distribution of $\vx_{t-1}$ consistent with the forward process, regardless of the value chosen for $\sigma_t$ [eq_10].

Different choices of $\sigma_t$ select different generative processes while reusing the same trained network, so no retraining is required [§sec_4_1].

| Choice of $\sigma_t$ | Forward process | Generative process | Step randomness |
|---|---|---|---|
| DDPM value, for all $t$ | Markovian [§sec_4_1] | Ordinary DDPM | Stochastic — fresh noise drawn at every step [§sec_4_1] |
| $0$, for all $t$ | Deterministic given $\vx_0$ and $t$ [§sec_4_1] | DDIM | None — fixed map from $\vx_T$ to $\vx_0$ [§sec_4_1] |

## The Math {#the-math}

$$
\begin{aligned}
\vx_{t-1} & = \sqrt{\alpha_{t-1}} \underbrace{\left(\frac{\vx_t - \sqrt{1 - \alpha_t} \epsilon_^{(t)}(\vx_t)}{\sqrt{\alpha_t}}\right)}_{\text{`` predicted } \vx_0 \text{''}} + \underbrace{\sqrt{1 - \alpha_{t-1} - \sigma_t^2} \cdot \epsilon_^{(t)}(\vx_t)}_{\text{``direction pointing to } \vx_t \text{''}} + \underbrace{\sigma_t \epsilon_t}_{\text{random noise}}
\end{aligned}
$$
[eq_10]

```annotated-eq
latex: "\\vx_{t-1} = \\sqrt{\\alpha_{t-1}}\\left(\\frac{\\vx_t - \\sqrt{1-\\alpha_t}\\,\\epsilon_\\theta^{(t)}(\\vx_t)}{\\sqrt{\\alpha_t}}\\right) + \\sqrt{1-\\alpha_{t-1}-\\sigma_t^2}\\cdot \\epsilon_\\theta^{(t)}(\\vx_t) + \\sigma_t \\epsilon_t"
terms:
  - tex: "\\left(\\frac{\\vx_t - \\sqrt{1-\\alpha_t}\\,\\epsilon_\\theta^{(t)}(\\vx_t)}{\\sqrt{\\alpha_t}}\\right)"
    role: 1
    words: "Predicted clean sample $\\vx_0$, solved from the forward-process relation using the network's noise estimate [eq_10]"
  - tex: "\\sqrt{1-\\alpha_{t-1}-\\sigma_t^2}\\cdot \\epsilon_\\theta^{(t)}(\\vx_t)"
    role: 2
    words: "Direction back toward $\\vx_t$, sized so the marginal distribution stays correct for any $\\sigma_t$ [eq_10]"
  - tex: "\\sigma_t \\epsilon_t"
    role: 3
    words: "Independent random noise, the only stochastic piece and the term that vanishes when $\\sigma_t=0$ [eq_10]"
```

The boundary case worth tracing by hand is $\sigma_t=0$ for every $t$. The last term drops out entirely, leaving only the rescaled prediction and the direction term [eq_10].

With that term gone, $\vx_{t-1}$ becomes a fixed function of $\vx_t$ and $\epsilon_\theta^{(t)}(\vx_t)$ alone, so two runs started from the same $\vx_T$ reach the same $\vx_0$ [§sec_4_1].

This update is a special case of the broader family of non-Markovian generative processes the paper defines; every member shares this same formula and differs only in $\sigma_t$ [§sec_4_1].

## Go Deeper {#go-deeper}

- This equation is one instance of the [[Generalized Generative Processes]] family it is defined inside — the family is the object, this update is one member of it.
- Setting $\sigma_t=0$ turns the update into the discretized ODE step studied under [[Euler Integration / ODE Connection]], which is why deterministic DDIM sampling behaves like integrating a continuous trajectory.
- [[Sample Consistency in DDIMs]] builds on this deterministic case: because the map from $\vx_T$ to $\vx_0$ is fixed, different $\vx_T$ samples stay consistent with each other across step counts.
- This update is one instance among the [[Closed-Form Sampling Step Equations]] the paper derives for the whole non-Markovian family.

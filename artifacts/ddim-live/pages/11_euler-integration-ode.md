```markdown
# Euler Integration / ODE Connection

## TL;DR {#tldr}

DDIM's sampling update is a first-order Euler step for an ordinary differential equation, not just a heuristic denoising rule.

Because the update follows a genuine ODE, the same discretization that generates an image from noise can also run backward, encoding an image into its latent noise vector.

## Intuition {#intuition}

Euler's method traces a curve by repeatedly taking a small straight-line step in whatever direction the curve is currently moving.

DDIM's sampling update does the same thing to the sequence of denoised images, moving the current point a small distance set by the model's noise prediction at that step.

Shrinking the step size makes the walk trace the true curve more faithfully, the same accuracy-versus-cost tradeoff any Euler integrator faces.

Because the curve is deterministic in both directions, walking it backward from a real image retraces the same path back toward pure noise — which is why DDIM can also act as an encoder.

## Mechanics {#mechanics}

The paper reparameterizes the update using $\bar{x} = x/\sqrt{\alpha}$ and $\sigma = \sqrt{(1-\alpha)/\alpha}$, treating $\alpha$ and $\sigma$ as functions of a continuous time variable $t$ rather than a fixed discrete schedule [§sec_4_3].

In this continuous limit, the DDIM iterate can be read as a single Euler step over an ODE in $\bar{x}(t)$, with the initial condition set at a very large $t$, corresponding to $x_T$ [§sec_4_3].

Because the ODE is well-defined in both time directions, taking enough discretization steps lets the same process run in reverse — encoding an observation $x_0$ forward toward $x_T$ by simulating the ODE, rather than only sampling from $x_T$ down to $x_0$ [§sec_4_3].

That reversibility is what makes DDIM useful for downstream applications needing latent representations of real data, since standard DDPM sampling has no equivalent deterministic encoding path [§sec_4_3].

A concurrent line of work derives a probability flow ODE that recovers the marginal densities of a score-based stochastic differential equation, producing a similar sampling schedule from a different starting point [§sec_4_3].

The paper proves its own ODE is equivalent to a special case of that probability flow ODE — the continuous-time analogue of DDPM — with the proof given in the appendix [§sec_4_3].

Even though the underlying ODEs are equivalent, their Euler discretizations are not [§sec_4_3].

DDIM takes steps with respect to $\sigma_t = \sqrt{(1-\alpha_t)/\alpha_t}$, which depends less directly on the scaling of time, while the probability flow ODE takes steps with respect to $t$ itself [§sec_4_3].

The two updates coincide when $\Delta t$ and the corresponding change in $\sigma$ are close enough, but diverge with fewer sampling steps, which is exactly where the choice of step variable matters most [§sec_4_3].

## The Math {#the-math}

The discrete DDIM update, rewritten in the variables $\bar{x}$ and $\sigma$, exposes its resemblance to a first-order numerical solver for an ODE [§sec_4_3].

$$
\frac{\vx_{t-\Delta t}}{\sqrt{\alpha_{t-\Delta t}}}  = \frac{\vx_t}{\sqrt{\alpha_t}}  + \left(\sqrt{\frac{1 - \alpha_{t-\Delta t}}{\alpha_{t-\Delta t}}} - \sqrt{\frac{1 - \alpha_{t}}{\alpha_t}}\right) \epsilon_^{(t)}(\vx_t)
$$
[eq_11]

Equation eq_11 restates the DDIM update in the reparameterized variable $\bar{x}_t = x_t/\sqrt{\alpha_t}$: the new point equals the old one plus a step scaled by how much $\sigma_t = \sqrt{(1-\alpha_t)/\alpha_t}$ changed over the interval [eq_11].

That form is exactly a finite-difference approximation, since it has the shape "next value equals current value plus (change in a parameter) times (a rate)" [eq_11].

```derivation
shape: Take the DDIM update to its continuous-time limit as an Euler step.
steps:
  - latex: "\\frac{\\vx_{t-\\Delta t}}{\\sqrt{\\alpha_{t-\\Delta t}}}  = \\frac{\\vx_t}{\\sqrt{\\alpha_t}}  + \\left(\\sqrt{\\frac{1 - \\alpha_{t-\\Delta t}}{\\alpha_{t-\\Delta t}}} - \\sqrt{\\frac{1 - \\alpha_{t}}{\\alpha_t}}\\right) \\epsilon_^{(t)}(\\vx_t)"
    why: "The discrete DDIM step in reparameterized coordinates x̄ = x/√α and σ = √((1-α)/α) [eq_11]"
  - latex: "\\diff \\bar{\\vx}(t) = \\epsilon_^{(t)}\\left(\\frac{\\bar{\\vx}(t)}{\\sqrt{\\sigma^2 + 1}}\\right) \\diff \\sigma(t)"
    why: "As Δt shrinks to 0 the bracketed finite difference in σ becomes the differential dσ(t), turning the update into an ODE [eq_12]"
```

$$
\diff \bar{\vx}(t) = \epsilon_^{(t)}\left(\frac{\bar{\vx}(t)}{\sqrt{\sigma^2 + 1}}\right) \diff \sigma(t) ,
$$
[eq_12]

Equation eq_12 is the ODE that DDIM's discrete update approximates: the change in $\bar{x}$ over an infinitesimal change in $\sigma$ equals the model's noise prediction at the corresponding point [eq_12].

The initial condition for this ODE is set at a very large $t$, matching $x_T$, so integrating it forward in $\sigma$ is one deterministic pass through the reverse process [§sec_4_3].

**DDIM's Euler step vs. the probability flow ODE's Euler step:** both scale the noise prediction by a change over the interval, but they scale it differently, as eq_13 shows [§sec_4_3].

$$
\frac{\vx_{t-\Delta t}}{\sqrt{\alpha_{t-\Delta t}}}  = \frac{\vx_t}{\sqrt{\alpha_t}}  + \frac{1}{2}\left(\frac{1 - \alpha_{t-\Delta t}}{\alpha_{t-\Delta t}} - \frac{1 - \alpha_{t}}{\alpha_t}\right) \cdot \sqrt{\frac{\alpha_t}{1 - \alpha_t}} \cdot \epsilon_^{(t)}(\vx_t)
$$
[eq_13]

Equation eq_13 scales the noise prediction by a change in $\sigma_t^2$ rather than a change in $\sigma_t$ itself, and $\frac{1}{2}\Delta(\sigma^2)\sqrt{\alpha_t/(1-\alpha_t)}$ only approximates $\Delta\sigma$ when the step is small [eq_13].

That means eq_11 and eq_13 agree in the continuous limit but generally disagree at any finite step size, the same divergence described in Mechanics [eq_13].

## Go Deeper {#go-deeper}

The paper's own proposition states that the DDIM ODE, run with the optimal model, has an equivalent probability flow ODE corresponding to the Variance-Exploding SDE — a continuous-time analogue of DDPM's discrete diffusion process — with the full proof deferred to the appendix [§sec_4_3].

Because the two ODEs are equivalent but not identical in their discretizations, choosing DDIM's $\sigma$-based Euler step over the probability flow ODE's $t$-based step is itself a design decision with consequences for few-step sampling quality [§sec_4_3].
```

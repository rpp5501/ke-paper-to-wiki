That tool call was unnecessary — this task is just rewriting the page content, no file lookup needed. Here's the corrected page with the flagged paragraphs split at their claim seams and the two unanchored lead-ins fixed:

# Relevance to Neural ODEs

## TL;DR {#tldr}
- DDIM's deterministic sampling step is algebraically an Euler-integration step, not just a denoising update.
- Reparameterizing $\vx_t$ and $\alpha_t$ into continuous-time variables turns the discrete DDIM chain into a well-defined ODE.
- Because ODEs run forward and backward without injected noise, DDIM can *encode* $\vx_0$ into a latent $\vx_T$ — something DDPM's stochastic reverse process cannot do.
- DDIM's ODE is equivalent, in continuous time, to a special case of a concurrently proposed probability-flow ODE for the Variance-Exploding SDE — but the two papers' finite-step samplers still differ.

## Intuition {#intuition}

Euler's method solves a differential equation by repeatedly taking a small step: current value, plus step size, times the slope at that point. DDIM's sampling update has exactly this shape once it's rearranged — the "slope" is the network's noise prediction, and the "step size" is a small change in a reparameterized time variable.

That resemblance is not a coincidence: building on DDIM's generalized non-Markovian generative process, the update can be read as one discretization of an underlying ODE.

Treating it that way explains a property DDPM lacks. An ODE has no randomness injected at each step, so running it backward exactly undoes running it forward — letting DDIM turn a real image into a latent code and back.

The same continuous-time object turns out to connect DDIM to a different derivation entirely. A concurrent line of work reaches an ODE from score-based generative modeling with SDEs; DDIM's ODE turns out to be a special case of theirs, even though the two were derived from different starting points.

## Mechanics {#mechanics}

**From denoising step to Euler step.** The DDIM update can be rearranged so a single coefficient multiplies the noise prediction, matching the shape Euler's method uses for an ODE: a current value plus a step size times a derivative estimate [§sec_4_3].

To make that shape explicit, DDIM reparameterizes two quantities: $\bar\vx = \vx/\sqrt\alpha$, which absorbs the signal scaling, and $\sigma = \sqrt{(1-\alpha)/\alpha}$, a function of $t$ that is continuous and increasing [§sec_4_3].

As the step size shrinks, eq_11's finite difference in this reparameterized variable becomes a derivative, giving the ODE stated below [eq_12].

- **Why $\sigma(t)$ must be increasing:** Euler's method needs a time variable that moves monotonically forward, so each step covers new ground instead of reversing progress already made [§sec_4_3].
- **What the initial condition encodes:** the ODE starts from $\vx_T$ at a very large $t$, corresponding to $\sigma(T)\to\infty$, i.e. pure noise [§sec_4_3].

**Why this makes DDIM invertible.** DDPM's reverse step injects fresh Gaussian noise at every $t$, so no deterministic map from $\vx_{t-1}$ back to $\vx_t$ exists. DDIM's Euler step injects no such noise, so running the same ODE with a negative step size recovers $\vx_t$ from $\vx_{t-1}$, and iterating this encodes $\vx_0$ into $\vx_T$ [§sec_4_3].

**A different derivation, the same ODE.** A concurrent paper derives a probability-flow ODE that reproduces the marginals of a variance-exploding SDE from score estimates. The proposition states DDIM's ODE is equivalent to this special case [§sec_4_3].

Even so, the finite-step samplers built from each ODE are not identical, because they take Euler steps with respect to different time variables [§sec_4_3].

## The Math {#the-math}

The discrete DDIM iterate, rearranged into the form that exposes its Euler-method structure, is written as follows [eq_11]:

$$
\frac{\vx_{t-\Delta t}}{\sqrt{\alpha_{t-\Delta t}}}  = \frac{\vx_t}{\sqrt{\alpha_t}}  + \left(\sqrt{\frac{1 - \alpha_{t-\Delta t}}{\alpha_{t-\Delta t}}} - \sqrt{\frac{1 - \alpha_{t}}{\alpha_t}}\right) \epsilon_^{(t)}(\vx_t)
$$
[eq_11]

Reading the left side as $\bar\vx_{t-\Delta t}$ and the bracket as a step in $\sigma(t) = \sqrt{(1-\alpha_t)/\alpha_t}$ turns this into an Euler update; taking $\Delta t \to 0$ gives the ODE below [eq_12]:

$$
\diff \bar{\vx}(t) = \epsilon_^{(t)}\left(\frac{\bar{\vx}(t)}{\sqrt{\sigma^2 + 1}}\right) \diff \sigma(t) ,
$$
[eq_12]

```derivation
shape: Reparameterize the discrete DDIM update into the continuous-time ODE.
steps:
  - latex: "\\frac{\\vx_{t-\\Delta t}}{\\sqrt{\\alpha_{t-\\Delta t}}}  = \\frac{\\vx_t}{\\sqrt{\\alpha_t}}  + \\left(\\sqrt{\\frac{1 - \\alpha_{t-\\Delta t}}{\\alpha_{t-\\Delta t}}} - \\sqrt{\\frac{1 - \\alpha_{t}}{\\alpha_t}}\\right) \\epsilon_^{(t)}(\\vx_t)"
    why: "Start from the DDIM iterate already rearranged to isolate the coefficient on the noise prediction [eq_11]"
  - latex: "\\bar\\vx(t) := \\vx_t/\\sqrt{\\alpha_t}, \\quad \\sigma(t) := \\sqrt{(1-\\alpha_t)/\\alpha_t}"
    why: "Define a rescaled state and a continuous, increasing time variable so the bracket becomes a step in a single scalar [§sec_4_3]"
  - latex: "\\bar\\vx(t-\\Delta t) - \\bar\\vx(t) = \\epsilon_^{(t)}(\\vx_t)\\,\\big(\\sigma(t-\\Delta t) - \\sigma(t)\\big)"
    why: "Substituting the definitions turns the DDIM update into a finite difference in $\\bar\\vx$ over a finite difference in $\\sigma$ [§sec_4_3]"
  - latex: "\\diff \\bar{\\vx}(t) = \\epsilon_^{(t)}\\left(\\frac{\\bar{\\vx}(t)}{\\sqrt{\\sigma^2 + 1}}\\right) \\diff \\sigma(t)"
    why: "Taking $\\Delta t \\to 0$ turns both finite differences into differentials, and rewriting $\\vx_t$ in terms of $\\bar\\vx(t)$ and $\\sigma(t)$ gives the ODE [eq_12]"
```

```annotated-eq
latex: "\\diff \\bar{\\vx}(t) = \\epsilon_^{(t)}\\left(\\frac{\\bar{\\vx}(t)}{\\sqrt{\\sigma^2 + 1}}\\right) \\diff \\sigma(t)"
terms:
  - tex: "\\diff \\bar{\\vx}(t)"
    role: 1
    words: "The infinitesimal change in the rescaled state — the quantity Euler's method accumulates one step at a time [eq_12]"
  - tex: "\\epsilon_^{(t)}\\left(\\frac{\\bar{\\vx}(t)}{\\sqrt{\\sigma^2 + 1}}\\right)"
    role: 2
    words: "The network's noise prediction, evaluated at the point rescaled back into the original coordinates — this plays the role of the ODE's velocity field [eq_12]"
  - tex: "\\diff \\sigma(t)"
    role: 3
    words: "The infinitesimal step in continuous time, replacing the finite square-root difference from eq_11 [eq_12]"
```

The proposition claims more than this derivation alone shows: with the optimal model, this ODE is equivalent to the probability-flow ODE for the Variance-Exploding SDE from a concurrent, independently-derived line of work [§sec_4_3].

That concurrent work discretizes its own ODE with a different Euler step, shown here in DDIM's variables for direct comparison [eq_13]:

$$
\frac{\vx_{t-\Delta t}}{\sqrt{\alpha_{t-\Delta t}}}  = \frac{\vx_t}{\sqrt{\alpha_t}}  + \frac{1}{2}\left(\frac{1 - \alpha_{t-\Delta t}}{\alpha_{t-\Delta t}} - \frac{1 - \alpha_{t}}{\alpha_t}\right) \cdot \sqrt{\frac{\alpha_t}{1 - \alpha_t}} \cdot \epsilon_^{(t)}(\vx_t)
$$
[eq_13]

| Discretization | Steps with respect to | Coefficient on $\epsilon_^{(t)}(\vx_t)$ | Anchor |
|---|---|---|---|
| DDIM (this paper) | $\sigma(t) = \sqrt{(1-\alpha_t)/\alpha_t}$ | $\sqrt{\frac{1-\alpha_{t-\Delta t}}{\alpha_{t-\Delta t}}} - \sqrt{\frac{1-\alpha_t}{\alpha_t}}$ | [eq_11] |
| Probability-flow ODE (concurrent work) | $t$ itself | $\frac{1}{2}\left(\frac{1-\alpha_{t-\Delta t}}{\alpha_{t-\Delta t}} - \frac{1-\alpha_t}{\alpha_t}\right)\sqrt{\frac{\alpha_t}{1-\alpha_t}}$ | [eq_13] |

```derivation
shape: Show DDIM's coefficient reduces to the probability-flow coefficient as the step shrinks.
steps:
  - latex: "a := \\frac{1-\\alpha_{t-\\Delta t}}{\\alpha_{t-\\Delta t}}, \\quad b := \\frac{1-\\alpha_t}{\\alpha_t}"
    why: "Name the two ratios that eq_11's bracket compares, so the algebra below is in one variable [eq_11]"
  - latex: "\\sqrt{a} - \\sqrt{b} = \\frac{a-b}{\\sqrt{a}+\\sqrt{b}}"
    why: "Rationalize eq_11's coefficient; this identity holds exactly, for any step size [eq_11]"
  - latex: "\\Delta t \\to 0 \\implies a \\to b \\implies \\sqrt{a}+\\sqrt{b} \\to 2\\sqrt{b}"
    why: "As the step shrinks the two ratios converge, so the denominator collapses to twice the smaller square root [eq_11]"
  - latex: "\\sqrt{a}-\\sqrt{b} \\to \\frac{a-b}{2\\sqrt{b}} = \\frac{1}{2}(a-b)\\sqrt{\\frac{\\alpha_t}{1-\\alpha_t}}"
    why: "This limit is exactly eq_13's coefficient, so the two Euler discretizations agree to first order in $\\Delta t$ [eq_13]"
```

For a small step, the two coefficients in the table above agree to first order, which is what makes the two ODEs equivalent in continuous time [eq_11][eq_13].

For a large step — the regime DDIM is built for, since its appeal is sampling in far fewer than $T$ steps — $a$ and $b$ are not close, the approximation $\sqrt a + \sqrt b \approx 2\sqrt b$ breaks down, and the two coefficients diverge [§sec_4_3].

This is the paper's own explanation for why its sampler and the concurrent work's sampler are not interchangeable in the few-step regime, even though the ODEs they discretize are the same [§sec_4_3].

The equivalence the proposition claims is between the *continuous-time* ODEs: DDIM's ODE and the probability-flow ODE for the Variance-Exploding SDE describe the same trajectory as $\Delta t \to 0$ [§sec_4_3].

Discretizing each into a finite number of Euler steps is a separate choice. DDIM steps with respect to $\sigma(t) = \sqrt{(1-\alpha_t)/\alpha_t}$, while the concurrent work steps with respect to $t$ itself, so the two finite-step samplers need not agree even though their underlying ODEs do [§sec_4_3].

## Go Deeper {#go-deeper}

- The full proof that DDIM's ODE is a special case of the probability-flow ODE for the Variance-Exploding SDE is in the paper's appendix, not reproduced in this evidence [§sec_4_3].
- The concurrent work reaches its ODE from a score-based generative model formulated as an SDE — a different derivation path arriving at an equivalent continuous-time object [§sec_4_3].
- The paper flags, without developing further, that DDIM's encoding map $\vx_0 \to \vx_T$ might be useful as a learned latent representation for downstream tasks — an open direction rather than a demonstrated result here [§sec_4_3].

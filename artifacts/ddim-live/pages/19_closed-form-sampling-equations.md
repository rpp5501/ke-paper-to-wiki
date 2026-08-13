# Closed-Form Sampling Step Equations
## TL;DR {#tldr}
- The general DDIM/DDPM update from the paper's abstract sampling equation reduces to two closed forms depending on a single knob, η.
- Setting η away from 1 shrinks the injected-noise term σ_τi(η), trading stochasticity for determinism without retraining.
- At η=1 the update becomes the DDPM-style step in eq_51, which reuses the DDIM coefficients for the non-stochastic parts but swaps in a different noise coefficient.

## Intuition {#intuition}
Think of each sampling step as three ingredients mixed together: a best guess at the clean image, a course-correction pointing back toward the current noisy state, and a pinch of fresh randomness.

The paper's closed-form equations just spell out how much of each ingredient to use at every step, and η is the dial that controls how big that pinch of randomness is.

Turning η down toward 0 makes the process almost deterministic — same starting noise, same output every time. Turning it up toward 1 recovers something close to the original DDPM sampler, which was always stochastic. The two equations in this section are literally the same formula evaluated at two different settings of that dial.

## Mechanics {#mechanics}

**The formula for σ_τi(η) itself is not supplied here.** It's defined by the general sampling equation referenced at the start of this section, outside this excerpt's evidence [§sec_12_3]. This page only has the two closed forms that result from that formula once η is fixed generically or set to 1 [eq_50] [eq_51].

**The general update, eq_50, has three additive terms.** The first term rescales a predicted denoised sample by sqrt(α_τi-1); the second term redirects toward x_τi using the model's noise prediction; the third term injects σ_τi(η) times fresh Gaussian noise [eq_50].

The coefficient on the non-stochastic direction term is sqrt(1 - α_τi-1 - σ_τi(η)^2), so it shrinks automatically as σ_τi(η) grows [eq_50]. This keeps the marginal variance of x_τi-1 fixed regardless of how η is chosen [§sec_12_3].

**Setting η=1 recovers the DDPM-like update, eq_51.** The predicted-x0 term and its coefficient sqrt(α_τi-1) are unchanged from eq_50 [eq_51]. Only the noise coefficient changes, becoming σ̂_τi instead of σ_τi(η) [eq_51].

This substitution matters because the two updates share every coefficient except the one controlling injected noise [§sec_12_3]. The paper notes this η=1 update is more stochastic than the general one, and that extra stochasticity is exactly why it performs worse when the number of sampling steps is small [§sec_12_3].

## The Math {#the-math}

$$
\vx_{\tau_{i-1}}(\eta) = \sqrt{\alpha_{\tau_{i-1}}} \left(\frac{\vx_{\tau_{i}} - \sqrt{1 - \alpha_{\tau_i}} \epsilon_^{(\tau_i)}(\vx_{\tau_{i}})}{\sqrt{\alpha_{\tau_i}}}\right) + \sqrt{1 - \alpha_{\tau_{i-1}} - \sigma_{\tau_i}(\eta)^2} \cdot \epsilon_^{(\tau_i)}(\vx_{\tau_{i}}) + \sigma_{\tau_i}(\eta) \epsilon
$$
[eq_50]

```annotated-eq
latex: "\\vx_{\\tau_{i-1}}(\\eta) = \\sqrt{\\alpha_{\\tau_{i-1}}} \\left(\\frac{\\vx_{\\tau_{i}} - \\sqrt{1 - \\alpha_{\\tau_i}} \\epsilon_^{(\\tau_i)}(\\vx_{\\tau_{i}})}{\\sqrt{\\alpha_{\\tau_i}}}\\right) + \\sqrt{1 - \\alpha_{\\tau_{i-1}} - \\sigma_{\\tau_i}(\\eta)^2} \\cdot \\epsilon_^{(\\tau_i)}(\\vx_{\\tau_{i}}) + \\sigma_{\\tau_i}(\\eta) \\epsilon"
terms:
  - tex: "\\sqrt{\\alpha_{\\tau_{i-1}}} \\left(\\frac{\\vx_{\\tau_{i}} - \\sqrt{1 - \\alpha_{\\tau_i}} \\epsilon_^{(\\tau_i)}(\\vx_{\\tau_{i}})}{\\sqrt{\\alpha_{\\tau_i}}}\\right)"
    role: 1
    words: "The predicted clean sample, rescaled to the noise level of step τ_{i-1} [eq_50]"
  - tex: "\\sqrt{1 - \\alpha_{\\tau_{i-1}} - \\sigma_{\\tau_i}(\\eta)^2} \\cdot \\epsilon_^{(\\tau_i)}(\\vx_{\\tau_{i}})"
    role: 2
    words: "The direction back toward x_τi, reusing the same predicted noise so the update stays consistent with the model's estimate [eq_50]"
  - tex: "\\sigma_{\\tau_i}(\\eta) \\epsilon"
    role: 3
    words: "Fresh injected noise, scaled by η's chosen coefficient — the only term that changes between eq_50 and eq_51 [eq_50]"
```

$$
\vx_{\tau_{i-1}} = \sqrt{\alpha_{\tau_{i-1}}} \left(\frac{\vx_{\tau_{i}} - \sqrt{1 - \alpha_{\tau_i}} \epsilon_^{(\tau_i)}(\vx_{\tau_{i}})}{\sqrt{\alpha_{\tau_i}}}\right) + \sqrt{1 - \alpha_{\tau_{i-1}} - \sigma_{\tau_i}(1)^2} \cdot \epsilon_^{(\tau_i)}(\vx_{\tau_{i}}) + \hat{\sigma}_{\tau_{i}} \epsilon
$$
[eq_51]

```derivation
shape: Specialize the general update to η = 1, the DDPM-like case.
steps:
  - latex: "\\sigma_{\\tau_i}(\\eta)^2 \\;\\to\\; \\sigma_{\\tau_i}(1)^2"
    why: "Fixing η at 1 selects a single point on the noise-coefficient family defined in the general update [eq_50]"
  - latex: "\\sigma_{\\tau_i}(1) \\;=\\; \\hat{\\sigma}_{\\tau_i}"
    why: "The paper renames this fixed value σ̂_τi in the DDPM-like update, keeping every other coefficient the same [eq_51]"
```

**Boundary case: η at each end of its range.** At η=0, σ_τi(η)=0 and eq_50 loses its noise term entirely, giving the fully deterministic DDIM update [eq_50]. At η=1, eq_50 collapses to eq_51, the DDPM-style step [eq_51].

**Why this matters for short schedules:** more stochasticity per step compounds sampling error when there are few steps available to correct it [§sec_12_3].

The paper attributes eq_51's worse performance at small step counts directly to this extra injected noise, since every other coefficient matches the general update [§sec_12_3].

## Go Deeper {#go-deeper}
- η parameterizes a whole family of generative processes sharing the same marginals; eq_50 and eq_51 are just two named members of that family — η free, and η=1 [§sec_12_3].
- Because the direction-to-x_τi coefficient in eq_50 is forced to sqrt(1-α_τi-1-σ_τi(η)^2), choosing σ_τi(η) is really choosing how a fixed variance budget splits between noise and signal-consistent correction [eq_50].
- The paper frames eq_51's extra stochasticity as the reason it underperforms at small step counts, implying the deterministic end of the η range is preferable when the sampling budget is tight [§sec_12_3].

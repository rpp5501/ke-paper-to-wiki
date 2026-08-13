# Proofs of q_σ Properties
## TL;DR {#tldr}

Three proofs underwrite the [[q_sigma(x_1:T|x_0) Construction]]:

- **Marginals are preserved.** Induction shows q_σ(x_t|x_0) equals the target Gaussian N(√α_t x_0, (1−α_t)I) at every t, not only at the endpoints [eq_21].
- **The training loss is unchanged.** The resulting variational bound J_σ reduces algebraically to the same ε-prediction loss L_γ used to train a standard DDPM [eq_28].
- **Sampling is a known ODE.** In continuous time, DDIM's update becomes an ODE identical to the VE-SDE probability-flow ODE, so DDIM sampling is a discretization of score-based generation [eq_39].

## Intuition {#intuition}

**Why does a different reverse process still land on the same marginals?** The construction freely chose q_σ(x_{t-1}|x_t,x_0) subject only to reproducing q_σ(x_t|x_0) at the next step; induction confirms that constraint is enough to pin down every earlier marginal too, all the way back to x_0.

**Why can DDIM reuse a DDPM checkpoint?** Because after expanding the KL terms in the variational bound, the arithmetic collapses to the identical squared-error loss between true and predicted noise that already trained the network — no retraining, no new architecture.

**Why does deterministic sampling connect to score-based diffusion?** Shrinking the DDIM step size to zero turns the sampling recursion into an ODE, and a change of time variable shows that ODE is exactly the probability-flow ODE that generates samples from a variance-exploding score-based model.

## Mechanics {#mechanics}

**Marginal preservation, by induction.** The proof fixes σ_t as given and shows by induction on t, from T down to 0, that if q_σ(x_t|x_0) already matches the forward marginal, combining it with the defined conditional q_σ(x_{t-1}|x_t,x_0) yields a marginal q_σ(x_{t-1}|x_0) of the same Gaussian family, with the base case t=T holding by construction [§sec_10].

- Assume the induction hypothesis holds at step t [eq_21].
- Apply the fixed conditional linking t and t−1 [eq_22].
- Gaussian-conditioning algebra collapses the combined mean to exactly √α_{t-1} x_0, the σ_t-dependent correction term cancelling [eq_23].
- The same algebra collapses the combined covariance to exactly (1−α_{t-1})I, independent of the free parameter σ_t [eq_24].

Because the collapse holds for every choice of σ_t, the whole family {q_σ} shares the same marginals — σ_t only changes how much of x_t's uncertainty comes from x_0 versus fresh noise at each step, not the marginal itself [§sec_10].

**Objective collapses to the DDPM loss.** Expanding the variational bound J_σ into per-timestep KL divergences, each term compares two Gaussians with the same fixed covariance, so the KL reduces to a squared distance between their means [eq_25][eq_26].

- Substituting the parametrization x_0=(x_t−√(1−α_t)ε)/√α_t turns the mean-squared error into a squared error between the true noise ε and the predicted noise ε_θ(x_t) [eq_26].
- The boundary term at t=1 (reconstruction likelihood) reduces to the identical form by the same substitution, needing no separate treatment [eq_27].
- Summed across t, J_σ equals L_γ, the weighted noise-prediction loss already used to train DDPM, differing only by a per-t constant that doesn't depend on θ during optimization [eq_28].

This is why a network trained with the ordinary DDPM objective is already optimal for every member of the q_σ family, including deterministic DDIM — nothing about the loss changes when σ_t is varied [§sec_10].

**DDIM sampling is a VE-SDE ODE in disguise.** The argument first builds a bijection between DDIM's (x_t, α_t) and the VE-SDE's (x̄(t), σ(t)) by rescaling x(t) by 1/√α(t), making both processes additive-noise processes in the same variable [eq_29][eq_30].

- The DDIM Euler step, rewritten in the rescaled variable, becomes a finite difference in σ(t) rather than in α_t [eq_32].
- Taking the step size to zero turns that finite difference into an ODE for DDIM sampling [eq_34].
- The optimal DDIM noise predictor and the VE-SDE score function are both defined as minimizers of a denoising objective, letting the score be rewritten directly in terms of the noise predictor [eq_35][eq_37].
- Substituting that equivalence into the probability-flow ODE and rearranging reproduces the DDIM ODE exactly, so the two describe the same continuous-time trajectory given matching initial conditions [eq_36][eq_39].

## The Math {#the-math}

**Preserving the marginal.** The induction step turns the assumption that q_σ(x_t|x_0) is Gaussian into a proof that q_σ(x_{t-1}|x_0) is too, with both mean and covariance collapsing to exactly the target values [§sec_10].

```derivation
shape: Show the recursive conditional preserves the marginal from t to t-1.
steps:
  - latex: "q_\\sigma(\\vx_{t} | \\vx_0) = \\gN(\\sqrt{\\alpha_t} \\vx_0, (1 - \\alpha_t) \\mI)"
    why: "Induction hypothesis: assume the marginal is correct at step t [eq_21]"
  - latex: "q_\\sigma(\\vx_{t-1} | \\vx_0) = \\gN(\\sqrt{\\alpha_{t-1}} \\vx_0, (1 - \\alpha_{t-1}) \\mI)"
    why: "Goal: show the same form holds one step earlier [eq_22]"
  - latex: "\\mu_{t-1} = \\sqrt{\\alpha_{t-1}} \\vx_{0} + \\sqrt{1 - \\alpha_{t-1} - \\sigma^2_t} \\cdot \\frac{\\sqrt{\\alpha_t} \\vx_0 - \\sqrt{\\alpha_{t}} \\vx_0}{\\sqrt{1 - \\alpha_{t}}} = \\sqrt{\\alpha_{t-1}} \\vx_{0}"
    why: "Standard Gaussian-conditioning algebra collapses the mean to exactly the target value, the correction term vanishing [eq_23]"
  - latex: "\\Sigma_{t-1} = \\sigma_t^2 \\mI + \\frac{1 - \\alpha_{t-1} - \\sigma^2_t}{1 - \\alpha_t} (1 - \\alpha_t) \\mI = (1 - \\alpha_{t-1}) \\mI"
    why: "The same algebra collapses the covariance to exactly the target value, independent of the free parameter sigma_t [eq_24]"
```

**Collapsing to the noise-prediction loss.** Each KL term in the variational bound reduces, through the fixed-covariance Gaussian identity and the x_0-from-ε reparametrization, to a term already summed as L_γ in the DDPM training objective [§sec_10].

```derivation
shape: Reduce the variational bound J_sigma to a per-step noise-prediction loss.
steps:
  - latex: "J_\\sigma(\\epsilon_) := \\bb{E}_{\\vx_{0:T} \\sim q(\\vx_{0:T})} \\left[\\log q_\\sigma(\\vx_T | \\vx_0) + \\sum_{t=2}^{T} \\log q_\\sigma(\\vx_{t-1} | \\vx_t, \\vx_0) - \\sum_{t=1}^{T} \\log p_^{(t)}(\\vx_{t-1} | \\vx_t) \\right] \\equiv \\bb{E}_{\\vx_{0:T} \\sim q(\\vx_{0:T})} \\left[\\sum_{t=2}^{T} \\KL(q_\\sigma(\\vx_{t-1} | \\vx_t, \\vx_0)) \\Vert p_^{(t)}(\\vx_{t-1} | \\vx_t)) - \\log p_^{(1)}(\\vx_0 | \\vx_1) \\right]"
    why: "Rewrites the variational bound as a sum of per-step KL terms plus a t=1 reconstruction term, the standard ELBO decomposition [eq_25]"
  - latex: "\\bb{E}_{\\vx_{0}, \\vx_t \\sim q(\\vx_{0}, \\vx_t)} [\\KL(q_\\sigma(\\vx_{t-1} | \\vx_t, \\vx_0)) \\Vert p_^{(t)}(\\vx_{t-1} | \\vx_t))] = \\bb{E}_{\\vx_{0}, \\vx_t \\sim q(\\vx_{0}, \\vx_t)}[\\KL(q_\\sigma(\\vx_{t-1} | \\vx_t, \\vx_0)) \\Vert q_\\sigma(\\vx_{t-1} | \\vx_t, f_{}^{(t)}(\\vx_t)))]"
    why: "The model's reverse step is defined as q_sigma itself, but with x_0 replaced by the network's denoised estimate f_theta^(t)(x_t), so the KL compares two members of the same Gaussian family [eq_26]"
  - latex: "\\equiv \\bb{E}_{\\vx_{0}, \\vx_t \\sim q(\\vx_{0}, \\vx_t)}\\left[\\frac{\\norm{\\vx_0 - f_{}^{(t)}(\\vx_t)}_2^2}{2 \\sigma_t^2}\\right]"
    why: "Two Gaussians with identical covariance sigma_t^2 I have a KL equal to a scaled squared distance between their means — here x_0 and f_theta^(t)(x_t) [eq_26]"
  - latex: "= \\bb{E}\\left[\\frac{\\norm{\\frac{\\vx_t - \\sqrt{1 - \\alpha_t} \\epsilon}{\\sqrt{\\alpha_t}} - \\frac{\\vx_t - \\sqrt{1 - \\alpha_t} \\epsilon_{}^{(t)}(\\vx_t)}{\\sqrt{\\alpha_t}}}_2^2}{2 \\sigma_t^2}\\right]"
    why: "Substituting x_0's reparametrization in terms of x_t and the true noise epsilon, and f_theta's matching parametrization in terms of the predicted noise, turns the x_0-space error into a difference of two noise estimates [eq_26]"
  - latex: "= \\bb{E}\\left[\\frac{\\norm{\\epsilon - \\epsilon_{}^{(t)}(\\vx_t)}_2^2}{2 d \\sigma_t^2 \\alpha_t}\\right]"
    why: "The shared x_t and sqrt(1-alpha_t) terms cancel, leaving exactly the squared error between true and predicted noise, weighted by 1/(2 d sigma_t^2 alpha_t) [eq_26]"
  - latex: "\\bb{E}_{\\vx_{0}, \\vx_1 \\sim q(\\vx_{0}, \\vx_1)} \\left[ - \\log p_^{(1)}(\\vx_0 | \\vx_1) \\right] \\equiv \\bb{E}\\left[\\frac{\\norm{\\epsilon - \\epsilon_{}^{(1)}(\\vx_1)}_2^2}{2 d \\sigma_1^2 \\alpha_1}\\right]"
    why: "The t=1 reconstruction term collapses to the identical noise-squared-error form by the same argument, so no special-cased likelihood is needed [eq_27]"
  - latex: "J_\\sigma(\\epsilon_) \\equiv \\sum_{t=1}^{T} \\frac{1}{2 d \\sigma_t^2 \\alpha_t} \\bb{E}\\left[\\norm{\\epsilon_{}^{(t)}(\\vx_t) - \\epsilon_t}_2^2 \\right] = L_\\gamma(\\epsilon_)"
    why: "Summing every t shows J_sigma equals L_gamma, the weighted noise-prediction loss already used to train DDPM, so training is unaffected by the choice of sigma [eq_28]"
```

**DDIM's ODE equals the VE-SDE probability-flow ODE.** The reparametrization step establishes a bijection between the two time variables, and the two independently-derived ODEs become the same equation once the score is rewritten via the noise predictor [§sec_10].

```derivation
shape: Show the continuous-time DDIM update and the VE-SDE probability-flow ODE are the same ODE.
steps:
  - latex: "\\bar{\\vx}(t) = \\bar{\\vx}(0) + \\sigma(t) \\epsilon, \\quad \\epsilon \\sim \\gN(0, \\mI)"
    why: "Defines a VE-SDE-style variable bar-x(t) with noise scale sigma(t), the convention the DDIM recursion will be rewritten into [eq_29]"
  - latex: "\\frac{\\vx(t)}{\\sqrt{\\alpha(t)}} = \\frac{\\vx(0)}{\\sqrt{\\alpha(0)}} + \\sqrt{\\frac{1 - \\alpha(t)}{\\alpha(t)}} \\epsilon, \\quad \\epsilon \\sim \\gN(0, \\mI)"
    why: "Rescaling DDIM's x(t) by 1/sqrt(alpha(t)) puts its marginal in the same additive-noise form as bar-x(t), giving the bijection between the two time parametrizations [eq_30]"
  - latex: "\\frac{\\vx_{t-\\Delta t}}{\\sqrt{\\alpha_{t-\\Delta t}}} = \\frac{\\vx_t}{\\sqrt{\\alpha_t}} + \\left(\\sqrt{\\frac{1 - \\alpha_{t-\\Delta t}}{\\alpha_{t-\\Delta t}}} - \\sqrt{\\frac{1 - \\alpha_{t}}{\\alpha_t}}\\right) \\epsilon_^{(t)}(\\vx_t)"
    why: "The DDIM sampling recursion, rewritten in the rescaled variable, becomes a finite difference in sigma(t) rather than in alpha_t [eq_32]"
  - latex: "\\frac{\\diff \\bar{\\vx}(t)}{\\diff t} = \\frac{\\diff \\sigma(t)}{\\diff t} \\epsilon_^{(t)}\\left(\\frac{\\bar{\\vx}(t)}{\\sqrt{\\sigma^2(t) + 1}}\\right)"
    why: "Taking the step size to zero turns the finite difference into the DDIM sampling ODE [eq_34]"
  - latex: "\\epsilon_^{(t)} = \\argmin_{f_t} \\bb{E}_{\\vx(0) \\sim q(\\vx), \\epsilon \\sim \\gN(0, \\mI)}[\\norm{f_t(\\vx(t)) - \\epsilon}_2^2]"
    why: "The optimal noise predictor is the denoising-score-matching minimizer on the DDIM side [eq_35]"
  - latex: "\\diff \\bar{\\vx} = -\\frac{1}{2} g(t)^2 \\nabla_{\\bar{\\vx}} \\log p_t(\\bar{\\vx}) \\diff t"
    why: "The general probability-flow ODE for the VE-SDE, written in terms of the score of the perturbed data distribution [eq_36]"
  - latex: "\\nabla_{\\bar{\\vx}} \\log p_t = \\argmin_{g_t} \\bb{E}_{\\vx(0) \\sim q(\\vx), \\epsilon \\sim \\gN(0, \\mI)}[\\norm{g_t(\\bar{\\vx}) + \\epsilon / \\sigma(t)}_2^2]"
    why: "The score is likewise the minimizer of a denoising objective on the VE-SDE side; matching this minimizer to eq_35's gives the identity score = -epsilon_theta/sigma(t) [eq_37]"
  - latex: "\\diff \\bar{\\vx}(t) = \\frac{1}{2} \\frac{\\diff \\sigma^2(t)}{\\diff t} \\frac{\\epsilon_^{(t)}\\left(\\frac{\\bar{\\vx}(t)}{\\sqrt{\\sigma^2(t) + 1}}\\right)}{\\sigma(t)} \\diff t"
    why: "Substituting the score-equivalence and the definition of sigma(t) into the VE-SDE ODE gives this intermediate form [eq_38]"
  - latex: "\\frac{\\diff \\bar{\\vx}(t)}{\\diff t} = \\frac{\\diff \\sigma(t)}{\\diff t} \\epsilon_^{(t)}\\left(\\frac{\\bar{\\vx}(t)}{\\sqrt{\\sigma^2(t) + 1}}\\right)"
    why: "Rearranging terms (using d(sigma^2)/dt = 2 sigma d(sigma)/dt) reproduces exactly the DDIM ODE derived above, confirming the two processes coincide given matching initial conditions [eq_39]"
```

## Go Deeper {#go-deeper}

- σ_t stays a free parameter throughout every proof — marginal preservation and loss equivalence hold for any choice, which is exactly why [[q_sigma(x_1:T|x_0) Construction]] can dial σ_t from the full DDPM variance down to σ_t=0 (deterministic DDIM) without touching training [§sec_10].
- The ODE-equivalence proof treats t as continuous, a limit the discrete DDIM schedule only approximates; the supplied evidence gives no discretization-error bound for finite step counts [§sec_10].
- No global context beyond the concept's placement under [[q_sigma(x_1:T|x_0) Construction]] was supplied, so the intuition here is built directly from the local proof text rather than outside framing.

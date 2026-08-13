# Objective $L_\gamma$

## TL;DR {#tldr}
$L_\gamma$ is a family of weighted denoising losses, one per choice of weights $\gamma_t$. DDIM proves that for every non-Markovian variance schedule $\sigma$, the true variational objective $J_\sigma$ equals some $L_\gamma$ plus a constant — so one trained model serves every $\sigma$ in the family.

## Intuition {#intuition}
Treat $L_\gamma$ as a recipe, not a single formula: predict the noise in $x_t$ at every timestep, weight each timestep's error by $\gamma_t$, and sum. DDPM already trains with one member of this family.

DDIM's contribution is showing that recipe also happens to be the correct training objective for a whole family of generative processes indexed by $\sigma$ — without any retraining needed as $\sigma$ changes.

## Mechanics {#mechanics}
The generative process starts from one trained prediction: given noisy $x_t$, the network $\epsilon_\theta^{(t)}$ predicts the noise that was added, and inverting the forward corruption turns that noise prediction into a prediction of $x_0$ [eq_7].

For $t>1$, this predicted $x_0$ is substituted into $q_\sigma(x_{t-1}\mid x_t,x_0)$, the reverse conditional already fixed for the non-Markovian forward process, to define the generative step $p_\theta^{(t)}(x_{t-1}\mid x_t)$ [eq_8].

At $t=1$, the process instead samples from a Gaussian centered at the $x_0$ prediction with covariance $\sigma_1^2 I$; this boundary case is needed so the generative density is supported everywhere, including at $x_0$ itself [eq_8].

Training minimizes $J_\sigma$, the KL divergence between the forward process $q_\sigma(x_{1:T}\mid x_0)$ and the generative process $p_\theta(x_{0:T})$, with $p_\theta$ factorized according to [eq_8] and $q_\sigma$ factorized according to its own Markov-free definition [eq_9].

The paper's central claim removes an apparent problem: naively, $J_\sigma$ looks like a different objective for every variance schedule $\sigma$, but there exist weights $\gamma$ and a constant $C$ such that $J_\sigma = L_\gamma + C$ for any $\sigma$ [§sec_3_2].

That equivalence matters only because of how $L_\gamma$'s optimum behaves: if the network $\epsilon_\theta^{(t)}$ does not share parameters across timesteps, each summand of $L_\gamma$ is minimized independently, so the optimal $\theta^*$ does not depend on the weights $\gamma$ at all [§sec_3_2].

This shared optimum has two consequences [§sec_3_2]:

- It justifies DDPM's practice of training with $L_1$ — the equal-weighted, $\gamma$-independent member of the family — as a surrogate for the true variational lower bound [§sec_3_2].
- Since $J_\sigma$ equals some $L_\gamma$ plus a constant, its optimum is the same $\theta^*$, so $L_1$ is also a valid surrogate for $J_\sigma$, whatever $\sigma$ is chosen at sampling time [§sec_3_2].

In other words, a single model trained once with the simple $L_1$ noise-prediction loss already optimizes the variational objective for every generative process in the $\sigma$-indexed family, whatever variance schedule is chosen at sampling time [§sec_3_2].

## The Math {#the-math}
The chain from noise prediction to trainable objective has three pieces: how $x_0$ is predicted, how that prediction defines a generative step, and how those steps combine into the loss actually minimized [§sec_3_2].

$$f_^{(t)}(\vx_t) := (\vx_t - \sqrt{1 - \alpha_t} \cdot \epsilon_{}^{(t)}(\vx_t)) / \sqrt{\alpha_t}.$$
[eq_7]

```annotated-eq
latex: "f_^{(t)}(\\vx_t) := (\\vx_t - \\sqrt{1 - \\alpha_t} \\cdot \\epsilon_{}^{(t)}(\\vx_t)) / \\sqrt{\\alpha_t}."
terms:
  - tex: "\\epsilon_{}^{(t)}(\\vx_t)"
    role: 1
    words: "The network's prediction of the noise that was added to produce x_t, trained without ever seeing x_0 directly [eq_7]"
  - tex: "\\sqrt{1-\\alpha_t}"
    role: 2
    words: "The forward process's noise scale at step t, used to undo exactly the corruption that scale introduced [eq_7]"
  - tex: "\\sqrt{\\alpha_t}"
    role: 3
    words: "Rescales the denoised residual back onto the signal's original magnitude, inverting the forward corruption x_t = sqrt(alpha_t) x_0 + sqrt(1-alpha_t) epsilon_t [eq_7]"
```

A concrete case: with $\alpha_t = 0.81$, $x_t = 1.0$, and a noise prediction $\epsilon_\theta^{(t)}(x_t) = 0.2$, eq_7 gives $f_\theta^{(t)}(x_t) = (1.0 - \sqrt{0.19}\cdot 0.2)/\sqrt{0.81} \approx (1.0 - 0.087)/0.9 \approx 1.014$ as the predicted $x_0$ [eq_7].

$$p_^{(t)}(\vx_{t-1} | \vx_t) = \begin{cases}
    \gN(f_^{(1)}(\vx_1), \sigma_1^2 \mI)  & \text{if} \ t = 1 \\
    q_\sigma(\vx_{t-1} | \vx_t, f_{}^{(t)}(\vx_t)) & \text{otherwise,}
    \end{cases}$$
[eq_8]

Both branches reuse the same reverse conditional $q_\sigma$: the $t=1$ branch is what that conditional degenerates to once $x_0$ is replaced by its own prediction and given a fixed variance, so the piecewise definition is one formula evaluated two ways [eq_8].

$$\begin{aligned}
& J_\sigma(\epsilon_) :=
   \bb{E}_{\vx_{0:T} \sim q_\sigma(\vx_{0:T})}[\log q_\sigma(\vx_{1:T} | \vx_0) - \log p_(\vx_{0:T})] \\
   = & \ \bb{E}_{\vx_{0:T} \sim q_\sigma(\vx_{0:T})} \left[\log q_\sigma(\vx_T | \vx_0) + \sum_{t=2}^{T} \log q_\sigma(\vx_{t-1} | \vx_t, \vx_0) - \sum_{t=1}^{T} \log p_^{(t)}(\vx_{t-1} | \vx_t) - \log p_(\vx_T) \right]
\end{aligned}$$
[eq_9]

```derivation
shape: Expand the variational bound J_σ into per-timestep KL terms.
steps:
  - latex: "J_\\sigma(\\epsilon_\\theta) := \\mathbb{E}_{q_\\sigma(x_{0:T})}[\\log q_\\sigma(x_{1:T}|x_0) - \\log p_\\theta(x_{0:T})]"
    why: "The training objective is the KL divergence between the fixed forward process and the trainable generative process, in expectation over real data [eq_9]"
  - latex: "= \\mathbb{E}_{q_\\sigma(x_{0:T})}\\Big[\\log q_\\sigma(x_T|x_0) + \\sum_{t=2}^{T}\\log q_\\sigma(x_{t-1}|x_t,x_0) - \\sum_{t=1}^{T}\\log p_\\theta^{(t)}(x_{t-1}|x_t) - \\log p_\\theta(x_T)\\Big]"
    why: "Factorizing both processes along the chain turns one global KL into a sum of per-timestep terms, each comparing the fixed reverse conditional to the trainable one [eq_9]"
```

## Go Deeper {#go-deeper}
This page sits one level under **Unified Variational Inference Objective**, the parent concept that ties $J_\sigma$, $L_\gamma$, and the theorem together into DDIM's core justification for training-free flexibility at sampling time.

The supplied evidence states the theorem's conclusion but not the explicit formula for $\gamma_t$ in terms of $\sigma$ and the noise schedule $\alpha_t$; that derivation lives in the paper's proof and is not reproduced here.

A useful check: if $\epsilon_\theta^{(t)}$ shares parameters across every $t$, as time-conditioned networks do in practice, does the parameter-sharing argument for $L_1$ still guarantee the same optimum as $J_\sigma$? The text's argument explicitly requires unshared parameters, so shared-parameter training is not covered by this guarantee [§sec_3_2].

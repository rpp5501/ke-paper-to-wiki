# Unified Variational Inference Objective
## TL;DR {#tldr}

DDIM trains one noise-prediction network $\epsilon_\theta$ and reuses it across an entire family of non-Markovian reverse processes indexed by $\sigma$.

The variational objective $J_\sigma$ that would need to be optimized for each $\sigma$ turns out to be equivalent (up to a constant) to some $L_\gamma$ from the DDPM objective family, so the same trained network is optimal for every $\sigma$ [§sec_3_2].

## Intuition {#intuition}

Picture the trained network as one tool: given a noisy $x_t$, it estimates the clean signal $x_0$ hiding inside it. Everything downstream — how noisy the next step $x_{t-1}$ should be — is decided by $\sigma$, a knob set at sampling time, not by the network [§sec_3_2].

Because the network only ever predicts $x_0$, the same weights serve a deterministic sampler ($\sigma=0$), a DDPM-like stochastic sampler, or anything in between. Retraining per $\sigma$ is unnecessary [§sec_3_2].

## Mechanics {#mechanics}

$f_\theta^{(t)}(x_t)$ is the network's point estimate of $x_0$: it inverts the forward marginal $q(x_t\mid x_0)$, so it needs only $x_t$ and the predicted noise $\epsilon_\theta^{(t)}(x_t)$, never $t$'s neighbors [eq_7].

$p_\theta^{(t)}(x_{t-1}\mid x_t)$ plugs that estimate into the same reverse conditional $q_\sigma(x_{t-1}\mid x_t, x_0)$ used to build the forward process, substituting $f_\theta^{(t)}(x_t)$ for the unknown $x_0$ [eq_8].

**Boundary case $t=1$:** there is no $x_0$ left to condition a reverse step on, so $p_\theta^{(1)}$ falls back to $\mathcal{N}(f_\theta^{(1)}(x_1), \sigma_1^2 I)$ instead of $q_\sigma$ [eq_8].

This added Gaussian noise gives the generative process full support everywhere, matching how the forward process also never collapses to a delta at $x_0$ [§sec_3_2].

```algorithm
title: Generative step at time t (Eq. 7–8)
lines:
  - code: "xhat0 = f_theta^{(t)}(x_t) = (x_t - sqrt(1-alpha_t) * eps_theta^{(t)}(x_t)) / sqrt(alpha_t)"
    intent: "The network predicts x0 from the noisy x_t via the same closed form used to define x_t from x0 in the forward process [eq_7]"
  - code: "if t == 1: x_0 = xhat0 + sigma_1 * noise"
    intent: "There is no further x_{t-1} to sample at the last step; a small Gaussian keeps p_theta supported everywhere [eq_8]"
  - code: "else: x_{t-1} ~ q_sigma(x_{t-1} | x_t, xhat0)"
    intent: "Otherwise the predicted x0 is plugged into the same non-Markovian posterior used to build the forward process [eq_8]"
```

$J_\sigma$ is the ELBO for this generative process: it factorizes $q_\sigma(x_{1:T}\mid x_0)$ along the non-Markovian forward process and $p_\theta(x_{0:T})$ along the $p_\theta^{(t)}$ chain just defined [eq_9].

Written this way, $J_\sigma$ looks like it needs a separate network per $\sigma$, since each $\sigma$ defines a different $q_\sigma$ and hence a different objective [§sec_3_2].

## The Math {#the-math}

$$
f_^{(t)}(\vx_t) := (\vx_t - \sqrt{1 - \alpha_t} \cdot \epsilon_{}^{(t)}(\vx_t)) / \sqrt{\alpha_t}.
$$
[eq_7]

This is the closed-form inverse of the forward marginal $x_t=\sqrt{\alpha_t}x_0+\sqrt{1-\alpha_t}\epsilon$: solve that relation for $x_0$ and replace the unknown $\epsilon$ with the network's prediction $\epsilon_\theta^{(t)}(x_t)$ [eq_7].

$$
p_^{(t)}(\vx_{t-1} | \vx_t) = \begin{cases}
    \gN(f_^{(1)}(\vx_1), \sigma_1^2 \mI)  & \text{if} \ t = 1 \\
    q_\sigma(\vx_{t-1} | \vx_t, f_{}^{(t)}(\vx_t)) & \text{otherwise,}
    \end{cases}
$$
[eq_8]

The two cases were already walked through in Mechanics: a Gaussian fallback at $t=1$, and the learned posterior $q_\sigma$ with $x_0$ replaced by its estimate everywhere else [eq_8].

$$
\begin{aligned}
& J_\sigma(\epsilon_) :=
   \bb{E}_{\vx_{0:T} \sim q_\sigma(\vx_{0:T})}[\log q_\sigma(\vx_{1:T} | \vx_0) - \log p_(\vx_{0:T})] \\
   = & \ \bb{E}_{\vx_{0:T} \sim q_\sigma(\vx_{0:T})} \left[\log q_\sigma(\vx_T | \vx_0) + \sum_{t=2}^{T} \log q_\sigma(\vx_{t-1} | \vx_t, \vx_0) - \sum_{t=1}^{T} \log p_^{(t)}(\vx_{t-1} | \vx_t) - \log p_(\vx_T) \right]
\end{aligned}
$$
[eq_9]

```annotated-eq
latex: "\\log q_\\sigma(\\vx_T | \\vx_0) + \\sum_{t=2}^{T} \\log q_\\sigma(\\vx_{t-1} | \\vx_t, \\vx_0) - \\sum_{t=1}^{T} \\log p_^{(t)}(\\vx_{t-1} | \\vx_t) - \\log p_(\\vx_T)"
terms:
  - tex: "\\log q_\\sigma(\\vx_T | \\vx_0)"
    role: 1
    words: "Entropy of the fixed forward endpoint — a constant that contributes no gradient during training [eq_9]"
  - tex: "\\sum_{t=2}^{T} \\log q_\\sigma(\\vx_{t-1} | \\vx_t, \\vx_0)"
    role: 2
    words: "The known reverse posteriors defining the non-Markovian forward process — fixed, not learned [eq_9]"
  - tex: "\\sum_{t=1}^{T} \\log p_^{(t)}(\\vx_{t-1} | \\vx_t)"
    role: 3
    words: "The learned generative chain from [eq_8] — the only term the network's gradient touches [eq_9]"
  - tex: "\\log p_(\\vx_T)"
    role: 4
    words: "Log-density under the fixed Gaussian prior [eq_9]"
```

Only the middle sum carries trainable parameters, which is why $J_\sigma$ reduces at each $t$ to a regression from $\epsilon_\theta^{(t)}(x_t)$ toward the true noise $\epsilon$ [§sec_3_2].

## Go Deeper {#go-deeper}

**The unification theorem:** for every $\sigma$, there exist weights $\gamma$ such that $J_\sigma$ equals $L_\gamma$ plus a constant — the same objective family DDPM used, just reweighted per timestep [§sec_3_2].

When parameters aren't shared across $t$ in $\epsilon_\theta$, $L_\gamma$'s optimum is reached by maximizing each timestep's term separately — so it doesn't depend on $\gamma$ at all [§sec_3_2].

Since $J_\sigma \equiv L_\gamma$ for some $\gamma$, the same argument carries over: the optimal $\epsilon_\theta$ for $J_\sigma$ doesn't depend on $\sigma$ either, so one training run serves every generative process in the family [§sec_3_2].

That's what licenses reusing DDPM's $L_\gamma$-style surrogate as the training objective for DDIM's family of samplers: train once with the familiar objective, then choose $\sigma$ — including $\sigma=0$ for the deterministic DDIM sampler — at generation time [§sec_3_2].

The evidence states this theorem but doesn't include its proof — the paper marks it as proved elsewhere and only gives the statement here [§sec_3_2].

So the mechanism connecting $J_\sigma$ to $L_\gamma$ — which weights $\gamma$ arise, and why the sum decomposes cleanly per timestep — can't be reconstructed from what's supplied here [§sec_3_2].

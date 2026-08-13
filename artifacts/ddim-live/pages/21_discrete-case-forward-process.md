I'll rewrite the page now, fixing the flagged paragraphs by splitting them at their natural conceptual seams while keeping everything else the same.

# Non-Markovian Forward Process (Discrete Case)

## TL;DR {#tldr}
The paper extends its non-Markovian, DDIM-style forward process from continuous Gaussian data to categorical, one-hot data. The reverse posterior stays a simple three-way mixture, the KL divergence between true and learned reverse steps is closed-form, and training reduces to an ordinary multi-class classification loss.

## Intuition {#intuition}

The same non-Markovian, DDIM-style construction the paper builds for Gaussian-noised images can be repeated for categorical data. A label just has three things that can happen to it at each step instead of a continuous perturbation.

**Why bother with a discrete version at all?** It shows the trick behind DDIM's speedup isn't tied to Gaussian noise specifically. Choosing a non-Markovian process with the right marginals, then training a reverse model on a closed-form KL, works the same way for a one-hot class label.

At every step, a label either stays at its current noisy value, gets redrawn toward the model's guessed original label, or gets replaced with pure uniform noise. As the reverse sampler's noise parameter shrinks toward zero, this stops being exploratory: the model overwhelmingly keeps the noisy label or commits to its single best prediction, rather than spreading probability across every class.

## Mechanics {#mechanics}

The data $\vx_0$ is a one-hot vector over $K$ classes. As in the continuous case, the forward process is defined by first fixing a per-step marginal, before any reverse model is introduced [§sec_9].

**Forward marginal.** $q(\vx_t \mid \vx_0)$ is a categorical distribution that mixes the true one-hot vector with a uniform vector $\vone_K$, weighted by a schedule $\alpha_t$ that decreases from near $1$ at $t=0$ to near $0$ at $t=T$ [eq_15].

**Reverse posterior.** Conditioned on both the noisy label $\vx_t$ and the true label $\vx_0$, $q(\vx_{t-1}\mid\vx_t,\vx_0)$ is a three-way mixture over what $\vx_{t-1}$ becomes [eq_16]:

- With probability $\sigma_t$, $\vx_{t-1}$ copies the current noisy state $\vx_t$ [eq_16]
- With probability $\alpha_{t-1}-\sigma_t\alpha_t$, $\vx_{t-1}$ copies the true label $\vx_0$ [eq_16]
- With probability $(1-\alpha_{t-1})-(1-\alpha_t)\sigma_t$, $\vx_{t-1}$ is replaced by pure uniform noise $\vone_K$ [eq_16]

Written as a single categorical instead of a case split, these same three probabilities become mixture weights on $\vx_t$, $\vx_0$, and $\vone_K$ directly — the two forms are algebraically identical [eq_17].

**Parametrizing the reverse model.** The learned reverse step $p_\theta(\vx_{t-1}\mid\vx_t)$ mirrors this posterior exactly, but substitutes the unknown $\vx_0$ with a network prediction $f_\theta^{(t)}(\vx_t)$, a $K$-dimensional vector guessed from the noisy input [eq_18].

As $\sigma_t \to 0$, the mixture weight on pure noise shrinks along with the weight on copying $\vx_t$, so sampling grows less stochastic and increasingly deterministic given the model's prediction [§sec_9].

Because $q(\vx_{t-1}\mid\vx_t,\vx_0)$ and $p_\theta(\vx_{t-1}\mid\vx_t)$ are both categorical, the KL divergence between them is well-defined and closed-form — simply the KL between two categoricals, with no Monte Carlo estimate needed [eq_19].

**Training objective.** Because both $q(\vx_{t-1} \mid \vx_t, \vx_0)$ and $p_\theta(\vx_{t-1}\mid\vx_t)$ are categoricals whose weight on $\vx_0$ versus $f_\theta^{(t)}(\vx_t)$ dominates as $\sigma_t\to0$, the KL between them is bounded above using convexity of KL divergence [eq_20].

That bound scales the KL between $\mathrm{Cat}(\vx_0)$ and $\mathrm{Cat}(f_\theta^{(t)}(\vx_t))$ by the factor $(\alpha_{t-1}-\sigma_t\alpha_t)$, and is tight as the right-hand side goes to zero [eq_20].

## The Math {#the-math}

The forward marginal mixes the true one-hot value with uniform noise via a decreasing schedule $\alpha_t$ [eq_15]:

$$
q(\vx_t | \vx_0) = \mathrm{Cat}(\alpha_t \vx_0 + (1 - \alpha_t) \vone_K)
$$
[eq_15]

The reverse posterior conditioned on both $\vx_t$ and $\vx_0$ is a three-branch categorical, matching the case split described in Mechanics [eq_16]:

$$
q(\vx_{t-1} | \vx_t, \vx_0) = \begin{cases}
    \mathrm{Cat}(\vx_t) & \text{with probability } \sigma_t \\
    \mathrm{Cat}(\vx_0) & \text{with probability } (\alpha_{t-1} - \sigma_t \alpha_t) \\
    \mathrm{Cat}(\vone_K) & \text{with probability } (1 - \alpha_{t-1}) - (1 - \alpha_t) \sigma_t
    \end{cases},
$$
[eq_16]

The same posterior, written as one categorical instead of a case split, sums the three branches into a single probability vector [eq_17]:

$$
q(\vx_{t-1} | \vx_t, \vx_0) = \mathrm{Cat}\left(\sigma_t \vx_t + (\alpha_{t-1} - \sigma_t \alpha_t) \vx_0 + ((1 - \alpha_{t-1}) - (1 - \alpha_t) \sigma_t) \vone_K\right),
$$
[eq_17]

Substituting the network's prediction $f_\theta^{(t)}(\vx_t)$ for the unknown $\vx_0$ gives the trainable reverse step [eq_18]:

$$
p_(\vx_{t-1} | \vx_t) = \mathrm{Cat}\left(\sigma_t \vx_t + (\alpha_{t-1} - \sigma_t \alpha_t) f_^{(t)}(\vx_t) + ((1 - \alpha_{t-1}) - (1 - \alpha_t) \sigma_t) \vone_K\right),
$$
[eq_18]

Training compares this reverse step against the true posterior with a closed-form categorical KL divergence [eq_19]:

$$
\KL(q(\vx_{t-1} | \vx_t, \vx_0) \Vert p_(\vx_{t-1} | \vx_t))
$$
[eq_19]

Convexity of KL divergence turns this per-step term into an upper bound [eq_20]:

$$
\KL(q(\vx_{t-1} | \vx_t, \vx_0) \Vert p_(\vx_{t-1} | \vx_t)) \leq (\alpha_{t-1} - \sigma_t \alpha_t) \KL(\mathrm{Cat}(\vx_0) \Vert \mathrm{Cat}(f_^{(t)}(\vx_t))).
$$
[eq_20]

The right-hand side of [eq_20] is, up to constants, a multi-class classification loss: it compares the true label $\vx_0$ against the model's predicted label distribution $f_\theta^{(t)}(\vx_t)$ [eq_20].

This mirrors the paper's argument for the Gaussian case — changing $\sigma_t$ reweights the loss but does not change what minimizing it accomplishes, since the bound is tight as it goes to zero [eq_20].

## Go Deeper {#go-deeper}

The paper explicitly leaves empirical evaluation of this discrete construction as future work, so no results, ablations, or sample quality figures are supplied for it [§sec_9]. The construction is presented purely to show that the non-Markovian, DDIM-style forward process is not special to Gaussian diffusion — the same freedom to choose $q(\vx_{t-1}\mid\vx_t,\vx_0)$ subject to fixed marginals, and the same collapse of the training objective to a familiar loss, carries over to categorical data [§sec_9].

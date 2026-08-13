# Discussion
## TL;DR {#tldr}

DDIM reframes diffusion sampling as a purely variational, non-Markovian construction, buying faster sampling and latent-space interpolation without changing the training objective [§sec_7]. The discussion then opens four directions it does not resolve: non-Gaussian continuous noise, discrete forward processes, ODE-solver techniques for fewer steps, and links to other implicit generative models [§sec_7].

## Intuition {#intuition}

DDIM's core move was to loosen the forward process from a fixed Markov chain to a family of non-Markovian processes that still match DDPM's training objective. The discussion asks what that loosening makes possible now that it exists [§sec_7].

Four threads follow from the same insight:

- Swap Gaussian noise for another continuous distribution, now that Markovianity no longer forces it [§sec_7].
- Swap continuous noise for a discrete, combinatorial forward process, as already sketched for the multinomial case [§sec_7].
- Borrow ODE-solver techniques such as multi-step methods to cut sampling steps further [§sec_7].
- Check whether DDIM shares other properties of existing implicit generative models [§sec_7].

None of these are worked out in the paper; they are proposed as future work [§sec_7].

## Mechanics {#mechanics}

DDIM generates high-quality samples more efficiently than existing DDPMs and NCSNs [§sec_7].

It also supports meaningful interpolation in the latent space, a property the paper attributes directly to its deterministic, non-Markovian sampling path [§sec_7].

The non-Markovian construction is not special to Gaussian noise. The paper reads this as evidence that other continuous forward processes could work, a possibility the original Markovian diffusion framework closes off [§sec_7].

The paper reports a second demonstration: a discrete forward process built on a multinomial distribution, described in the appendix. It treats this as evidence that the non-Markovian idea generalizes past continuous noise to other combinatorial structures [§sec_7].

The sampling procedure is structurally similar to solving a neural ODE, since each step is a deterministic update rather than a stochastic transition. That similarity is what motivates comparing DDIM's sampler to the numerical-ODE literature [§sec_7].

The paper flags one open comparison without resolving it: whether DDIM shares other known properties of implicit generative models beyond efficient sampling and interpolation [§sec_7].

## The Math {#the-math}

A probability distribution is stable if a sum of independent copies of it, rescaled, has the same distribution again — Gaussian, Cauchy, and Lévy distributions all have this property [§sec_7].

Diffusion's forward process repeatedly adds independent noise, so after many steps the marginal is, up to rescaling, a sum of stable draws. Closing that sum back into the same family requires a stable noise distribution [§sec_7].

Only Gaussian among the stable distributions has finite variance; Cauchy and other stable laws have infinite or undefined variance. That is why the paper calls Gaussian noise load-bearing for the original Markovian framework, and why breaking Markovianity is what frees the choice of noise distribution [§sec_7].

Treating DDIM's update as one step of Euler's method for an ODE gives a local error of order $h^2$ per step and a global error of order $h$ over the whole trajectory, where $h$ is the step size set by the number of sampling steps [§sec_7].

Multi-step methods such as Adams-Bashforth reuse the outputs of prior steps to fit a higher-order polynomial to the trajectory, instead of taking the tangent from a single point the way Euler-style updates do [§sec_7].

A higher-order method reaches the same global error at a larger step size, so the same fixed error budget can be hit with fewer sampling steps. That is the concrete mechanism behind the paper's suggestion that ODE solver theory could shrink DDIM's step count further [§sec_7].

## Go Deeper {#go-deeper}

The paper leaves each of its four directions as an open question rather than a result: no non-Gaussian continuous process is constructed, no comparison to Adams-Bashforth or other multi-step solvers is run, and no other combinatorial forward process beyond the multinomial case is tried [§sec_7].

It also does not specify which properties of existing implicit generative models would be worth testing against DDIM's sampling and interpolation behavior, leaving that comparison unscoped for future work [§sec_7].

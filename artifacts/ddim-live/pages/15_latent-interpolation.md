# Interpolation in Latent Space
## TL;DR {#tldr}
- DDIM turns denoising into a single deterministic function from latent $x_T$ to sample $x_0$, so two latents can be interpolated and pushed through that function to get a smooth, semantically meaningful path between two images.
- DDPM cannot do this: its generative process is stochastic, so the same $x_T$ produces different $x_0$ on different runs, and there is no fixed function to interpolate along.

## Intuition {#intuition}
Think of DDIM as a camera that always develops the same latent code into the same picture. GANs work this way too: a fixed generator network maps a latent vector to an image, which is why interpolating between two latent vectors traces a path through recognizably blended images.

DDIM inherits that property because its reverse process is a fixed deterministic map from $x_T$ to $x_0$, unlike DDPM's step-by-step noise injection [§sec_5_3].

DDPM behaves more like re-shooting a scene from scratch: even starting from the identical latent, random choices made at every step change the final image. There is nothing fixed to hold still while sliding from one latent to another [§sec_5_3].

## Mechanics {#mechanics}
DDIM's generative process is a deterministic map from a latent $x_T$ to a sample $x_0$, the same property behind sample consistency in DDIMs. Because the high-level features of a DDIM sample are encoded entirely in $x_T$, the paper asks whether the semantic interpolation effect seen in other implicit models — GANs in particular — appears here too [§sec_5_3].

This differs from interpolation in DDPM, where drawing a sample from the same $x_T$ multiple times would give highly diverse $x_0$ because the generative process there is stochastic rather than deterministic [§sec_5_3].

The paper shows that simple interpolation in $x_T$-space, pushed through this fixed map, produces samples that interpolate meaningfully in image space between the two endpoints — controlling the generated image directly through the latent variable, something DDPMs cannot do [§sec_5_3].

```figure
id: fig_6
caption: A line of latents $x_T$ mapped through DDIM's fixed generative function produces a smooth line of images, not a jump between unrelated samples [§sec_5_3]
```

The figure shows this directly: interpolating $x_T$ with $\dim(\tau) = 50$ produces a visibly continuous sequence of images between the two endpoints, rather than an abrupt swap [§sec_5_3].

## The Math {#the-math}
| Property | DDIM | DDPM |
|---|---|---|
| Map from $x_T$ to $x_0$ | Fixed deterministic function $f$ | Stochastic process, redrawn at every step [§sec_5_3] |
| Same $x_T$, run twice | Returns the same $x_0$ both times | Can return two different $x_0$ [§sec_5_3] |
| Interpolating $x_T^{(\alpha)}$, $\alpha \in [0,1]$ | Traces one path $x_0^{(\alpha)} = f(x_T^{(\alpha)})$ | No fixed path exists to trace [§sec_5_3] |

Consider two source latents $x_T^{(0)}$ and $x_T^{(1)}$, each mapped to a sample by DDIM's generative process [§sec_5_3].

Because that process is a fixed deterministic function of $x_T$, call it $f$: $x_0^{(0)} = f(x_T^{(0)})$ and $x_0^{(1)} = f(x_T^{(1)})$, computed by the same network weights along the same schedule both times [§sec_5_3].

Form an interpolated latent $x_T^{(\alpha)}$ between the two for $\alpha \in [0,1]$, and push it through the same $f$ to get $x_0^{(\alpha)} = f(x_T^{(\alpha)})$ [§sec_5_3].

Because $f$ is one fixed function, $x_0^{(\alpha)}$ changes continuously as $\alpha$ sweeps from 0 to 1, tracing a single path of outputs between the two endpoints — the mechanism the paper reports as semantically meaningful interpolation [§sec_5_3].

Now repeat the construction under DDPM, whose generative process is stochastic rather than a fixed function [§sec_5_3].

Sampling twice from the same $x_T^{(\alpha)}$ under DDPM draws two different noise sequences along the reverse chain, so it can return two different outputs $x_0$ rather than the single value $f(x_T^{(\alpha)})$ DDIM guarantees [§sec_5_3].

There is no single map to hold fixed while $\alpha$ varies, so there is no path for the interpolation to trace — the paper states this directly: the same $x_T$ would lead to highly diverse $x_0$ under DDPM's stochastic process [§sec_5_3].

## Go Deeper {#go-deeper}
- The paper notes it includes more interpolation details and samples in the appendix, beyond the figure's line of images [§sec_5_3].
- This interpolation ability rests entirely on DDIM's deterministic sampling, so it is downstream of sample consistency in DDIMs rather than an independent mechanism: the map $f$ has to be fixed before "interpolating between two images" is even well-defined [§sec_5_3].
- The same construction is how latent-space interpolation works in GANs, since a GAN generator is likewise a fixed deterministic function of its latent code — DDIM's implicit process gives diffusion models this same knob for the first time.

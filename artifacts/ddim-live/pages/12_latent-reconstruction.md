# Reconstruction from Latent Space

## TL;DR {#tldr}
DDIM's deterministic sampling map is (almost) invertible: encoding a real image backward along its ODE trajectory and then decoding forward again recovers the image, with the reconstruction error shrinking as more steps are used. DDPM has no such property because its sampling is stochastic.

## Intuition {#intuition}
DDIM treats sampling as tracing a fixed path between an image and its latent noise, not as a random walk. Encoding an image runs that path backward, from image to noise; decoding runs it forward again, from noise to image.

Because the path is deterministic, walking it backward and then forward again should land close to the starting point — like retracing footsteps rather than free-falling through changing weather. DDPM has no such trail: each step injects fresh noise, so there is nothing to retrace.

## Mechanics {#mechanics}
DDIM is the Euler integrator for a specific ODE, so the same deterministic map that samples an image from noise can also run in reverse, from image to noise [§sec_5_4].

The paper tests this on the CIFAR-10 test set using the CIFAR-10 model, running S steps to encode an image to its latent and S steps to decode back, and reporting the per-dimension MSE between original and reconstruction, scaled to $[0,1]$ [§sec_5_4].

```algorithm
title: DDIM encode-decode round trip (Section 5.4)
lines:
  - code: "x_T = encode(x_0, S)      # reverse ODE, S Euler steps, image -> noise"
    intent: "Walks the deterministic reverse trajectory backward from the real image to its latent, using S discrete Euler steps [§sec_5_4]"
  - code: "x_0_hat = decode(x_T, S)  # forward ODE, S Euler steps, noise -> image"
    intent: "Walks the same trajectory forward from the recovered latent, using the same S steps as encoding [§sec_5_4]"
  - code: "error = mean((x_0 - x_0_hat)**2)"
    intent: "Per-dimension MSE measures how far the round trip drifts from the original image, reported for S=10..1000 [tab_2]"
```

The round trip approximately inverts because DDIM always follows the same deterministic map between $x_0$ and $x_T$ in both directions, unlike DDPM's stochastic step [§sec_5_4].

Because each direction takes only S discrete Euler steps rather than continuous integration, encoding and decoding trace slightly different discretizations of the same underlying ODE trajectory, leaving a residual gap that these results measure directly [§sec_5_4].

DDPM lacks this property because its sampling process is stochastic: each reverse step injects fresh Gaussian noise, so there is no single deterministic trajectory to retrace back to the original image [§sec_5_4].

**Results.** Reconstruction error falls monotonically as S grows, from 0.0140 at S=10 down to 0.0001 at S≥500 [tab_2].

| S (steps) | Per-dim MSE |
|---|---:|
| 10 | 0.0140 [tab_2] |
| 20 | 0.0065 [tab_2] |
| 50 | 0.0023 [tab_2] |
| 100 | 0.0009 [tab_2] |
| 200 | 0.0004 [tab_2] |
| 500 | 0.0001 [tab_2] |
| 1000 | 0.0001 [tab_2] |

## The Math {#the-math}
**Worked example: does error scale as $1/S$?** Multiplying S by its error should give a roughly constant value if error is proportional to $1/S$: 10 times 0.0140 equals 0.14, 100 times 0.0009 equals 0.09, and 200 times 0.0004 equals 0.08, all within the same order of magnitude rather than drifting with $S$ [tab_2].

The doubling steps in the table make the pattern sharper:

- S = 10 → 20 (a doubling of steps): error falls from 0.0140 to 0.0065, a ratio of 0.46 — close to the 0.5 an $O(1/S)$ error predicts [tab_2].
- S = 100 → 200 (a doubling of steps): error falls from 0.0009 to 0.0004, a ratio of 0.44 — again close to 0.5 [tab_2].
- S = 500 → 1000 (a doubling of steps): error stays at 0.0001 rather than halving, but the table is rounded to $10^{-4}$, so this floor likely hides a real decrease [tab_2].

This $O(1/S)$ scaling matches what a first-order integrator predicts: DDIM takes S Euler steps of size $h=1/S$ along the probability-flow ODE, and a first-order method's global error accumulates as $O(h)=O(1/S)$, so doubling S should roughly halve the error — which the ratios above confirm [§sec_5_4].

## Go Deeper {#go-deeper}
The $S=500 \to 1000$ tie is a good place to push further: is it purely the table's rounding to $10^{-4}$, or does the discretization error saturate against some other source of imperfection (model error, floating-point precision) once it gets small enough? The paper doesn't report unrounded values, so this is open.

This near-invertibility is also the empirical grounding for the paper's comparison of DDIM to Neural ODEs and normalizing flows — both families are valued precisely because their forward and inverse maps agree. Worth connecting back to [[Euler Integration / ODE Connection]] to see why a *higher*-order integrator (not just more steps) would be the natural next lever on this error.

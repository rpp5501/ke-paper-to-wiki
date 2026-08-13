# Datasets and Architectures

## TL;DR {#tldr}
DDIM reuses DDPM's own trained models — same datasets, same U-Net weights, same hyperparameter heuristic — and changes only the sampling process, so any speed or quality difference reported later can be attributed to the generative process itself [§sec_12_1].

## Intuition {#intuition}
DDIM's central claim is about a faster *sampling* procedure, not a better-trained network. If the authors had retrained fresh models for their experiments, an improvement in FID could just as easily come from a lucky training run as from the new sampling process. Reusing DDPM's exact checkpoints wherever they exist removes that confound and leaves the generative process as the only variable under test.

## Mechanics {#mechanics}
- Four datasets span resolution and content diversity: CIFAR10 (unconditional), CelebA, LSUN Bedroom, and LSUN Church test whether the change in generative process holds from small low-resolution images up to large scene photos [§sec_12_1].
- Hyperparameters follow the DDPM heuristic for every dataset, so any performance gap reported for DDIM versus DDPM is not confounded by a retuned model [§sec_12_1].
- One architecture serves all datasets: a U-Net built on a Wide ResNet, matching the network DDPM itself used [§sec_12_1].
- CIFAR10, Bedroom, and Church all use pretrained checkpoints taken directly from the original DDPM implementation, since those were already trained and public [§sec_12_1].
- CelebA is the exception: no DDPM checkpoint was released for it, so the authors trained their own model with the same denoising objective, on the original (non-HQ) CelebA dataset processed with the StyleGAN repository's dataset tool [§sec_12_1].
- Their CelebA model uses five feature-map resolutions, giving the U-Net enough downsampling depth to compress a full face image to a coarse bottleneck and back [§sec_12_1].

## The Math {#the-math}
At ten sampling steps the deterministic and stochastic processes are far apart: DDIM's Bedroom FID of 16.95 is well under half of DDPM's 42.78, a roughly 2.5x gap showing that with few steps the deterministic process front-loads sample quality far better than the stochastic one [tab_3].

That gap closes as the step budget grows: by 100 steps DDIM's Bedroom FID (6.62) and DDPM's (6.81) differ by only 0.19, meaning stochastic sampling needs many steps to average out its own injected noise but eventually nearly matches the deterministic process [tab_3].

Church shows the same shrinking gap but with a reversal: at 50 steps DDPM (11.16) is already close to DDIM (10.84), and by 100 steps DDPM pulls ahead to 8.27 against DDIM's 10.58, so on this harder scene dataset added stochasticity becomes an advantage once enough steps are available [tab_3].

| dim(τ) | Bedroom DDIM (η=0) | Bedroom DDPM (η=1) | Church DDIM (η=0) | Church DDPM (η=1) |
|---|---|---|---|---|
| 10 | 16.95 | 42.78 | 19.45 | 51.56 [tab_3] |
| 20 | 8.89 | 22.77 | 12.47 | 23.37 [tab_3] |
| 50 | 6.75 | 10.81 | 10.84 | 11.16 [tab_3] |
| 100 | 6.62 | 6.81 | 10.58 | 8.27 [tab_3] |

## Go Deeper {#go-deeper}
This fixed-model setup is what makes the sample-quality-versus-efficiency comparisons elsewhere in the paper interpretable: since the network and its trained weights never change, every FID difference reported across step counts and datasets isolates the effect of the generative process alone, which is the quantity the rest of the "Sample Quality and Efficiency" results are built to measure.

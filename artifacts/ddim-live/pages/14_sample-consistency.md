# Sample Consistency in DDIMs

## TL;DR {#tldr}

DDIM's deterministic sampling means the same starting noise $x_T$ produces images with the same high-level content, no matter how many steps the trajectory takes to get there [§sec_5_2].

## Intuition {#intuition}

Fix $x_T$ and run DDIM. Then vary only the number of denoising steps. The resulting images share their high-level features — pose, layout, overall identity — even though one trajectory took 20 steps and another took 1000 [§sec_5_2].

This suggests $x_T$ behaves like a compact code for the image's identity, while the sampling trajectory fills in fine detail [§sec_5_2].

## Mechanics {#mechanics}

DDIM's generative process is deterministic once $x_T$ is fixed: no noise is injected at any step after the initial sample, so the entire trajectory is a fixed function of $x_T$ [§sec_5_2].

The paper's experiment fixes $x_T$ and varies the number of sampling steps, then compares the resulting images [§sec_5_2] [fig_5].

```figure
id: fig_5
caption: The same $x_T$ decoded via trajectories of different length — high-level content matches across step counts, while fine detail differs [§sec_5_2]
```

Samples produced with only 20 steps already closely resemble samples produced with 1000 steps, in terms of high-level features [§sec_5_2].

Only minor details differ between the short and long trajectories, since detail quality — not overall content — is what benefits from extra steps [§sec_5_2].

$x_T$ alone functions as an informative latent encoding of the image's high-level content [§sec_5_2].

The step count instead controls detail quality: longer trajectories refine texture and fine structure without altering the image's identity [§sec_5_2].

## The Math {#the-math}

**Boundary case — 20 vs. 1000 steps:** both trajectories start from the same $x_T$ and apply the deterministic DDIM update, but one takes 50x fewer steps than the other [§sec_5_2].

Despite this 50x difference in step count, the two trajectories converge to images sharing the same high-level features — the extra 980 steps refine detail rather than change identity [§sec_5_2].

This behavior stems from determinism: since no randomness enters after $x_T$ is chosen, each trajectory is a fixed function of $x_T$ alone, so re-running the same $x_T$ cannot introduce variation [§sec_5_2].

## Go Deeper {#go-deeper}

Because $x_T$ behaves as a stable high-level encoding, this consistency property underlies interpolation in latent space: interpolating between two $x_T$ values produces a smooth interpolation between the corresponding images' high-level content [§sec_5_2].

The paper reports additional samples demonstrating this consistency in its appendix [§sec_5_2].

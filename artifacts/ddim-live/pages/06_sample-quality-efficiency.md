# Sample Quality and Efficiency

## TL;DR {#tldr}
DDIM reaches sample quality close to a 1000-step DDPM using only 20–100 steps, a 10× to 50× speedup, because its non-stochastic reverse process degrades gracefully as steps are removed while DDPM's stochastic process does not [§sec_5_1].

## Intuition {#intuition}
Fewer sampling steps means a bigger jump between consecutive noise levels. A stochastic reverse process injects fresh random noise at each jump, so large jumps let that noise dominate the signal [§sec_5_1].

DDIM's deterministic reverse process injects no such noise, so it tolerates large jumps far better than a stochastic one at the same step count [§sec_5_1].

This is why $\dim(\tau)$ and $\eta$ act as two separate knobs on one trade-off: $\dim(\tau)$ sets the compute budget, and $\eta$ sets how much of that budget goes to fighting self-inflicted stochasticity [§sec_5_1].

## Mechanics {#mechanics}
The paper measures FID on CIFAR10 and CelebA while varying the number of sampling steps $\dim(\tau)$ (10, 20, 50, 100, 1000) and the stochasticity $\eta$ (0.0, 0.2, 0.5, 1.0, and $\hat{\sigma}$) [tab_1].

| $\eta$ / $S$ (CIFAR10) | 10 | 20 | 50 | 100 | 1000 |
|---|---|---|---|---|---|
| 0.0 (DDIM) | 13.36 | 6.84 | 4.67 | 4.16 | 4.04 [tab_1] |
| 1.0 (DDPM) | 41.07 | 18.36 | 8.01 | 5.78 | 4.73 [tab_1] |
| $\hat{\sigma}$ (DDPM) | 367.43 | 133.37 | 32.72 | 9.99 | 3.17 [tab_1] |

DDIM ($\eta=0$) gets the lowest FID at every step count except $\dim(\tau)=1000$ with $\hat\sigma$, where it is only marginally worse [tab_1].

DDPM ($\eta=1$) degrades far more steeply as steps drop: its FID rises 8.7× from 1000 to 10 steps (4.73 → 41.07), while DDIM's rises only 3.3× over the same range (4.04 → 13.36) [tab_1].

$\hat\sigma$ is well suited to long trajectories, reaching FID 3.17 at 1000 steps on CIFAR10 — the best score in the table [tab_1].

```figure
id: fig_3
caption: Under a 10-step trajectory, DDPM and $\hat{\sigma}$ samples carry visible noisy artifacts that DDIM's do not, which is what drives their much worse FID at short trajectories [fig_3]
```

At 10 steps $\hat\sigma$'s FID reaches 367.43, over 27× worse than DDIM's 13.36; fig_3 shows visible noisy perturbations, and FID is especially sensitive to that kind of artifact [fig_3][tab_1].

```figure
id: fig_4
caption: Sampling time grows linearly in the number of steps, so the FID trade-off above is directly a wall-clock trade-off [fig_4]
```

fig_4 shows sampling time scales linearly with $\dim(\tau)$, confirming that fewer steps means proportionally less compute, not just better FID per step [fig_4].

DDIM matches roughly 1000-step DDPM quality using 20–100 steps, a 10×–50× speedup; on CelebA the 100-step DDPM (FID 13.93) and 20-step DDIM (FID 14.11) are nearly identical [tab_1].

That CelebA pair shows DDIM reaching DDPM's 100-step quality with only 20 steps — a 5× reduction at matched quality, not just matched step count [tab_1].

DDPM could reach similar quality by also using more steps, but it needs roughly 100× more than DDIM's minimum to do so, and never beats DDIM's FID at matched step counts below 1000 [tab_1].

## The Math {#the-math}
The speedup claim is arithmetic on $S$: $1000/100=10$, $1000/50=20$, $1000/20=50$, matching the paper's "$10\times$ to $50\times$" figure directly from the column headers of [tab_1].

The DDPM/DDIM FID ratio at matched $S$ shrinks from $3.07\times$ ($41.07/13.36$ at $S=10$) to $1.17\times$ ($4.73/4.04$ at $S=1000$), so stochasticity's cost concentrates at coarse trajectories [tab_1].

$\hat\sigma$ shows the opposite pattern: its own FID falls $115\times$ from $S=10$ to $S=1000$ ($367.43\to3.17$), far more than DDIM's $3.3\times$ drop over the same range [tab_1].

That asymmetry is the boundary case worth isolating: $\hat\sigma$'s variance is calibrated for the full 1000-step trajectory and breaks down once steps are removed, while DDIM's deterministic map has no per-step variance to miscalibrate [§sec_5_1].

## Go Deeper {#go-deeper}
This trade-off is DDIM's central empirical result: the same trained model, reused at test time with a shorter subsequence $\tau$ and $\eta=0$, closes most of the gap to the full 1000-step model [§sec_5_1].

The architectures and training setup behind these CIFAR10 and CelebA numbers sit under Datasets and Architectures; this page only covers what varying $\dim(\tau)$ and $\eta$ does to FID and wall-clock time [§sec_5_1].

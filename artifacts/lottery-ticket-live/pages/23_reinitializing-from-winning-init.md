# Reinitializing from Winning Ticket Distribution

## TL;DR {#tldr}
Resampling a winning ticket's weights per layer from the distribution $\mathcal{D}_m$ they came from — not their exact values — recovers almost none of the winning ticket's advantage. It performs about as poorly as reinitializing from the network's original distribution $\mathcal{D}$: the specific paired value matters, not just its marginal scale.

## Intuition {#intuition}
Picture a winning ticket's per-layer initial values as a bag of numbers with a certain shape — some skew, some spread. The bag itself does not identify winning tickets; where each number sits does.

$\mathcal{D}_m$ reinitialization keeps the bag's shape but reshuffles which number lands on which surviving connection. If the numbers' provenance mattered only as a distribution, reshuffling within that distribution should still help. It does not — performance drops back to what plain Gaussian reinitialization gives.

## Mechanics {#mechanics}
For a winning ticket with mask $m$, reinitializing from $\mathcal{D}_m$ swaps out the ticket's exact values for new ones drawn from the same per-layer distribution, then retrains and compares against the standard $\mathcal{D}$-reinitialization baseline [§sec_13_3].

- **Collect $\mathcal{D}_m$:** for each layer, gather the original initial values of only the surviving weights, $\mathcal{D}_m = \{\theta_0^{(i)} \mid m^{(i)}=1\}$ [§sec_13_3].
- **Resample:** draw a fresh $\theta'_0$ i.i.d. per layer from that layer's $\mathcal{D}_m$, discarding the exact original values but keeping their marginal statistics [§sec_13_3].
- **Fix the mask:** keep $m$ unchanged so the same connections survive; only their initial values change [§sec_13_3].
- **Retrain and compare:** train $f(x; m \odot \theta'_0)$ and measure it against reinitialization from the network's original distribution $\mathcal{D}$, the existing random-reinit baseline [§sec_13_3].

Winning tickets reinitialized from $\mathcal{D}_m$ perform little better than those reinitialized from $\mathcal{D}$, and the same result held when the authors repeated the test on SGD-trained winning tickets [§sec_13_3]. The supplied text does not give the exact accuracy values behind this comparison; Figure 17 shows them graphically for the Lenet winning tickets [§sec_13_3].

```figure
id: fig_17
caption: Accuracy of Lenet winning tickets reinitialized per layer from D_m, alongside the standard D-reinit baseline — the two curves track each other closely [§sec_13_3]
```

## The Math {#the-math}
Three initialization schemes share the same mask $m$ but differ in what they keep from the original run, and the difference between them isolates whether a winning ticket's advantage lives in the *identity* of each surviving weight's initial value or only in the *distribution* that value was drawn from [§sec_13_3].

| Scheme | Values used | Per-weight identity preserved? | Per-layer distribution preserved? |
|---|---|---|---|
| Winning ticket $\theta_0$ | exact original values | yes | yes [§sec_13_3] |
| $\mathcal{D}_m$ resample $\theta'_0$ | fresh draw from $\mathcal{D}_m$, per layer | no | yes [§sec_13_3] |
| $\mathcal{D}$ reinit (baseline) | fresh draw from original $\mathcal{D}$ | no | no [§sec_13_3] |

The $\mathcal{D}_m$ row is the case that separates the two hypotheses: it keeps the per-layer distribution but not the identity, so if distribution alone carried the advantage it should train like the winning ticket and unlike the $\mathcal{D}$ baseline. The observed result places it with the $\mathcal{D}$ baseline instead, little better than full reinitialization [§sec_13_3].

That the surviving weights' distribution alone does not help rules out a purely statistical account of winning-ticket initializations: whatever makes $\theta_0$ special is tied to the specific value at each position relative to the mask, not to the shape of the distribution it was drawn from [§sec_13_3].

## Go Deeper {#go-deeper}
No external resource is attached to this concept in the research note. What remains open is *why* per-weight identity matters — this experiment shows that the per-layer distribution alone is insufficient, but does not identify which property of the exact initial value (its sign, its magnitude, or its position within the mask) is doing the work [§sec_13_3].

# MAE by Completion Length
## TL;DR {#tldr}
- Probe MAE is lowest (≈20–30 tokens) for completions near the dataset mode (130–220 tokens).
- It's mildly worse (≈40–50) on the short tail (80–110 tokens), which is noisier because few samples fall in those bins.
- It degrades sharply (≈80–130) on the long tail ($T>300$, especially 400–460), which is the regime the paper's curated retraction failure case is drawn from.

## Intuition {#intuition}
A probe's accuracy at any completion length depends on how well that length is represented in training data, not on some intrinsic property of long or short outputs.

Because most training completions cluster near $130$–$220$ tokens, the probe learns that range best and extrapolates progressively worse the further a completion's true length sits from the mode.

## Mechanics {#mechanics}
MAE is lowest for completions whose total length sits near the dataset mode — the $130$–$220$-token range — where MAE is $\approx 20$–$30$ tokens and most of the training mass lives, since probes generalize best where they saw the most examples. [§sec_8_3]

The short-$T$ tail ($80$–$110$ tokens) is only mildly worse, MAE $\approx 40$–$50$, but this bin also has few samples, so the estimate itself is noisier rather than reflecting a real difficulty gap. [§sec_8_3]

The long-$T$ tail ($T>300$) degrades sharply: bins in the $400$–$460$ range show MAE of $80$–$130$ tokens, several times worse than the mode bins, on completions that are much less frequent in training. [§sec_8_3] [fig_5]

The long-tail bins are exactly where the curated retraction examples in the paper's dynamic-length section are drawn from: the probe's worst absolute errors there are the source of those cited failure cases, not a separate anomaly. [§sec_8_3]

| Completion length bin | MAE (tokens) | Notes |
|---|---|---|
| 80–110 (short tail) | ≈40–50 | Few samples per bin, noisier estimate [§sec_8_3] |
| 130–220 (mode) | ≈20–30 | Most training mass lives here [§sec_8_3] |
| 400–460 (long tail) | ≈80–130 | Sharp degradation, source of retraction examples [§sec_8_3] |

```figure
id: fig_5
caption: MAE (orange, left axis) tracks the training-data mode directly, while sample count (coral bars, right axis) thins out exactly where MAE spikes [§sec_8_3]
```

## The Math {#the-math}
Bin-to-bin arithmetic quantifies the degradation directly: the long-tail bins (400–460 tokens) report MAE of 80–130, against 20–30 in the mode bins (130–220 tokens) — a four- to four-and-a-third-fold increase in absolute error for completions in the least-represented length range. [§sec_8_3]

The short-tail bins (80–110 tokens) show a smaller but still real gap: MAE of 40–50 against 20–30 near the mode, a 1.5- to 2-fold increase, consistent with fewer training examples rather than any intrinsic difficulty of short completions. [§sec_8_3]

The curated retraction example anchors this scaling to a concrete case: the probe reads $4.84$ against a true $r_t = 814$, a relative error of $(814-4.84)/814 \approx 99\%$. [§sec_8_3]

That true remaining count, $814$ tokens, exceeds the highest bin plotted in the figure ($400$–$460$ tokens), so the sharpest degradation the figure shows is a floor rather than a ceiling. [§sec_8_3]

Completions further into the tail than any bin the probe was aggregated over are exactly where the paper's own curated failure case lives, which is consistent with — not an exception to — the bin-wise pattern. [§sec_8_3]

## Go Deeper {#go-deeper}
No external resources were supplied for this concept. For the qualitative story behind these numbers, the dynamic-retraction section referenced above walks through the curated long-tail failure case that this bin-wise MAE breakdown explains quantitatively.

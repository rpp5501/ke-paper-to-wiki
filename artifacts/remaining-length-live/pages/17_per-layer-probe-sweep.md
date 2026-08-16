# Per-Layer Probe Sweep

## TL;DR {#tldr}
- A separate linear probe trained at each layer shows *where* the remaining-length signal lives, not just that it exists.
- MAE stays near the constant-median baseline for the earliest layers, drops sharply through the middle of the network, and levels off in the upper third around layer 80 [§sec_8_1].
- The all-layers probe (concatenating every layer's hidden state) beats every single-layer probe, so the signal is spread across layers rather than concentrated in one [§sec_8_1].

## Intuition {#intuition}
Think of the network's depth as a processing pipeline, not a lookup table: each layer refines the raw tokens into more abstract, task-relevant features.

A quantity like "how many tokens remain" is a global summary of the whole sequence so far, not a property of any single token, so a linear probe can't read it off until the network has done enough integrating computation [§sec_8_1].

## Mechanics {#mechanics}
The per-layer sweep trains one Remaining Count Probe per layer $\ell$, using only that layer's hidden state as input. Sweeping $\ell$ from 0 (the embedding output) to $L$ (the final hidden state) turns the single headline number into a curve, and the shape of that curve is the localization result [§sec_8_1].

That curve has three regimes: MAE is highest at the earliest layers, drops sharply through the middle of the network, and flattens out in the upper third, stabilizing around layer 80. The early layers sit essentially at the constant-median baseline, meaning they contribute no more than always guessing the median remaining length [§sec_8_1].

```figure
id: fig_4
caption: MAE falls from the constant-median baseline at the embedding layer to its lowest point in the upper third of the network — the shape that localizes the remaining-length signal to computation rather than to any single layer [§sec_8_1]
```

Layer 0 is the token-embedding output, so a probe there tests a specific hypothesis: that remaining length is legible from the current token's identity alone. If it were, layer-0 MAE would already match the headline numbers [§sec_8_1].

Instead layer-0 MAE sits at the constant-median baseline, which rules out that shortcut: the signal is a computed quantity that emerges only after several layers of integration, not a stored property of the current token [§sec_8_1].

The all-layers probe used for the headline result concatenates the hidden state from every layer instead of picking one. It outperforms every single-layer probe in the sweep, including the best one on the plateau — the all-layers cell sits below the best single-layer entry [§sec_8_1].

That gap is the second finding: no single layer carries the whole signal, and information from multiple layers combines additively in the linear readout. The per-layer sweep and the all-layers result are complementary — one locates the signal in depth, the other shows it is distributed rather than concentrated [§sec_8_1].

## The Math {#the-math}
Write $m^\*$ for the best single-layer MAE and $m_{\text{all}}$ for the all-layers MAE. A single-layer probe is a linear functional of one layer's hidden state; the all-layers probe is a linear functional of the concatenation of every layer's hidden state, which contains each single layer as a subspace [§sec_8_1].

That containment guarantees $m_{\text{all}} \le m^\*$ for free: the all-layers probe could zero out every layer but the best one and match it exactly. What the sweep actually reports is stronger — the all-layers cell sits strictly below the best single-layer entry, not merely tied with it [§sec_8_1].

A strict drop means the optimal linear combination is not simply picking the best layer and ignoring the rest. Some other layer must carry a residual about remaining length that the best layer's probe direction cannot see — which is the concrete content behind "information from multiple layers contributes additively" [§sec_8_1].

The boundary case makes this concrete: if the sweep had instead shown $m_{\text{all}} = m^\*$, the correct reading would be that one layer already contains the whole signal and the rest are redundant. The strict inequality observed is what rules that reading out [§sec_8_1].

## Go Deeper {#go-deeper}
No external resource was supplied for this concept. The natural companion is the headline all-layers result in §Results: the per-layer sweep explains *where* that number's signal lives, while the concatenated-layer probe shows *why* no single layer can be dropped without losing accuracy [§sec_8_1].

# Noise Robustness of Winning Tickets
## TL;DR {#tldr}
- Winning tickets tolerate Gaussian noise added to their initialization far better than a full random reinitialization, and accuracy degrades gradually rather than collapsing as noise grows [§sec_13_7].
- Follow-up work traces this robustness to the sign of each initialization weight, not its exact magnitude [S1].

## Intuition {#intuition}
A winning ticket's initialization matters less as an exact point in weight space and more as a direction: which weights start positive and which start negative [S1].

Gaussian noise nudges each weight around its original value but rarely flips which side of zero it lands on, so the direction mostly survives even when the exact numbers don't [S1].

Random reinitialization is the opposite extreme — it keeps neither the exact values nor the direction — which is why it trains far worse than even a heavily noised winning ticket [S2].

## Mechanics {#mechanics}
For each layer of the winning ticket's Lenet initialization, the experiment adds Gaussian noise scaled to that layer's own initialization standard deviation, then retrains the pruned network from this noised starting point instead of the exact original values [§sec_13_7].

Four noise multiples are tested — 0.5σ, σ, 2σ, and 3σ — producing a spectrum from a light perturbation to a heavy one, all scaled per layer rather than applied globally [fig_25].

| Noise multiple | Effect on winning ticket | Evidence |
|---|---|---|
| 0.5σ | Accuracy is barely changed from the noise-free winning ticket | [§sec_13_7] |
| σ, 2σ | Accuracy and learning speed decline steadily as noise grows | [§sec_13_7] |
| 3σ | Still outperforms the random-reinitialization control | [§sec_13_7] |

```figure
id: fig_25
caption: Winning-ticket accuracy on Lenet/MNIST as Gaussian noise of increasing multiples of each layer's initialization std is added, showing gradual rather than sudden degradation [§sec_13_7]
```

A winning ticket's initialization carries two separable properties: the exact magnitude of each weight, and the sign of that weight relative to zero [S1].

The follow-up noise-injection study isolates which property matters by perturbing magnitude while often leaving sign untouched, and finds accuracy tracks sign preservation rather than closeness in magnitude [S1].

Random reinitialization preserves neither property, giving this comparison its worst-case floor, while the winning ticket's exact initialization preserves both and gives its best case [S2].

## The Math {#the-math}
At noise multiple k = 0, the perturbed initialization equals the original winning-ticket initialization exactly, so training should reproduce the unperturbed winning-ticket curve [§sec_13_7].

As k grows, injected noise increasingly dominates the original value at each weight, so the noised sign becomes less tied to the original sign, pushing performance toward the random-reinitialization floor in the limit [S1].

The four tested multiples sample the middle of this range without reaching either boundary: accuracy declines steadily from 0.5σ to 3σ but never collapses to the random-reinit floor, consistent with sign preservation degrading gradually rather than all at once [§sec_13_7].

## Go Deeper {#go-deeper}
- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask (Uber Engineering blog)](https://www.uber.com/blog/deconstructing-lottery-tickets/) — start here: an author-written, plot-driven walkthrough of the noise-injection experiment, more approachable than the paper.
- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask](https://arxiv.org/abs/1905.01067) — the paper that runs this noise-injection experiment and separates sign preservation from magnitude preservation as the load-bearing property.
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the source paper defining the winning-ticket vs. random-reinitialization baseline that every noise level here is measured against.

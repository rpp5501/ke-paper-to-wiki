# Iterative Magnitude Pruning (IMP)
## TL;DR {#tldr}

- IMP repeats train → prune a small fraction → reset survivors to their original initialization, instead of pruning straight to the target sparsity in one shot.
- Iterative removal finds smaller winning tickets that still match dense-network accuracy than one-shot pruning at the same final sparsity.
- The two strategies compared in this appendix differ only in *when* weights get reset to their initial values.

## Intuition {#intuition}

One-shot pruning judges every weight's importance from a single trained snapshot, then cuts the bottom fraction all at once — a weight that looks unimportant in that snapshot might matter once its noisier neighbors are gone.

Iterative pruning removes only a small slice — typically 20% — after each round, then retrains the smaller network before making the next cut. Each cut is informed by how the previous round's survivors actually behaved together, not by one noisy estimate.

## Mechanics {#mechanics}

IMP proceeds in rounds rather than a single cut. Each round trains the current unpruned subnetwork to convergence, ranks the surviving weights by magnitude, and prunes the lowest s% — typically 20% — creating a smaller mask [§sec_9].

The two strategies in this appendix differ only in what happens to the surviving weights after each prune: Strategy 1 resets them to θ₀ before retraining, while Strategy 2 keeps the already-trained values and resets only once, after pruning stops [§sec_9].

```algorithm
title: Strategy 1 — iterative pruning with resetting
lines:
  - code: "θ = θ0; m = 1^{|θ|}"
    intent: "Start from a full, unpruned network at its original random initialization [§sec_9]"
  - code: "train f(x; m ⊙ θ) for j iterations → m ⊙ θj"
    intent: "Train the current subnetwork to the point used to rank weight magnitudes [§sec_9]"
  - code: "prune s% of remaining weights → m′, P_m′ = (P_m − s)%"
    intent: "Remove the smallest-magnitude survivors, shrinking the fraction of weights kept unpruned [§sec_9]"
  - code: "θ = θ0; m = m′"
    intent: "Reset every surviving weight back to its value at initialization before the next round [§sec_9]"
  - code: "repeat until sufficiently pruned"
    intent: "Each round's mask is found by retraining around the previous round's sparse structure, not by one noisy pass [§sec_9]"
```

```algorithm
title: Strategy 2 — iterative pruning with continued training
lines:
  - code: "θ = θ0; m = 1^{|θ|}"
    intent: "Same starting point as Strategy 1: full network at original initialization [§sec_9]"
  - code: "train f(x; m ⊙ θ) for j iterations"
    intent: "Train the current subnetwork, same as Strategy 1's training step [§sec_9]"
  - code: "prune s% of remaining weights → m′"
    intent: "Same magnitude-based pruning rule as Strategy 1 [§sec_9]"
  - code: "m = m′; repeat (no reset) until sufficiently pruned"
    intent: "Retraining continues from the already-trained weights instead of resetting, so each round starts from where the last round left off [§sec_9]"
  - code: "θ = θ0 once, after pruning stops"
    intent: "Only the final surviving weights are reset to initialization, after the target sparsity is reached [§sec_9]"
```

The measured difference between the two schedules is consistent across architectures, shown in Figure 9 for Lenet and Figure 10 for Conv-2/4/6 [§sec_9]:

| Strategy | Weight reset timing | Validation accuracy | Early-stopping iteration |
|---|---|---|---|
| Strategy 1 (resetting) | Reset to θ₀ after every round, before retraining | Higher across Lenet and Conv-2/4/6 [§sec_9] | Faster, at smaller network sizes [§sec_9] |
| Strategy 2 (continued training) | Reset once, only after pruning stops | Lower than Strategy 1 at matched sparsity [§sec_9] | Slower than Strategy 1 [§sec_9] |

```figure
id: fig_9
caption: Early-stopping iteration and accuracy as Lenet is pruned round by round — resetting (Strategy 1) tracks higher accuracy at smaller network sizes than continued training (Strategy 2) [§sec_9]
```

At larger scale — ResNet-50 on ImageNet, BERT — resetting all the way back to iteration 0 becomes unstable under SGD's noise. IMP is then paired with rewinding to a small number of steps into training instead of to initialization, which restores stability without discarding the layer-wise sparsity pattern IMP already found [S2].

Round count and per-round rate trade off directly: aggressive one-shot or high-rate pruning is cheap but destroys the ticket, while smaller per-round rates near 20% cost more rounds of full retraining but yield tickets trainable to full accuracy at higher final sparsity [S3].

## The Math {#the-math}

Take s = 20%, the rate used throughout the paper's main experiments. After round 1, 80% of the original weights remain; after round 2, 80% of that 80% remains — not 80% minus another 20 percentage points [§sec_9].

```derivation
shape: Sparsity remaining after n rounds of pruning s% of the surviving weights per round.
steps:
  - latex: "P_0 = 100\\%"
    why: "Before any pruning, the mask m = 1^{|\\theta|} keeps every weight [§sec_9]"
  - latex: "P_{m'} = (P_m - s)\\%"
    why: "Each round's mask density is set relative to the current mask's density, not to the original count, per the strategy definition [§sec_9]"
  - latex: "P_n = (1 - s/100)^n \\times 100\\%"
    why: "Unrolling the recurrence across n rounds turns per-round removal into a compounding product, since each round removes s% of what remains rather than s% of the original count [§sec_9]"
```

This compounding is why the schedule needs many rounds to reach high sparsity: density falls to 0.8^n of the original count after n rounds, so reaching roughly 10% density takes about eleven rounds, since 0.8^11 ≈ 0.086 [§sec_9].

Each of those eleven rounds pays the full cost of training the subnetwork to convergence. That cost is exactly what the slower, smaller-rate schedule buys: tickets that stay trainable to full accuracy at higher final sparsity than an aggressive high-rate schedule reaches [S3].

At the limit s = 100%, IMP collapses to one-shot pruning: a single round removes everything not already zero, which is exactly the one-shot procedure this appendix's iterative strategies are contrasted against [§sec_9].

## Go Deeper {#go-deeper}

- [Lottery Ticket Hypothesis - Papers with Code](https://paperswithcode.com/method/lottery-ticket-hypothesis) — start here for diagrams and a plain-language summary of the train-prune-rewind loop before digging into code or the rewinding-instability papers.
- [OpenLTH: A Framework for Lottery Ticket Hypothesis Research](https://github.com/facebookresearch/open_lth) — the official Frankle-lab codebase implementing this exact train/prune/rewind loop, runnable to reproduce IMP results directly.
- [Comparing Rewinding and Fine-tuning in Neural Network Pruning](https://arxiv.org/abs/2003.02389) — studies the per-round pruning rate and rewinding-vs-fine-tuning tradeoffs raised above in detail.
- [Linear Mode Connectivity and the Lottery Ticket Hypothesis](https://arxiv.org/abs/1912.05671) — explains why naive rewind-to-init IMP becomes unstable at scale and motivates rewinding to an early checkpoint instead.

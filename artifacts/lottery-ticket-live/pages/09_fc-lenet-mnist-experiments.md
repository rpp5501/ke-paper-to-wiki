```markdown
# Fully-Connected LeNet/MNIST Experiments
## TL;DR {#tldr}

- Iterative magnitude pruning (IMP) on FC LeNet-300-100 finds winning tickets that train faster and generalize slightly better than the full network, down to about 21% of the original weights.
- Below roughly 21%, the benefit shrinks; by 3.6% remaining, a winning ticket performs like the unpruned network.
- Randomly reinitializing the same sparse mask destroys the speedup and generalization gain — the specific initial weights, not just the sparse structure, are doing the work.
- One-shot pruning also finds winning tickets, but iterative pruning finds smaller and better ones.

## Intuition {#intuition}

Think of the dense LeNet-300-100 as many bundled lottery tickets — subnetworks whose specific random starting weights make some of them well primed for gradient descent. Iterative magnitude pruning finds a winning one by repeatedly training, discarding the smallest weights, and resetting survivors to their original, not their trained, values.

The surprise is what happens when you swap in fresh random weights for the exact same surviving connections: the advantage disappears. A winning ticket isn't just a lucky shape — it's a lucky shape paired with the specific random draw it started from.

## Mechanics {#mechanics}

**Architecture and pruning rule.** Lenet-300-100 has two fully-connected hidden layers of 300 and 100 units, using Gaussian Glorot initialization [fig_2]. Each round prunes the lowest-magnitude weights within each layer separately, except the output layer, which is pruned at half the rate of the rest of the network [§sec_2].

**Iterative vs. one-shot pruning.** The main results repeat prune-train-reset for many rounds, removing 20% of remaining weights each round; one-shot pruning instead prunes straight to a target sparsity in a single step, trading away IMP's repeated-training cost [§sec_2].

Figure 3 tracks how learning speed and test accuracy shift as pruning deepens, averaged over five trials per pruning level [§sec_2] [fig_3].

```figure
id: fig_3
caption: Winning tickets at moderate sparsity reach the same test accuracy in fewer training iterations than the original network [§sec_2]
```

The pattern in that curve, and its reversal, is summarized by pruning level:

| $P_m$ | What happens relative to the original network |
|---|---|
| 51.3% | Reaches higher test accuracy faster than the original network, but slower than at 21.1% [§sec_2] |
| 21.1% | Fastest learner: early-stopping iteration is 38% earlier than the original network [§sec_2] |
| 13.5% | Test-accuracy peak: more than 0.3 percentage points above the original network [§sec_2] |
| 3.6% | Regresses to the original network's early-stopping speed and accuracy [§sec_2] |

Figure 4a plots the early-stopping iteration — a proxy for learning speed — against percent of weights remaining, for iterative pruning in 20% steps [§sec_2] [fig_4].

```figure
id: fig_4
caption: Early-stopping iteration and accuracy both improve then reverse as sparsity increases, tracing the same rise-then-fall pattern for iterative pruning [§sec_2]
```

Early-stopping iteration and test accuracy both improve as $P_m$ falls from 100% to 21%, then both degrade back toward the original network's level by $P_m = 3.6\%$ [§sec_2] [fig_4].

At early stopping, training accuracy rises with pruning in the same pattern as test accuracy — on its own, consistent with winning tickets simply optimizing better, not generalizing better [§sec_2].

But at iteration 50,000, nearly every network has reached 100% training accuracy while pruned tickets still show up to 0.35 percentage points higher test accuracy than the original network [§sec_2].

Since training accuracy is pinned at 100% but test accuracy still favors the winning ticket, the train/test gap is smaller for winning tickets — evidence of genuinely better generalization, not just better optimization [§sec_2].

**The random-reinitialization control.** To isolate the role of initialization, the paper keeps a winning ticket's mask $m$ but redraws its weights from the same initialization distribution, $\theta_0' \sim \mathcal{D}_\theta$, three times per point (15 runs total) [§sec_2].

Reinitialized networks learn progressively slower as pruning increases — the opposite of winning tickets — and lose test accuracy after only modest pruning [§sec_2].

The average reinitialized ticket's test accuracy starts dropping at $P_m = 21.1\%$, versus $P_m = 2.9\%$ for winning tickets themselves [§sec_2].

At $P_m = 21\%$, the winning ticket reaches minimum validation loss 2.51x faster than its reinitialized counterpart and is half a percentage point more accurate [§sec_2].

**One-shot pruning.** Pruning straight to a target sparsity in a single step, rather than repeating prune-train-reset, also finds winning tickets [§sec_2].

For $67.5\% \geq P_m \geq 17.6\%$, one-shot tickets reach minimum validation loss earlier than the original network; for $95.0\% \geq P_m \geq 5.17\%$, their test accuracy exceeds it [§sec_2].

Iterative pruning still wins overall: it reaches faster learning and higher test accuracy at smaller network sizes than one-shot pruning does, which is why the rest of the paper focuses on iterative pruning [§sec_2].

## The Math {#the-math}

Sparsity is measured directly, not inferred: $P_m = \frac{\lVert m \rVert_0}{|\theta|}$, the fraction of weights the mask $m$ keeps nonzero out of the total parameter count $|\theta|$ [§sec_2].

The paper reports two speed ratios separately — how much faster the winning ticket is than the original network, and how much faster it is than its reinitialized twin. Chaining them exposes a result the paper states but never multiplies out:

```derivation
shape: Chain two reported speed ratios to find how much slower the reinitialized ticket is than the original network.
steps:
  - latex: "T_{wt} = 0.62\\, T_{orig}"
    why: "The winning ticket at Pm=21.1% early-stops 38% earlier than the original network, so it needs only 100% - 38% = 62% of the original's iterations [§sec_2]"
  - latex: "T_{reinit} = 2.51\\, T_{wt}"
    why: "At Pm=21%, that same winning ticket reaches minimum validation loss 2.51x faster than its reinitialized counterpart, so reinit needs 2.51x the ticket's iterations [§sec_2]"
  - latex: "T_{reinit} = 2.51 \\times 0.62\\, T_{orig} \\approx 1.56\\, T_{orig}"
    why: "Substituting the first line into the second shows the reinitialized network needs about 56% more iterations than the original unpruned network to early-stop, despite sharing the winning ticket's exact sparse structure [§sec_2]"
```

The reinitialized network ends up slower than both the winning ticket it was copied from and the dense network it was pruned out of — the sparse structure alone does nothing without the original initialization attached to it [§sec_2].

## Go Deeper {#go-deeper}

- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the primary source for these FC LeNet-300-100 MNIST experiments, with the full sparsity-vs-accuracy curves and the random reinitialization control described above.
- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask](https://www.uber.com/blog/deconstructing-lottery-tickets/) — visual diagrams of the pruning masks on this same MNIST/LeNet setup, and evidence that the sign pattern of a winning ticket's weights carries most of the benefit.
- [Stabilizing the Lottery Ticket Hypothesis](https://arxiv.org/abs/1903.01611) — explains why naive IMP can be unstable to SGD noise and introduces rewinding to an early iteration instead of iteration 0, directly relevant to reproducing these FC LeNet results reliably.
```

# Early-Stopping Iteration Metric
## TL;DR {#tldr}

The early-stopping iteration metric is the checkpoint at which a network's validation loss is lowest, used throughout the paper as a proxy for how fast a network learns; the test accuracy at that checkpoint is reported alongside it [§sec_10].

## Intuition {#intuition}

Picture the FC Lenet/MNIST runs from the prerequisite experiment: validation loss drops early as the network learns useful weights, flattens, then climbs again once it starts memorizing noise in the training set [§sec_10].

The metric marks the bottom of that dip: a network reaching its lowest validation loss sooner is treated as having learned faster, independent of how long training continues afterward [§sec_10].

## Mechanics {#mechanics}

As training proceeds, validation loss traces a U-shape: it falls quickly during early iterations, flattens into a shallow bottom, and then climbs again as the network overfits the training set [§sec_10].

The early-stopping criterion locates that bottom directly: the iteration of minimum validation loss, not a fixed epoch budget or a patience-based heuristic [§sec_10].

Each curve in Figure fig_11 is averaged over five training runs at a fixed pruning level, with Lenet trained by Adam at a learning rate of 0.0012 [fig_11].

The three panels separate distinct regimes: winning tickets that both start faster and settle lower, winning tickets that start faster but plateau higher, and winning tickets compared against randomly reinitialized networks that lose the speed advantage entirely [fig_11].

The metric is validated by an independent cross-check rather than assumed: the order in which experiments cross the early-stopping threshold in Figure fig_11 matches the order in which they cross a fixed test-accuracy threshold in the companion accuracy figure [§sec_10].

This agreement is what licenses treating minimum-validation-loss iteration as a proxy for learning speed, rather than as an arbitrary stopping rule with no bearing on downstream accuracy [§sec_10].

```algorithm
title: Early-stopping iteration criterion
lines:
  - code: "for t in checkpoints:"
    intent: "Evaluate the network on the held-out validation set at each recorded training iteration [§sec_10]"
  - code: "    record loss_val[t]"
    intent: "Validation loss falls, bottoms out, then rises as the network overfits, so the full trace is needed to find the bottom [§sec_10]"
  - code: "t_star = argmin_t loss_val[t]"
    intent: "The iteration of minimum validation loss is the early-stopping point used as the learning-speed proxy [§sec_10]"
  - code: "report loss_val[t_star], test_acc[t_star]"
    intent: "The paper contextualizes learning speed with the test accuracy achieved at that same iteration [§sec_10]"
```

```figure
id: fig_11
caption: The validation-loss bottom each panel's early-stopping iteration marks, compared across pruning levels and against random reinitialization [fig_11]
```

## The Math {#the-math}

The criterion has a boundary case worth naming explicitly: if validation loss is still falling at the last recorded checkpoint, the minimum sits at the final iteration and the criterion reports no overfitting bottom at all [§sec_10].

That case does not arise in the trends sec_10 reports, where every configuration eventually turns upward, but it marks the limit of what the argmin over a finite checkpoint set can tell a reader [§sec_10].

A subtler failure mode is a validation curve with more than one local dip: an early noisy fluctuation could register as the global minimum before the true, broader bottom the paper's argument depends on [§sec_10].

Averaging five runs per curve, as Figure fig_11 does, is the paper's defense against this: noise that could create a spurious early minimum in one run is smoothed out across the average [fig_11].

A concrete case makes the mechanics precise: if a network's validation loss is $[0.9, 0.6, 0.45, 0.50, 0.55, 0.70]$ at six successive checkpoints, the criterion reports iteration 3, and the test accuracy recorded there — not at iteration 6 — is what the paper compares across pruning levels [§sec_10].

## Go Deeper {#go-deeper}

No research note is attached to this concept, so no external resource can be linked here.

The primary source for the criterion itself is Figure fig_11 and the surrounding discussion in sec_10, cited throughout above [§sec_10].

# Pruning at Iteration 0

## TL;DR {#tldr}
The paper tests whether a winning ticket's mask can be found from initialization magnitude alone, with no training at all. It cannot: masks pruned by magnitude at iteration 0 train worse than even the random-reinitialization control that iterative pruning normally beats.

## Intuition {#intuition}
[[Winning Ticket Initialization Distribution]] showed winning-ticket weights end up close to their original initialization values, and that magnitude at init correlates with which weights iterative magnitude pruning (IMP) eventually keeps. The natural next question is whether that correlation is strong enough to run in reverse — read the magnitudes off an untrained network and pick the mask before spending any compute on training and pruning rounds.

## Mechanics {#mechanics}
The initialization-distribution plots suggest a story: weights that start small stay small, never grow large enough to survive iterative magnitude pruning, and so never join the winning ticket [§sec_13_4].

This story has one exception — the first hidden layer of the adam-trained winning tickets does not follow the small-stays-small pattern [§sec_13_4].

If the story holds everywhere else, a low-magnitude weight was never going to matter, so it should be safe to prune before training even starts [§sec_13_4].

```algorithm
title: Pruning-at-iteration-0 test [§sec_13_4]
lines:
  - code: "mask = magnitude_prune(theta_0, target_sparsity)"
    intent: "Score and prune weights by their magnitude at initialization, before any training happens [§sec_13_4]"
  - code: "theta = theta_0 * mask"
    intent: "Keep the surviving weights at their original initialization values, matching how a winning ticket is normally defined [§sec_13_4]"
  - code: "train(theta, optimizer=adam)"
    intent: "Train only the masked network and measure whether it reaches winning-ticket-level accuracy [§sec_13_4]"
```

Winning tickets selected this way score worse than iterative pruning's own random-reinitialization control, the weakest baseline the paper otherwise beats [§sec_13_4].

The authors repeated the test on SGD-trained tickets and found the same shortfall, so the result is not specific to the adam optimizer [§sec_13_4].

```figure
id: fig_18
caption: Accuracy of Lenet winning tickets when the mask is set by initial magnitude alone, before any training, then trained with adam — the direct empirical test of pruning at iteration 0 [§sec_13_4]
```

## The Math {#the-math}
**The observation and the test invert different directions of the same claim.** IMP shows winning-ticket weights end up with a characteristic initialization magnitude — a fact about which weights survive training and pruning [§sec_13_4].

Pruning at iteration 0 tests the reverse: whether that magnitude alone, read off before training, is enough to pick the surviving weights in advance [§sec_13_4].

**The boundary case that explains the gap:** the first hidden layer of the adam-trained tickets breaks the small-stays-small pattern, so a low initial magnitude there does not predict pruning fate [§sec_13_4].

That single exception is a counterexample inside the paper's own data — it shows init magnitude is not a reliable predictor even where the authors could check it directly, before any cross-paper comparison is needed [§sec_13_4].

The gap this exposes is not unique to this paper's experiment; later work measured it directly across several init-only scoring rules:

| Selection method | What it uses | Training cost | High-sparsity outcome |
|---|---|---|---|
| Magnitude at init (this test) | θ₀ magnitude only | Zero | Worse than IMP's random-reinit control [S1] |
| Supermask search | θ₀ values, mask optimized, weights never trained | Mask search only | Above-chance accuracy with no weight training at all [S2] |
| SNIP / GraSP / SynFlow | θ₀ + one gradient or data pass | One forward/backward pass | Consistently below IMP-with-rewinding at high sparsity [S3] |
| IMP with rewinding | Full train → prune → rewind cycles | Many training rounds | Reference/best performance at high sparsity [S3] |

**The gap is largest exactly where it matters most:** at high sparsity, only IMP's own training-then-pruning signal separates good masks from bad ones, and every init-only shortcut loses ground precisely in that regime [S3].

Whether a richer init-only criterion could close that remaining gap is still an open question [S2][S3].

## Go Deeper {#go-deeper}
- [Lottery Ticket Hypothesis — Papers with Code method page](https://paperswithcode.com/method/lottery-ticket-hypothesis) — a quick visual of the iterative-pruning-plus-rewind pipeline that pruning-at-iteration-0 is trying to shortcut; read this first if the mechanics above feel abstract.
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the original paper, source of the initialization-magnitude observation this concept tests.
- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask](https://arxiv.org/abs/1905.01067) — the direct follow-up: searches for masks on the untrained network and finds ones that beat chance with zero weight training.
- [Pruning Neural Networks at Initialization: Why Are We Missing the Mark?](https://arxiv.org/abs/2009.08576) — benchmarks SNIP/GraSP/SynFlow-style init-only pruning against post-training magnitude pruning, quantifying how much signal iteration-0 selection is missing.

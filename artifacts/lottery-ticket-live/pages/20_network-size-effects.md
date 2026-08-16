# Network Size Effects

## TL;DR {#tldr}
Making the LeNet network wider changes how good a winning ticket you find, but not necessarily how fast it learns or how sparse it can get before losing accuracy — the three questions "how accurate," "how fast," and "how sparse" have three different answers to whether bigger is better.

## Intuition {#intuition}
If a winning ticket exists because a lucky sub-network was drawn at initialization, then a bigger network is a bigger lottery: more tickets bought means better odds of holding a winner. That intuition predicts wider LeNet variants should find better winning tickets — the open question is which measure of "better" it actually improves.

## Mechanics {#mechanics}
**The paper tests three ways to judge a winning ticket, and gets three different answers.** Widening LeNet's hidden layers (keeping the 3:1 layer ratio) shifts accuracy, learning speed, and the return-to-baseline sparsity — but not equally, and not in the same direction [§sec_14_6].

| Criterion | Effect of a larger initial network |
|---|---|
| Accuracy at a fixed remaining-weight count | Larger networks reach higher accuracy at any given number of remaining weights [fig_31] |
| Early-stopping iteration | Barely changes; larger networks learn only marginally faster [fig_31] |
| Sparsity where accuracy returns to baseline | No advantage — all sizes return to baseline in roughly the same 9,000–15,000-weight range [§sec_14_6] |

```figure
id: fig_31
caption: Early-stopping iteration (left) and accuracy (right) against the raw number of weights remaining, one line per hidden-layer width — accuracy separates by network size while iteration count barely does [§sec_14_6]
```

**Two explanations compete for why larger networks reach higher accuracy at the same weight count.** Either gradient descent finds a genuinely better winning ticket because there are more subnetworks to search among, or the larger network's pruned mask can express sparse configurations no initially-smaller network has the units to represent [§sec_14_6].

**The early-stopping result isolates learning speed from learning quality.** Pruned to the same weight count, networks derived from different initial sizes reach their stopping point at almost the same iteration — bigger initial capacity buys higher accuracy, not faster convergence [fig_31].

**The return-to-baseline sparsity is where the size advantage disappears entirely.** Regardless of whether the original network was small or large, its winning ticket matches the original accuracy again once pruned down to somewhere between 9,000 and 15,000 weights [§sec_14_6].

**A boundary case separates the criteria's independence.** Two networks pruned to the same 10,000 weights — one starting wider than the default 300/100 LeNet, one starting at it — can match on early-stopping iteration and match on return-to-baseline sparsity while still differing in final accuracy, because the three questions do not covary [§sec_14_6].

## The Math {#the-math}
**The paper's number is a weight count, and the sparsity percentage it corresponds to depends on where the network started.** The default LeNet-300-100 has 784×300 + 300×100 + 100×10 = 266,200 weights, so the reported "returns to baseline between 9,000 and 15,000 weights" window is about 3.4%–5.6% of the original network still present [§sec_14_6].

Doubling both hidden layers while keeping the 3:1 ratio multiplies the weight count without moving the absolute window. A 600/200 LeNet has 784×600 + 600×200 + 200×10 = 592,400 weights [§sec_14_6].

That same 9,000–15,000-weight window is now only about 1.5%–2.5% of the network, not the 3.4%–5.6% it was for the default size — flat on the weight axis, but a shrinking percentage on the sparsity axis [§sec_14_6].

The range itself — 9,000 to 15,000, not a single weight count — reflects that this is an empirical crossing point measured across repeated pruning runs, not a sharp analytic threshold; some runs cross back into baseline-matching accuracy a little earlier or later than others [§sec_14_6].

## Go Deeper {#go-deeper}
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the paper this page draws its figures and numbers from; open it to see the full accuracy-vs-weights and iteration-vs-weights curves for every tested LeNet width.
- [lottery-ticket-hypothesis (Google Research)](https://github.com/google-research/lottery-ticket-hypothesis) — the official code; change the hidden-layer widths directly and rerun the pruning loop to see the size effect firsthand.
- [Stabilizing the Lottery Ticket Hypothesis](https://arxiv.org/abs/1903.01611) — shows what happens when capacity grows in depth instead of width (ResNet-20, VGG-19), where the reset-to-initialization approach breaks down and rewinding to an early iteration is needed instead.

# Degradation Problem
## TL;DR {#tldr}
Stacking more layers onto a deep plain network eventually makes it harder to train, not easier — even though a deeper network could simply copy the shallow network and let the extra layers do nothing. This is the degradation problem: training error rises with depth, so it isn't overfitting. It's the empirical puzzle that motivates residual learning.

## Intuition {#intuition}
Think of a deep network as a relay team: adding more runners shouldn't hurt the team's time, because the new runners could simply pass the baton along untouched. A deeper network has the same option — the extra layers can learn to leave their input unchanged, an identity mapping, and match the shallower network exactly.

If a shallow network already reaches some training accuracy, a deeper version built by copying it and appending identity layers should match that accuracy — it can't do worse, because the extra layers change nothing.

But real deep plain networks don't behave this way. Once depth passes a point, training accuracy gets worse, not the same — the network fails to find even the easy, guaranteed-safe solution of doing nothing in the extra layers.

## Mechanics {#mechanics}
Once normalized initialization and intermediate normalization layers let very deep plain networks start converging under SGD, a new problem appears: accuracy saturates and then degrades as depth keeps increasing [§sec_1].

This isn't the vanishing/exploding-gradient problem — that one blocks convergence from the start and is largely solved by the same initialization and normalization techniques. Degradation shows up only after training is already converging [§sec_1].

Degradation is also not overfitting: adding layers increases training error itself, not just the gap between training and test error. A network that fits its own training set worse cannot be blamed on generalization [§sec_1].

```figure
id: fig_1
caption: The 56-layer plain network trains and tests worse than its 20-layer counterpart on CIFAR-10 — depth alone made optimization harder, not better [§sec_1]
```

The existence argument follows directly: take a shallow architecture and a deeper counterpart that adds extra layers on top of it. If those added layers are set to the identity mapping and the rest are copied from the trained shallow model, the deeper model reproduces the shallow one's training error exactly [§sec_1].

So a deeper model should never need higher training error than its shallower counterpart — the solution always exists. But the paper reports that current solvers can't find a comparably good solution in feasible time, which is the degradation problem stated precisely: not a capacity limit, but an optimization failure [§sec_1].

The paper's response is architectural: instead of asking stacked layers to fit the desired mapping directly, it lets them fit a residual mapping and adds the input back via a shortcut connection — deferred fully to the Deep Residual Learning concept [§sec_1].

## The Math {#the-math}
**A constructive upper bound:** take a trained shallow network with L layers reaching training error e. Build a deeper network with L+K layers by copying the shallow network's L layers verbatim and setting the remaining K layers to the identity mapping [§sec_1].

This construction reproduces training error e exactly, so the best deep network's achievable training error can be no higher than the best shallow network's — a proof that a good solution exists, not a claim that any given optimizer will find it [§sec_1].

Fig. 1's own comparison shows the bound isn't what solvers reach: the 56-layer plain network's training error is higher than the 20-layer network's, even though the identity-layer construction guarantees a deeper network can match the shallower one's error [fig_1].

That gap — between the error the construction proves is reachable and the higher error SGD actually finds — is exactly what "degradation" names: capacity was never the bottleneck, search was [§sec_1].

## Go Deeper {#go-deeper}
The fix lives in the next concept: Deep Residual Learning reframes what each stack of layers has to learn, using a shortcut connection like the one below.

```figure
id: fig_2
caption: The shortcut adds the block's input straight to its output, so the stacked layers only need to learn the residual — the architecture built to sidestep the degradation problem above [§sec_1]
```

Vanishing/exploding gradients is a related but distinct failure mode, addressed earlier by normalized initialization and intermediate normalization layers — it is not the cause of degradation itself [§sec_1].

CIFAR-10 Depth Analysis extends this same shallow-versus-deep comparison to plain and residual networks with over 100 and over 1000 layers.

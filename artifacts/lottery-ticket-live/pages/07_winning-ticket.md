# Winning Ticket
## TL;DR {#tldr}

A winning ticket is a sparse subnetwork inside a larger randomly-initialized network that, when trained alone from its original initialization, matches or beats the full network's accuracy in no more iterations [§sec_1].

Three conditions must hold jointly: it trains at least as fast ($j' \leq j$), reaches at least as high test accuracy ($a' \geq a$), and uses far fewer parameters ($\lVert m \rVert_0 \ll |\theta|$) [§sec_1].

Winning tickets found by the paper's pruning procedure are 10–20% of the original network's size [§sec_1].

The initialization matters as much as the architecture: resetting a winning ticket's surviving weights to random values instead of their original values destroys its advantage [§sec_1].

## Intuition {#intuition}

Buying many lottery tickets raises the odds that one of them wins, but each ticket's own numbers were fixed before the draw — only its combination of numbers explains why it wins.

A winning ticket in a neural network is the same idea: a small combination of connections and initial values already primed to train well, sitting inside a much larger, mostly unlucky network [§sec_1].

A dense network is easier to train from scratch than a sparse one because it contains many candidate subnetworks — more chances that one of them is a winning ticket [§sec_1].

Reinitializing a winning ticket's weights randomly removes its luck. The same sparse architecture trained from new random values learns slower and less accurately, showing structure alone does not explain the win [§sec_1].

## Mechanics {#mechanics}

A winning ticket is identified by first training the full dense network, then pruning its smallest-magnitude weights, and finally resetting every surviving weight to its own value from before training began [§sec_1].

```algorithm
title: The paper's central experiment — finding a winning ticket
lines:
  - code: "θ0 ~ D_θ; initialize f(x; θ0)"
    intent: "Draw the dense network's random initialization that the winning ticket will later be reset to [§sec_1]"
  - code: "train f for j iterations -> θ_j"
    intent: "Train the full dense network to find which weights end up large, i.e. which ones the optimizer relied on [§sec_1]"
  - code: "m = mask pruning the smallest-magnitude p% of θ_j"
    intent: "Unstructured magnitude pruning: the surviving connections define the winning ticket's sparse architecture [§sec_1]"
  - code: "winning ticket = f(x; m ⊙ θ0)"
    intent: "Reset every surviving weight to its pre-training value θ0, not its trained value — this reset is what the paper's approach adds over prior one-shot pruning [§sec_1]"
```

One-shot pruning runs this procedure once: train, prune $p\%$, reset. Iterative pruning repeats it over $n$ rounds, pruning $p^{1/n}\%$ of the surviving weights each round, and finds smaller winning tickets than one-shot pruning does [§sec_1].

The mask $m \in \{0, 1\}^{|\theta|}$ records which connections survive pruning; the unpruned entries define the winning ticket's architecture, and each corresponding weight is reset to $\theta_0$ rather than left at its trained value [§sec_1].

The paper finds winning tickets in fully-connected networks for MNIST and convolutional networks for CIFAR10, across SGD, momentum, and Adam, and alongside dropout, weight decay, batchnorm, and residual connections [§sec_1].

In deeper networks, finding winning tickets becomes sensitive to the learning rate: the pruning procedure needs a warmup schedule to succeed at higher learning rates [§sec_1].

Figure 1 shows the effect directly: winning tickets stay flat as sparsity increases while randomly sampled subnetworks of the same size degrade [§sec_1].

```figure
id: fig_1
caption: Winning tickets (solid) hold flat on early-stopping iteration and test accuracy as sparsity increases, while random subnetworks of the same size (dashed) degrade [§sec_1]
```

## The Math {#the-math}

The hypothesis is stated as three joint conditions on a mask $m \in \{0, 1\}^{|\theta|}$ applied to initialization $\theta_0$: the ticket must reach minimum validation loss in $j' \leq j$ iterations, reach test accuracy $a' \geq a$, and satisfy $\lVert m \rVert_0 \ll |\theta|$ [§sec_1].

Dropping any one condition breaks the claim. A mask that trains fast and is tiny but never matches accuracy is just an under-parameterized network — the ordinary pruning failure mode the paper contrasts winning tickets against [§sec_1].

A mask that eventually matches accuracy but only after far more iterations than $j$ would show sparsity trading capacity for training speed, not revealing an already-well-initialized subnetwork [§sec_1].

And a mask satisfying speed and accuracy without $\lVert m \rVert_0 \ll |\theta|$ would just be the original dense network relabeled — sparsity is what makes the initialization's role visible at all [§sec_1].

Iterative pruning removes $p^{1/n}\%$ of surviving weights each round rather than $p\%$ all at once [§sec_1].

As an illustration of the schedule (not the paper's reported numbers): keeping 80% of survivors each round for $n=3$ rounds leaves $0.8^3 \approx 51\%$ of the original weights — the same end sparsity a single pruning pass reaching 49% would produce, but reached in three smaller, gentler cuts [§sec_1].

Because each round resets survivors to $\theta_0$ and retrains before the next cut, iterative pruning lets the mask adapt round by round — which is why the paper reports it finds smaller winning tickets than pruning $p\%$ in a single pass [§sec_1].

Push sparsity too far and the third condition survives while the first two fail: Figure 1's dashed lines show randomly sampled subnetworks of very small size learning more slowly and settling at lower accuracy as sparsity increases, never becoming winning tickets [§sec_1].

The reset step matters just as much as the sparsity level. The same mask $m$ keeping its trained weights $\theta_j$ instead of being reset to $\theta_0$ is not a winning ticket by this paper's definition — only structure, not the found initialization, would then be responsible for any success [§sec_1].

## Go Deeper {#go-deeper}

No external resources were supplied for this concept. The neighboring concepts in this paper's map extend it directly: Random Reinitialization Control (contrasts with resetting to $\theta_0$), and Winning Ticket Initialization Distribution, Winning Ticket Connectivity, and Noise Robustness of Winning Tickets (each part of this one) [§sec_1].

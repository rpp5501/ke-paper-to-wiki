# The Lottery Ticket Hypothesis

## TL;DR {#tldr}
- A dense, randomly-initialized network contains a sparse subnetwork that, trained alone from the *same* initial weights, matches the full network's accuracy in no more iterations.
- These subnetworks are called **winning tickets**; they are found by training, pruning small-magnitude weights, and resetting the survivors back to their original values.
- Winning tickets are usually 10–20% of the original size. Reinitializing them randomly destroys the advantage — the original initialization matters, not just which connections survive.

## Intuition {#intuition}

Pruning shrinks a trained network after the fact, cutting away weights that contributed little to the final result. The puzzle is that the smaller architecture pruning reveals rarely trains well on its own — starting from scratch with that shape tends to learn slower and land at lower accuracy than the original dense network did.

The lottery ticket hypothesis reframes the puzzle: architecture alone isn't the story. What made the dense network trainable was a lucky pairing — sparse structure with a specific starting point for its surviving weights. Reset those weights to a new random draw, and the same subnetwork stops learning well.

The name is metaphorical but precise: each initial weight is a lottery ticket, and only some combinations are "winning" — capable of learning once isolated. This motivates a practical hope: if winning tickets could be spotted early, training could search for and prune toward them instead of training the full dense network throughout.

This differs from ordinary pruning and distillation, which only ever claim a smaller network can *run* efficiently after training. The hypothesis instead claims a smaller network already sits inside the big one, ready to *train* efficiently, if only it is given back its original initialization.

## Mechanics {#mechanics}

Start from a dense feed-forward network $f(x;\theta)$ with initial weights $\theta = \theta_0 \sim \mathcal{D}_\theta$, drawn from whatever initialization distribution the architecture uses. Training this network with SGD reaches its lowest validation loss $l$ at iteration $j$, with test accuracy $a$ at that point [§sec_1].

Now apply a binary mask $m \in \{0,1\}^{|\theta|}$ that zeros out some weights, so the masked network $f(x; m \odot \theta)$ starts from $m \odot \theta_0$ — the *same* initial values as before, just for fewer connections. Trained the same way, it reaches loss $l'$ at iteration $j'$ with accuracy $a'$ [§sec_1].

The hypothesis is three conditions on that mask holding simultaneously: the masked network trains in no more iterations ($j' \le j$), reaches at least as high accuracy ($a' \ge a$), and uses far fewer parameters ($\lVert m \rVert_0 \ll |\theta|$) [§sec_1].

The paper turns this existence claim into a search procedure — its central experiment for finding one such mask [§sec_1]:

```algorithm
title: Central experiment — one-shot pruning to a winning ticket
lines:
  - code: "θ0 ~ D_θ; initialize f(x; θ0)"
    intent: "Draw a fresh random initialization for the dense network [§sec_1]"
  - code: "train f for j iterations → θj"
    intent: "Train the full dense network to convergence, producing trained weights θj [§sec_1]"
  - code: "m = mask pruning the smallest-magnitude p% of θj"
    intent: "Magnitude is the pruning criterion: weights near zero are judged least useful and removed [§sec_1]"
  - code: "reset surviving weights to θ0 → f(x; m⊙θ0)"
    intent: "This reset — not just keeping the pruned architecture — is what turns a pruned network into a winning ticket [§sec_1]"
```

As described, this is **one-shot pruning**: train once, prune $p\%$, reset. The paper's main results instead use **iterative magnitude pruning**, which repeats the train-prune-reset cycle over $n$ rounds, removing $p^{1/n}\%$ of the surviving weights each round. Iterative pruning finds smaller winning tickets than one-shot pruning does [§sec_1].

A separate ablation tests whether the *architecture* alone explains a winning ticket's success: reinitialize the surviving connections to a new random draw $\theta'_0 \sim \mathcal{D}_\theta$ instead of resetting to $\theta_0$. These randomly-reinitialized networks perform far worse, showing that the mask's sparse shape is not sufficient — the original initialization is doing real work [§sec_1].

```figure
id: fig_1
caption: Sparser networks found by random pruning (dashed) learn slower and plateau lower as sparsity increases, while winning tickets (solid) at the same sparsity learn faster and reach higher accuracy [§sec_1]
```

## The Math {#the-math}

The hypothesis's three conditions are independent claims, and each can fail without the others failing — that independence is what makes "winning ticket" a nontrivial thing to find, not just "any sparse subnetwork" [§sec_1].

```annotated-eq
latex: "\\exists\\, m : j' \\le j,\\ a' \\ge a,\\ \\lVert m \\rVert_0 \\ll |\\theta|"
terms:
  - tex: "m"
    role: 1
    words: "The binary mask defining which connections survive — the object the search procedure is trying to find [§sec_1]"
  - tex: "j' \\le j"
    role: 2
    words: "Speed condition: the masked network reaches minimum validation loss in no more iterations than the original [§sec_1]"
  - tex: "a' \\ge a"
    role: 3
    words: "Accuracy condition: at that point it matches or beats the original network's test accuracy [§sec_1]"
  - tex: "\\lVert m \\rVert_0 \\ll |\\theta|"
    role: 4
    words: "Sparsity condition: the surviving parameter count is much smaller than the full network — without this the other two are trivially satisfiable by m = all-ones [§sec_1]"
```

Concretely: the winning tickets the paper reports for LeNet on MNIST and for its convolutional networks on CIFAR10 sit at 10–20% of the original parameter count, and often below that, while still meeting or exceeding the original test accuracy in at most as many iterations [§sec_1].

There is a limit to how far this holds: winning tickets keep learning faster and matching the dense baseline as they shrink, but only down to a critical sparsity — pruned past that point, performance degrades sharply [S1].

The reinitialization ablation is the paper's own counterexample to a structure-only account: take the exact mask $m$ of a winning ticket, but draw fresh weights $\theta'_0 \sim \mathcal{D}_\theta$ instead of resetting to $\theta_0$. Conditions $j' \le j$ and $a' \ge a$ both fail — the same sparse architecture no longer trains well [§sec_1].

## Go Deeper {#go-deeper}

- [Lottery Ticket Hypothesis (Method)](https://paperswithcode.com/method/lottery-ticket-hypothesis) — a diagram of the train-prune-rewind loop; start here if the reset step in the algorithm above isn't clicking, and it links onward to papers that apply the technique.
- [The Lottery Ticket Hypothesis for Pre-trained BERT Networks](https://doi.org/10.48550/arxiv.2007.12223) — shows winning tickets exist inside large pretrained transformers too, not just the small vision networks this paper studies.
- [Sparse Transfer Learning via Winning Lottery Tickets](https://doi.org/10.48550/arxiv.1905.07785) — tests whether a winning ticket found on one task stays trainable on a different task, probing what the subnetwork actually captures.
- [Drawing Early-Bird Tickets: Towards More Efficient Training of Deep Networks](https://doi.org/10.48550/arxiv.1909.11957) — shows winning tickets can be spotted early in training rather than after full training, the training-efficiency payoff this concept's neighborhood points to.

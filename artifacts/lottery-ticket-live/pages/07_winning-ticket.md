# Winning Ticket

## TL;DR {#tldr}
- A winning ticket is a sparse subnetwork that matches or beats the full network's accuracy in the same or fewer iterations, once reset to its own original initial weights [S1].
- It's found by pruning a trained network's smallest-magnitude weights and resetting the survivors — not by pruning alone [S1].
- The initial *values* the surviving weights need aren't as strict as the initial *signs* they carry [S3].

## Intuition {#intuition}
Think of a dense network as buying many lottery tickets at once: each connection starts at its own random initial value, and most combinations of connections are duds that learn slowly or not at all [S1].

A winning ticket is the rare sub-combination that happened to draw a lucky initialization: kept in isolation and trained from that same start, it learns as fast as the whole network and reaches comparable or better accuracy [S1].

The luck isn't in the sparse wiring pattern alone. Reinitialize the same surviving connections to fresh random values and the advantage disappears — the ticket needs its own original draw, not just its shape [S1].

Later work narrows what "lucky" means: what mostly matters is the *sign* each surviving weight started with, not its exact magnitude — a mask that only preserves original signs still trains well [S3].

## Mechanics {#mechanics}
Frankle & Carbin identify a winning ticket with a train-prune-reset loop applied to a single dense network, shown below [§sec_1].

```algorithm
title: Central experiment — identifying a winning ticket
lines:
  - code: "θ_0 ~ D_θ; initialize f(x; θ_0)"
    intent: "Draw the dense network's random initial weights — these exact values are what the winning ticket will later be reset to [§sec_1]"
  - code: "train f(x; θ_0) for j iterations → θ_j"
    intent: "Train the full dense network to get magnitude information about which weights turned out to matter [§sec_1]"
  - code: "mask m = prune p% of θ_j by smallest magnitude"
    intent: "Weights that stayed near zero after training are judged least useful and pruned [§sec_1]"
  - code: "reset surviving weights to θ_0, forming f(x; m ⊙ θ_0)"
    intent: "Unique to this method: survivors go back to their original initial values rather than keeping their trained values or being reinitialized [§sec_1]"
```

This single pass is one-shot pruning. The paper's main results instead use iterative magnitude pruning (IMP): repeat the loop for $n$ rounds, each round pruning $p^{1/n}\%$ of the weights that survived the previous round [§sec_1].

Iterative pruning finds smaller winning tickets than one-shot at the same accuracy, because each round removes only a modest fraction of what remains instead of cutting the full target sparsity in one shot [§sec_1].

The random reinitialization control isolates which part of the recipe matters: keep the winning ticket's mask $m$ but redraw its surviving weights from $\mathcal{D}_\theta$ instead of resetting to $\theta_0$, and accuracy drops well below the original network [S1].

Zhou et al. test this further: freezing only the sign of each surviving weight at its original value, while randomizing its magnitude, still trains close to full accuracy — even the mask alone ("supermask") beats chance with zero training [S3].

```figure
id: fig_1
caption: Solid lines are winning tickets found by IMP; dashed lines are randomly sampled subnetworks of the same sparsity — the gap between them is the whole claim of this concept [§sec_1]
```

At every sparsity level tested, winning tickets (solid) reach the early-stopping iteration sooner and end at equal or higher test accuracy than random subnetworks of the same size (dashed), which get slower and less accurate as sparsity increases [fig_1].

## The Math {#the-math}
The hypothesis names $f(x; m \odot \theta_0)$ as the object of interest: the same network, restricted to a mask $m$, evaluated at the *original* initialization $\theta_0$ rather than a fresh one [§sec_1].

```annotated-eq
latex: "f(x; m \\odot \\theta_0)"
terms:
  - tex: "f(x; \\cdot)"
    role: 1
    words: "The unchanged network architecture and forward pass — only which parameters are used changes, not the function itself [§sec_1]"
  - tex: "m \\in \\{0,1\\}^{|\\theta|}"
    role: 2
    words: "The binary mask found by pruning; a 0 zeroes out a connection permanently, a 1 keeps it trainable [§sec_1]"
  - tex: "\\theta_0"
    role: 3
    words: "The original random draw — reset to these values, not retrained values or a new draw, is what makes it a winning ticket rather than just a sparse network [§sec_1]"
```

The hypothesis packs three separate claims into one existence statement about $m$ [§sec_1]:

- **At least as fast:** $j' \leq j$ — the ticket reaches minimum validation loss in no more iterations than the original dense network [§sec_1].
- **At least as accurate:** $a' \geq a$ — its test accuracy at that iteration matches or beats the original [§sec_1].
- **Actually sparse:** $\lVert m \rVert_0 \ll |\theta|$ — the surviving connections are a small fraction of the original count, not merely a relabeling [§sec_1].

A concrete case shows why the per-round rate $p^{1/n}\%$ matters: suppose the target is a winning ticket at 20% of the original size, reached over $n=5$ rounds of iterative pruning [§sec_1].

The per-round survival rate $r$ solves $r^5 = 0.20$, giving $r \approx 0.7248$: each round keeps about 72.5% of the weights that survived the previous round, pruning roughly 27.5% of them [§sec_1].

One-shot pruning would remove that same 80% in a single cut. Iterative pruning removes it in five gentler steps, each discarding only the weakest ~27.5% of what remains, which is why it finds smaller tickets at matched accuracy [§sec_1].

## Go Deeper {#go-deeper}
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the original paper; its own figures are the canonical picture of what a winning ticket is and how IMP finds one. Start here.
- [OpenLTH](https://github.com/facebookresearch/open_lth) — a research framework implementing the prune-train-rewind loop end to end, useful for seeing IMP as actual runnable code.
- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask](https://arxiv.org/abs/1905.01067) — isolates whether a ticket's advantage comes from its exact initial values or just the sign pattern and mask structure; read once the base definition is clear.

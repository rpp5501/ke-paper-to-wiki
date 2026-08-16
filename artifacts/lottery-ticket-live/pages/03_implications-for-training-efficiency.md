# Implications for Training Efficiency

## TL;DR {#tldr}

Winning tickets reach the original network's accuracy with far fewer parameters, but only when trained from their original initialization [§sec_5].

This raises a question about SGD itself: does training need all of a network's parameters, or does overparameterization just give SGD many chances to find one well-initialized subnetwork [§sec_5]?

## Intuition {#intuition}

Think of an overparameterized network as buying many lottery tickets at once. Most subnetworks inside it are duds, but a few are "winning" initializations that train well on their own [S1].

That reframes what overparameterization buys you. Instead of needing every parameter to represent the final function, SGD may only need enough parameters to have good odds of containing one well-initialized subnetwork [§sec_5].

This predicts an Occam's Hill in test accuracy as pruning proceeds. Accuracy first rises as pruning strips away excess, possibly overfitting capacity, then falls once pruning removes so much capacity that the surviving subnetwork can no longer represent the task [§sec_5].

## Mechanics {#mechanics}

A winning ticket reinitialized randomly learns more slowly and reaches lower test accuracy than the same subnetwork trained from its original initialization. This shows the initialization itself carries information the pruning process uncovered, not just the sparse architecture [§sec_5].

One tempting explanation is that winning-ticket weights are already close to their trained values, so training barely has to move them. Appendix experiments show the opposite: winning-ticket weights move further from their initialization than other weights do [§sec_5].

So the benefit isn't stasis but something about how this starting point interacts with the optimizer, dataset, and model — for example, an initialization that happens to sit in a region of the loss landscape the chosen optimizer handles particularly well [§sec_5].

Other work complicates this picture: pruned VGG-19 networks, trained from a fresh random reinitialization, are found to match the original network's accuracy at up to 80% sparsity [§sec_5].

This paper's own experiments confirm that match at 80% sparsity, but push further: at up to 98.5% pruning, VGG-19 still yields winning tickets, and at that level reinitializing them causes accuracy to drop substantially [§sec_5].

The reconciling hypothesis is a sparsity threshold: highly overparameterized networks can be pruned, reinitialized, and retrained successfully up to a point, but beyond it only the fortuitous winning-ticket initialization keeps accuracy up [§sec_5].

Because winning tickets are found using heavy use of training data, their sparse structure may encode an inductive bias suited to the task — echoing how a network's pooling geometry can determine which data it separates more parameter-efficiently than a shallow network could [§sec_5].

Winning tickets also generalize better than the original network while matching its training accuracy, and test accuracy rises then falls as pruning proceeds — an Occam's Hill where the original network has too much complexity and the most-pruned one has too little [§sec_5].

This fits the conventional view that compact hypotheses generalize better, and recent theory proves tighter generalization bounds for networks that compress further under pruning, quantization, or noise. The lottery ticket hypothesis adds a complementary claim: large networks may explicitly contain these simpler representations rather than merely tolerating compression after the fact [§sec_5].

This connects to theoretical work showing sufficiently overparameterized two-layer ReLU networks, trained with SGD, provably converge to global optima. Whether a winning ticket's presence is necessary or sufficient for SGD to reach a given accuracy is still open; the paper conjectures instead that SGD seeks out and trains a well-initialized subnetwork it finds within the larger network [§sec_5].

**Later work pulls this "why" apart into competing explanations.** Three follow-ups each isolate a different piece of what makes a winning ticket work [S1].

- Zhou et al. find that even the *sign pattern* of a winning ticket's initial weights, without any weight training at all, forms a "supermask" that performs far above chance — implying sign and structure matter as much as the trained magnitudes [S2].
- Liu et al. complicate the efficiency story: for many pruned architectures, training from a fresh random initialization matches or beats fine-tuning the inherited winning weights, suggesting the discovered *architecture* may matter more than its specific initialization values [S3].
- Frankle et al. test whether winning tickets can be found cheaply before training finishes. Fast saliency-based criteria like SNIP and GraSP largely fail to match iterative-magnitude-pruning tickets at higher sparsities, so turning this into a training-time shortcut remains open [S4].

## The Math {#the-math}

**Two sparsity levels bound where initialization starts to matter.** At 80% pruning, 20% of VGG-19's original weights remain, and a random reinitialization of that subnetwork matches the original network's accuracy [§sec_5].

At 98.5% pruning, only 1.5% of the original weights remain — about 13 times fewer than at the 80% level. At this higher sparsity, the paper's own experiments find winning tickets, but reinitializing them causes accuracy to drop substantially [§sec_5].

That's the boundary case the threshold hypothesis rests on: somewhere between 20% and 1.5% of weights remaining, a network stops having enough redundant capacity for a random reinitialization to land on a workable solution, and starts needing the specific, discovered initialization instead [§sec_5].

**The overparameterization-as-search story has a boundary too.** If SGD's job is simply to search an overparameterized network for a well-initialized subnetwork, a cheap saliency score computed at initialization should be able to locate it before training even starts [S4].

SNIP and GraSP are exactly such scores, and at high sparsity they fail to match iterative-magnitude-pruning tickets. So whatever makes a winning ticket findable by SGD during training isn't yet capturable by a one-shot criterion applied before training begins [S4].

## Go Deeper {#go-deeper}

- [Deconstructing Lottery Tickets: Zeros, Signs, and the Supermask](https://www.uber.com/blog/deconstructing-lottery-tickets/) — a figure-heavy walkthrough showing that the sign pattern of a winning ticket's initialization alone performs far above chance untrained; start here for the intuition behind why the initialization's values may matter less than its structure.
- [The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks](https://arxiv.org/abs/1803.03635) — the source paper itself, with its own full discussion of what winning tickets imply for efficient training.
- [Rethinking the Value of Network Pruning](https://arxiv.org/abs/1810.05270) — directly tests whether the pruned architecture or the inherited winning-ticket initialization drives the efficiency gains, complicating the overparameterization-as-search story.
- [Pruning Neural Networks at Initialization: Why Are We Missing the Mark?](https://arxiv.org/abs/2009.08576) — tests whether winning tickets can be identified cheaply before training finishes to make training itself faster, and finds current cheap criteria fall short.

# Discrete Symmetry and Structure of Minima
## TL;DR {#tldr}

- Permutation symmetry doesn't connect minima into valleys — it duplicates each minimum into many separate copies scattered through parameter space.
- The count of copies grows factorially with layer width; adding one extra neuron per layer can instead merge separate replicas into a single connected manifold.
- Quotienting out these symmetries collapses redundant copies into one representative, shrinking the effective search space.

## Intuition {#intuition}

Think of a hidden layer's neurons as interchangeable name tags. Swapping which tag sits on which unit produces a different point in parameter space that computes exactly the same function.

Discrete symmetry acts like a relabeling, not a slide. A continuous symmetry moves a minimum smoothly to a nearby point along a valley; a discrete one instead teleports it to a separate copy built from a different labeling, with nothing filling the space in between.

Each permutation of a layer yields one such copy, and every layer contributes its own independent choice, so the copies multiply across the whole network. That is why the paper treats discrete symmetry as a combinatorial explosion rather than a geometric shape: what matters is how many disconnected copies of one minimum exist, not how wide a valley is.

## Mechanics {#mechanics}

Permutation is the most-studied discrete symmetry: all permutations of a given hidden layer's units land in the same loss level set, so they are not merely nearby but exactly loss-equal [§sec_3_2].

That equal-loss property does not make them one basin. Level-set membership only says the loss value matches; it says nothing about whether a continuous path between two permuted copies stays at that loss, which is a separate, stronger question [§sec_3_2].

Adding just one extra neuron to each layer of a minimal tanh network is enough to merge these separate permutation replicas into a single connected manifold, showing the replicas can be stitched together by a small architectural change even though permutation itself does not connect them [§sec_3_2].

Later work extends this by characterizing full functional equivalence classes for tanh networks and by examining minima directly in function space after quotienting out both permutation and scaling symmetry together [§sec_3_2].

Quotienting has a practical payoff distinct from the counting result: collapsing symmetry-equivalent parameterizations into one representative shrinks the effective search space and can simplify sampling, since a sampler no longer wastes effort revisiting functionally identical points [§sec_3_2].

| Result | What it establishes | Anchor |
|---|---|---|
| Permutations of a layer | Land in the same loss level set (equal loss, not necessarily connected) | [§sec_3_2] |
| One extra neuron per layer (minimal tanh net) | Merges permutation replicas into a single connected manifold | [§sec_3_2] |
| Functional equivalence classes (tanh nets) | Full characterization of which parameterizations compute the same function | [§sec_3_2] |
| Quotient by permutation + scaling | Minima examined directly in function space, redundancy removed | [§sec_3_2] |

## The Math {#the-math}

```derivation
shape: Count how many parameter-space copies of one function exist under layer-wise permutation.
steps:
  - latex: "n! \\text{ orderings of one hidden layer's units}"
    why: "Swapping two units' incoming and outgoing weights leaves the computed function unchanged, so every ordering is a separate point at the same loss [§sec_3_2]"
  - latex: "S_{n_1} \\times \\cdots \\times S_{n_L}"
    why: "Each of the L hidden layers permutes independently, so the symmetry group of the whole network is the product of the per-layer permutation groups [§sec_3_2]"
  - latex: "n_1!\\, n_2! \\cdots n_L!"
    why: "The size of a product group is the product of the factor sizes, giving the total count of functionally identical parameter settings for one minimum [§sec_3_2]"
```

Two boundary cases make the group size concrete:

- $n = 1$: a layer with a single unit contributes a factor of $1! = 1$ — one unit has nothing to swap with, so it adds no redundant copies [§sec_3_2].
- $n = 8$: a modest eight-unit layer alone already contributes $8! = 40320$ — this is the combinatorial explosion the factorial-growth result names, and it multiplies again with every other layer in the network [§sec_3_2].

Quotienting collapses this entire orbit of $n_1! \cdots n_L!$ equivalent parameterizations down to one representative, which is the shrinkage in effective search space the section credits with simplifying sampling [§sec_3_2].

## Go Deeper {#go-deeper}

No verified external resource was supplied for this concept.

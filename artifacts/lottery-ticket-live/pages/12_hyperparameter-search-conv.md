# Hyperparameter Search (Convolutional)

## TL;DR {#tldr}

- This appendix sweeps optimizers and hyperparameters for the Conv-2, Conv-4, and Conv-6 architectures used in the paper's CIFAR10 experiments. [§sec_15]
- It serves two roles: documenting the settings used in the main results, and checking whether the lottery ticket effect survives under different training choices. [§sec_15]
- A pruning result that only reproduces under one narrow hyperparameter setting is a weaker claim than one that reproduces across several. [§sec_15]

## Intuition {#intuition}

A single successful pruning run could be luck: the right optimizer, the right learning rate, and the right architecture happening to line up. Sweeping hyperparameters is how the paper checks that winning tickets are a property of the pruning-and-rewinding procedure itself, not an artifact of one training recipe. [§sec_15]

## Mechanics {#mechanics}

**What the sweep covers:** the appendix explores the space of optimization algorithms and hyperparameters specifically for Conv-2, Conv-4, and Conv-6, the three convolutional architectures evaluated in the main CIFAR10 experiments. [§sec_15]

**Why it mirrors the fully-connected appendix:** it follows the same two-purpose structure as the paper's earlier hyperparameter appendix for MNIST — first pinning down which settings produced the numbers reported in the body of the paper, then re-running the lottery ticket experiment under alternative settings to see whether pruning still finds trainable sparse subnetworks. [§sec_15]

**What a passing sweep establishes:** if winning tickets keep appearing across the swept optimizers and hyperparameters, the pruning result generalizes beyond the one configuration reported in the main text. [§sec_15]

## The Math {#the-math}

**Boundary case:** if winning tickets had only ever been found under one specific optimizer and learning rate, the finding would describe a property of that configuration rather than a general phenomenon of the pruning procedure. [§sec_15]

The appendix's search is what rules this out: repeating the iterative pruning experiment across Conv-2, Conv-4, and Conv-6 under several optimizers and hyperparameter settings, and checking whether the same pattern — sparse subnetworks that train as well or better than the original — reproduces under each one. [§sec_15]

A sweep that fails this test would look like a fragile result: winning tickets appearing for the reported optimizer but disappearing under a different learning rate or a different optimization algorithm, which would tie the phenomenon to that specific recipe rather than to pruning-and-rewinding itself. [§sec_15]

## Go Deeper {#go-deeper}

No research-note resources were supplied for this concept. The supplied evidence for this appendix is limited to its own scope paragraph [§sec_15]; the settings it validates feed directly into [[convolutional-cifar10-experiments]], and its companion split of pruning rates between convolutional and fully-connected layers is covered separately in [[pruning-convolutions-vs-fully-connected-layers]].

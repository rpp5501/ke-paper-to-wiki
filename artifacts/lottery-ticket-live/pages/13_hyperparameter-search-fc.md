# Hyperparameter Search (Fully-Connected)

## TL;DR {#tldr}

This appendix reruns the fully-connected Lenet/MNIST lottery ticket experiment across a range of hyperparameter settings, rather than the single configuration used in the main paper, to check whether the winning-ticket pattern is general or an artifact of that one choice.

## Intuition {#intuition}

Think of the main paper's lottery ticket result as a recipe tested once, in one kitchen, at one oven temperature. It worked — but a single trial cannot say whether the recipe itself is good, or whether that particular kitchen happened to be forgiving.

This appendix is the retest: the same recipe, tried at many oven temperatures, to see if it still comes out the same way.

## Mechanics {#mechanics}

This appendix accompanies the fully-connected Lenet/MNIST experiments in the main paper's body, and exists to explore the hyperparameter space around that architecture rather than to introduce new results of its own [§sec_14].

It serves two purposes: to explain why the main body settled on the hyperparameters it used, and to check how far the lottery ticket pattern observed there extends to other hyperparameter choices [§sec_14].

## The Math {#the-math}

**The confound a single configuration leaves open:** the main-body experiments run the lottery ticket procedure at one fixed setting of the Lenet hyperparameters, so the observed pattern — winning tickets training faster or matching accuracy at higher sparsity — could be a property of the method, or a coincidence of that setting [§sec_14].

**What sweeping separates:** this appendix repeats the lottery ticket experiment across a range of hyperparameter settings around that one configuration, rather than reporting a second experiment at a second fixed point [§sec_14].

**Why that separates the confound:** a pattern that holds at only one setting is evidence about that setting, not about the pruning method; a pattern that holds across the swept range is evidence the earlier finding was not an artifact of the specific values chosen for the main body [§sec_14].

**The case that would separate them:** if the pattern vanished at some hyperparameter settings while holding at others, that would show the lottery ticket effect is conditional on those settings rather than a general property of iterative pruning, and would narrow which configurations the hypothesis is claimed to hold for [§sec_14].

## Go Deeper {#go-deeper}

No external resource has been curated for this concept — the research note lookup returned none for it.

The primary source is the appendix itself (Section 14 of the paper), which is what every claim on this page draws from. For the main-body result this appendix stress-tests, see the Fully-Connected Lenet/MNIST Experiments concept; for the network-width axis of the hyperparameter space treated on its own page, see Network Size Effects.

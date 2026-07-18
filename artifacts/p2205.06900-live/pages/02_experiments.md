# Experiments {#experiments}

## TL;DR {#tldr}
This concept covers the empirical evaluation of MM-BD, the Maximum-Margin Backdoor Detection method, showing how the approach is validated as a UnivBD (Universal Backdoor Detector) across a range of standard image classification benchmarks.

## Intuition {#intuition}
Because MM-BD is pitched as a universal detector — one that should catch backdoors regardless of the trigger pattern used to plant them — its claims need to be stress-tested on datasets that differ meaningfully from one another. Varying the image resolution, image size, and number of classes across benchmarks gives a sense of whether the maximum-margin statistic generalizes, rather than only working in the narrow setting it was originally designed around.

## Mechanics {#mechanics}
The evaluation is built around four benchmark datasets chosen specifically because they differ in image resolution, image size, and number of classes: CIFAR-10, CIFAR-100, TinyImageNet, and GTSRB [§sec_4]. This spread of datasets is the mechanism by which the experiments test the "universal" part of UnivBD's design — a detector that only performs well on one resolution or class-count regime would not support the broader claim [§sec_4]. Further dataset specifics (splits, sizes, preprocessing) are deferred to an appendix rather than detailed in this section [§sec_4].

## The Math {#the-math}
The local context for this section contains no equations — it describes the experimental setup (dataset selection) rather than the detection statistic itself, so no formulas are reproduced here [§sec_4].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no additional resources to list beyond the paper section already cited (sec_4).

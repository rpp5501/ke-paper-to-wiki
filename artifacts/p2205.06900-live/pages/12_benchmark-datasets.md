# Benchmark Datasets

## TL;DR {#tldr}
This concept covers the benchmark datasets used to evaluate MM-BD, the post-training backdoor detection method. These datasets serve as the experimental testbed for validating that MM-BD's maximum margin statistic can detect backdoor attacks with arbitrary trigger pattern types across varying image resolutions, image sizes, and class counts.

## Intuition {#intuition}
To show that a detection method generalizes rather than overfitting to one narrow setting, it needs to be tested across datasets that differ meaningfully in scale and complexity — more classes, larger images, and more visually cluttered scenes all stress a detector differently. Using a spread of such datasets is how the paper builds confidence that MM-BD's detection capability isn't an artifact of a single, convenient dataset.

## Mechanics {#mechanics}
The experiments are conducted mainly on four benchmark datasets with different image resolution, image size, and number of classes: CIFAR-10, CIFAR-100, TinyImageNet, and GTSRB [§sec_4]. These datasets were chosen specifically because they vary along axes (resolution, size, class count) relevant to testing whether the detector's performance holds across different problem scales [§sec_4]. Further details of these datasets are deferred to an appendix rather than being included in the main experimental section [§sec_4].

## The Math {#the-math}
The local context for this concept contains no equations — the benchmark datasets are described only narratively as the experimental setup, with no associated formulas [§sec_4].

## Go Deeper {#go-deeper}
No research note is available for this concept, so no additional resources can be listed here.

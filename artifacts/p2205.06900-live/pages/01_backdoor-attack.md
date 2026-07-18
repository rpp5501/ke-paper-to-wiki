# Backdoor Attack (BA)

## TL;DR {#tldr}
A backdoor attack (BA) corrupts a classifier during training so that it behaves normally on clean inputs but reliably misclassifies any input into an attacker-chosen target class whenever a secret trigger pattern is present. It is the threat model that backdoor detection methods, including the maximum-margin approach in MM-BD: Maximum-Margin Backdoor Detection, are built to catch, and it sits in direct opposition to Backdoor Defense, whose goal is to prevent or detect exactly this behavior.

## Intuition {#intuition}
Think of a BA as planting a secret password into a model: the model works exactly as expected until it sees a specific visual cue, at which point it deliberately outputs whatever answer the attacker wants, regardless of the input's true content. The attack is designed to be stealthy on two fronts — the model's accuracy on ordinary, trigger-free inputs stays high so nothing looks wrong under normal testing, and the trigger pattern itself is kept small or subtle so it isn't noticed by a human inspecting the poisoned training data or the triggered test samples.

## Mechanics {#mechanics}
A BA targets a classifier operating over some sample space and label space, and it pursues two simultaneous goals: the victim model must learn to output the attacker's target class whenever a test sample from any source class is embedded with the backdoor pattern (BP), while still correctly classifying clean, BP-free samples [§sec_2_1]. The attack is typically carried out by poisoning the training set — a small number of samples originally drawn from the source classes are embedded with the same BP that will later be used at test time and are relabeled to the target class, so the model learns to associate the trigger with the target output during ordinary training [§sec_2_1]. This threat model originated in and has been most intensively studied for image classification, though it has since been extended to other domains and tasks [§sec_2_1].

For images, the BP itself can take several forms: an additive, imperceptibly small perturbation added directly to pixel values and clipped to stay in range; a local patch inserted via an image-wide binary mask so only a small region is altered; or a pattern blended into the image using a mask and a blending factor kept close to zero for imperceptibility [§sec_2_1]. More recent variants move beyond these simple pixel-space edits, using a reflection-based BP that mimics a physical reflection on a smooth surface, a warping-based BP that applies a spatial transformation to existing pixels rather than adding new content, or a BP embedded directly in the frequency domain of the image [§sec_2_1].

## The Math {#the-math}
The local context describes the BP embedding mechanisms in words (additive, patch-based, and blend-based perturbations) but does not provide them as formal labeled equations, so no display equations can be reproduced verbatim here [§sec_2_1].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here. For related material within this wiki, see the prerequisite MM-BD: Maximum-Margin Backdoor Detection to understand how BAs are detected, and Backdoor Defense for the contrasting defender's perspective.

# Additive Perturbation BP
## TL;DR {#tldr}
Additive Perturbation is one of three backdoor pattern (BP) families studied in MM-BD, alongside patch replacement and blending. It creates a backdoor trigger by adding a fixed perturbation signal directly to the pixel values of an image, rather than replacing a region of the image or blending in a separate pattern.

## Intuition {#intuition}
Instead of pasting a visible patch onto an image or fading in a ghostly overlay, an additive perturbation BP nudges pixel intensities across the image (or at a single pixel) by a small, consistent amount whenever the attacker wants to trigger the backdoor. Because the change can be spread globally in a structured way (like a chessboard) or localized to a single pixel, it sits at one extreme of trigger "visibility" and locality compared to the patch and blending families it is grouped with under BP Type Settings.

## Mechanics {#mechanics}
Within the taxonomy of BP types considered in the paper, additive perturbation covers two concrete instantiations: a global chessboard pattern applied across the image, and a local pixel perturbation confined to a single pixel [§sec_4_1_1]. These are labeled A1 and A2 respectively in the paper's shorthand, distinguishing them from the patch-replacement BPs (A3 noisy patch, A4 unicolor patch) and the blended BP (A5 blended noisy patch) [§sec_4_1_1]. For A2, the specific pixel to be perturbed is chosen at random and then held fixed for the duration of that attack, giving each generated backdoor attack (BA) a distinct but static trigger location [§sec_4_1_1]. Each of A1-A5 is combined with either a single-source-class ('S') or multiple-source-class ('M') setting and one randomly chosen target class to define a full backdoor attack instance, which is then realized by training a classifier using the classical data-poisoning protocol [§sec_4_1_1].

## The Math {#the-math}
The local context for this concept is descriptive (defining BP settings and naming conventions) and contains no equations, so there is no formal expression to reproduce for Additive Perturbation BP itself [§sec_4_1_1].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.

# Blending BP
## TL;DR {#tldr}
Blending BP is one of three backdoor pattern (BP) types studied in MM-BD's experimental settings, alongside additive perturbation and patch replacement. It defines backdoors created by blending a patch or pattern into the input image rather than adding a perturbation or fully replacing a region, and it is used to test whether the detector generalizes across different backdoor pattern types.

## Intuition {#intuition}
Instead of swapping in a hard-edged patch or nudging pixel values additively, a blending BP softly merges a trigger pattern with the original image content, producing a backdoor that is visually blended into the scene rather than pasted on top of it. This makes blending backdoors a useful stress test for detectors, since the trigger is embedded in a qualitatively different way than additive or patch-replacement triggers, helping validate that a detection method isn't overfit to one style of backdoor pattern.

## Mechanics {#mechanics}
Within the paper's settings, the blended BP is instantiated concretely as a "blended noisy patch," which the authors abbreviate as A5 for reference throughout their experiments [§sec_4_1_1]. Like the other patch-based BP (A3, A4), the blended patch's color and location are randomly selected and then fixed for the duration of each individual attack, distinguishing it from the additive perturbation BPs where a chessboard pattern is global (A1) or a single pixel location is randomly selected and fixed (A2) [§sec_4_1_1]. The blending BP is paired with the same experimental scaffolding as the other four BPs (A1-A4): each is combined with a randomly chosen single target class and either a single ('S') or multiple ('M') source-class setting to form a distinct backdoor attack (BA) configuration, e.g., "A5-M" denotes a blended BP attack with multiple source classes [§sec_4_1_1]. On CIFAR-10, blending BP attacks are generated for both the 'S' and 'M' source-class settings, while on CIFAR-100 and GTSRB only the 'M' setting is used due to insufficient per-class images to construct successful single-source attacks with limited poisoning data [§sec_4_1_1]. For TinyImageNet, the blending BP was not selected as the single BA ensemble generated for that dataset — the authors instead arbitrarily chose the A3-M configuration given the high cost of training on TinyImageNet, so blending-specific results are absent for that dataset [§sec_4_1_1].

## The Math {#the-math}
The local context for this concept is drawn from the experimental settings section and does not include a formal embedding function or equation for the blending BP, only a textual description referencing an embedding function defined elsewhere in the paper; no [eq_N] entry is available here to reproduce [§sec_4_1_1].

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no additional resources to list here.

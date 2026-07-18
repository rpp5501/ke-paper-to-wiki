# Patch Replacement BP
## TL;DR {#tldr}
Patch Replacement is one of the three canonical backdoor pattern (BP) families studied in MM-BD, alongside additive perturbation and blending. Instead of adding a signal to the image, this BP type works by overwriting a region of the input with a fixed, attacker-chosen patch, and it is one of the settings varied when constructing the paper's ensembles of backdoor attacks (BAs) used to stress-test the detector.

## Intuition {#intuition}
Think of patch replacement as pasting a sticker onto part of an image rather than tinting the whole picture: a chunk of pixels is simply swapped out for something else — random-looking noise or a solid block of color — and the classifier is trained to treat that sticker as the trigger for the target class. Because the swap is spatially localized and visually distinct from additive or blended triggers, it represents a structurally different kind of BP that the detector needs to handle alongside the other two types.

## Mechanics {#mechanics}
Within the patch replacement family, the paper considers two concrete variants: a noisy patch and a unicolor patch, denoted A3 and A4 respectively in the paper's five-BP taxonomy (A1–A5) [§sec_4_1_1]. For both of these patch-based BPs, the color and the location of the patch are randomly selected but then held fixed for each individual attack, so every backdoored image in a given attack instance carries the same patch in the same place [§sec_4_1_1]. These attacks are generated using the classical data poisoning protocol, with one target class chosen at random per attack and either a single ("S") or multiple ("M") source classes, and each resulting BA is verified to achieve high attack success rate with negligible clean-accuracy degradation before being included in an ensemble [§sec_4_1_1].

## The Math {#the-math}
The local context describes the experimental settings for patch replacement BPs (patch type, color/location randomization, source/target class configuration) but does not provide the underlying embedding-function equations for this BP type, so no equation can be reproduced here [§sec_4_1_1].

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no additional resources to list beyond the settings described in Sec. 4.1.1 of the paper itself.

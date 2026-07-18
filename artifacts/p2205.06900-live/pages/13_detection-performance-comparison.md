# Detection Performance Comparison
## TL;DR {#tldr}
This concept covers the empirical comparison of UnivBD (the Universal Backdoor Detector) against a set of state-of-the-art post-training backdoor-attack (BA) detectors — NC, TABOR, ABS, PT-RED, META, and TND — across multiple datasets and backdoor pattern (BP) types. The headline finding is that existing detectors each work well only for the narrow class of BP types they were designed around, while UnivBD maintains high detection accuracy and low false-detection rates across all BP types, all with greater computational efficiency and without needing any legitimate images.

## Intuition {#intuition}
Each baseline detector bakes in an implicit assumption about what a backdoor trigger looks like — a small patch, an additive perturbation, a particular color or shape — so it only "sees" attacks that match that assumption and is blind to the rest. Comparing detectors head-to-head across a deliberately diverse set of BP types exposes these blind spots directly: a detector that shines on one attack family can fail almost completely on another. UnivBD's comparative advantage is framed not as being better at any one narrow task, but as being invariant to BP type altogether, which is the core motivating contrast for this comparison.

## Mechanics {#mechanics}
The comparison setup fixes practical choices for both sides: baselines are run with their original implementations with only modest changes such as tuning the detection threshold to maximize their own performance, and META specifically uses the original authors' code to train its meta-classifier [§sec_4_1_2]. UnivBD itself is run with gradient ascent (50 random initializations, uniform pixel-value initialization) to solve its optimization problem, with a detection threshold corresponding to 0.95 detection confidence; the paper notes these optimization choices are not critical to final accuracy [§sec_4_1_2].

On CIFAR-10, CIFAR-100, Tiny-ImageNet, and GTSRB, results are reported as detection counts across BP families A1–A5 (in both single-source "S" and multi-source "M" settings), plus the fraction of clean (unattacked) classifiers correctly identified as clean [§sec_4_1_2]. PT-RED and META are evaluated only on CIFAR-10 because their computational cost is prohibitive on the other datasets, and only a subset of BA ensembles is reported for CIFAR-100, Tiny-ImageNet, and GTSRB due to time and space constraints [§sec_4_1_2].

The accuracy pattern confirms the type-specific blind spots predicted by intuition: NC detects patch-replacement BPs (A3–A4) well but fails on the local-perturbation BP (A2); ABS and META, designed for patch BPs (A3–A5), do not address additive-perturbation BPs (A1–A2); PT-RED is effective for additive-perturbation BPs (A1–A2) but generally ineffective elsewhere; and TABOR and TND underperform across the board due to extra constraints they impose on trigger shape or color [§sec_4_1_2].

UnivBD is reported as achieving high detection accuracy across all BP types (A1–A5) with a low false-detection rate on every dataset tested, and even a joint deployment of ABS and PT-RED together only reaches comparable accuracy to UnivBD while incurring more false detections and substantially higher computational cost [§sec_4_1_2].

A further axis of comparison is source-class sensitivity: NC, TABOR, ABS, and TND all assume a BA has multiple source classes (the "M" setting) and are correspondingly weaker against single-source-class ("S") attacks, whereas UnivBD makes no such assumption and is reported as generally invariant to the number of source classes [§sec_4_1_2]. UnivBD is also distinguished by not requiring any legitimate (clean) images for detection, unlike the other methods compared [§sec_4_1_2].

A companion efficiency comparison reports average execution time (seconds, on an NVIDIA RTX-3090) for each detector across the four datasets, with UnivBD consistently the fastest of the group, and the paper notes this can be reduced further by using fewer random initializations without significant accuracy loss [§sec_4_1_2].

## The Math {#the-math}
The local context for this concept is a results/discussion section reporting detection-accuracy tables and execution-time tables; it references UnivBD's underlying optimization problem only in passing ("solve problem () using gradient ascent") and does not reproduce any labeled equation here, so there is no [eq_N] content to display for this concept. [§sec_4_1_2]

## Go Deeper {#go-deeper}
No research note is available for this concept, so no external resources can be linked here.

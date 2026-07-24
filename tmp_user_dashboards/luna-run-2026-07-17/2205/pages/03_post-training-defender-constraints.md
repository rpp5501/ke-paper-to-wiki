# Post-Training Defender Constraints

## TL;DR {#tldr}
MM-BD is designed for a downstream user who has the trained classifier but no training set, no known trigger, and no clean reference classifier.

## Intuition {#intuition}
This is an inspection problem, not a retraining problem. The defender has the finished artifact and must decide whether its behavior contains a hidden route, even when the evidence used to build the route is gone or proprietary.

## Mechanics {#mechanics}
The paper lists five assumptions: the defender does not know whether an attack exists, does not know the pattern type, lacks the training set, lacks a clean classifier for comparison, and may not possess clean examples. MM-BD needs no clean samples for detection, although MM-BM later uses a small clean set for accuracy preservation [§sec_1].

## The Math {#the-math}
The detection input is the model itself: $g_c(\cdot)$ is queried over the input domain $\mathcal{X}$, while the clean sample set $D$ appears only in the mitigation problem [§sec_1]. This separation is the reason the detector can be data-free at inference time [§sec_1].

## Go Deeper {#go-deeper}
- Clean-Data-Free Estimation shows how random inputs replace a reference dataset.
- Unsupervised Anomaly Inference shows how a decision is made without labels.
- Accuracy-Preserving Lagrangian explains the extra data needed for repair.

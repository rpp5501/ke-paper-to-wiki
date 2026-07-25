# Clean-Data-Free Estimation

## TL;DR {#tldr}
Detection does not need legitimate images: it generates random valid inputs and optimizes the inspected classifier's logits directly.

## Intuition {#intuition}
A conventional inspector compares a suspicious model with trusted examples. MM-BD instead asks the model to reveal its own strongest class separation, using random probes as starting points rather than semantic samples.

## Mechanics {#mechanics}
For each class, the detector initializes inputs randomly inside the valid domain, performs projected gradient ascent on the margin, and retains the largest local solution across starts [§sec_1]. The paper emphasizes that this avoids the clean-sample requirement of many reverse-engineering detectors [§sec_1].

## The Math {#the-math}
The optimization uses only $g_c$ and $\mathcal{X}$: $$r_c=\max_{\mathbf{x}\in\mathcal{X}}m_c(\mathbf{x})$$ [§sec_1]. The clean set $D$ is absent from this expression; it enters only the separate MM-BM mitigation constraint [§sec_1].

## Go Deeper {#go-deeper}
- Post-Training Defender Constraints defines the information boundary.
- Projected Gradient Estimation explains the random-probe solver.
- Unsupervised Anomaly Inference explains why labels are unnecessary.

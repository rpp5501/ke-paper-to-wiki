# Optimizer
## TL;DR {#tldr}
The Optimizer is the training-time mechanism that updates the Transformer's weights during learning, sitting within the broader Training process for the model described in "Attention Is All You Need." It governs how quickly and how stably the network converges as it learns to perform sequence transduction.

## Intuition {#intuition}
Think of the optimizer as the "steering and throttle" for training: it decides how big a step to take when adjusting weights after each batch, and how that step size should change over time. Early in training, small cautious steps help the model avoid instability while its internal representations are still poorly formed; later, steadily shrinking steps let it settle into a good solution rather than overshooting it. This scheduling behavior is what ties the Optimizer concept to the parent Training process — it's one of the key knobs that makes large-scale Transformer training actually work in practice.

## Mechanics {#mechanics}
Training uses the Adam optimizer, configured with specific values, as described in the Optimizer section [§sec_5_3].

Rather than holding the learning rate constant, the authors vary it over the course of training according to a schedule: the rate increases linearly for an initial number of warmup steps, then decreases proportionally to the inverse square root of the step number thereafter [§sec_5_3].

## The Math {#the-math}
The learning rate schedule is given by [eq_5], which combines an inverse-square-root decay term with a linear warmup term, taking the minimum of the two scaled by the model dimensionality — so the rate rises during the warmup phase and falls afterward as training progresses [eq_5].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no additional resources to list here.

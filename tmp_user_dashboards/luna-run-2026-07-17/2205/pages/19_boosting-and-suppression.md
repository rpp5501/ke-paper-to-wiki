# Target-Logit Boosting and Non-Target Suppression

## TL;DR {#tldr}
Repeated backdoor features can both boost the target logit and suppress competing logits, producing the margin anomaly MM-BD measures.

## Intuition {#intuition}
A backdoor is not merely a louder target class. It can also make the alternatives quieter when the model sees the feature combination associated with the poison. The margin captures both effects in one comparison.

## Mechanics {#mechanics}
The paper attributes the abnormal target margin to overfitting on a common poisoned feature. It contrasts this with ordinary class-discriminating features, which vary across examples and therefore do not create the same reusable direction [§sec_1]. The appendix shows why maximizing only a target logit can create false detections when semantically neighboring classes rise together [§sec_1].

## The Math {#the-math}
For a target $t$, the relevant contrast is $$g_t(\mathbf{x})-\max_{k\ne t}g_k(\mathbf{x})$$ [§sec_1]. In the paper's linearized argument, confident clean and triggered classifications imply a target-versus-source response to the trigger of at least $2\tau$ under the stated assumptions [§sec_1].

## Go Deeper {#go-deeper}
- Pre-Softmax Logit Landscape provides the geometric view.
- Maximum-Margin Objective formalizes the two-sided comparison.
- Empirical Scope and Failure Modes notes intrinsic backdoors that can mimic this effect.

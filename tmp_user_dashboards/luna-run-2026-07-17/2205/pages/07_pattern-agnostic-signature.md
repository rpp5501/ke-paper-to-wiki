# Pattern-Agnostic Attack Signature

## TL;DR {#tldr}
The proposed signature is not the trigger image itself; it is the unusually large target-class margin produced by repeated backdoor features in the trained model.

## Intuition {#intuition}
Different keys can open the same faulty lock. The pixel pattern may be a patch, noise, a blend, or a more advanced construction, but the repeated association can still leave the same kind of geometric scar in the classifier's output surface.

## Mechanics {#mechanics}
MM-BD avoids reverse-engineering a patch or assuming a perturbation norm. It optimizes the classifier's margin directly, so the input-space embedding mechanism is treated as an unknown nuisance [§sec_1]. The paper argues that even sample-specific triggers can share semantic regularities in latent space, which may preserve detectability [§sec_1].

## The Math {#the-math}
The intended separation is $$r_t \gg r_c\quad\text{for non-target }c$$ [§sec_1]. This is a comparative claim about the target statistic among classes, not a guarantee for every attack; the paper explicitly discusses intrinsic backdoors and adaptive attacks as limits [§sec_1].

## Go Deeper {#go-deeper}
- Trigger-Embedding Families catalogs the explicit image mechanisms used in experiments.
- Target-Logit Boosting and Non-Target Suppression gives the causal intuition.
- Adaptive Min-Max Attack shows how an attacker can target the signature.

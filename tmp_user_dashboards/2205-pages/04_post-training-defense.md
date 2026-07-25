# Post-Training Defense Scenario

## TL;DR {#tldr}
In the post-training setting the defender receives only the finished classifier — no training data, no poisoned samples, often only a handful of clean images — and must still decide whether it hides a backdoor. This is the hardest, most realistic defense position, and the one UnivBD targets.

## Intuition {#intuition}
You buy a pretrained model from a vendor. You cannot see how it was trained or on what. You may have a few clean pictures to poke it with, nothing more. Can you tell if it was sabotaged? Defenses that clean the training set are useless here — the training set is gone. The only thing you hold is the model's input–output behavior.

That constraint is exactly why the method works through the logit landscape: the surface is fully determined by the model you already have.

## Mechanics {#mechanics}
The defender assumes access to the trained classifier and a small set of clean inputs, but no access to the training set, the triggers, or the attacker's target class [§sec_3].

Every quantity the detector uses — logits, margins, gradients — is computable from the model alone, so the method respects these limits [§sec_3].

## The Math {#the-math}
The scenario is defined by what is *available* rather than an equation: the detector is a function of the model $f$ and a small clean set $\mathcal{D}$ only,

$$ \text{decision} = \mathcal{A}\big(f,\ \mathcal{D}\big), \qquad \mathcal{D}\ \text{small and clean}. $$

No term depends on training data or trigger knowledge, which is what makes the defense deployable on third-party models [§sec_3].

## Go Deeper {#go-deeper}
- Universal Backdoor Detection is the concrete procedure $\mathcal{A}$.
- Backdoor Mitigation handles the case where retraining from a trusted source is impossible [§sec_3_3].

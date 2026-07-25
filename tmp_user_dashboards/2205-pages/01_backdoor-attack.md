# Backdoor Attack

## TL;DR {#tldr}
A backdoor attack poisons training so a model behaves normally on ordinary inputs but flips to an attacker-chosen class whenever a small fixed trigger is present. It is the threat this paper detects — after the model is already trained.

## Intuition {#intuition}
Picture a security guard who does their job perfectly, except that anyone wearing a particular red pin is waved through no matter what. The guard looks trustworthy on every normal test; the pin is a secret backdoor. A backdoored classifier is the same: clean accuracy stays high, so the attack hides, while any input carrying the trigger is quietly routed to the target class.

The attacker only needs the trigger to be *common* — the same pattern reused across inputs — because that is what the network can latch onto during training.

## Mechanics {#mechanics}
The attacker adds poisoned examples that carry a trigger and are labeled as the target class. The victim network learns two things at once: correct behavior on clean data, and "trigger present ⇒ target class" [§sec_2_1].

Success is judged by two numbers: high accuracy on clean inputs (so the attack is stealthy) and a high attack success rate on triggered inputs [§sec_2_1].

## The Math {#the-math}
Let $f$ be the classifier over inputs $\mathbf{x}$ in domain $\mathcal{X}$ with labels in $\mathcal{Y}$, and let $\Delta(\cdot)$ embed the trigger. A backdoor attack wants, for the target class $t$,

$$ f(\mathbf{x}) = y_{\text{true}} \quad\text{yet}\quad f\!\left(\Delta(\mathbf{x})\right) = t \quad \text{for most } \mathbf{x}. $$

Because the same $\Delta$ works across many inputs, the trigger leaves a consistent imprint on the target class's decision region — the imprint this paper hunts for [§sec_2_1].

## Go Deeper {#go-deeper}
- Backdoor Trigger details the additive / patch / blended embedding functions $\Delta$.
- Target Class is the single class whose decision region is warped.
- Post-Training Defense Scenario fixes what the defender is (and is not) allowed to use.

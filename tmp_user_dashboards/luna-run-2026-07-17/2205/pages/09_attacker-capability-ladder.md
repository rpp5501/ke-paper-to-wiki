# Basic, Advanced, and Adaptive Attackers

## TL;DR {#tldr}
The paper evaluates increasingly capable attackers, from classical poisoning to attackers who control training and explicitly optimize against MM-BD.

## Intuition {#intuition}
Think of three adversaries. One can slip notes into the training pile. Another can rehearse with a surrogate model. The strongest knows the detector's test and changes training so the backdoor works while its geometric fingerprint is less obvious.

## Mechanics {#mechanics}
A basic attacker can poison data but lacks the original training samples and process control. An advanced attacker may gather data or control training. An adaptive attacker has full training control and full knowledge of MM-BD, so it can add a margin-suppressing term to its objective [§sec_1].

## The Math {#the-math}
The adaptive setting makes the attacker solve a nested problem of the form $$\min_{\phi}\;L_{\mathrm{clean}}(\phi)+L_{\mathrm{backdoor}}(\phi)+\beta_M L_M(t;\phi)$$ [§sec_1]. The paper defines $L_M$ as the target class's maximum margin, so increasing $\beta_M$ pressures the attack to hide the detector's signal [§sec_1].

## Go Deeper {#go-deeper}
- Adaptive Min-Max Attack expands the last rung into an explicit objective.
- Backdoor Threat Model describes the defender's target.
- Empirical Scope and Failure Modes summarizes the cost and trade-offs of evasion.

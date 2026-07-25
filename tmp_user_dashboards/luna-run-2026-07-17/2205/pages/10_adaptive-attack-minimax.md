# Adaptive Min-Max Attack

## TL;DR {#tldr}
An adaptive attacker can add a penalty on the target maximum margin, but the paper reports a cost in attack success, clean accuracy, optimization time, or some combination.

## Intuition {#intuition}
The attacker is trying to keep two things true at once: the trigger must still work, and the detector must no longer see a tall target hill. Flattening the hill while preserving the backdoor turns training into a harder nested optimization problem.

## Mechanics {#mechanics}
The adaptive objective adds the target margin to ordinary clean and poisoned cross-entropy training. The paper reports that stronger margin penalties can make attacks undetectable, but also degrade ASR or ACC; a stronger variant that regularizes other classes is even more expensive [§sec_1].

## The Math {#the-math}
With model parameters $\phi$, the adaptive attack includes $$L_M(t;\phi)=\max_{\mathbf{x}\in\mathcal{X}}\left[g_t(\mathbf{x};\phi)-\max_{k\ne t}g_k(\mathbf{x};\phi)\right]$$ [§sec_1]. The attacker minimizes a weighted sum of clean loss, backdoor loss, and $\beta_ML_M$ [§sec_1].

## Go Deeper {#go-deeper}
- Attacker Capability Ladder provides the capability assumptions.
- Pattern-Agnostic Attack Signature is the quantity being hidden.
- Empirical Scope and Failure Modes gives the paper's limitation boundary.

# Universal Post-Training Backdoor Detection (MM-BD)

## TL;DR {#tldr}
MM-BD detects a backdoored classifier by searching its pre-softmax logit landscape for a class with an unusually large maximum margin, without assuming the trigger type or using clean samples for detection.

## Intuition {#intuition}
Imagine testing a sealed machine by asking what output it can make when you are allowed to feed it arbitrary inputs. A backdoor target class has learned an unusually reusable route to dominance: many different starting points can be pushed toward a large separation from every competing class. MM-BD treats that geometric oddity as the evidence of compromise.

## Mechanics {#mechanics}
The detector has two stages. It estimates one maximum-margin statistic per class with multi-start projected gradient ascent, then tests whether the largest statistic is an outlier under a null distribution fitted from the other classes [§sec_1]. If the p-value is below the fixed significance level, the class owning the largest statistic is reported as the likely target [§sec_1].

## The Math {#the-math}
For class $c$, the paper's statistic is $$r_c = \max_{\mathbf{x}\in\mathcal{X}}\left[g_c(\mathbf{x})-\max_{k\ne c}g_k(\mathbf{x})\right]$$ [§sec_1]. The detector sets $r_{\max}=\max_c r_c$ and uses $$p_v = 1-H_0(r_{\max})^{K-1}$$ [§sec_1].

## Go Deeper {#go-deeper}
- Backdoor Threat Model explains what the attacker and defender can access.
- Maximum-Margin Objective derives the statistic used by the detector.
- Maximum-Margin Backdoor Mitigation (MM-BM) covers the optional repair path.

# Algorithm for BA Mitigation
## TL;DR {#tldr}
This concept is the mitigation-side algorithm of MM-BD: once a backdoor is detected, it automatically tunes a Lagrange multiplier to find the tightest per-neuron activation bound that suppresses the backdoor's effect while preserving clean-data accuracy. It sits under the broader "Mitigation of Backdoor Attack" effort and is defined in terms of the Lagrangian Minimization for Neuron Bounding.

## Intuition {#intuition}
Rather than picking a fixed penalty weight by hand and hoping it balances "kill the backdoor" against "don't break clean accuracy," the algorithm adjusts that weight on the fly across iterations, growing or shrinking it as needed until both goals are satisfied simultaneously. The result is an automatic dial that clamps down on the neurons responsible for the backdoor's outsized influence, without a human having to retune it for every model or trigger.

## Mechanics {#mechanics}
The algorithm targets internal-layer neurons flagged by the paper's detection statistic — the units whose activations on putative-trigger inputs deviate most from the clean-data order-statistic distribution used for detection [S1]. It takes as inputs a dataset, the unbounded logit functions, an accuracy constraint, a step size, a maximum iteration count, and a scaling factor, and is initialized with a large multiplier and a small positive threshold before iterating [§sec_5]. Instead of using a fixed Lagrange multiplier, the procedure updates it automatically at each iteration, searching for the smallest per-neuron activation upper bound such that enforcing it drives the detection statistic back below threshold, trading off statistic penalty against clean-accuracy loss via Lagrangian relaxation — in the same spirit as the gradient-based reverse-engineering used by Neural Cleanse [S2]. Clipping the flagged neurons' activations to this learned bound caps the "extra" signal the trigger can inject into downstream layers, suppressing the target-class logit boost below what is needed to override genuine class evidence, even when the trigger is still present in the input [S1][S3].

This per-neuron Lagrangian-bound formulation is distinct from adjacent optimization-based mitigations: I-BAU instead perturbs or unlearns weights via implicit hypergradients over a min-max trigger objective, and CLP bounds channel Lipschitz constants rather than raw activations [S3][S4].

## The Math {#the-math}
The local context references the Lagrangian objective from the neuron-bounding formulation and its minimization procedure (Alg. 1), but the specific equation text and numbered display forms were not resolved in this section beyond the algorithm's stated inputs, initialization, and outputs — so no [eq_N] block can be faithfully reproduced here [§sec_5].

## Go Deeper {#go-deeper}
- A Benchmark Study of Backdoor Data Poisoning Defenses for Deep Neural Network Classifiers and A Novel Defense (https://arxiv.org/abs/2005.12439) — works out the detection-statistic-driven constrained optimization for bounding suspect-neuron activations that this concept describes.
- Neural Cleanse reference implementation (https://github.com/bolunwang/backdoor) — canonical optimization-plus-activation-patching pipeline that the Lagrangian-bound mitigation generalizes.
- Adversarial Unlearning of Backdoors via Implicit Hypergradient (I-BAU) (https://arxiv.org/abs/2110.03735) — contrasting optimization-based mitigation useful for comparing against the Lagrangian-bound formulation.
- Data-free Backdoor Removal based on Channel Lipschitzness (CLP) (https://arxiv.org/abs/2208.03111) — related bounding-style mitigation offering a comparison point for per-neuron activation bounds.

# Empirical Scope and Failure Modes

## TL;DR {#tldr}
The paper evaluates MM-BD across four image datasets and additional speech and point-cloud settings, while documenting false positives, intrinsic backdoors, and adaptive evasion limits.

## Intuition {#intuition}
A detector can be strong in its intended regime and still have honest blind spots. Here the important question is not only whether the method works on standard poisoned models, but also whether clean training quirks or a determined attacker can produce the same signature.

## Mechanics {#mechanics}
The main experiments cover CIFAR-10, CIFAR-100, TinyImageNet, and GTSRB with additive, patch, and blended patterns, and compare against NC, TABOR, ABS, PT-RED, META, and TND [§sec_1]. The paper reports broadly pattern-invariant detection, but point-cloud performance is weaker in the presence of intrinsic backdoors; class imbalance and deliberately margin-regularized clean models can cause false positives [§sec_1].

## The Math {#the-math}
The nominal false-positive control uses $\theta=0.05$, but the paper notes that estimating $H_0$ from few classes can make observed rates differ from the nominal level [§sec_1]. For adaptive attacks, lowering the target margin can be expressed as an extra term in the attacker objective, creating a direct detector-versus-attacker trade-off [§sec_1].

## Go Deeper {#go-deeper}
- Adaptive Min-Max Attack details the strongest evasion experiment.
- Order-Statistic p-Value explains why class count affects calibration.
- Maximum-Margin Backdoor Mitigation (MM-BM) covers the separate repair results.

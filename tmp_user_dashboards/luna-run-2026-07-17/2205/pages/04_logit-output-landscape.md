# Pre-Softmax Logit Landscape

## TL;DR {#tldr}
The logit landscape is the set of class score functions before softmax; MM-BD searches this landscape because a backdoor changes its geometry before probabilities are normalized.

## Intuition {#intuition}
Softmax is a translator that turns scores into probabilities. MM-BD listens to the raw voices before translation, where it can compare how far one class can rise above all others rather than being distracted by normalization.

## Mechanics {#mechanics}
Let $g_c(\mathbf{x})$ be the logit for class $c$. For every candidate class, MM-BD asks how large the gap to the strongest rival can become over valid inputs. A backdoor repeats a common feature during poisoning, so the target's score surface can acquire a sharper, more reusable direction than ordinary class evidence [§sec_1].

## The Math {#the-math}
The class margin at an input is $$m_c(\mathbf{x})=g_c(\mathbf{x})-\max_{k\ne c}g_k(\mathbf{x})$$ [§sec_1]. The landscape statistic is the supremum of this margin over $\mathcal{X}$, so it measures separability from the strongest competitor rather than the absolute value of one logit [§sec_1].

## Go Deeper {#go-deeper}
- Maximum-Margin Objective turns the landscape into a statistic.
- Boosting and Suppression explains the backdoor-induced deformation.
- Projected Gradient Estimation describes how the search is approximated.

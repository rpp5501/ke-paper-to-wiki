# Maximum Margin (MM) Statistic

## TL;DR {#tldr}
The MM statistic is one number per class: the biggest logit gap that a single small perturbation, shared across a batch of clean images, can open up for that class. A backdoored class's MM statistic is a glaring outlier.

## Intuition {#intuition}
Ask each class the same question: "how far above all your rivals can I push your score using one universal nudge that I'm allowed to add to any image?" For an honest class the answer is modest — no single nudge fools the network on everything. For the backdoored class the answer is huge, because the trigger *is* exactly such a universal nudge, and the network was trained to obey it.

So we never need to know the trigger. We just measure how much margin each class can be handed, and watch for the one that answers far too generously.

## Mechanics {#mechanics}
For a candidate target class $t$, we search over a small common perturbation $\mathbf{x}$ (constrained to the valid input range $\mathcal{X}$) that maximizes the gap between $g_t$ and the strongest competing logit, aggregated over a set of clean images [§sec_3_1].

The resulting maximized gap is the class's MM statistic. Computing it for every class yields the sample the detector then screens for an outlier [§sec_3_2].

## The Math {#the-math}
The MM statistic for target $t$ is the value of the maximization

$$ \operatorname{MM}(t) = \max_{\mathbf{x} \in \mathcal{X}}\ \Big[\, g_t(\mathbf{x}) - \max_{c \neq t} g_c(\mathbf{x}) \,\Big], $$

i.e. the largest achievable margin of $t$ over its nearest rival under one shared perturbation [eq_1]. A backdoor makes $\operatorname{MM}(t)$ for the true target far exceed the values seen for clean classes [§sec_3_1].

## Go Deeper {#go-deeper}
- Estimating the Margin by Gradient Ascent solves this maximization in practice [§sec_3_2].
- Detection via an Atypical Margin turns the vector of $\operatorname{MM}(t)$ values into a decision.

# Universal Backdoor Detection (UnivBD)

## TL;DR {#tldr}
UnivBD decides if a trained model is backdoored by computing each class's maximum margin statistic, then flagging the model when one class's margin is a statistical outlier — all without clean-vs-poison labels, trigger knowledge, or the training set. "Universal" means one test catches additive, patch, and blended triggers alike.

## Intuition {#intuition}
Line up every class and ask each the same question from the MM statistic: how much margin can one shared nudge buy you? Plot the answers. Honest classes cluster together; a backdoored class stands far to the right, an obvious outlier. UnivBD is essentially that outlier test, made rigorous with a p-value so the alarm threshold isn't a guess.

Because the test only looks at how reachable each class's margin is, it doesn't care what the trigger looks like — every trigger family produces the same tell.

## Mechanics {#mechanics}
For each candidate target class, UnivBD estimates the MM statistic by projected gradient ascent, giving one value per class [§sec_3_2]. It then fits a null model to the bulk of these values and computes an order-statistic p-value for the largest one; a small p-value flags the model and names the outlier class as the suspected target [§sec_3_2].

If a backdoor is detected and re-sourcing the model is not possible, the same logit-landscape view drives mitigation by bounding neuron activations [§sec_3_3].

## The Math {#the-math}
Let $r_{\max} = \max_t \operatorname{MM}(t)$ be the largest margin statistic and $H_0$ the fitted null CDF over the clean classes' statistics. With $K$ classes, the detection p-value is

$$ \mathrm{pv} = 1 - H_0\!\left(r_{\max}\right)^{K-1}, $$

the probability that the biggest of $K-1$ null draws would reach $r_{\max}$. A small $\mathrm{pv}$ rejects "clean model" and flags the argmax class as the target [eq_3] [§sec_3_2].

## Go Deeper {#go-deeper}
- Order-Statistic p-value explains the $(K-1)$ exponent and why the maximum is used.
- Null Distribution of Margins is the robust reference $H_0$.
- Detection Performance benchmarks UnivBD against NC, ABS, and other detectors [§sec_4_1_2].

# Maximum Margin (MM) Statistic
## TL;DR {#tldr}
The Maximum Margin (MM) statistic is the core detection signal behind MM-BD, a method for spotting whether a trained classifier has been backdoored — and it works after training is finished, without needing access to any poisoned or backdoor-triggered samples, and regardless of what kind of backdoor pattern (BP) was used.

## Intuition {#intuition}
The idea builds on the broader post-training detection scenario, where a defender only has the final trained model and a batch of clean data, and must decide if an attacker secretly inserted a backdoor. Within the detection procedure this statistic feeds into, the insight is that a backdoor leaves a distinctive fingerprint on the shape of the classifier's decision landscape: for the class the attacker targeted, it becomes unusually easy to push almost any input toward being classified as that class by a wide margin, while no such easy shortcut exists for the other, legitimately-learned classes.

## Mechanics {#mechanics}
The detector looks at the influence of a backdoor attack (BA) on the landscape of the classifier's logit functions, and does so in a way that is independent of the specific backdoor pattern type used by the attacker [§sec_3_1]. For a BA with a given target class, the method computes, for each class, the maximum margin between that class's logit and the second-largest logit across the input space; the claim is that this margin will be far larger for the true target class than for any other class [§sec_3_1]. This happens because the backdoor pattern is a single, common trigger the attacker stamps onto poisoned training samples (and later onto test samples), whereas the features that genuinely discriminate a class exhibit high natural variability, so the network must overfit to the common trigger for it to reliably override that variability at a low poisoning rate, which abnormally boosts the target class's logit and depresses the others [§sec_3_1]. A toy experiment with two-dimensional inputs, three Gaussian-mixture classes, and two backdoor attacks (differing only in poisoning rate, both targeting class 3) confirms this: plotting the margin between each class's logit and the largest of the remaining logits shows the target class's margin is abnormally large for both attacks, and the effect is even more pronounced at the higher poisoning rate, since attackers prefer higher poisoning rates to guarantee the backdoor succeeds [§sec_3_1].

## The Math {#the-math}
The key-idea inequality formalizes the asymmetry described above, contrasting the maximum margin achievable for the true backdoor target class $t$ against that of any other candidate class $c$ [eq_1]:

$$
\max_{{\bf x}\in{\mathcal X}} \big[ g_t({\bf x}) - \max_{k\in{\mathcal Y}\setminus t} g_{k}({\bf x})\big] \gg \max_{{\bf x}\in{\mathcal X}} \big[ g_c({\bf x}) - \max_{k'\in{\mathcal Y}\setminus c} g_{k'}({\bf x})\big]
$$ [eq_1]

Here $g_k(\cdot)$ denotes the logit function for class $k$, and for each class the inner term maximizes, over the whole input space $\mathcal{X}$, the gap between that class's logit and the best-competing logit among all other classes — i.e., exactly the maximum margin (MM) statistic computed per class in the mechanics above [§sec_3_1].

## Go Deeper {#go-deeper}
No research note is attached to this concept in the local context, so no further readings can be listed here.

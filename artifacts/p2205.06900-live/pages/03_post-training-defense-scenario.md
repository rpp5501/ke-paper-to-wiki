# Post-Training Detection Scenario
## TL;DR {#tldr}
The post-training detection scenario is the defense setting MM-BD is built for: a defender who only has a trained classifier in hand, with no access to the original training data and no clean reference model to compare against. Detection must work regardless of what the backdoor pattern looks like or how many classes the attacker used as sources, which is what motivates the Maximum Margin (MM) statistic as a general-purpose detector.

## Intuition {#intuition}
Most backdoor defenses assume some help — a held-out clean dataset, a known trigger shape, or a reference model trained without the attack. The post-training scenario strips all of that away: the defender receives a classifier after the fact and must decide, from the model's behavior alone, whether it has been poisoned. This is the harder, more realistic setting, since in practice a defender rarely knows in advance what kind of trigger an attacker used or how many classes were targeted. It sets up the need for a detection statistic that makes no assumptions about backdoor pattern (BP) type or source-class count — the role filled by the Maximum Margin (MM) statistic.

## Mechanics {#mechanics}
The defender operates strictly after training has finished, with no access to the classifier's training set and no clean classifiers available for reference, and the method targets the image domain under this constraint [§sec_3]. Crucially, the approach makes no assumptions about the backdoor pattern type or about how many source classes are involved in the attack, which distinguishes the scenario from defenses that presuppose a specific trigger form (e.g., a fixed patch) or a single-source attack [§sec_3]. Within this scenario, the method proceeds in two conceptual stages: first an estimation step that produces a novel maximum margin statistic for each class, followed by an unsupervised detection inference step that uses those statistics to flag backdoors; a further mitigation step is proposed to address attacks once detected [§sec_3].

## The Math {#the-math}
The local context for this concept covers only the framing of the post-training detection scenario and does not include any equations — the estimation and inference formulas belong to the downstream MM statistic and detection procedure rather than to the scenario definition itself [§sec_3].

## Go Deeper {#go-deeper}
No research note is available for this concept, so there are no external resources to list here.

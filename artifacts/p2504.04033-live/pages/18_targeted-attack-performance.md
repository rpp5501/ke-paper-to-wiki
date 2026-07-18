# Targeted Attribute Inference Attack Performance

## TL;DR {#tldr}
This concept covers the experimental results measuring how well a Targeted Attribute Inference Attack performs once an adversary narrows its focus to a smaller, higher-vulnerability subset of records rather than attacking the full dataset indiscriminately. It sits within the paper's Experiments section and builds directly on the general Targeted Attribute Inference Attack methodology, showing empirically that shrinking the attack budget (the fraction of records targeted) consistently raises the attacker's success rate compared to the untargeted baseline.

## Intuition {#intuition}
The core idea is that not all records are equally vulnerable to attribute inference — some subgroups of the population leak more information than others. Instead of running an inference attack uniformly across everyone, an adversary can first identify the most vulnerable subgroup and concentrate its effort there, achieving a much higher success rate for the same or less effort. Performance here is a way of quantifying that advantage: as the adversary is allowed to target smaller and smaller slices of the vulnerable population, its accuracy climbs, revealing how uneven privacy risk is distributed across a dataset rather than assuming risk is uniform.

## Mechanics {#mechanics}
Performance is measured as attack success rate (accuracy) for two underlying inference algorithms, CSMIA and LOMIA, run in both a single attribute-based and a nested (multi-attribute) targeted configuration, and benchmarked against two imputation-attack baselines, ImpI (auxiliary data matching the original distribution) and ImpP (auxiliary data with a different distribution) [§sec_6_4].

For the single attribute-based attack, the adversary sweeps the attack budget from 1 (the untargeted case) down to as low as 0.05, using the grouping attribute with the largest range in angular difference for each dataset (chosen per-dataset for Census19, Texas-100X, and Adult), and accuracy rises steadily as the budget shrinks: CSMIA gains 17.12 points on Census19, 5.65 on Texas-100X, and 16.66 on Adult over the untargeted case, while LOMIA gains 20.48, 13.31, and 15.68 points respectively [§sec_6_4].

The nested attribute-based attack extends this by conditioning on an ordered set of top-d attributes, with performance measured at increasing "depth" (number of nested attributes); performance again improves as depth increases, reaching very high success rates on Texas-100X and Adult at a depth of 5 for both CSMIA and LOMIA variants [§sec_6_4].

The imputation baselines behave differently under the same sweep: ImpP shows no consistent improvement as the budget shrinks, indicating that a targeted imputation attack fails to beat an untargeted one when the adversary's auxiliary data has a different distribution from the private training data, whereas ImpI does improve with a smaller budget but at a slower rate than the proposed attack, suggesting its gains depend on how well group-level success rates on the auxiliary set correlate with the original data [§sec_6_4].

A separate ablation varies the number of MLP hidden layers (2 to 4) for target models trained on Census19 and reruns both the single and nested targeted attacks at full and reduced budgets; results are similar across all three architectures, indicating that model depth/complexity does not meaningfully affect vulnerability to these targeted inference attacks [§sec_6_4].

## The Math {#the-math}
The local context reports empirical attack-success-rate tables and their discussion but does not provide any labeled equations ([eq_N] entries) defining how these attacks or their metrics are formalized, so no equation block can be reproduced here [§sec_6_4].

## Go Deeper {#go-deeper}
No research note is associated with this concept, so there are no external resources to list here.

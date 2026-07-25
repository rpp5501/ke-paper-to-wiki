# The imputation attack that supposedly beats model inversion

## TL;DR {#tldr}

Prior work said attribute inference attacks are weak because a simpler trick — guessing from similar people — usually beats them; this paper questions how fair that comparison is.

The imputation attack sidesteps the target model entirely. Instead of querying the model at all, the adversary collects a small auxiliary dataset (roughly 10% the size of the target data), trains an ordinary imputation model on it, and uses that to guess the missing sensitive attribute for target records. Prior work found this outperforms genuine model-inversion attacks like CSMIA and LOMIA on average, which was read as evidence that attribute inference attacks are not a serious threat. This page is about what the imputation attack actually assumes to win that comparison, and why the paper thinks the comparison was measuring the wrong thing.

## Intuition {#intuition}

Suppose you want to guess someone's marital status from their income and job title. One way is to query a model that was trained on people like them and see what it predicts. A completely different way is to just go find a bunch of other people with similar incomes and job titles, look up their marital status directly, and guess by analogy. The second approach doesn't touch the target model at all — it works even if you can't query it, so long as you have a reference group that looks like the people you're trying to unmask.

That second approach is the imputation attack. It needs one thing the model-based attacks don't: an auxiliary dataset that resembles the target population. Earlier work handed the imputation attacker that auxiliary dataset and found it won, badly, against CSMIA and LOMIA — around 62–71% accuracy against numbers not much better than guessing. That result got read as a verdict on the whole category of attribute inference attacks: unimpressive, so not very dangerous.

This paper's objection is not that the imputation attack cheated exactly, but that the win was fragile in a specific and revealing way. It only holds when the auxiliary dataset matches the target data closely — same overall rate of the sensitive attribute, and, more subtly, the same relationship between the sensitive attribute and the output *within every group*, not just on average. Real adversaries essentially never have that. And once the correlation between the sensitive attribute and the output gets high — which the paper shows is exactly the condition under which model-based attacks get dangerous — the imputation attack's advantage evaporates, because its auxiliary data was never built to reflect that high correlation in the first place.

So the imputation attack functions in this paper less as a competitor to be beaten outright, and more as a control: a baseline that reveals, by where it fails, what conditions actually drive privacy leakage.

## Mechanics {#mechanics}

**How the attack works.** The adversary builds an attack dataset the same way LOMIA does — but instead of querying the target model to construct it, uses an auxiliary dataset. An imputation model is trained on this auxiliary data and then used to infer the sensitive attribute value on the target records — no queries to the target model are needed at all [§sec_2].

**The ideal-vs-practical distinction.** An *ideal* imputation attack assumes the auxiliary dataset matches the target data's distribution precisely — same correlation structure, same marginal priors, down to the level of individual groups. A *practical* imputation attack uses whatever auxiliary data a realistic outside adversary could actually obtain, which will generally drift from the target distribution at either the whole-dataset level or the group level. The paper argues only the practical version is a fair stand-in for a real adversary, since an external attacker with no relationship to the data owner has no way to guarantee a distribution match [§sec_6_2].

**Where the win collapses — dataset-level drift.** Varying the auxiliary dataset's marginal prior from 0.5 down to 0.1 (versus the training data's actual 0.52) across auxiliary sizes from 100 to 5,000 records, the imputation attack's accuracy falls below CSMIA (69.97%) and LOMIA (70.61%) once the marginal prior drifts to 0.1 or 0.2, regardless of how much auxiliary data is used. The imputation attack only wins when its marginal prior is close to the real one [§sec_6_2].

**Where the win collapses — group-level drift.** Even with an auxiliary dataset whose dataset-wide correlation matches the training data almost exactly (-0.44 vs. -0.4412), individual occupation groups in the real data range from -0.17 to -0.55 correlation — a spread the auxiliary data, built to be uniform, cannot reproduce. Under this group-level drift, CSMIA and LOMIA beat the practical imputation attack in three of the five most vulnerable groups, while the *ideal* imputation attack (which does get to see the true group-level distribution) stays close to CSMIA and LOMIA in two of those three groups [§sec_6_2].

**The conclusion the paper draws.** Practical imputation attacks — the only version a real adversary can run — are likely to underperform model-based attacks precisely in the high-correlation, high-vulnerability regime that matters most. The paper's stance is not that imputation attacks are useless as a baseline, but that they should be read as a *floor*: the ideal imputation attack is a useful benchmark for how much leakage exists, while the practical imputation attack is the fairer comparison for evaluating a genuine adversary, and it is the one CSMIA/LOMIA actually clear [§sec_6_2].

## The Math {#the-math}

This page's material is empirical rather than formal — there is no dedicated equation for the imputation attack itself in the pack. The one relevant piece of formalism is the general attack-success-rate notation used to compare it against CSMIA and LOMIA:

$$
ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}), \mathcal{A})
$$

where \(\mathcal{A}\) is instantiated as the imputation attack (ideal or practical), \(\mathcal{M}\) is the target model, and \(\mathcal{N}(\mathbb{D})\) is the non-sensitive portion of the data. The comparisons throughout are numeric accuracy tables rather than derived formulas [§sec_2].

## Go Deeper {#go-deeper}

- **[§sec_6_2] Ideal vs. Practical Imputation Attacks** — the full dataset-level and group-level drift experiments; the core evidence for why the imputation-attack comparison was misleading.
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — shows CSMIA/LOMIA tracking correlation while Imputation and NeuronImportance do not, which is the mechanism behind the imputation attack's collapse at high correlation.
- **[§sec_6_4] Targeted Attribute Inference Attack** — where ImpI and ImpP (ideal and practical imputation) reappear as baselines against the paper's targeted attacks, with ImpP failing to improve as the attack budget shrinks.
- Related concepts: `attribute-inference-attack` for the family of attacks the imputation baseline is contrasted against, `ideal-vs-practical-imputation-gap` for the concept this page's central finding feeds into.

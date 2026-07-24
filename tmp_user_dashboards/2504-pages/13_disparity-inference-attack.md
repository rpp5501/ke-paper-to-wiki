# Disparity inference attack: ranking groups by privacy risk

## TL;DR {#tldr}

An attacker who can't tell whose data is vulnerable can still rank groups by risk using only what the model reveals through ordinary queries.

The disparity inference attack does not try to guess anyone's sensitive attribute. Its goal is narrower and, in a sense, prior: figure out *which groups* in the dataset are the vulnerable ones, without ever having access to the true sensitive values needed to check the answer directly. It does this by computing the angular difference for each group — a black-box proxy for how strongly the sensitive attribute and the output are correlated in that group — and sorting groups by that number. On Census19 this ranking correlates with the true vulnerability ordering at Kendall's Tau 0.6914 (CSMIA) and 0.7579 (LOMIA), while a baseline attacker with a full-size auxiliary dataset scores near zero.

## Intuition {#intuition}

Picture a burglar casing a neighborhood who can't check which houses have valuables inside, but can watch how nervously each house's motion-sensor light behaves. A house where the light flickers wildly at the slightest movement is telling the burglar something, even though the burglar never sees inside. The disparity inference attack works on the same principle: it can't observe which groups actually leak (that would require the very sensitive data it's trying to steal), so it watches a proxy signal instead — one visible from outside, and it turns out to be a reliable stand-in for the thing it can't see directly.

The proxy is the angular difference, developed on the `confidence-score-distribution-histograms` page: when you re-query the model with the same record but different assumed values of the sensitive attribute, the model's confidence scores tilt in a way that reflects how imbalanced the sensitive attribute's values are within that group's output classes. A group where the model is very sure of its answer under one sensitive value and much less sure under the other is a group where the correlation is strong — and correlation is exactly what earlier experiments show drives attack success.

So the disparity inference attack's move is: compute this tilt for every group, and use it purely as a sorting key. It never needs to know whether the ranking is correct in an absolute sense — it only needs the *order* to be right, because the payoff (a subsequent targeted attack) only cares about which groups are worth attacking, not by how much.

There is a structural reason this problem is hard rather than trivial. An adversary who actually knew each group's true attack success rate would already have solved the underlying attack — there would be nothing left to infer. The disparity inference attack has to work with a strictly weaker signal (queries and confidence scores only) and still produce a ranking good enough to be useful.

## Mechanics {#mechanics}

**Setup.** The target dataset \(\mathbb{D}\) is partitioned into \(k\) non-overlapping groups \(\mathbb{D}_1, \ldots, \mathbb{D}_k\) by some non-sensitive attribute the adversary can observe — State, for instance. The adversary's goal is the true vulnerability ranking of these groups — but computing that ranking directly is impossible without the sensitive values the attack is trying to recover in the first place [§sec_5_2].

**Attack steps.** The adversary queries the target model using the confidence-matrix procedure (Algorithm 1 in the paper) to build a confidence matrix over \(\mathbb{D}\). Then, for each group \(\mathbb{D}_i\), the angular difference \(\Delta_i\) is computed from that group's confidence matrix (Algorithm 2). Finally, the groups are ranked by decreasing \(\Delta_i\), and that ranking is output as the attack's answer [§sec_5_2].

**Why this is a legitimate substitute.** The link between angular difference and true attack success rate isn't assumed — it's demonstrated. Plotting angular difference against actual attack accuracy for the 51 states of Census19 shows a strong, visibly monotonic relationship for both CSMIA and LOMIA: high angular difference groups have high attack accuracy, low angular difference groups have low attack accuracy [§sec_6_3].

**Evaluation methodology.** Ranking quality is measured with Kendall's Tau and Spearman's R against the true (experimenter-known, adversary-unknown) vulnerability ranking, since the datasets were constructed with each group's correlation set explicitly (Census19: 51 states with correlation \(-0.01 \times i\) for state index \(i\); Texas-100X: 10 PAT_STATUS groups with correlation from 0 to 0.45 in steps of 0.05). Values close to 0 mean the ranking carries no information; values far from 0 in either direction mean it does, since a perfectly reversed ranking is still fully informative [§sec_6_3].

**Results against a real baseline.** A baseline attacker is given an auxiliary dataset the same size as the training set (but with a different distribution) and ranks groups by CSMIA accuracy measured on that auxiliary data. On Census19 the disparity inference attack reaches Kendall's Tau 0.6914 (CSMIA) and 0.7579 (LOMIA) with p-values around \(10^{-12}\)–\(10^{-15}\); the baseline scores -0.0759 and -0.0931, with p-values around 0.34–0.44 — statistically indistinguishable from chance. On Texas-100X the disparity inference attack's coefficients are strongly negative (Kendall's Tau -0.7778 for CSMIA), which the paper still counts as strong ranking quality, since a consistently reversed order is as informative as a matching one — what matters is distance from zero [§sec_6_3].

**Downstream role.** The ranking this attack produces is not an end in itself. It is the input the targeted attribute inference attacks (single-attribute and nested) consume to decide which subset of the data to spend a limited query budget attacking [§sec_5_2].

## The Math {#the-math}

Let \(\mathcal{M}\) be the target model trained on \(\mathcal{N}(\mathbb{D})\), the non-sensitive portion of dataset \(\mathbb{D}\), divided into \(k\) non-overlapping subsets \(\mathbb{D}_1, \ldots, \mathbb{D}_k\). The attack success rate of algorithm \(\mathcal{A}\) on a subset is written \(ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}_i), \mathcal{A})\).

The **attack vulnerability ranking** \(R = (r_1, r_2, \ldots, r_k)\) is a permutation of the group indices sorted so that every earlier group has attack success rate at least as high as every later group [eq_1]:

```annotated-eq
latex: 'ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}_{r_i}), \mathcal{A}) \geq ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}_{r_j}), \mathcal{A}) \quad \forall\; 1 \leq i < j \leq k'
terms:
  - tex: 'r_i, r_j'
    role: 1
    words: "positions in the ranking — group r_1 is the most vulnerable, r_k the least"
  - tex: '\mathcal{N}(\mathbb{D}_{r_i})'
    role: 4
    words: "the non-sensitive columns of that group's records — all the adversary gets to see"
  - tex: 'ASR'
    role: 2
    words: "attack success rate — unobservable to the adversary, which is the whole problem"
```

The attacker's goal is to find \(R\), or a ranking close to it. The definition itself is what makes the problem non-trivial: the attacker does not know the true sensitive attribute values, and therefore cannot evaluate \(ASR\) for any group directly. If they could, ranking would be trivial — and so would the underlying inference attack [eq_1].

Because \(ASR\) is unobservable, the attack substitutes the angular difference \(\Delta_i\) — computed purely from confidence scores obtained by querying the model — as the sort key. The full procedure:

```algorithm
title: "Disparity inference attack — rank groups by privacy risk with black-box queries only"
lines:
  - code: "for each group D_i defined by a non-sensitive attribute value:"
    intent: "Groups are carved out by values the adversary can see (e.g. race = X, occupation = Y) — no sensitive values are needed to form them."
  - code: "    for each record x in N(D_i):"
    intent: "Take only the non-sensitive portion of each record — the adversary's actual view."
  - code: "        query M(x, s) for every candidate sensitive value s"
    intent: "Re-ask the same question under each possible secret. The model's confidence shifts because training bias tied the secret to the output."
  - code: "    build the group's confidence matrix from these scores"
    intent: "Rows are records, columns are the model's confidence under each candidate value — the raw material for the geometry that follows."
  - code: "    fit a regression line per class label; take Δ_i = mean pairwise angle"
    intent: "The comet-shaped clouds tilt by an amount that tracks the group's sensitive-output correlation; the angle between fitted lines turns that tilt into one number [§sec_5_2]."
  - code: "return groups sorted by decreasing Δ_i"
    intent: "This ordering is the estimate of the true vulnerability ranking R — Kendall's Tau of 0.69–0.76 on Census19, where an auxiliary-data baseline lands near zero [§sec_6_3]."
```

The angular difference itself, \(\Delta\), is defined as the mean pairwise angle between regression lines fitted to per-class-label confidence-score submatrices — its full derivation belongs to the `confidence-score-distribution-histograms` page, since it is where the quantity is built, not where it is used.

```figure
id: comet-plot
caption: "Planned interactive: per-class confidence clouds whose tilt (the angular difference) you can steer by adjusting a group's sensitive-output correlation."
```

## Go Deeper {#go-deeper}

- **[§sec_4_2] Comparing Correlation between Groups** — where angular difference is defined and motivated; read this first if the substitution of \(\Delta_i\) for \(ASR\) above feels unmotivated.
- **[§sec_5_1] Computing Angular Difference** — the algorithmic detail (confidence matrix construction, regression-line fitting) behind the numbers this attack ranks by.
- **[§sec_6_3] Disparity Inference Attack Performance** — the full Kendall's Tau / Spearman's R table and the 51-state / 10-group experimental setup summarized above.
- **[§sec_5_3] Targeted Attribute Inference Attack** — what the ranking produced here is used for next.
- Related concepts: `angular-difference` for the proxy metric itself, `csmia` and `lomia` for the underlying attacks whose success this ranking predicts, `targeted-attack-objective-and-budget` for the attack this one feeds.

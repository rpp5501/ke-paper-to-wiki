# Single attribute-based targeted attack: pick the widest angular-difference spread

## TL;DR {#tldr}

This attack picks one attribute to group records by, finds its most vulnerable groups using angular difference, and attacks only those, beating an untargeted attack on the same budget.

This is the simplest of the paper's two targeted attribute inference attacks. Instead of exploring every possible way of splitting the dataset into subsets — which is computationally hopeless — it restricts the search to groups defined by a single non-sensitive attribute (state, occupation, sex, whatever the dataset offers), picks whichever attribute shows the widest range of angular difference across its groups, and then aggregates that attribute's most vulnerable groups until it fills the attack budget. The result, measured on Census19, Texas-100X, and Adult, is a substantial accuracy gain over attacking the full dataset with no targeting at all.

## Intuition {#intuition}

Suppose you're allowed to attack only 10% of a large population's records, and you want to choose which 10% maximizes your success rate. Trying every possible 10% subset is obviously infeasible. A much cheaper strategy: pick one variable that plausibly correlates with vulnerability — say, occupation — split the population by it, and see which occupations look most exploitable. If occupation turns out to have almost no relationship with vulnerability, this strategy won't help, but if it does, you've found real structure to exploit for very little search cost.

The paper formalizes exactly this shortcut, using angular difference as the vulnerability proxy instead of anything requiring ground truth. For each non-sensitive attribute the dataset offers, split the data into the groups that attribute defines (Male/Female for sex, fifty-one values for state, and so on), and compute the angular difference within each resulting group. Some attributes will produce groups whose angular differences are all similar to each other — that attribute isn't where the vulnerability lives. Other attributes will produce a wide spread: some groups with high angular difference, others with low. That spread is the signal. The attribute with the widest range of angular differences is, intuitively, the one whose groups differ most in how strongly the sensitive attribute correlates with the output — which is exactly the property the paper has already tied to attack success.

Once that attribute is chosen, the rest is straightforward: rank its groups by angular difference and keep adding the most vulnerable ones to the target set until the attack budget is used up. The adversary never needs to know the true sensitive values of anyone in these groups to make this selection — angular difference is computable purely from confidence scores the model returns to ordinary queries.

## Mechanics {#mechanics}

**Step 1 — sample within budget.** The adversary draws a sample \(\mathbb{D}_q\) from the full dataset subject to a query budget \(q\), which caps how many model queries the attack is allowed to spend on this exploration phase [§sec_5_3_1].

**Step 2 — build the confidence matrix.** The confidence matrix and prediction-correctness vector are generated on \(\mathbb{D}_q\), using the same querying procedure that underlies CSMIA and the angular-difference computation more generally [§sec_5_3_1] [§sec_5_1].

**Step 3 — sweep every candidate attribute.** For each non-sensitive attribute \(a\), \(\mathbb{D}_q\) is split into the subsets that attribute's possible values define, and angular difference is computed on each subset, producing a vector of angular-difference values per attribute [§sec_5_3_1].

**Step 4 — pick the attribute with the widest spread.** The attribute whose vector of angular differences has the largest range is selected. The paper's intuition is explicit here: the attribute with the widest range in its subsets' angular differences is likely to contain the most vulnerable subsets among all single-attribute partitions [§sec_5_3_1]. This is why STATE is chosen for Census19, PAT_STATUS for Texas-100X, and Occupation for Adult — these attributes exhibited the greatest range in angular difference among the candidates [§sec_6_4].

**Step 5 — rank that attribute's groups.** The chosen attribute's groups are ordered by their angular-difference values, from most to least vulnerable [§sec_5_3_1].

**Step 6 — aggregate until the budget is met.** Groups are added to the target set in decreasing order of angular difference until the target set size satisfies the attack budget condition, and the resulting subset is output as \(\mathbb{D}_{target}\) [§sec_5_3_1].

**The measured payoff.** Evaluated with \(\kappa\) shrinking from 1 (untargeted) down to 0.05, targeted CSMIA accuracy on Census19 rises from 62.56% to 73.27%, and LOMIA from 61.24% to 73.78%, both trends holding almost monotonically as the budget shrinks [§sec_6_4]. The same pattern shows on Texas-100X and Adult, and the paper reports overall gains of 17.12 percentage points (CSMIA) and 20.48 (LOMIA) on Census19, versus 5.65/13.31 on Texas-100X and 16.66/15.68 on Adult [§sec_6_4]. Crucially, the paper's imputation baseline with mismatched auxiliary data (ImpP) does *not* show this improving trend as the budget shrinks, while the ideal-distribution imputation baseline (ImpI) improves more slowly than the paper's own attack — evidence that the targeting is working because angular difference tracks real group-level correlation, not because smaller subsets are just easier to overfit [§sec_6_4].

## The Math {#the-math}

The single attribute-based attack is a concrete, tractable instance of the general targeted attack objective. Recall that objective seeks \(\mathbb{D}_{target} \subseteq \mathbb{D}\) satisfying a size condition against the attack budget \(\kappa \in (0, 0.5]\),

$$
\left| \frac{|\mathbb{D}_{target}|}{|\mathbb{D}|} - \kappa \right| < \epsilon
$$

[eq_2], and a performance condition requiring \(\mathbb{D}_{target}\) to outperform every subset at least as large as itself,

$$
\begin{aligned}
ASR(\mathcal{M},\, \mathcal{N}(\mathbb{D}_{\text{target}}),\, \mathcal{A}) &\geq ASR(\mathcal{M},\, \mathcal{N}(\mathbb{D}'),\, \mathcal{A}) \\
\forall\, \mathbb{D}' \in \{\mathbb{D}' \subset \mathbb{D} \mid |\mathbb{D}'| &> |\mathbb{D}_{\text{target}}|\}
\end{aligned}
$$

[eq_3]. Evaluating this over every possible subset of \(\mathbb{D}\) is computationally intractable, which is exactly why the search is restricted to subsets carved out by a single non-sensitive attribute's values [§sec_5_3].

For attribute \(a\) with possible values producing groups \(G_1, \ldots, G_p\), let \(\delta_a = (\Delta_\angle(G_1), \ldots, \Delta_\angle(G_p))\) be the vector of angular differences over those groups. The selected attribute is the one whose groups spread widest:

```annotated-eq
latex: 'a^{*} = \arg\max_{a} \; \big(\max(\delta_a) - \min(\delta_a)\big)'
terms:
  - tex: 'a^{*}'
    role: 1
    words: "the grouping attribute the attacker commits to"
  - tex: '\delta_a'
    role: 4
    words: "the vector of angular differences across attribute a's groups"
  - tex: '\max(\delta_a) - \min(\delta_a)'
    role: 2
    words: "the spread — a wide spread means this attribute separates leaky groups from safe ones"
```

The full procedure, given a budget \(\kappa\):

```algorithm
title: "Single attribute-based targeted attack"
lines:
  - code: "for each non-sensitive attribute a:"
    intent: "Every attribute the adversary can see is a candidate way of slicing the dataset into groups."
  - code: "    compute angular difference Δ for each of a's groups"
    intent: "Reuse the disparity inference machinery: per-group confidence matrices, fitted regression lines, mean pairwise angle."
  - code: "select a* with the widest spread max(δ_a) − min(δ_a)"
    intent: "A wide angular-difference spread is the black-box tell that this attribute's groups differ most in real vulnerability [§sec_5_3_1]."
  - code: "sort a*'s groups by increasing Δ; take groups from the top"
    intent: "Greedy accumulation from the riskiest end — a direct proxy for the ASR-dominance condition, without ever computing true ASR [eq_3]."
  - code: "stop at the smallest t whose union meets the budget κ"
    intent: "The target set is the union of the top-t groups, sized to the fraction of the dataset the attack budget allows [eq_2]."
```

Because the groups are already sorted by angular difference, this greedy accumulation from the top is a direct proxy for satisfying the ASR-dominance condition in eq_3, without ever computing true \(ASR\) on any candidate subset. On Census19 it lifts CSMIA from 62.56% untargeted to 73.27% at \(\kappa = 0.05\), and LOMIA from 61.24% to 73.78% [§sec_6_4].

## Go Deeper {#go-deeper}

- **[§sec_5_3_1] Single Attribute-based Targeted Attack** — the six-step algorithm this page walks through in full.
- **[§sec_5_3] Targeted Attribute Inference Attack** — the general objective and intractability argument that motivates restricting the search to single-attribute partitions.
- **[§sec_6_4] Targeted Attribute Inference Attack** — the full results tables across Census19, Texas-100X, and Adult, plus the comparison against imputation baselines that shows the trend is attribute-specific rather than a generic small-subset effect.
- **[§sec_5_3_2] Nested Attribute-based Targeted Attack** — the natural extension that intersects above-average-risk segments from multiple attributes instead of relying on just one.
- Related concepts: `angular-difference` for the ranking key this attack sweeps over every attribute, `targeted-attack-objective-and-budget` for the formal objective this attack approximates, and `nested-attribute-targeted-attack` for the multi-attribute generalization built directly on top of this one.

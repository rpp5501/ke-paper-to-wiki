# Nested attribute-based targeted attack: intersecting above-average-risk segments

## TL;DR {#tldr}

Instead of picking one risky attribute to attack, this method intersects the riskiest slices of several attributes at once, shrinking the target group further and pushing accuracy even higher.

The single-attribute targeted attack picks the one non-sensitive attribute with the widest spread of risk and takes its worst groups. The nested version goes further: it selects several risky attributes, takes each one's above-average-risk segment (the vulnerable half of its groups), and intersects those segments to build a smaller, more concentrated target set. Because evaluating every possible combination of nested groups is exponentially expensive, the search is capped at a fixed depth \(d\) and built greedily, attribute by attribute.

## Intuition {#intuition}

A single risk factor rarely tells the whole story. Being in a high-risk occupation is one signal; living in a high-risk state is another. Someone who is both is plausibly at more risk than either factor alone would suggest — the same logic epidemiologists use when they note that smoking *and* a sedentary lifestyle *and* high cholesterol together identify a much smaller, much higher-risk group than any single factor screened in isolation.

The nested attack applies exactly this logic to attribute inference. Rather than committing to one grouping attribute (say, occupation) and taking its worst groups, it looks at several attributes — occupation, state, whatever else is available — finds each one's "above-average-risk" half, and intersects those halves. A record that lands in the risky half of *every* selected attribute is a much sharper bet than a record that's only risky along one dimension. The intersection is smaller than any single attribute's risky segment, but the group inside it is, on average, more exposed.

The catch is combinatorics: checking every possible combination of attributes and value-ranges to find the single best nested group would be exponentially expensive. The paper sidesteps this with a greedy shortcut — pick the attributes with the widest angular-difference spread first (reusing the same ranking the single-attribute attack computes), intersect a fixed number of them, and stop. That fixed number, the depth \(d\), is chosen by the attacker; the results tables show it growing as the attack budget shrinks — more depth buys a smaller, more concentrated, more accurate target set, at the cost of covering fewer records overall.

## Mechanics {#mechanics}

**Move 1 — reuse the single-attribute ranking machinery.** The nested attack starts by repeating the first three steps of the single-attribute attack: sample a query-budget-limited subset \(\mathbb{D}_q\), compute the confidence matrix, and for every non-sensitive attribute compute the range of angular differences across its groups [§sec_5_3_1], [§sec_5_3_2].

**Move 2 — pick the top-\(d\) attributes.** Rather than choosing one attribute, the adversary selects the \(d\) attributes with the widest angular-difference ranges. Depth \(d\) is a parameter the attacker sets; the results tables show depth increasing as the attack budget shrinks — Census19 goes from no nesting at \(\kappa=1\) up to depth 4 at \(\kappa=0.1\), and Texas-100X reaches depth 5 at \(\kappa=0.01\) [§sec_6_4].

**Move 3 — take each attribute's above-average-risk segment.** For each of the \(d\) selected attributes, groups are ranked by angular difference and the most vulnerable groups are collected until they cover close to half of that attribute's total records — this is the "above-average-risk segment" for that attribute [§sec_5_3_2].

**Move 4 — intersect.** The nested groups are formed by intersecting the above-average-risk segments across the selected attributes. Because the attack budget may not permit taking the full above-average-risk segment from the last-chosen attribute, the adversary greedily includes as many of its groups as the budget allows [§sec_5_3_2].

**Move 5 — the payoff, with a caveat.** On Census19, nested CSMIA reaches 69.36% and LOMIA reaches 70.26% at depth 4 (\(\kappa=0.1\)), both above the untargeted 62.56%/61.24% baseline. On Adult, nested CSMIA and LOMIA reach 86.74%/86.77% at depth 4. On Texas-100X, both reach 100.00% at depth 5 (\(\kappa=0.01\)) [§sec_6_4] — a striking number, but one earned by narrowing the target set to a very small budget, not by a general improvement in attack strength.

**Move 6 — why greedy, not exhaustive.** The search is deliberately capped at depth \(d\) and built attribute-by-attribute because evaluating every possible combination of intersecting groups is exponentially costly; the greedy approach trades optimality for tractability [§sec_5_3_2].

## The Math {#the-math}

The nested attack still targets the same objective as every targeted attack in this paper: find \(\mathbb{D}_{target} \subseteq \mathbb{D}\) meeting a size condition on the attack budget \(\kappa\),

$$
\left| \frac{|\mathbb{D}_{target}|}{|\mathbb{D}|} - \kappa \right| < \epsilon
$$

and outperforming every subset at least as large as itself [eq_2], [eq_3]:

$$
ASR\big(\mathcal{M}, \mathcal{N}(\mathbb{D}_{target}), \mathcal{A}\big) \;\geq\; ASR\big(\mathcal{M}, \mathcal{N}(\mathbb{D}'), \mathcal{A}\big) \qquad \forall\, \mathbb{D}' \subset \mathbb{D},\ |\mathbb{D}'| > |\mathbb{D}_{target}|
$$

What the nested attack changes is how \(\mathbb{D}_{target}\) is constructed. For a selected attribute \(a\) with groups \(\mathbb{D}_{a,1}, \dots, \mathbb{D}_{a,k}\) and angular differences \(\delta_{a,1}, \dots, \delta_{a,k}\), order the groups by decreasing angular difference and define the above-average-risk segment \(R_a\) as the shortest prefix of that ordering whose combined records cover roughly half of attribute \(a\)'s total:

$$
R_a \;=\; \{\, i_1, \dots, i_j \,\} \quad \text{such that} \quad \sum_{k=1}^{j} \big|\mathbb{D}_{a,i_k}\big| \;\approx\; \tfrac{1}{2} \sum_{i} \big|\mathbb{D}_{a,i}\big|
$$

Given the top-\(d\) attributes chosen for their angular-difference range, the nested target set is the union over intersections of these segments:

```annotated-eq
latex: '\mathbb{D}_{target} = \bigcup \Big(\, \bigcap_{a \,\in\, \text{top-}d} \mathbb{D}_{a, R_a} \,\Big)'
terms:
  - tex: '\mathbb{D}_{a, R_a}'
    role: 1
    words: "attribute a's above-average-risk records — its riskiest groups, covering about half of a's records"
  - tex: '\bigcap_{a \in \text{top-}d}'
    role: 2
    words: "intersect across the d best attributes: keep records risky under every one of them"
  - tex: '\text{top-}d'
    role: 3
    words: "the d attributes with the widest angular-difference spread"
```

```algorithm
title: "Nested attribute-based targeted attack"
lines:
  - code: "rank attributes by angular-difference spread; keep the top d"
    intent: "Same attribute-quality signal as the single-attribute attack, but several attributes get to vote."
  - code: "for each kept attribute a: R_a = riskiest prefix covering ~half of a's records"
    intent: "Per attribute, keep only the above-average-risk half — the segment where that attribute says the leak is."
  - code: "intersect the segments; the survivors are the target set"
    intent: "A record that is above-average-risk under every top attribute is risky with much higher confidence than under any single slice [§sec_5_3_2]."
  - code: "trim on the last-included attribute until the budget κ is met"
    intent: "Intersections shrink fast; trimming the final attribute's contribution tunes the set to the exact budget [eq_2]."
```

The nesting is why this variant reaches deeper into small budgets than the single-attribute attack: each additional attribute multiplies selectivity without needing any new kind of signal [§sec_5_3_2].

## Go Deeper {#go-deeper}

- **[§sec_5_3_2] Nested Attribute-based Targeted Attack** — the full step-by-step construction this page is built from, including the greedy depth-\(d\) selection and above-average-risk segment definition.
- **[§sec_5_3_1] Single Attribute-based Targeted Attack** — the simpler attack whose ranking machinery (steps 1-3) the nested attack reuses directly.
- **[§sec_6_4] Targeted Attribute Inference Attack** — the results tables showing accuracy climbing with depth, including the 100% figures on Texas-100X that need the small-budget caveat.
- **[§sec_5_3] Targeted Attribute Inference Attack** — the shared formal objective (\(\kappa\), \(\epsilon\), Condition 2) that both single-attribute and nested attacks are built to satisfy.
- Related concepts: `single-attribute-targeted-attack` for the one-attribute precursor, `targeted-attack-objective-and-budget` for the formal condition being solved, and `targeted-attack-performance-gains` for the full results context, including caution about relative-vs-absolute accuracy figures.

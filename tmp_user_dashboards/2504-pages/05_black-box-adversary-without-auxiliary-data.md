# The adversary: black-box queries, no auxiliary data, no marginal priors

## TL;DR {#tldr}

The attacker in this paper only gets to ask the model questions and read its answers — no stolen slice of the training data, and no knowledge of how common the secret actually is.

That restraint is the point. Prior attribute inference attacks lean on an auxiliary dataset matching the target's distribution, or on knowing the marginal priors of the sensitive attribute. Both are assumptions a real outsider cannot satisfy, and the paper shows that when they fail, the attacks depending on them collapse. By assuming strictly less, this adversary is one that could actually exist — which is what makes the results a threat rather than a thought experiment. The paper also deliberately reverses the asymmetry when evaluating its defense, granting the adversary *more* power there.

## Intuition {#intuition}

Threat models are where privacy papers quietly decide their own conclusions. Grant the attacker enough, and any system looks broken; grant them little enough, and everything looks safe. So the interesting question about any attack is rarely "did it work" but "what did it need in order to work, and could anyone actually have that?"

The assumption doing the most damage in this literature is the auxiliary dataset: a collection of records drawn from the same distribution as the private training data, with the sensitive values filled in. Say that out loud and the problem is obvious. If you already have a pile of records that look just like the training data, complete with the secrets, then you already know how the secrets relate to everything else. The model has become an accessory to a conclusion you could reach without it. Worse, the assumption is self-undermining: an attacker with that data is an attacker who barely needed to attack.

This paper's adversary gives that up. They can query the model and see the label and confidence scores. They know the public attributes. They know what values the sensitive attribute *can* take — which is nearly free, since a queryable model usually advertises its input options. And that is the whole list. Crucially, they do not know the marginal priors — the relative frequencies of the sensitive values — which prior attacks needed. So they cannot fall back on "most people are married, guess married." They have to get the information out of the model, or not at all.

This is what makes angular difference interesting rather than merely clever. It isn't just another metric; it is a way of computing something about the training data's structure that seems to require the training data, using only the shape of the model's responses. The confidence scores from querying a record under each candidate secret carry a trace of what the model learned, and aggregating that trace over a group reveals the group's correlation level well enough to rank groups against each other.

There is a nice piece of intellectual honesty in how the paper handles its own defense. When attacking, it assumes a weak adversary — that's the conservative choice, since a weak attacker succeeding is stronger evidence than a strong one succeeding. When evaluating the defense, it flips and assumes a *stronger* adversary, because a defense that only stops weak attackers has not been tested. Each direction assumes the case least favorable to the paper's own claim.

## Mechanics {#mechanics}

**What the adversary has.** Three capabilities, stated as a list: access to the black-box target model, meaning they can query it with \(x\) and receive the output label \(y\) plus the corresponding confidence scores; full knowledge of the non-sensitive attributes; and knowledge of every possible value of the sensitive attribute and of any non-sensitive attributes they treat as group attributes [§sec_3].

**Why that is not a weak assumption in context.** These capabilities are standard for model inversion — most current attacks in this family assume at least this much. The paper is precise about the gradations: Yeom et al., Fredrikson et al., and CSMIA need full non-sensitive attribute knowledge for the specific target record \(x\), whereas LOMIA needs complete non-sensitive attribute information for the entire target dataset [§sec_3]. Knowing all possible non-sensitive attribute values is realistic because publicly queryable ML models typically reveal the permitted values of query attributes — and that knowledge is exactly what lets the attacker enumerate the groups the targeted attacks then search over [§sec_3].

**What the adversary gives up.** Two things, both of which prior work assumed. The adversary does not need to know the marginal priors — the relative frequencies of the sensitive attribute values — to conduct the attack. And the adversary can attack without an auxiliary dataset at all, unlike most existing attribute inference attacks, which require auxiliary data matching the target distribution; CSMIA and LOMIA are the exceptions that also avoid it [§sec_3].

**Why dropping auxiliary data is the load-bearing choice.** It is impractical to assume an adversary external to the organization owning the private data could acquire an auxiliary dataset mirroring its distribution at a granular level; any realistically obtained dataset will differ either at the macro level, computed across the whole dataset, or at the micro level, computed for specific subsets [§sec_6_2]. The paper measures what that drift costs. Perturbing the auxiliary marginal prior \(\eta\) away from Adult's training value of 0.52, the imputation attack at \(\eta = 0.1\) and \(\eta = 0.2\) drops below both CSMIA (69.97%) and LOMIA (70.61%) regardless of auxiliary dataset size across the range 100 to 5000 records [§sec_6_2]. The paper's verdict is that practical imputation attacks — the only kind a realistic adversary can run — are likely to underperform attribute inference attacks *despite* having access to auxiliary data the attribute inference attacks never assume [§sec_6_2].

**What the adversary does with what they have.** Everything downstream is built from query access alone. Querying each record under every candidate sensitive value builds the confidence matrix [§sec_5_1]; the angular difference computed from it substitutes for the group correlation the adversary cannot measure [§sec_4_2]; ranking groups by it is the disparity inference attack [§sec_5_2]. Query volume is explicitly budgeted rather than assumed free: the targeted attacks first sample a subset \(\mathbb{D}_q\) sized by a query budget \(q\), and compute angular differences on that sample instead of the full dataset [§sec_5_3_1]. The paper notes the targeted attacks reach higher accuracy than untargeted ones while requiring far fewer queries to the target model [§sec_1].

**The asymmetry for the defense.** When performing attacks the paper assumes an adversary with fewer capabilities, to investigate privacy leakage under practical constraints; when evaluating the defense it assumes an adversary with greater capabilities, to rigorously test the defense's strength [§sec_3]. The defender's own threat model is correspondingly generous: the defender has the full dataset and the trained model, operates as a single entity with complete control over data and training, and is aware of which groups are vulnerable — which is practical, since a defender can simulate attacks and compute per-group correlations directly [§sec_7_2]. The defender can do the thing the attacker cannot; that gap is the entire reason angular difference had to be invented.

## The Math {#the-math}

The threat model is stated in prose as a list of capabilities, not as equations — there is no formalism to reproduce here [§sec_3]. What can be made precise is the *interface* those capabilities define, since it determines everything the adversary can compute.

The adversary's access to \(\mathcal{M}\) is the map

$$
x \;\longmapsto\; \big(\, y,\; \Pr(\mathcal{M}(x)) \,\big)
$$

taking a fully specified record to a predicted label and a confidence score. They hold \(n(x)\), the non-sensitive attribute vector, and \(\mathcal{S}\), the set of possible sensitive values — but not \(s(x)\), and not the marginal distribution over \(\mathcal{S}\) [§sec_3].

From this interface alone, the only object the adversary can construct is the set of hypothetical completions of a record, \(T(x)\), obtained by varying the sensitive attribute value, and the confidence scores those completions return. Collected over the dataset this is the **confidence matrix** [§sec_5_1]:

```annotated-eq
latex: '\mathcal{C} = \big[\, \mathbf{c}(x) \,\big]_{x \in \mathbb{D}}, \qquad \mathbf{c}(x) = \Big( \Pr(\mathcal{M}(x^{\prime})) \Big)_{x^{\prime} \in T(x)} \in \mathbb{R}^{|\mathcal{S}|}'
terms:
  - tex: '\mathcal{C}'
    role: 1
    words: "the confidence matrix — one row per record, one column per candidate secret"
  - tex: 'T(x)'
    role: 4
    words: "the record's hypothetical completions, one per possible sensitive value"
  - tex: '\Pr(\mathcal{M}(x^{\prime}))'
    role: 2
    words: "the model's confidence when asked about each completion — the only signal the black box leaks"
  - tex: '|\mathcal{S}|'
    role: 3
    words: "number of candidate secrets — and the per-record query cost"
```

Reading off the dimensions gives the query cost: \(|T(x)| = |\mathcal{S}|\) queries per record, so \(|\mathcal{S}| \cdot |\mathbb{D}|\) to fill the matrix — which is why the targeted attacks sample a subset \(\mathbb{D}_q\) with \(|\mathbb{D}_q| \leq q\) under a query budget \(q\) rather than querying everything [§sec_5_3_1].

Alongside \(\mathcal{C}\), the confidence matrix generation algorithm returns a **prediction correctness vector** \(t\), a boolean per record recording whether all predictions returned for that record were correct. Angular difference is computed only from records where predictions are correct for any sensitive attribute value, on the hypothesis that for these records the differences in confidence scores across sensitive values are highly indicative of the correlation level [§sec_5_1]. This filter is where the threat model's limits become a design constraint: the adversary cannot check their inferences against ground truth, so \(t\) — computable from the known label \(y\) alone — is the only quality signal available.

Everything the paper's adversary ever computes is a function of \(\mathcal{C}\) and \(t\). No term for \(\mathbb{D}_{aux}\) appears anywhere in the attack pipeline, and no prior over \(\mathcal{S}\) does either — which is the threat model's claim, discharged.

## Go Deeper {#go-deeper}

- **[§sec_3] Attack Threat Model** — the primary source, and short. Read it directly for the exact capability list and the comparison against Yeom et al., Fredrikson et al., CSMIA, and LOMIA.
- **[§sec_6_2] Ideal vs. Practical Imputation Attacks** — the empirical justification for dropping the auxiliary-data assumption. This is the section that turns a modeling preference into a measured result.
- **[§sec_5_1] Computing Angular Difference** — the confidence matrix and prediction correctness vector, i.e. everything this adversary can actually build from query access.
- **[§sec_5_3_1] Single Attribute-based Targeted Attack** — where the query budget \(q\) appears and constrains the attack, showing queries are treated as a real cost.
- **[§sec_7_2] Balanced Correlation Defense (BCorr)** — the defender's threat model, useful read against this one: the defender has exactly what the attacker lacks.
- Related concepts: `attribute-inference-attack` for the prerequisite setup, `imputation-attack-baseline` for the assumption being rejected, `confidence-score-gap` for what this adversary can see, and `confidence-matrix` for the one object they can build.

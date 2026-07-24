# Attribute inference attack: recovering a sensitive value from a model's outputs

## TL;DR {#tldr}

An attribute inference attack guesses a person's private information by feeding the public facts about them into a trained model and watching how it responds.

The attack targets people whose records were in the training data. The adversary knows everything non-sensitive about a record and wants the one thing that is missing — marital status, sex, a diagnosis. Because a model has to learn the associations in its training set to predict well, those associations can be run in reverse. This page covers the setup, the two concrete algorithms the paper builds on (CSMIA and LOMIA), and the reason the field has been underrating this attack class: it was benchmarked against an imputation baseline that assumes the attacker already has data they could never realistically get.

## Intuition {#intuition}

A model trained to predict income has to learn what income correlates with. If married people in the training data earned more, the model absorbed that. Now flip the setup around. Suppose I know your age, your occupation, your state, your education — all the boring public stuff — and I know the model says you are high income. What I do not know is whether you are married.

So I ask the model twice. Once claiming you are married, once claiming you are single. Everything else stays fixed. If the model only outputs "high income" when I claim you are married, then whatever the model learned about the world, it thinks married is the version of you that fits. That is a guess about your marital status, extracted from a system that was never meant to answer that question.

Two things make this specific and worth naming. First, the target is a member of the training data, so the model's beliefs about them aren't just general statistics — they were partly *shaped* by that person's record. Second, this is a different creature from the model inversion attacks people usually picture. Those reconstruct a representative image of a class — a blurry face for a face-recognition class. Attribute inference works on tabular data and goes after a specific cell in a specific row. Tabular data is the most common kind of structured data there is, and it is the least studied for this kind of leakage.

There is an obvious objection, and it is the one the field ran with for years. If you want to know whether someone is married, why bother with the model? Just collect a similar dataset, train a classifier to predict marital status from the public attributes, and apply it. That is an *imputation attack*, and prior evaluation found it beat attribute inference — which made attribute inference look like a solved non-problem.

The paper's answer is that this comparison is rigged in the baseline's favor. The imputation attacker is assumed to hold auxiliary data matching the target's distribution. If your auxiliary data really matched at that level of detail, you would already have the answers. A realistic attacker's data drifts — different base rates, different group-level structure — and the paper shows that when it does, the imputation attack falls apart while the model-querying attacks do not. So the baseline that "beat" attribute inference is one no real adversary can run.

## Mechanics {#mechanics}

**The setup.** Let \(n(x)\) be the non-sensitive portion of a record \(x\) and \(\mathcal{M}\) the target model. The adversary's objective is to predict \(s(x)\), the sensitive attribute value. Some variants of the attack need extra knowledge, notably an auxiliary dataset \(\mathbb{D}_{aux}\) — and which variants need it is exactly what separates the practical attacks from the impractical ones [§sec_2].

**CSMIA (confidence score-based model inversion).** For a record \(x\) whose true class label \(y\) is known, the adversary constructs one query per candidate sensitive value: \(x_i\) with \(n(x_i) = n(x)\) and \(s(x_i) = s_i\). The model returns a prediction \(y_i\) and a confidence \(conf_i\) for each. The decision rule has three branches: if exactly one \(y_i\) matches \(y\), output that \(s_i\); if several match, output the one with the *highest* confidence; if none match, output the one with the *lowest* confidence [§sec_2]. The flip in the tie-break is the subtle part — when some candidate reproduces the true label, high confidence signals the model finds that combination natural, but when nothing reproduces the true label the adversary is reading a different signal, and the least-confident wrong answer is the most informative one.

**LOMIA (label-only model inversion).** Same queries, no confidence scores. The adversary keeps only the records where exactly one \(x_i\) produced a true prediction — the unambiguous ones — and turns them into a labeled training set with \((x, y)\) as input and \(s_i\) as output. An attack model is trained on that set and used to infer the sensitive value for all the remaining records [§sec_2]. LOMIA effectively bootstraps a supervised dataset out of the target model's own behavior, which is why it needs the non-sensitive attributes for the whole target dataset rather than for one record [§sec_3].

**The baselines it gets compared against.** The imputation attack builds an attack dataset the way LOMIA does but from \(\mathbb{D}_{aux}\), never querying the target model at all. The neuron importance attack is a white-box method that uses \(\mathbb{D}_{aux}\) to find the top 10 most correlated neurons in the MLP and thresholds their weighted activation sum [§sec_2]. Both depend on auxiliary data; neither tracks the target model's learned correlation the way CSMIA and LOMIA do [§sec_4_1].

**Why the severity was misjudged.** The paper separates *ideal* imputation, where auxiliary data matches the target distribution exactly, from *practical* imputation, where it drifts. Two experiments on Adult make the gap concrete. Varying the auxiliary marginal prior \(\eta\) away from the training data's 0.52, imputation accuracy at \(\eta = 0.1\) and \(\eta = 0.2\) drops below both CSMIA (69.97%) and LOMIA (70.61%) at every auxiliary size tested, from 100 up to 5000 records. In the second experiment the auxiliary data matches the overall correlation of \(-0.4412\) but flattens the per-group correlations, which really range from \(-0.17\) to \(-0.55\); CSMIA and LOMIA then beat practical imputation in the top 3 of 5 most vulnerable groups [§sec_6_2]. The paper's conclusion is a methodological one: practical imputation is the right baseline for judging an attack, and ideal imputation is a benchmark for how much leakage exists in principle [§sec_6_2].

## The Math {#the-math}

The objective is stated compactly. For a target record \(x\), the adversary wants:

```annotated-eq
latex: '\hat{s} = \mathcal{A}\big(\mathcal{M},\, n(x)\big) \quad \text{such that} \quad \hat{s} = s(x)'
terms:
  - tex: '\hat{s}'
    role: 1
    words: "the adversary's guess at the secret"
  - tex: 'n(x)'
    role: 4
    words: "the record's non-sensitive attributes — the public facts the adversary holds"
  - tex: 's(x)'
    role: 2
    words: "the true sensitive value — success means the guess matches it"
  - tex: '\mathcal{A}(\mathcal{M}, \cdot)'
    role: 3
    words: "an attack algorithm that may query the model but sees nothing else"
```

Success is measured as \(ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}), \mathcal{A})\), the attack success rate over the non-sensitive portion of the dataset [§sec_2]. The two concrete attacks build on the same construction:

```derivation
shape: "CSMIA in three moves: fabricate one record per possible secret, see which fabrications the model believes, decide."
steps:
  - latex: 'T(x) = \{\, x_i : n(x_i) = n(x),\; s(x_i) = s_i,\; s_i \in \mathcal{S} \,\}'
    why: "Fabricate one completion of the record per candidate secret — same public attributes, different sensitive value. |S| queries per record [§sec_2]."
  - latex: 'Y_{match} = \{\, i : y_i = y \,\}'
    why: "Collect which candidate secrets make the model reproduce the record's true label. The model 'believes' those completions."
  - latex: '\hat{s} = \begin{cases} s_i, & |Y_{match}| = 1 \\ s_{\arg\max_{i \in Y_{match}} conf_i}, & |Y_{match}| > 1 \\ s_{\arg\min_{i \in [1,k]} conf_i}, & |Y_{match}| = 0 \end{cases}'
    why: "If exactly one secret fits, take it. If several fit, take the one the model is most confident about. If none fit, take the one it is least confident about — the model's discomfort is itself a signal [§sec_2]."
```

This same query set \(T(x)\) is what the rest of the paper reuses: collecting \(\Pr(\mathcal{M}(x'))\) for every \(x' \in T(x)\), over every record, is precisely the confidence matrix from which angular difference is computed [§sec_5_1].

LOMIA discards the confidences and keeps only the unambiguous records, training an attack model \(\mathcal{A}_{\text{LOMIA}}\) on

$$
\mathbb{D}_{\text{attack}} \;=\; \big\{\, \big((n(x), y),\; s_i\big) \;:\; |Y_{\text{match}}(x)| = 1,\; i \in Y_{\text{match}}(x) \,\big\}
$$

and applying it to the records that were ambiguous [§sec_2]. The imputation attack builds the structurally identical dataset from \(\mathbb{D}_{aux}\) instead — the only difference is the source of the labels, and it is the difference that decides whether the attack measures the model or measures the world [§sec_2].

## Go Deeper {#go-deeper}

- **[§sec_2] Preliminaries** — the paper's own compact definitions of CSMIA, LOMIA, imputation, and neuron importance. Short, and worth reading verbatim; every later section assumes these four.
- **[§sec_6_2] Ideal vs. Practical Imputation Attacks** — the experiments that dismantle the "imputation beats attribute inference" conclusion. This is the section that justifies taking the attack seriously at all.
- **[§sec_3] Attack Threat Model** — spells out exactly what each attack family needs to know, including why LOMIA needs the whole dataset's non-sensitive attributes while CSMIA needs only the target record's.
- **[§sec_12_1] Datasets** — how Census19, Texas-100X, and Adult are preprocessed and which attribute is treated as sensitive in each (marital status, SEXCODE, and marital status respectively).
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — shows CSMIA and LOMIA accuracy tracking correlation while imputation and neuron importance do not, which is the empirical wedge between model-querying and data-holding attacks.
- Related concepts: `csmia` and `lomia` for the algorithms in detail, `imputation-attack-baseline` for the baseline being displaced, and `disparate-vulnerability` for why the single accuracy number reported for these attacks is misleading.

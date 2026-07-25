# CSMIA: confidence-score-based model inversion

## TL;DR {#tldr}

CSMIA guesses a hidden attribute by asking the model once per possible value and reading off which answer the model trusts most.

CSMIA (Confidence-Score-based Model Inversion Attack) is one of the two concrete attack algorithms this paper builds everything else on top of. Given a record with a known output label and an unknown sensitive value, the adversary queries the model once for every candidate sensitive value, keeping everything else about the record fixed. It then applies a three-way decision rule over the returned labels and confidence scores to pick the sensitive value that best explains what the model said. The rule looks fiddly at first, but each branch is answering a different question about what the model's behavior implies.

## Intuition {#intuition}

Suppose a model predicts income from a handful of public facts, and you want to know whether a specific person in its training data is married or single. You don't get to ask the model that directly — you can only ask it to predict income, and you control what you tell it about marital status when you ask.

So you ask twice: once telling the model the person is married, once telling it the person is single. You already know the *real* income label for this person, because that part is public. Now look at what each query returned.

If exactly one of your two queries reproduced the real income label, that's a strong hint: the model only "recognized" this person as themselves when you fed it the marital status that matches training-time associations. Go with that value.

If both queries reproduced the real label, the model can't distinguish the two versions of the record — so you fall back on confidence. Whichever version the model was *more sure* about is the one that looks more like what it learned during training, so you pick that one.

If neither query reproduced the real label, something stranger is happening: the model is simply wrong for this record no matter what you tell it about marital status. Here the paper's rule flips — it picks the *least* confident of the two wrong answers. The reasoning is that a genuinely wrong, low-confidence guess is closer to a shrug, and the more confidently-wrong option is more likely to reflect a habit the model formed around the *other* value, so the low-confidence one is the better bet for the truth.

The whole trick works because a trained model absorbs the associations between sensitive attributes and outputs that were present in its training data — CSMIA is just probing those absorbed associations from outside, one query at a time.

## Mechanics {#mechanics}

**The query set.** For a target record \(x\) with known non-sensitive attributes \(n(x)\) and known true label \(y\), CSMIA builds one variant per possible sensitive value: \(x_i\) with \(n(x_i) = n(x)\) and \(s(x_i) = s_i\), for each \(s_i\) in the set of possible sensitive values \(\mathcal{S}\). Querying the model on every \(x_i\) returns a predicted label \(y_i\) and a confidence score \(conf_i\) for each candidate [§sec_2].

**The three-way rule.** Let \(Y_{\text{match}}\) be the indices whose prediction reproduced the true label \(y\). CSMIA outputs: the unique matching value if exactly one query matched; the highest-confidence matching value if several matched; and the lowest-confidence value overall if none matched [§sec_2]. The asymmetry in the tie-break (highest confidence when something matched, lowest when nothing did) is doing real work — it treats "confident and consistent with the true label" and "least confidently wrong" as two different kinds of evidence for the same conclusion, rather than applying one rule uniformly.

**What CSMIA needs to know.** CSMIA requires full non-sensitive attribute knowledge only for the specific target record being attacked, not for the whole dataset — a lighter requirement than LOMIA, which needs non-sensitive attributes across the entire target dataset to build its attack model [§sec_3].

**Why masking confidence scores doesn't save you.** CSMIA and its sibling LOMIA are singled out in the paper's threat model discussion as attacks that don't need an auxiliary dataset at all, unlike most prior attribute inference attacks [§sec_3]. Because CSMIA's signal comes from confidence scores the model already exposes to any black-box caller, and because LOMIA gets comparable results using only labels, hiding confidence scores does not close off the attack family — it only forces the adversary from CSMIA toward LOMIA.

**Why CSMIA tracks correlation.** The paper's controlled-correlation experiment shows CSMIA and LOMIA accuracy climbing monotonically as the sensitive-output correlation in the training data increases in magnitude, a trend that attacks relying on auxiliary data (imputation, neuron importance) do not follow [§sec_4_1]. This is the empirical basis for treating CSMIA as a probe of the model's *learned* associations rather than of any external data source, and it is why the whole confidence-matrix / angular-difference machinery later in the paper is built by literally reusing CSMIA's query pattern across every record in a group [§sec_5_1].

## The Math {#the-math}

For a target record \(x\), CSMIA's query set is

$$
T(x) \;=\; \{\, x_i \;:\; n(x_i) = n(x),\; s(x_i) = s_i,\; s_i \in \mathcal{S} \,\}
$$

so \(|T(x)| = |\mathcal{S}|\) queries are made per record [§sec_2]. Writing \(Y_{\text{match}} = \{\, i : y_i = y \,\}\) for the indices whose prediction matches the true label, the decision rule is

$$
\hat{s} \;=\;
\begin{cases}
s_i, & |Y_{\text{match}}| = 1,\; i \in Y_{\text{match}} \\[4pt]
s_{\arg\max_{i \in Y_{\text{match}}} conf_i}, & |Y_{\text{match}}| > 1 \\[4pt]
s_{\arg\min_{i \in [1,|\mathcal{S}|]} conf_i}, & |Y_{\text{match}}| = 0
\end{cases}
$$

This rule has no free parameters and no training step of its own — it is applied record by record [§sec_2]. Its output feeds attack success rate directly: \(ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}), \mathcal{A})\) is simply the fraction of records where \(\hat{s} = s(x)\) [§sec_2]. The same query set \(T(x)\), run across every record in a dataset, is exactly what later becomes the confidence matrix: collecting \(\Pr(\mathcal{M}(x'))\) for every \(x' \in T(x)\) over every \(x \in \mathbb{D}\) gives the object that angular difference is computed from [§sec_5_1].

## Go Deeper {#go-deeper}

- **[§sec_2] Preliminaries** — the paper's own compact definitions of CSMIA, LOMIA, imputation, and neuron importance side by side; worth reading as a set since CSMIA is defined by contrast with the others.
- **[§sec_3] Attack Threat Model** — spells out exactly why CSMIA needs only the target record's non-sensitive attributes while LOMIA needs the whole dataset's.
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — the experiment showing CSMIA accuracy tracking correlation, which is the empirical justification for building the rest of the paper's attacks on top of CSMIA's query pattern.
- **[§sec_5_1] Computing Angular Difference** — shows how CSMIA's per-record query set is reused, across a whole group of records, to build the confidence matrix that the disparity attacks depend on.
- Related concepts: `lomia` for the label-only sibling attack, `attribute-inference-attack` for the general setup CSMIA instantiates, and `confidence-matrix` for how CSMIA's queries are scaled up to a group.

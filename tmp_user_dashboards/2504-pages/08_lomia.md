# LOMIA: label-only model inversion

## TL;DR {#tldr}

LOMIA guesses a person's secret attribute by checking which guess makes the model's predicted label come out right — nothing about confidence scores required.

CSMIA needs the model to hand over confidence scores along with its label. LOMIA doesn't: it queries the model once per candidate sensitive value, keeps only the queries whose label matches truth, and uses those clean examples to train a small second model that generalizes the pattern to everyone else. That LOMIA works at all is itself a finding — it proves that a defense which merely hides confidence scores from the API response does nothing to stop attribute inference.

## Intuition {#intuition}

Picture a witness who won't tell you a suspect's alibi directly, but who will confirm or deny any story you propose. You try "the suspect was home" and the witness says false. You try "the suspect was at work" and the witness says true. You didn't need the witness's confidence, tone, or hesitation — a single true/false per guess was enough to pin down the answer, provided exactly one of your stories checked out.

That is the entire trick behind LOMIA. For a person's record, the adversary tries every possible value of the secret attribute — married, single — plugs each hypothetical into the model, and reads off only the predicted class label, not how sure the model was. If exactly one hypothetical produces the label that matches the record's true, publicly-known outcome (e.g., this person really is high-income), that hypothetical is very likely the truth: the model's prediction "worked" only when it was fed the correct secret.

Of course, not every record cooperates — sometimes more than one guess produces a matching label, or none do, and those ambiguous cases can't be resolved this way. LOMIA's answer is to not even try to resolve them directly. Instead, it treats the unambiguous records as free, labeled training data: their non-sensitive attributes are the input, their (uniquely determined) secret attribute is the answer. A small attack model trained on that clean subset can then be pointed at the ambiguous remainder and asked to guess.

The result is an attack that needs less from the model than CSMIA, works purely off yes/no label queries, and — because it needs no confidence scores at all — can't be defeated just by an API that returns labels only.

## Mechanics {#mechanics}

**Move 1 — generate hypotheticals.** For a record with non-sensitive attributes \(n(x)\) and known class label \(y\), the adversary constructs one query per candidate sensitive value and submits each to the target model, recording only the predicted label, exactly as CSMIA does before it looks at confidence scores [§sec_2].

**Move 2 — filter to the unambiguous.** A record is kept for training the attack model only if exactly one of its candidate queries returned the true label \(y\); that candidate's sensitive value becomes the training target. Multi-match and no-match records are set aside as unresolved by this step [§sec_2].

**Move 3 — train and generalize.** An attack model is trained on the clean, filtered set — mapping non-sensitive attributes to sensitive value — and then applied to the records that Move 2 could not resolve directly [§sec_2].

**Move 4 — feed the rest of the paper's attacks.** LOMIA is one of the two base attribute inference attacks (alongside CSMIA) that every later technique in this paper is built on top of. The disparity inference attack ranks groups by how well LOMIA (and CSMIA) would perform on them without ever running the attack itself [§sec_5_2], and LOMIA's ranking quality on Census19 reaches a Kendall's Tau of 0.7579 against ground truth, versus roughly zero for an auxiliary-data baseline [§sec_6_3]. Under the single-attribute targeted attack, LOMIA's accuracy on Census19 rises from 61.24% untargeted to 73.78% at a budget of 0.05 [§sec_6_4].

**Move 5 — why it matters for defenses.** Because LOMIA never touches confidence scores, defenses that respond to attribute inference by hiding or rounding confidence outputs leave LOMIA completely untouched — a point the paper inherits directly from the work that introduced LOMIA [§sec_8].

## The Math {#the-math}

Let \(\mathcal{S}\) be the set of possible sensitive values, \(n(x)\) the non-sensitive portion of record \(x\), and \(y(x)\) its true class label. For each candidate value \(s_i \in \mathcal{S}\), form the hypothetical record \(x_i' = (n(x), s_i)\) and query the model for its predicted label only:

$$
\hat{y}_i = \mathcal{M}(x_i')
$$

A record is added to the LOMIA attack-training set exactly when precisely one candidate matches the true label:

$$
\left|\{\, i : \hat{y}_i = y(x) \,\}\right| = 1 \quad\Longrightarrow\quad (n(x),\ s_{i^*}) \in \text{attack training data}, \qquad \hat{y}_{i^*} = y(x)
$$

where \(s_{i^*}\) is the uniquely matching candidate value. The attack model \(g: n(x) \mapsto s\) is trained on this set and applied to every record failing the uniqueness condition [§sec_2]. Notice there is no confidence term anywhere in this construction — \(\hat{y}_i\) is a hard label, which is precisely why LOMIA survives confidence-masking defenses.

## Go Deeper {#go-deeper}

- **[§sec_2] Preliminaries** — the source definition of LOMIA alongside CSMIA, the imputation baseline, and the formal statement of disparate vulnerability that motivates all of it.
- **[§sec_6_3] Disparity Inference Attack Performance** — LOMIA's ranking quality (Kendall's Tau 0.7579) when its accuracy is used as the disparity proxy's ground truth.
- **[§sec_6_4] Targeted Attribute Inference Attack** — the full accuracy-vs-budget table where LOMIA's targeted variant is evaluated across Census19, Texas-100X, and Adult.
- **[§sec_8] Related Works** — the origin claim that LOMIA defeats confidence-masking defenses, which is why this paper treats LOMIA as a first-class attack rather than a CSMIA footnote.
- Related concepts: `csmia` for the confidence-score-using sibling attack, `angular-difference` for the black-box proxy that predicts where LOMIA will succeed without running it, and `disparity-inference-attack` for how LOMIA's group-level accuracy becomes a ranking target.

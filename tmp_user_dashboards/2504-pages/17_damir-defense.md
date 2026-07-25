# DAMIR: making mutual information regularization disparity-aware (and why it falls short)

## TL;DR {#tldr}

Training a model to forget less about its most-leaked group doesn't reliably close the privacy gap between groups — sometimes it barely moves the needle at all.

Mutual information regularization (MIR) is an existing defense that penalizes a model during training for encoding a statistical link between the sensitive attribute and its output, on the theory that less mutual information means less to invert. Applied normally, MIR reduces attack success averaged over the whole dataset but leaves disparity between groups intact, or worse. This paper's fix — DAMIR — applies that same penalty only to the vulnerable group's records instead of the whole dataset. It helps somewhat against CSMIA, and barely at all against LOMIA, and only reaches full disparity mitigation by badly damaging model accuracy.

## Intuition {#intuition}

Think of MIR as telling the model, "be a little vaguer about everyone's private details, on average." That is a blunt instrument: it makes the model less useful across the board in exchange for a general reduction in privacy leakage, and there's nothing in the incentive that specifically protects the group being leaked the most — the model can happily become vaguer about the group that was already safe while staying just as revealing about the group that wasn't.

DAMIR tries to be more surgical: instead of applying the "be vaguer" penalty to the model's behavior on the whole dataset, it applies that penalty only when the model is dealing with records from the identified vulnerable group. The hope is that this targets the fix at the actual disparity instead of diffusing it across everyone.

The experiment sets up a clean before/after: a Census19 subset where the Male group's sensitive-output correlation is -0.4 and the Female group's is only -0.1, so Male records should be substantially more attackable than Female records if nothing is done. Turning up the regularization strength on plain MIR does eventually shrink the accuracy gap between the two groups — but only at strengths high enough to noticeably degrade the model's overall accuracy, which defeats the point of a "defense" that a real deployer would actually want to use. DAMIR does somewhat better against CSMIA: it can narrow the gap without wrecking accuracy nearly as much, though it still can't close the gap completely without paying a real utility cost. Against LOMIA it barely helps at all — closing the disparity gap without heavily damaging the model appears essentially out of reach.

The lesson the paper draws is not "DAMIR is a bad idea" so much as "penalizing the *output* of unequal correlation doesn't reliably fix the *cause* of unequal correlation." That diagnosis is what motivates the paper's own defense (BCorr), which attacks group-level correlation directly instead of penalizing whatever downstream statistic the model ends up encoding.

## Mechanics {#mechanics}

**Move 1 — the existing defense.** Mutual information regularization adds a secondary loss term during training that pushes the model toward reducing the mutual information between the sensitive attribute and its output, with a hyperparameter \(\beta\) controlling how strongly that secondary loss is weighted against the primary task loss. It reduces the success of untargeted attribute inference attacks but does not reduce disparity between groups — and can even worsen it, per prior evaluation [§sec_7_1].

**Move 2 — the disparity-aware adjustment.** DAMIR's single change is where the mutual-information loss is computed: instead of averaging it over the whole training set, it is computed only on records belonging to the identified vulnerable group, so the regularization pressure targets that group specifically rather than diffusing across the dataset [§sec_7_1].

**Move 3 — the test setup.** Both MIR and DAMIR are applied while training on a Census19 subset where the Male group's correlation is -0.4 and the Female group's is -0.1 — an intentionally lopsided setup designed to produce clear disparity if undefended. \(\beta\) is swept from 0.001 to 0.4, and the paper tracks the attack success rate difference (ASRD) between Male and Female groups alongside target model accuracy for both defenses [§sec_7_1].

**Move 4 — the results.** Plain MIR only reduces disparity at high \(\beta\), and only by paying a large accuracy cost. DAMIR does modestly better under CSMIA — some disparity reduction is achievable without major utility loss — but complete disparity mitigation is only reachable at a considerable accuracy cost even for DAMIR. Under LOMIA, DAMIR performs worse: reducing disparity without significantly damaging model utility appears effectively impossible [§sec_7_1].

**Move 5 — the diagnosis that follows.** Because the paper has already established that unequal group-level correlation is the *cause* of disparity, and MIR/DAMIR only ever penalize a downstream statistical footprint of that correlation rather than the correlation itself, their limited and inconsistent success is consistent with the paper's broader thesis. This is the contrast the paper draws deliberately against its own defense, BCorr, which instead resamples the training data so that group-level correlation is equalized directly [§sec_7_2].

## The Math {#the-math}

The paper describes MIR's training objective in words rather than a preserved formula: a task loss plus a secondary loss weighted by \(\beta\) that penalizes mutual information between the sensitive attribute \(s\) and the output \(y\). Written out, that description corresponds to an objective of the form

$$
\mathcal{L} \;=\; \mathcal{L}_{\text{task}} \;+\; \beta \cdot I\big(s(x);\, \mathcal{M}(x)\big)
$$

with DAMIR's only structural change being that the mutual information term \(I(\cdot;\cdot)\) is estimated using only records from the vulnerable group rather than the full training set [§sec_7_1].

Both defenses are evaluated using ASRD, the metric this paper introduces to quantify group disparity directly. Given a target model \(\mathcal{M}\) trained on \(\mathbb{D}\) and groups \(\mathbb{D}_1, \dots, \mathbb{D}_k\) defined by a non-sensitive grouping attribute \(a\):

$$
ASRD(\mathcal{M}, \mathbb{D}, a, \mathcal{A}) \;=\; \max_i\, ASR_i \;-\; \min_j\, ASR_j, \qquad ASR_i = ASR\big(\mathcal{M}, \mathcal{N}(\mathbb{D}_i), \mathcal{A}\big)
$$

A defense that fully eliminates disparity drives \(ASRD \to 0\); MIR and DAMIR are judged by how much they lower ASRD relative to how much they lower target-model accuracy, and the paper's finding is that this trade-off is unfavorable except at extreme regularization strength [§sec_7_2].

## Go Deeper {#go-deeper}

- **[§sec_7_1] Disparity-Aware Mutual Information Regularization (DAMIR)** — the source for everything on this page: the MIR baseline, the DAMIR adjustment, and the Male/Female experiment.
- **[§sec_7_2] Balanced Correlation Defense (BCorr)** — the paper's own defense and the direct contrast to DAMIR: it targets the cause (correlation) rather than a downstream statistic, and the ASRD metric formalized here is used to evaluate both.
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — the causal claim (correlation drives vulnerability) that explains why penalizing mutual information is an indirect, and therefore unreliable, way to fix disparity.
- Related concepts: `bcorr-defense` for the defense that succeeds where DAMIR struggles, `asrd-metric` for the disparity measurement both defenses are scored against, and `correlation-drives-vulnerability` for the causal chain DAMIR only partially interrupts.

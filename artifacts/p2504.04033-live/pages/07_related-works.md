# Related Works

## TL;DR {#tldr}
This section surveys prior research on model inversion and attribute inference attacks, tracing the field from Fredrikson et al.'s foundational work through more recent studies on disparity, defenses, and related attack types like property inference. It positions the paper's contribution — identifying correlation between sensitive attributes and model output as a key driver of disparate vulnerability — against this backdrop, contrasting the *survey and positioning* role of this section with the concrete techniques described in the paper's own Attack Methodology.

## Intuition {#intuition}
Rather than proposing a new attack in isolation, this section situates the paper's findings within a lineage of work on what models unintentionally reveal about their training data. It shows where existing threat models, defenses, and disparity analyses fall short — either by relying on impractical attacker assumptions, failing to pin down a consistent cause of disparate vulnerability, or targeting a different attack family — and uses those gaps to motivate why correlation-based analysis is a meaningful step forward.

## Mechanics {#mechanics}
Fredrikson et al. originated model inversion attacks for linear regression and later extended them to non-linear ML models, defining the two major attack subtypes — attribute inference (recovering sensitive attributes) and class representative reconstruction (recovering training-data-like instances) — while Mehnaz et al. gave the first evidence that attribute inference vulnerability is disparate across subgroups [§sec_8].

Several threat-model lines are noted as limited in practicality: Gong et al. and Jia et al.'s social-media attribute inference relies on users who already disclose private attributes publicly, restricting applicability to settings where matching public/private pairs exist for auxiliary data, and Tramer et al.'s poisoning-based attack assumes an adversary can poison training data, which is unrealistic for private data outside crowdsourced or collaborative settings [§sec_8].

Yeom et al. studied how "influence" of a sensitive attribute on predictions relates to attack advantage, finding a non-monotonic relationship where advantage first grows then shrinks with influence, which this paper contrasts with its own finding that attribute–output correlation is a consistent, monotonic driver of vulnerability [§sec_8].

On defenses, Wang et al. proposed mutual information regularization against model inversion attacks, Mehnaz et al. introduced CSMIA and LOMIA (the latter showing attacks succeed even without confidence scores, undermining score-masking defenses), and a fairness-constraint defense was shown effective for membership inference but ineffective for attribute inference — a baseline the paper reuses to demonstrate the same ineffectiveness against disparate vulnerability [§sec_8].

Jayaraman et al. found that existing attribute inference attacks underperform a pure imputation attack using auxiliary data, but this paper's own evaluation shows the opposite once private training data has high correlation, where existing attacks surpass imputation [§sec_8].

Dibbo et al. examined potential contributors to disparity in attribute inference attacks but found no consistent factor, and their evaluation lacked datasets spanning a moderate correlation range — a gap this paper addresses by identifying correlation as the missing consistent factor [§sec_8].

Kulynych et al. proposed a defense for disparate vulnerability in membership inference attacks (not attribute inference), and Zhong et al. proposed a defense against disparate vulnerability in link inference attacks for GNNs that does not transfer to tabular attribute inference, leaving both attack settings without an applicable defense prior to this work [§sec_8].

Property inference attacks are noted as a related but distinct line, introduced earlier and later extended to deep learning, but existing work in that space targets properties like group size rather than the attribute–output correlation this paper focuses on [§sec_8].

## The Math {#the-math}
The local context for this Related Works section is prose-only prior-work discussion; no equations are attributed to it, so no formal math is reproduced here [§sec_8].

## Go Deeper {#go-deeper}
No research note or external resource list is associated with this concept, so there are no linked resources to summarize beyond the in-text prior work already surveyed above.

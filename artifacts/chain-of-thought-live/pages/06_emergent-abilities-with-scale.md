# Emergent Abilities with Model Scale

## TL;DR {#tldr}

- Chain-of-thought reasoning is *emergent*: its benefit can't be extrapolated from small-model trends, and it actively hurts most models under 10B parameters.
- A manual read of 45 errors made by 62B-parameter PaLM sorted them into semantic-understanding, missing-step, and other errors — scaling to 540B fixed a substantial share of all three.
- Small models fail for three separate reasons: weak symbol mapping, weak arithmetic, and outputs that never resolve to a parseable answer.

## Intuition {#intuition}

Think of a student who has memorized every vocabulary word but cannot yet chain them into an argument. Below some level of overall ability, added scratch space does not help — the student lacks the pieces to combine, not the room to write them down.

Once the student crosses a threshold of language and logic skill, that same scratch space becomes useful: now the missing piece is structure, not knowledge, and showing the work supplies exactly that structure.

This is why chain-of-thought is called "emergent" rather than merely "improving with scale": a smooth increase in underlying ability produces a threshold effect in the score, not a smooth one, because the technique needs a minimum stock of skills before it has anything to organize [§sec_11_1].

## Mechanics {#mechanics}

The authors read 45 problems that PaLM 62B answered incorrectly and manually sorted the errors into three buckets, using a coarse scheme borrowed from earlier chain-of-thought error-analysis work [§sec_11_1].

| Category | Count (of 45) | What it means |
|---|---|---|
| Semantic understanding | 20 | Model misunderstood the meaning of the problem [§sec_11_1] |
| One step missing | 18 | Reasoning chain skipped a needed step [§sec_11_1] |
| Other | 7 | Hallucinations, repetitive outputs, symbol-mapping errors [§sec_11_1] |

```figure
id: fig_4
caption: How much of each PaLM 62B error category — semantic understanding, missing step, other — was resolved simply by scaling to 540B parameters [§sec_11_1]
```

Scaling from 62B to 540B did not just fix one category of error — it fixed a substantial share of mistakes in semantic understanding, missing-step, and the miscellaneous "other" bucket alike, which is why the authors treat the improvement as broad rather than narrowly arithmetic [§sec_11_1].

```figure
id: fig_5
caption: A semantic-understanding error and a missing-step error, each wrong at 62B and corrected once PaLM reached 540B [§sec_11_1]
```

These worked examples show the fix is not stylistic — the 540B model reasons through a step the 62B model skipped entirely, or reads the question's meaning correctly, rather than just rephrasing the same broken logic [§sec_11_1].

**Three concrete ways small models fail**, noticed qualitatively and independent of the category counts above [§sec_11_1]:
- Symbol mapping: small models fail even at symbolic reasoning tasks that only require copying the logical structure already given in the few-shot exemplars [§sec_11_1].
- Arithmetic: small models have inherently weaker arithmetic ability, so simple operations fail even when no semantic understanding is required [§sec_11_1].
- Unparseable output: small models often never produce a parseable final answer, due to repetition or logic that never terminates [§sec_11_1].

## The Math {#the-math}

No display equation applies to this concept — the evidence here is a set of empirical error counts and a scaling comparison, not a formula, so this tier works through them as a boundary case instead [§sec_11_1].

Of the 45 errors PaLM 62B made, semantic understanding accounts for 20/45 ≈ 44%, missing-step for 18/45 = 40%, and other for 7/45 ≈ 16% [§sec_11_1].

A purely single-cause explanation predicts a sharp cutoff: fixing one skill, say arithmetic, should close only the errors tied to that skill and leave the rest untouched [§sec_11_1].

The paper instead reports gains across all three categories when scaling to 540B, which rules out a narrow single-skill fix and is the evidence the authors use to favor a multi-ability account of the emergence [§sec_11_1].

## Go Deeper {#go-deeper}

The paper frames the full picture as "a complicated phenomena" involving a variety of emergent abilities — semantic understanding, symbol mapping, staying on topic, arithmetic ability, and faithfulness — and leaves open what pretraining data, architecture, and optimization objective causally produce them [§sec_11_1].

- The categorization scheme is coarse and borrowed from prior error-analysis work, so the line between "semantic understanding" and "one step missing" is a judgment call, not a formal taxonomy [§sec_11_1].
- Model scale is often conflated with other factors, such as training compute, so scale alone may not be the causal lever [§sec_11_1].
- This concept builds on Chain-of-Thought Prompting: the error analysis only makes sense once the base technique — few-shot exemplars with intermediate reasoning steps — is in place.

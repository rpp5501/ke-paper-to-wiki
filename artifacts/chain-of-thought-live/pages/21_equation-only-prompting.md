Fixing the two issues: splitting the five overlong paragraphs at their actual claim boundaries, and adding the missing anchor in Mechanics. Here's the corrected page.

```markdown
# Equation-Only Prompting
## TL;DR {#tldr}

Equation-only prompting is an ablation of chain-of-thought prompting: the exemplars keep only the intermediate arithmetic equation, with no natural-language reasoning around it. It helps on datasets that need just a few reasoning steps, but on GSM8K it fails to substantially beat standard prompting — evidence that CoT's natural-language steps are doing more than staging arithmetic.

## Intuition {#intuition}

Think of chain-of-thought as showing your work and equation-only as showing just the final formula. For a question like "3 apples plus 2 more" that gap barely matters, because turning the sentence into an equation is nearly mechanical. For a question that first requires figuring out *what* to compute — is "25 more" an added count or a percentage? — skipping the sentence-level reasoning means skipping the part of the problem that was actually hard.

This is why the concept sits inside the Ablation Study: it holds the exemplar format fixed and removes one ingredient (the natural-language steps) to see what chain-of-thought prompting was contributing beyond just an intermediate computation.

## Mechanics {#mechanics}

Equation-only prompting is an ablation of chain-of-thought prompting that keeps the exemplar structure but replaces the full natural-language reasoning chain with just the arithmetic equation needed to reach the answer. [§sec_11_4]

**Where this isolates the variable:** if equation-only prompting matches chain-of-thought's accuracy on a dataset, the natural-language reasoning wasn't doing the work — the equation alone carried it. [§sec_11_4]

If equation-only prompting falls short of chain-of-thought, the natural-language steps between the equation are where the model's reasoning capacity actually lives. [§sec_11_4]

Equation-only prompting helps on datasets that require only a few reasoning steps — SVAMP, ASDiv, and MAWPS — but does not substantially improve performance on GSM8K. [§sec_11_4]

The paper attributes this gap to semantic difficulty rather than arithmetic difficulty: GSM8K questions are too semantically challenging for the model to translate directly into a single equation. [§sec_11_4]

| Dataset type | Equation-only outcome |
|---|---|
| Few-step arithmetic (SVAMP, ASDiv, MAWPS) | Equation-only prompting helps, since translating the sentence into an equation is close to mechanical [§sec_11_4] |
| Semantically dense (GSM8K) | Equation-only prompting does not substantially improve over standard prompting, since the translation step itself is the hard part [§sec_11_4] |

## The Math {#the-math}

The local evidence does not include the accuracy numbers behind this comparison, only the qualitative pattern above and one worked example — that example carries the quantitative reasoning here. [§sec_11_4]

**The equation-only attempt** collapses the whole question into a single formula, (4 + 20 × 0.25) = 6, and reports 6 as the answer. [§sec_11_4]

That formula reads "25 more points" as literally adding 20 × 0.25 to the first score, and even evaluated on its own terms 4 + 5 = 9, not 6 — the equation is both a semantic misread and an arithmetic slip. [§sec_11_4]

**The chain-of-thought attempt** works the same question in natural language first: it restates that the second 20 minutes scored 25% more than the first, computes 4 × 1.25 = 5, then adds 4 + 5 = 9. [§sec_11_4]

The intermediate sentence "he scored 25 more in the second 20 minutes" is what lets the model correctly convert a percentage relationship into multiplication instead of addition — a translation step the equation-only format has nowhere to write down. [§sec_11_4]

**The boundary case this exposes:** equation-only prompting degrades exactly where a question requires an intermediate semantic decision — like whether "25 more" means an added count or a percentage — before any arithmetic can be written. [§sec_11_4]

On datasets with shallow semantics — SVAMP, ASDiv, MAWPS — that decision is close to trivial, so skipping straight to the equation loses little; GSM8K's questions push that decision far enough that skipping it collapses the model's accuracy. [§sec_11_4]

## Go Deeper {#go-deeper}

- Contrast this directly against Chain-of-Thought Prompting: the two ablations share every exemplar except the presence of natural-language reasoning steps, making equation-only prompting the cleanest isolation of what those steps contribute.
- Equation-only prompting is one arm of the paper's broader Ablation Study, which also tests variation-only and other reduced prompt formats to separate which ingredient of a CoT exemplar drives the accuracy gain.
```

The five long paragraphs are now split at their claim seams (equation vs. its evaluation, CoT's steps vs. the translation it enables, the boundary claim vs. its dataset-specific consequence), and the previously-unanchored Mechanics and The Math claims now end in `[§sec_11_4]`.

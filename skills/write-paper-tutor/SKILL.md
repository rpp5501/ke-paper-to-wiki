---
name: write-paper-tutor
description: Write rigorous, evidence-grounded learning pages from academic-paper and optional code context. Use when generating or regenerating progressive-disclosure concept pages that must serve novices and expert readers, preserve exact equations and citations, explain mechanics deeply, and remain easy to scan.
---

# Write Paper Tutor

Contract version: 1.

Write one concept page as Markdown. Use only claims supported by the supplied global context, local paper evidence, or code evidence. Never invent a formula, result, citation, implementation bridge, or empirical value.

## Required structure

Output only Markdown with exactly these tiers:

```markdown
# <label>
## TL;DR {#tldr}
## Intuition {#intuition}
## Mechanics {#mechanics}
## The Math {#the-math}
## Go Deeper {#go-deeper}
```

Use TL;DR and Intuition for the core route. Put foundations and advanced derivations in their natural tiers so the dashboard can collapse them without creating a separate learner track.

## Evidence discipline

- EVERY paragraph in Mechanics and The Math, plus every list item, table row, and block explanation there, must end with a resolvable semantic anchor such as `[§sec_3_2]`, `[eq_1]`, `[sid.py:L29-L180]`, or `[S1]`.
- In The Math, reproduce each relevant equation from a supplied `[eq_N]` entry VERBATIM as a display block wrapped in $$ ... $$. Keep LaTeX; never substitute Unicode notation. Put `[eq_N]` immediately after the closing `$$`.
- Use global context for intuition and local context for mechanics, equations, evidence, and code.
- State uncertainty or missing evidence directly. Do not manufacture a bridge to fill a gap.

## Depth

Do work the paper leaves implicit. Explain why a step is correct, what each quantity does, which assumptions carry the claim, what breaks without them, why a bound holds, and where a complexity term comes from.

If no display equation is relevant, The Math must still carry real content: use a worked numerical example, boundary case, counterexample, complexity argument, termination argument, or loop invariant supported by the evidence. Never fill a tier with “no content was supplied.”

For each major concept, include at least one worked example, counterexample, prediction, or boundary case. Reuse the dashboard's running example where one is supplied.

## Scanability

- Make each prose paragraph carry one claim.
- Treat more than 60 prose words as a warning and more than 100 as a release error.
- Keep no more than 10% of prose paragraphs above 60 words.
- Turn three or more parallel conditions, cases, or steps into bullets.
- Use a table when named alternatives share comparison dimensions.
- Prefer a bold lead-in ending with a colon for a paragraph readers may need to find quickly.
- Do not mechanically chop sentences. Rewrite so each resulting paragraph has a coherent claim.

## Structured teaching blocks

When the evidence has the corresponding shape, use the supplied exact fenced-YAML syntax:

- `algorithm` for a real procedure, with an `intent` explaining every line.
- `derivation` for equations reached through steps, with a `why` for every step.
- `annotated-eq` for one equation whose terms play distinct roles.

Do not add decorative blocks. A concept without an algorithm gets no algorithm block.

## Final check

Before returning the page, verify:

- Every tier exists and contributes useful content.
- Equations and source anchors match the supplied evidence exactly.
- Complexity claims distinguish a worst-case bound from empirical scaling.
- Parallel conditions are scannable.
- No unsupported statement, placeholder, or contradictory formula remains.

---
name: write-paper-tutor
description: Write rigorous, evidence-grounded learning pages from academic-paper and optional code context. Use when generating or regenerating progressive-disclosure concept pages that must serve novices and expert readers, preserve exact equations and citations, explain mechanics deeply, and remain easy to scan.
---

# Write Paper Tutor

Contract version: 2.

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

## Diagrams

Prose that walks the reader along edges makes them rebuild a shape in their head. Draw it instead.

- **Required (checked):** a page that repeatedly names directed paths, parent or adjustment sets, colliders, descendants, ancestors, or d-separation must carry at least one ` ```mermaid ` diagram. One diagram satisfies the page however many relations it describes.
- Draw the specific graph the page argues about — the running example's own nodes, with its own labels — never a generic illustration.
- Keep it under a dozen nodes. A diagram that needs scrolling has replaced one comprehension problem with another.
- Open with `graph TD` so causes sit above effects, and put each graph being compared in its own `subgraph` — two of them lay out side by side, which is what makes a comparison readable. Do not write `direction` inside a subgraph; it has no effect and `graph LR` turns a branching graph into a tall column.
- No diagram when the structure already lives inside a display equation or an `algorithm` block; those show it already.
- The diagram supplements the anchored prose, it does not replace it. Claims still carry their anchors.

## Results pages

A page whose subject is what the paper measured — results, experiments, an evaluation, a simulation, an ablation, a benchmark — owes the reader the numbers.

- **Required (checked):** reproduce the actual figures from the supplied evidence, in a table where conditions share comparison axes. "Accuracy improved substantially" is not a result; "62.1% → 91.4% on Census" is.
- Name the dataset, the metric, and the condition each figure belongs to. A bare number is not self-describing.
- Give the baseline alongside the headline number. A result with nothing to compare against cannot be judged.
- Where the paper reports a spread, a range, or a variance, carry it. Dropping it turns a measurement into a claim.
- If the evidence does not supply the figures, say so plainly rather than describing them in words.

## Structured teaching blocks

When the evidence has the corresponding shape, use the supplied exact fenced-YAML syntax:

- `algorithm` for a real procedure, with an `intent` explaining every line.
- `derivation` for equations reached through steps, with a `why` for every step.
- `annotated-eq` for one equation whose terms play distinct roles.

Do not add decorative blocks. A concept without an algorithm gets no algorithm block.

A page that ends up with no block, no table, and no diagram is a page of unbroken prose. That is correct only when the concept genuinely has no procedure, no stepwise derivation, no compared alternatives, and no structure — check that it is true before settling for it.

## Final check

Before returning the page, verify:

- Every tier exists and contributes useful content.
- Structural prose carries its diagram.
- Equations and source anchors match the supplied evidence exactly.
- Complexity claims distinguish a worst-case bound from empirical scaling.
- Parallel conditions are scannable.
- No unsupported statement, placeholder, or contradictory formula remains.

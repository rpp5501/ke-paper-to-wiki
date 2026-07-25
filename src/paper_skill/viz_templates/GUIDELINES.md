# Explorable style guidelines

The `viz review` critic argues from this file, not from taste. Cite the rule
you are applying by name. If a change cannot be justified against a rule
here, do not propose it.

Pattern adopted from llmsresearch/paperbanana (MIT, checked 2026-07-24),
which pairs a Stylist step with explicit written guidelines. We keep the
written-guidelines discipline and the bounded critic loop; we do not run a
second model as a judge.

## Scope of a review

Reviews may change **parameters only** — the numbers and strings fed into an
existing template, plus the bet `prompt` and the `caption`. A review never
edits template HTML, never adds a template, and never touches the page. If a
visual is wrong in a way params cannot fix, say so and stop; that is a
propose-and-confirm decision for the owner, not a review.

## 1. Faithfulness

- Every value shown must be traceable to the page it was built from. If the
  page says `d_k = 64`, the visual does not quietly use 8.
- The bet must have a determinate answer the visual actually reveals. A
  question the explorable cannot settle is a broken bet.
- Prefer the paper's own notation and symbol names over invented ones.
- Never imply a result the paper does not claim.

## 2. Conciseness

- One idea per explorable. If the caption needs "and", split or cut.
- The fewest controls that let the reader test the idea; a slider that does
  not change the conclusion is noise.
- Default parameter values should sit where the phenomenon is most visible,
  not at an arbitrary range end.
- Caption ≤ 2 sentences. Prompt ≤ 1 sentence.

## 3. Readability

- The reader must be able to predict before they reveal — commit-then-reveal
  is the whole pedagogy. Do not show the answer in the initial state.
- Labels carry units and symbols; bare numbers are not self-describing.
- Legible at the drawer's width without horizontal scrolling.
- Colour is never the only channel carrying meaning.
- Motion is optional and must respect reduced-motion preferences.

## Placement

`anchor_tier` says where the explorable sits on the page:

- `after-intuition` — the default. The visual builds intuition before the
  formalism arrives.
- `in-the-math` — for visuals that only make sense once the notation is on
  the page, e.g. a term-by-term decomposition of an equation.

Placement is proposed by the skill and confirmed by the owner; it is not
inferred at build time.

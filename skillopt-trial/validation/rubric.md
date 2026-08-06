# Paper-tutor weighted rubric

Score each dimension from 0 to 100, then apply its weight.

| Dimension | Weight | Full-credit behavior |
|---|---:|---|
| Factual and evidence accuracy | 15% | Every formula, result, assumption, citation, and code bridge is supported and resolves to the supplied paper or repository. |
| Conceptual depth | 20% | Explains mechanisms, assumptions, failure modes, and consequences rather than restating the source. |
| Prerequisite clarity | 15% | Introduces required ideas before first use and supplies concise novice refreshers without slowing expert readers. |
| Worked examples | 15% | Uses a correct, useful worked example, counterexample, prediction, or boundary case tied to the concept. |
| Visual explanation | 15% | Prose that walks the reader along a structure carries a diagram of the specific example it argues about; the diagram is readable, faithful to the page, and absent where an equation or algorithm block already shows the structure. |
| Scanability | 10% | One claim per paragraph; parallel cases use bullets; shared comparisons use tables; no prose paragraph exceeds 100 words and no more than 10% exceed 60. |
| Checkpoint quality | 10% | Includes an application-level check with plausible distractors and targeted remediation grounded in a source passage. |

## Automatic rejection

Reject the complete candidate if any output contains an invented or altered formula, nonexistent source, fabricated implementation bridge, unsupported result, concealed missing evidence, or unresolved critical reference.

## Acceptance gate

Accept only when all conditions hold:

- Weighted aggregate improves by at least 3 points over baseline.
- No paper-level aggregate regresses by more than 2 points.
- All deterministic correctness, equation, evidence/citation, schema, component, and accessibility gates remain green.
- The final privacy split was untouched during training and selection.
- A human approves the complete `SKILL.md` diff.

Record raw outputs and per-dimension scores. Never grade from summaries alone.

## Machine-readable policy

`validate_skillopt.py` reads this block, so it intentionally duplicates the
human-readable rubric above. Change it only through an explicit benchmark
policy decision.

```json
{
  "weights": {
    "factual_evidence_accuracy": 15,
    "conceptual_depth": 20,
    "prerequisite_clarity": 15,
    "worked_examples": 15,
    "visual_explanation": 15,
    "scanability": 10,
    "checkpoint_quality": 10
  },
  "automaticRejectionFlags": [
    "invented_formula",
    "altered_formula",
    "nonexistent_source",
    "fabricated_implementation_bridge",
    "unsupported_result",
    "concealed_missing_evidence",
    "unresolved_critical_reference"
  ],
  "minimumAggregateImprovement": 3,
  "maximumPaperRegression": 2,
  "deterministicGates": [
    "correctness",
    "equation",
    "evidence_citation",
    "schema",
    "component",
    "accessibility"
  ],
  "humanReviewRequired": true,
  "finalTestExcludedFromTuning": true
}
```

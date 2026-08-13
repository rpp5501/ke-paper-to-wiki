# Commonsense Reasoning

## TL;DR {#tldr}
Chain-of-thought prompting also works on commonsense reasoning — problems about physical and social interactions that need background world knowledge, not just symbolic math. On PaLM 540B it sets a new best on StrategyQA and beats an unaided human on Sports Understanding, but barely moves CSQA.

## Intuition {#intuition}
Math word problems break into explicit arithmetic steps that a chain of thought can walk through one at a time.

Commonsense questions hide their steps instead: judging whether a sports sentence is plausible, or inferring a date from context, both lean on background facts nobody states aloud. Chain-of-thought prompting asks the model to write that implicit reasoning down before answering.

## Mechanics {#mechanics}

**Five datasets, one requirement:** CoT is applied to problems needing general background knowledge about the physical and social world, not just symbolic math. [§sec_4]

- CSQA: commonsense questions about the world, often needing complex semantics over prior knowledge. [§sec_4]
- StrategyQA: requires inferring a multi-hop strategy to answer a question. [§sec_4]
- Date Understanding (BIG-bench): infer a date from a given context. [§sec_4]
- Sports Understanding (BIG-bench): judge whether a sports-related sentence is plausible or implausible. [§sec_4]
- SayCan: map a natural-language instruction to a sequence of robot actions from a discrete set. [§sec_4]

**Exemplar construction follows the same few-shot recipe as the math-word-problem experiments, adapted to what training data each dataset offers:** [§sec_4]

- CSQA and StrategyQA: exemplars are hand-composed chains of thought attached to examples randomly drawn from each dataset's training set. [§sec_4]
- Date Understanding and Sports Understanding: these BIG-bench tasks have no training set, so the first ten evaluation examples serve as exemplars, with results reported on the rest. [§sec_4]
- SayCan: six exemplars come from the training set used in prior work, again with hand-composed chains of thought. [§sec_4]

**Scaling behavior is consistent across all five tasks:** larger models improve standard-prompting accuracy, and chain-of-thought prompting adds a further gain on top, with the largest CoT improvements appearing at PaLM 540B. [§sec_4]

**CSQA is the boundary case:** the paper reports the chain-of-thought gain on CSQA as minimal, unlike StrategyQA and Sports Understanding, where chain-of-thought prompting sets a new bar against external baselines. [§sec_4]

**Figure 3 (no image available) plots PaLM's accuracy against the CSQA and StrategyQA leaderboard baselines and against the unaided sports-enthusiast baseline on Sports Understanding, for standard versus chain-of-thought prompting.** [fig_3]

| Dataset | Metric | PaLM 540B + CoT | Baseline compared | |
|---|---|---|---|---|
| StrategyQA | Accuracy | 75.6% | Prior state of the art: 69.4% | [§sec_4] |
| Sports Understanding | Accuracy | 95.4% | Unaided sports enthusiast: 84% | [§sec_4] |
| CSQA | Accuracy | Gain reported as minimal | — | [§sec_4] |
| Date Understanding | Accuracy | Not given in supplied evidence | — | [§sec_4] |
| SayCan | Accuracy | Not given in supplied evidence | — | [§sec_4] |

## The Math {#the-math}

StrategyQA's prior best system answers 69.4% of questions correctly, meaning it is wrong on 30.6% of them. [§sec_4]

PaLM 540B with chain-of-thought reaches 75.6% — an error rate of 24.4%, a (30.6 − 24.4) / 30.6 ≈ 20% relative cut in the errors the prior best system was making. [§sec_4]

Sports Understanding compares against an unaided human enthusiast, wrong 16% of the time (100 − 84). PaLM 540B with chain-of-thought is wrong only 4.6% of the time (100 − 95.4). [§sec_4]

That is a (16 − 4.6) / 16 ≈ 71% relative cut in errors against the human baseline — more than three times StrategyQA's ~20% relative cut against its prior best system. [§sec_4]

CSQA is the counterexample: the paper reports its chain-of-thought gain as minimal, so the error-reduction argument that works for StrategyQA and Sports Understanding does not transfer to every commonsense task — a reminder that the benefit is task-dependent, not universal. [§sec_4]

## Go Deeper {#go-deeper}
- Compare this against the math-word-problem results in the parent concept, Chain-of-Thought Prompting, where the gain is largest for multi-step arithmetic — commonsense reasoning shows the same scaling pattern but a much wider spread across tasks.
- SayCan's action-sequence output is a step toward embodied reasoning: mapping language to executable robot actions rather than to an answer string.
- The BIG-bench evaluation sets (Date Understanding, Sports Understanding) lack training splits, which is why their few-shot exemplars come from the evaluation set itself rather than a held-out training set.

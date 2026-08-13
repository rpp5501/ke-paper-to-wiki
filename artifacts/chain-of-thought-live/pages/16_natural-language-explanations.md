# Natural Language Explanations

## TL;DR {#tldr}
Natural language explanations (NLEs) are a prior line of work that pairs a prediction with a free-text justification, mainly to make neural networks more interpretable.

Chain-of-thought prompting looks similar on the page — reasoning text next to an answer — but it is built for a different job: decomposing a multi-hop problem into steps that lead to the final answer, with interpretability as a byproduct rather than the goal.

## Intuition {#intuition}
Imagine two students asked to justify an exam answer. One already knows the answer and writes the justification afterward, mainly so the grader can follow their thinking — that's how a natural language explanation works.

The other student has to work out the justification first, because writing it down is how they find the answer — that's chain-of-thought. Same-looking paragraph on the page, opposite causal role underneath.

## Mechanics {#mechanics}
Natural language explanations (NLEs) are a family of methods that attach a free-text rationale to a model's prediction, with the goal of making the model's behavior easier to interpret [§sec_13_2].

That line of work concentrates on natural language inference, and the rationale can be generated at the same time as the prediction or produced afterward, once the prediction is already fixed [§sec_13_2].

Chain-of-thought prompting places the reasoning text before the final answer, so the intermediate steps are generated first and the answer is conditioned on them rather than the other way around [§sec_13_2].

The goal is to let the model decompose a multi-hop task into smaller steps it can solve one at a time; the resulting gain in interpretability is a side effect of that decomposition, not the target [§sec_13_2].

| Dimension | Natural language explanation | Chain-of-thought |
|---|---|---|
| Primary goal | Model interpretability [§sec_13_2] | Decomposing multi-hop reasoning [§sec_13_2] |
| Timing of the explanation | Simultaneous with or after the prediction [§sec_13_2] | Before the final answer [§sec_13_2] |
| Task focus | Natural language inference and classification [§sec_13_2] | Arithmetic, commonsense, and symbolic tasks [§sec_13_2] |
| What's evaluated | Plausibility of the explanation [§sec_13_2] | Correctness of the final answer [§sec_13_2] |

Prior work combining prompt-based finetuning with NLE reports gains on NLI and classification, but its evaluation centers on whether the generated explanation is plausible, not on whether it caused a better answer [§sec_13_2].

Chain-of-thought prompting instead targets tasks that chain multiple reasoning hops — arithmetic, commonsense, and symbolic problems — where the intermediate steps are load-bearing for the final answer, not just a plausibility check [§sec_13_2].

## The Math {#the-math}
Take a two-hop arithmetic question: Roger has 5 tennis balls, then buys 2 cans of 3 balls each — how many does he have now? An explanation written in NLE style states the answer first and justifies it afterward: '11. He had 5 balls and bought 6 more' [§sec_13_2].

A chain-of-thought output produces the same numbers in the opposite order: 'He started with 5 balls. 2 cans of 3 balls is 6 balls. 5 + 6 = 11.' The final 11 is only reachable in this second version because 6 was already written down before the model needed it [§sec_13_2].

**Boundary case:** suppose a model writes step-like text before its answer on a natural language inference task, purely to make the prediction easier to interpret. By timing alone, that output looks like chain-of-thought [§sec_13_2].

The paper's own scoping still separates the two cases: chain-of-thought is defined by task scope — arithmetic, commonsense, and symbolic problems needing multiple reasoning hops — and by the decomposition goal, not by explanation order alone [§sec_13_2].

## Go Deeper {#go-deeper}
- Open question: does explanation order alone predict whether steps are causally used, or could a model post-hoc rationalize step-like text written before the answer [§sec_13_2]?
- The cited NLE work targets NLI and classification; whether its finetuning approach transfers to arithmetic or symbolic tasks isn't addressed in this excerpt [§sec_13_2].

# Chain-of-Thought Prompting
## TL;DR {#tldr}
- Chain-of-thought (CoT) prompting adds worked, step-by-step reasoning to the few-shot exemplars a model sees, instead of showing only input→output pairs.
- The model then generates its own intermediate reasoning steps before its final answer, mimicking how a person breaks a hard problem into smaller pieces.
- It needs no extra training — just different exemplars in the prompt — and mainly helps sufficiently large models.

## Intuition {#intuition}
Think about solving a multi-step math word problem by hand. A person doesn't jump straight to the answer — they decompose the problem into intermediate steps and solve each one in turn.

Chain-of-thought prompting asks a language model to do the same thing. Instead of showing only question→answer pairs, the few-shot exemplars show question→(reasoning steps)→answer, so the model learns to produce its own reasoning trail before committing to a final answer.

## Mechanics {#mechanics}
Chain-of-thought prompting works by changing what the few-shot exemplars contain, not by changing the model itself. Standard prompting exemplars pair each input directly with an output; chain-of-thought exemplars instead pair each input with a chain of intermediate reasoning steps and only then the output [§sec_2].

Given those exemplars, the model must continue the pattern: when it faces a new problem, it generates its own intermediate reasoning steps first, then a final answer, rather than emitting the answer directly [§sec_2].

The paper attributes several distinct benefits to this mechanism [§sec_2]:
- **Decomposable computation:** breaking a multi-step problem into steps lets the model spend additional computation on problems that need more reasoning steps [§sec_2]
- **Interpretability:** the chain of thought gives a window into how the model may have arrived at an answer, and a place to see where reasoning went wrong — though this doesn't fully characterize the model's underlying computation [§sec_2]
- **Broad applicability:** the same mechanism applies to math word problems, commonsense reasoning, and symbolic manipulation, and in principle to any task a human could solve via language [§sec_2]
- **No training required:** chain-of-thought reasoning can be elicited from a sufficiently large off-the-shelf language model just by including chain-of-thought exemplars in the few-shot prompt — no fine-tuning needed [§sec_2]

## The Math {#the-math}
**Worked example — computation tracks step count.** Consider: "Roger has 5 tennis balls. He buys 2 cans of 3 tennis balls each. How many does he have now?" Standard-prompting exemplars map this question directly to the number 11, so the model must produce that number in one step [§sec_2].

A chain-of-thought exemplar instead spells out the steps: Roger started with 5 balls, 2 cans of 3 balls each is 6 more balls, and 5 + 6 = 11. Given this pattern, the model allocates one reasoning step per arithmetic operation instead of collapsing the whole computation into a single hidden step [§sec_2].

**Boundary case — a single-step problem.** If a question needs only one operation, there's nothing left to decompose: the reasoning chain shrinks to that one step before the answer, so chain-of-thought and standard prompting call for the same amount of computation [§sec_2].

## Go Deeper {#go-deeper}
- Contrasts with **Standard Prompting**, which maps input to output with no intermediate steps, and with **Equation-Only Prompting**, which shows only the equation rather than natural-language reasoning.
- Builds on **Few-Shot In-Context Learning**: chain-of-thought exemplars are inserted into the same few-shot prompting setup rather than requiring new training.
- Applied to three task families in this paper: **Arithmetic Reasoning**, **Commonsense Reasoning**, and **Symbolic Reasoning** [§sec_2].
- See **Emergent Abilities with Model Scale** for why this mechanism only helps sufficiently large models, and **Discussion and Limitations** for open questions about what the chain of thought actually reflects.

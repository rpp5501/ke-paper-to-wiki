# Task Applicability

## TL;DR {#tldr}

Chain-of-thought prompting helps some tasks far more than others. It works best when a task demands multi-step reasoning, is run on a large model, and shows a flat scaling curve — otherwise the gains shrink or vanish [§sec_11_3].

## Intuition {#intuition}

Chain-of-thought is not a task-agnostic performance boost. It amplifies reasoning that a task already requires humans to do step by step — and does nothing for tasks that don't need that structure [§sec_11_3].

Picture chain-of-thought as a lever with three switches: task difficulty, model size, and scaling-curve shape. All three must be set correctly before the lever moves anything [§sec_11_3].

Flip any one switch off — an easy task, a small model, or a steeply rising scaling curve — and pulling the lever barely changes the outcome [§sec_11_3].

## Mechanics {#mechanics}

The paper names three conditions under which chain-of-thought prompting delivers its largest gains [§sec_11_3]:

- The task requires multi-step reasoning rather than a single inference [§sec_11_3]
- The model is large enough for the emergent reasoning ability to appear [§sec_11_3]
- The scaling curve for standard prompting is flat, leaving room chain-of-thought can capture [§sec_11_3]

GSM8K is the paper's clearest case for all three conditions holding at once. Its problems need several arithmetic steps, the gain appears at 540B parameters, and standard prompting's scaling curve stays flat there — so chain-of-thought produces its largest measured gain [§sec_11_3].

MAWPS subsets show the opposite pattern. SingleOp, SingleEq, and AddSub need only one or two steps, so the multi-step condition fails [§sec_11_3].

540B already scores 90 or higher on these subsets without chain-of-thought, so little room remains for any method to add [§sec_11_3].

Difficulty and headroom compound rather than act separately. An easy task fails the multi-step condition and simultaneously leaves less room to improve, so both mechanisms suppress the same result [§sec_11_3].

The paper restricts its experiments to arithmetic, commonsense, and symbolic reasoning, though it frames chain-of-thought as applicable in principle to any task where a human would use a chain of thought — machine translation is named as one untested example [§sec_11_3].

## The Math {#the-math}

**Headroom bounds the achievable gain.** MAWPS's SingleOp, SingleEq, and AddSub subsets score 90 or higher out of 100 under standard prompting alone, so chain-of-thought has at most 10 points left to add on those subsets — and observed gains land far below that ceiling [§sec_11_3].

**The boundary case makes the mechanism explicit.** A subset already at 100 accuracy has zero headroom left: no prompting strategy, chain-of-thought included, can register a measurable gain there no matter how many reasoning steps the task actually requires [§sec_11_3].

**GSM8K sits at the opposite end of this same arithmetic.** The paper singles it out as the largest chain-of-thought gain precisely because standard prompting leaves it far from ceiling, so headroom and task difficulty point the same direction rather than pulling against each other [§sec_11_3].

## Go Deeper {#go-deeper}

The paper's claim of general applicability is explicitly untested outside reasoning tasks. It names machine translation as an example task type where chain-of-thought's benefit remains an open empirical question, leaving the three conditions in Mechanics as the closest guide to predicting new cases [§sec_11_3].

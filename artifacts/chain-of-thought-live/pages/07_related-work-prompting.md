# Prompting (Related Work)
## TL;DR {#tldr}
- Chain-of-thought prompting belongs to the broader family of general prompting approaches, which optimize an input prompt so one model handles many tasks [§sec_13_1].
- It is distinguished from two neighboring lines of work by *where* the added text attaches: instructions go before the input, chain-of-thought reasoning comes after it as output [§sec_13_1].

## Intuition {#intuition}
Large language models can be steered without updating their weights, purely by rewriting the text handed to them [§sec_13_1]. Chain-of-thought prompting is one entry in that family, and the paper distinguishes itself from two neighboring lines of work by pointing at where the added text goes [§sec_13_1].

Three families share the goal of getting more task performance out of a fixed model through prompting alone:
- **General prompting**: optimize the input prompt so a single model handles many tasks [§sec_13_1].
- **Instruction-following**: prepend a task description to the input [§sec_13_1].
- **Sequential generation chaining**: combine successive outputs of a language model, shown to help in a 20-person HCI study [§sec_13_1].

Chain-of-thought prompting sits in the first family, but unlike instruction-following it augments the model's output rather than its input [§sec_13_1].

## Mechanics {#mechanics}
| Approach | What gets added | Where it attaches | Evidence |
|---|---|---|---|
| General prompting | An optimized input prompt | Input | [§sec_13_1] |
| Instruction-following | A task description | Prepended to the input | [§sec_13_1] |
| Chain-of-thought | Reasoning steps | Appended to the output | [§sec_13_1] |
| Sequential chaining (HCI) | Successive model generations | Combined together, not a single prompt | [§sec_13_1] |

Instruction-following and chain-of-thought prompting both attach metadata to an input–output pair, which is why the paper treats them as related [§sec_13_1].

The two methods differ in placement: instructions are prepended to the input, describing the task before the model sees the query, while chain-of-thought reasoning is appended to the output, produced by the model itself as it answers [§sec_13_1].

A second related direction, from human-computer interaction research, chains together sequential generations of a language model rather than augmenting a single prompt; a 20-person user study found this improved task outcomes [§sec_13_1].

## The Math {#the-math}
**Boundary case — where augmentation sits in the autoregressive chain.** A language model factors P(output | input) token by token, each token conditioned on everything already in the sequence [§sec_13_1].

Prepending an instruction inserts it before generation starts, so every output token conditions on it [§sec_13_1].

Appending a chain-of-thought trace works differently: the model must generate the reasoning tokens first, and only the final answer token conditions on that self-generated reasoning [§sec_13_1].

**Boundary case — reading the 20-person study.** The only quantitative detail this section offers is sample size: the sequential-chaining evidence comes from a 20-person user study, not a benchmark evaluated task by task [§sec_13_1].

Twenty participants is enough to show an effect in a controlled HCI study, but far too few to bound how the effect size would generalize across tasks or models [§sec_13_1].

## Go Deeper {#go-deeper}
This concept is the related-work anchor for [[Chain-of-Thought Prompting]] itself, and for the three ways it can be realized: [[Natural Language Explanations]], [[Program Synthesis and Execution]], and [[Intermediate Language Steps]]. Each of those pages picks up the "appended to the output" mechanic described above and specializes it.

# Few-Shot In-Context Learning

## TL;DR {#tldr}
Few-shot in-context learning prompts a frozen language model with a handful of input-output examples instead of updating its weights. The model infers the task pattern from the exemplars alone and applies it to a new input at inference time.

## Intuition {#intuition}
Imagine handing someone a few solved examples of a puzzle type and then a new, unsolved puzzle — no lecture, no rulebook, just pattern matching from the demonstrations. That is what few-shot in-context learning asks of a language model: read a short prompt containing several worked (input, output) pairs, then continue the pattern for a fresh input. Nothing about the model's parameters changes; the "learning" happens entirely inside the forward pass, encoded in the prompt itself.

## Mechanics {#mechanics}
Instead of finetuning a separate checkpoint for every new task, few-shot in-context learning prompts a single frozen model with a few input–output exemplars that demonstrate the task, and the model performs the task on a new input without any parameter update [§sec_1].

This approach succeeded for a range of simple question-answering tasks, where each exemplar could show the mapping directly and the target task required no more than pattern completion [§sec_1].

The method has a key limitation: it works poorly on tasks that require reasoning, and performance often fails to improve substantially even as language model scale increases [§sec_1].

Standard few-shot exemplars pair each input directly with its final output, giving the model no signal about the intermediate steps needed to reach that output on a harder problem [§sec_1].

## The Math {#the-math}
Consider a two-shot arithmetic prompt built the way standard few-shot prompting builds it: each exemplar pairs a word problem directly with its final numeric answer, with nothing in between [§sec_1].

The model therefore never sees, inside the prompt, what operations turn the problem's numbers into that answer — only the final mapping is demonstrated [§sec_1].

On a one- or two-step question this gap rarely matters — the model can often infer the mapping from surface pattern alone, which is why standard few-shot prompting succeeded on simple question-answering tasks [§sec_1].

On a multi-step word problem the same format forces the model to compress arithmetic, unit tracking, and multi-hop inference into a single output span, with no worked steps in the exemplars to imitate. This is the boundary case the paper identifies: reasoning tasks where standard few-shot prompting works poorly and stops improving with scale [§sec_1].

## Go Deeper {#go-deeper}
Few-shot in-context learning is the substrate chain-of-thought prompting builds on: it keeps the frozen-model, no-finetuning prompting format, but replaces each exemplar's bare final answer with the intermediate reasoning steps that get there. See Chain-of-Thought Prompting for how that change closes the reasoning gap identified above.

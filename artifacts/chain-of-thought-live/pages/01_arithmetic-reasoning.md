# Arithmetic Reasoning
## TL;DR {#tldr}
- Arithmetic reasoning here means math word problems that need several chained calculation steps, not simple fact lookup [§sec_3].
- Chain-of-thought prompting has the model write out those intermediate steps before giving a final answer, which measurably improves performance on this task [§sec_3].
- At 540B parameters, this prompting alone reaches parity with task-specific finetuned models and sets a new state of the art on GSM8K [§sec_3].

## Intuition {#intuition}
Picture a word problem asking for a total after several purchases and discounts.

A model that jumps straight to the final number must get every intermediate step right inside one hidden computation, with no way to check itself.

Writing the steps down first turns one hard leap into a chain of easier ones — the same reason people show their work on a math test [§sec_3].

## Mechanics {#mechanics}

**The task:** Arithmetic reasoning is evaluated with math word problems where a language model must combine several numeric facts and operations to reach one answer, a category language models often handle poorly without help [§sec_3].

**Why chain-of-thought helps here specifically:** Because these problems reward decomposition, a model that emits its intermediate reasoning as text gets to reuse each partial result instead of tracking it silently, which lowers the chance any one step corrupts the whole computation [§sec_3].

**Scale interacts with the effect:** The result is reported specifically for the 540B-parameter model, where chain-of-thought prompting performs comparably with task-specific finetuned models on several arithmetic benchmarks [§sec_3].

**A new state of the art:** On GSM8K, described as a challenging benchmark, chain-of-thought prompting with this model achieves a new state of the art, without any task-specific finetuning [§sec_3].

```figure
id: fig_2
caption: A worked arithmetic example showing the chain of thought between the question and the numeric answer [§sec_3]
```

## The Math {#the-math}

**Multi-step composition, not single-step lookup:** A typical problem in this category asks the model to chain several arithmetic operations, for example computing a subtotal, applying a discount, then adding tax, where each later step consumes the result of the one before it [§sec_3].

**Boundary case, one hop:** A one-step problem needs a single operation, so a direct-answer model and a chain-of-thought model have equal odds of success — there is nothing to decompose [§sec_3].

**Boundary case, three hops:** A three-step problem needs each operation's output to feed the next operation's input, so a direct-answer model must get all three right in one hidden pass, while a chain-of-thought model can verify or correct each intermediate value along the way [§sec_3].

## Go Deeper {#go-deeper}

This concept sits under **Chain-of-Thought Prompting**, the parent technique it applies to arithmetic problems specifically [§sec_3].

- **Arithmetic Experimental Setup** — the benchmarks and models this section's claim is evaluated on.
- **Arithmetic Reasoning Results** — the reported numbers behind "comparably with task-specific finetuned models" and "new state of the art."
- **Ablation Study** — checks whether the gain comes from chain-of-thought itself, not from prompt length or extra compute.
- **Robustness to Exemplars** — checks whether the effect holds across different chosen few-shot exemplars.

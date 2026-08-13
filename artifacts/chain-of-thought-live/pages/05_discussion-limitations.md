# Discussion and Limitations

## TL;DR {#tldr}
- Chain-of-thought (CoT) prompting improved arithmetic, commonsense, and symbolic reasoning using only prompting on off-the-shelf models — no finetuning [§sec_6].
- The gains show that standard prompting only reports a lower bound on a model's reasoning capability [§sec_6].
- Four limitations remain open: whether the network is truly "reasoning," annotation cost for finetuning, no guarantee of correct reasoning paths, and reasoning's dependence on large model scale [§sec_6].

## Intuition {#intuition}

Think of standard prompting as asking a model to blurt out an answer, and CoT as asking it to show its work. The three experiments point at the same result from different angles: reasoning tasks improve once the model is allowed to work step by step instead of answering directly.

That reframing carries real limitations. Showing work looks like reasoning, but the paper does not claim the network is actually reasoning inside — that question stays open, alongside costs and scale constraints that limit how CoT can be deployed today.

## Mechanics {#mechanics}

The three experiments generalize one mechanism across task types:

| Task | Finding |
|---|---|
| Arithmetic reasoning | Large improvement, robust to different annotators, exemplars, and language models [§sec_6] |
| Commonsense reasoning | CoT's linguistic form makes it generally applicable beyond math [§sec_6] |
| Symbolic reasoning | Enables out-of-distribution generalization to sequence lengths longer than those in the exemplars [§sec_6] |

All three results come from prompting an off-the-shelf model — no language models were finetuned to produce them [§sec_6].

Model scale drives when CoT works: for many reasoning tasks, standard prompting's scaling curve stays flat while CoT's curve rises sharply as models get larger [§sec_6]. That gap means standard-prompted performance is only a lower bound on what a model can do — its true ceiling sits higher than a flat standard-prompting curve reveals [§sec_6].

Two questions follow directly from that observation:

- How much further will reasoning ability improve with additional model scale [§sec_6]?
- What other prompting methods might expand the range of tasks language models can solve [§sec_6]?

The paper names four limitations to this approach:

| Limitation | Detail |
|---|---|
| Reasoning authenticity | CoT emulates human thought processes, but whether the network is actually reasoning is left as an open question [§sec_6] |
| Annotation cost | Cheap to annotate exemplars for few-shot prompting, but could be prohibitive for finetuning — though synthetic data or zero-shot generalization might help [§sec_6] |
| Correctness guarantee | Chains of thought are not guaranteed correct and can lead to right or wrong answers alike; improving factual generation is future work [§sec_6] |
| Scale dependence | CoT reasoning emerges only at large model scale, making it costly to serve; inducing it in smaller models is future work [§sec_6] |

## The Math {#the-math}

The discussion's central claim is a monotonicity argument rather than an equation: reasoning capability is at least as large as what CoT prompting reveals, which is at least as large as what standard prompting reveals [§sec_6].

```derivation
shape: Standard-prompting performance is a lower bound on a model's reasoning capability, not a measurement of its ceiling.
steps:
  - latex: "\\text{Perf}_{\\text{standard}}(M, T) \\le \\text{Perf}_{\\text{CoT}}(M, T)"
    why: "CoT prompting raises performance over standard prompting on the same model and task, so the standard-prompting score never exceeds the CoT score empirically [§sec_6]"
  - latex: "\\text{Perf}_{\\text{CoT}}(M, T) \\le C(M, T)"
    why: "A model cannot score above its true capability C(M,T) under any prompting strategy, since capability is the best achievable performance [§sec_6]"
  - latex: "\\text{Perf}_{\\text{standard}}(M, T) \\le C(M, T)"
    why: "Chaining the two inequalities shows standard prompting only lower-bounds capability — a flat standard-prompting curve does not mean the capability curve is flat too [§sec_6]"
```

This is why the paper treats the flat-versus-rising scaling curves as evidence: a rising CoT curve on a task where the standard curve is flat means the capability was there all along, just invisible under standard prompting [§sec_6].

**The annotation-cost argument compares two scaling regimes.** Few-shot CoT prompting pays a fixed cost: a handful of exemplars are annotated once and reused for every test example [§sec_6]. Finetuning pays a cost that scales with the training set's size, since each training example would need its own chain of thought [§sec_6].

As the training set grows, the fixed few-shot cost becomes negligible next to the finetuning cost — which is why the paper flags finetuning-scale annotation, not few-shot annotation, as the harder problem [§sec_6].

## Go Deeper {#go-deeper}

The open question of whether the model is "actually reasoning" versus pattern-matching a plausible-looking chain connects directly to the correctness-guarantee limitation: a chain can look like reasoning and still reach a wrong answer, which is exactly what an unconstrained language model produces without an external check on validity [§sec_6]. Both limitations point at the same underlying gap — CoT elicits reasoning-shaped text, not verified reasoning — which the paper leaves for future work on factual generation and smaller-model reasoning [§sec_6].

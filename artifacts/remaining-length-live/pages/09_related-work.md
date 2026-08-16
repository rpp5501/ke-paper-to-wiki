# Related Work

## TL;DR {#tldr}

This paper's core method — a linear probe reading remaining output length off the residual stream — sits at the intersection of three literatures, and answers a question none of them settle on its own:

- **Probing methodology** established that linear probes decode information from frozen activations, but also that probe accuracy alone is a weak claim, and that OOD generalization is rarely tested.
- **Planning and mid-trace re-estimation** work shows LLMs commit to future tokens and shift their internal state mid-generation, but has not put a number on what shifts.
- **Token-counting theory** bounds exact counting in transformers, a different problem from the continuous, approximate estimate this paper reports.

## Intuition {#intuition}

A linear probe is like holding an X-ray plate up to a layer's activations: if a straight line through the plate correlates with the property you care about, the property is "linearly there." The catch, raised repeatedly in prior work, is that an X-ray taken in one room might not read correctly in a different room — a probe trained on one dataset or topic can fail on another. This paper's contribution to that concern is to test the same X-ray plate across rooms it wasn't built for.

Separately, other work has asked whether LLMs plan ahead at all — for instance, committing to a rhyme before writing the line that reaches it. This paper asks the analogous question about length: does the model already "know," several tokens early, roughly how much more it is going to say?

## Mechanics {#mechanics}

**Linear probing traces to Alain & Bengio.** Training a small linear classifier on frozen intermediate activations reveals what information a layer encodes, without altering the network itself; this is the family of tool the paper applies to remaining output length [S1].

**Probe accuracy is not proof of use.** Hewitt & Liang show a probe's accuracy can reflect the probe's own capacity rather than the representation's true content; they introduce control tasks and a selectivity metric to separate the two [S2].

Belinkov's survey synthesizes this concern and explicitly flags generalization — whether a probe's decision boundary holds outside its training distribution — as an open weakness of the probing paradigm [S3].

**OOD generalization is the exception, not the norm.** Evaluations of LLM probes outside their training distribution are scarce, and transfer is often weak, with the cross-lingual refusal direction a notable exception [§sec_2].

Burns et al. show unsupervised linear directions can generalize across distribution shift better than naive supervised probes, which is why OOD robustness counts as a stronger validity test than in-distribution accuracy alone [S4].

This paper's contribution to that thread is its cross-dataset probe-transfer matrices, which test exactly the generalization gap Belinkov flags — on a continuous regression target, remaining length $r_t$ read from the residual stream, where prior OOD probe work is especially sparse [§sec_2].

**Circuit tracing shows LLMs plan ahead.** Attribution-based circuit tracing on Claude finds it commits to a rhyme word before writing the line that ends in it — evidence of planning over tokens not yet generated; this paper asks the analogous question over remaining length rather than rhyme choice [§sec_2].

**The "aha moment" literature is contested but related.** Mid-trace shifts around the DeepSeek-R1 aha moment have been read both skeptically and mechanistically, with no consensus on whether they reflect a genuine change in the model's computation [§sec_2].

The closest prior method in that literature trains a linear probe that reads out answer-confidence at every reasoning step; this paper's retraction-shift observation has the same shape, but on the length variable instead of confidence [§sec_2].

Engineered Wait-token interventions independently confirm that inserting extra reasoning tokens changes test-time compute, corroborating that models track — and can be steered on — how much computation remains [§sec_2].

**Token counting is a separate, orthogonal literature.** Theoretical results characterize transformers' capacity for exact counting: a $d \geq m$ phase transition for counting to $m$, attention over-squashing that limits global aggregation, and BPE boundary effects that corrupt token-level counts [§sec_2].

Those results bound *exact* $0/1$ counting over the prompt; this paper's target is a *continuous* regression over hidden states for tokens the model itself will still produce, with a headline $\mathrm{MAE} \approx 30$ on a 400-token completion [§sec_2].

The two threads are complementary rather than contradictory: an impossibility result for exact counting says nothing about whether an approximate estimate of remaining length is linearly recoverable, which is the question this paper answers empirically [§sec_2].

## The Math {#the-math}

**The comparison this section draws precisely.** Each prior literature sets a different bar for what counts as evidence of an internal capacity, and each stops short of this paper's claim in a different, specific way:

| Prior literature | What counts as evidence there | Where it stops short | This paper's answer |
|---|---|---|---|
| Probing methodology (Hewitt & Liang, Belinkov) | In-distribution probe accuracy | Accuracy alone doesn't show the property generalizes off-distribution [S2][S3] | Reports cross-dataset transfer matrices, not just in-distribution accuracy [§sec_2] |
| OOD probing (Burns et al.) | An unsupervised direction that transfers across a shift | Tested on discrete properties like truthfulness, not continuous regression targets [S4] | Evaluates OOD transfer of a continuous regression target, $r_t$, on the residual stream [§sec_2] |
| Circuit tracing / aha-moment probes | A mechanistic trace, or a confidence probe at one reasoning step | Shows *that* the model shifts mid-trace, not a magnitude for the shift | Reads out a numeric remaining-length estimate at every step, giving the shift a quantity [§sec_2] |
| Token-counting theory | An exact $0/1$ count over the prompt | Phase transitions and over-squashing bound exact counting, and are silent on approximate estimation | Reports $\mathrm{MAE} \approx 30$ tokens on a 400-token completion, outside that theory's scope [§sec_2] |

**Where token-counting theory would actually conflict with this paper.** An exact-counting impossibility result only bears on this paper's claim if the paper asserted exact recovery of remaining length; instead it reports an approximate regression with $\mathrm{MAE} \approx 30$ on 400-token completions — roughly 7.5% relative error — which no exact-counting limit rules out, since no exact count is claimed [§sec_2].

**The case that separates in-distribution accuracy from OOD validity.** A probe can score well on held-out examples from its own training distribution and still fail on a shifted dataset — exactly the failure mode Hewitt & Liang's selectivity metric and Belinkov's generalization critique predict [S2][S3].

The paper's cross-dataset transfer matrices are the test built to catch that failure, rather than reporting a single in-distribution accuracy number [§sec_2].

## Go Deeper {#go-deeper}

- [Finding Syntax with Structural Probes](https://nlp.stanford.edu/~johnhew/structural-probe.html) — the clearest visual walkthrough of what a linear probe on frozen activations actually does; start here if "linear probe" is a new idea.
- [Designing and Interpreting Probes with Control Tasks](https://arxiv.org/abs/1909.03368) — the paper behind the "accuracy isn't proof of use" caveat this page relies on, with the control-task methodology spelled out.
- [Probing Classifiers: Promises, Shortcomings, and Advances](https://arxiv.org/abs/2102.12452) — the survey that consolidates probing methodology and names generalization as its open weakness.
- [Discovering Latent Knowledge in Language Models Without Supervision](https://arxiv.org/abs/2212.03827) — the closest prior work to an OOD-generalization framing of probing, and the direct precedent for testing transfer across distribution shift.

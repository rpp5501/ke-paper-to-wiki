# Models and Datasets

## TL;DR {#tldr}

The paper probes three open-weight, instruction-tuned 7–8B models — Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3, and Olmo-3-7B-Instruct — across seven datasets [§sec_3_7].

Two are synthetic (Count, Countdown) with an exactly known remaining length; five are standard datasets spanning math, retrieval, and open-ended reasoning [§sec_3_7].

Hidden states are cached once per example and reused for every probe variant, so cost is dominated by one forward pass per example, not by how many probes are trained on it [§sec_3_7].

## Intuition {#intuition}

Why three model families instead of one? Llama, Mistral, and Olmo differ in tokenizer, pretraining mixture, and instruction-tuning recipe [§sec_3_7]. A signal that shows up in all three is a property of instruction-tuned language models generally; a signal that shows up in only one could just be an artifact of that model's training [§sec_3_7].

Restricting to the 7–8B parameter band keeps inference tractable on a single research GPU while still capturing models capable of complex instruction-following [S1][S2][S3].

All three ship fully open weights with documented training and instruction-tuning recipes, which is why they are favored here over closed, API-only models for probing internal properties [S1][S2][S3].

Prior work comparing similarly-sized instruction-tuned checkpoints (Mistral-7B vs. Llama-2-7B) found that model family and instruction-tuning recipe produce measurably different behavior even at matched parameter counts — a reason to test more than one checkpoint here [S5].

## Mechanics {#mechanics}

The three checkpoints are Llama-3.1-8B-Instruct, Olmo-3-7B-Instruct, and Mistral-7B-Instruct-v0.3, all in the 7–8B parameter range [§sec_3_7]. They differ in tokenizer, pretraining mixture, and instruction-tuning recipe, so agreement across all three isolates a property of instruction-tuned LLMs rather than one training pipeline [§sec_3_7].

Seven completion-style datasets are used in total: two synthetic (controlled-length) sets and five standard ones covering reasoning, retrieval, and open-ended writing [§sec_3_7].

Count and Countdown consist of completions to prompts where the eventual completion length $T$ is exactly determined by the prompt, with $n \in [0, 300]$ [§sec_3_7].

This makes them a controlled regime: a probe that performs well here is verifiably reading the relevant information out of the residual stream, rather than exploiting dataset-wide regularities [§sec_3_7].

The five standard datasets cover grade-school math, competition-level math, multiple-choice question answering with reasoning rationales, long-form reasoning traces, and short-form retrieval [§sec_3_7].

Together, Count, Countdown, and the five standard sets span a wide range of expected response lengths and structural regularities — a prerequisite for the cross-dataset experiments reported elsewhere in the paper [§sec_3_7].

The system prompt and the source field of the user message for each dataset are listed in the Appendix [§sec_3_7].

Hidden states are extracted for both train and eval splits in a single forward pass per example [§sec_3_7].

That cache is then reused for every probe in the family and for the per-layer variants reported in the Appendix [§sec_3_7].

So the computational cost of training the entire probe family is dominated by the one LM forward pass per example, not by how many probes are trained on the cached hidden states afterward [§sec_3_7].

## The Math {#the-math}

Three models times seven datasets gives 21 (model, dataset) pairs, and each pair needs its own set of hidden states before any probe can be trained on it [§sec_3_7].

Without caching, that 21-way product would have to be paid again for every probe variant and every layer probed [§sec_3_7]. With caching, the LM forward pass runs once per example — train and eval — and every later probe, at each layer, reads from that cache instead of re-running the model [§sec_3_7].

The synthetic range $n \in [0, 300]$ sets a controlled boundary: at $n=0$ the remaining length $T$ is trivially small, and at $n=300$ it is at its largest tested value, so a probe has to be accurate across the full span rather than just in one regime [§sec_3_7].

If only Llama were evaluated and the length signal turned out to be a quirk of its tokenizer or instruction-tuning recipe, seven-dataset agreement on that single model would look identical to seven-dataset agreement on a genuine cross-model property — the two hypotheses are separated only by adding Mistral and Olmo as independent checks [§sec_3_7][S5].

## Go Deeper {#go-deeper}

- [Llama-3.1-8B-Instruct model card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) — the canonical spec of the exact checkpoint used here, including its chat template and intended-use notes; open this first if you need to know exactly what was probed.
- [Introducing Llama 3.1: Our most capable models to date](https://ai.meta.com/blog/meta-llama-3-1/) — benchmark comparison charts placing Llama-3.1-8B-Instruct against other similarly-sized open models, context for why this checkpoint counts as a strong instruction-following baseline.
- [Mistral-7B-Instruct-v0.3 model card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) — documents what changed from v0.2 (extended vocabulary, function calling), relevant to why this exact version was chosen.
- [OLMo: Open Language Model (AI2)](https://allenai.org/olmo) — background on the fully-open OLMo family that Olmo-3-7B-Instruct belongs to, including released training data and code.

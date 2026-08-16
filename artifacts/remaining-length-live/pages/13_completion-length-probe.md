# Completion Length Probe

## TL;DR {#tldr}

- A linear probe on the prompt's last hidden state predicts the model's total completion length before it writes a single output token.
- It beats a constant-median statistical baseline in every one of 20 (model, dataset) cells tested, with the improvement ranging from about a quarter to nearly total error elimination.

## Intuition {#intuition}

A model seems to sense, before writing anything, roughly how long its answer will run — a factual question gets a short reply, a multi-step problem a long one. The Completion Length Probe tests whether that sense is linearly legible from the prompt's last hidden state alone.

Think of it like a writer glancing at a prompt and guessing the essay's final word count before drafting a single sentence. The probe formalizes that guess as a trained linear readout, and measures how much closer it gets than simply guessing the typical length every time.

## Mechanics {#mechanics}

The probe is a linear readout trained on the language model's last hidden state at the prompt's final token position, before generation begins. It outputs a single number, the predicted total completion length T̂₀, and is scored by mean absolute error against the realized length T [§sec_4_1].

The comparison point is a constant-median statistical baseline: for each (model, dataset) pair it always predicts the same value, the median completion length observed in that split, ignoring the specific prompt entirely. Any gap between the probe and this baseline is what the prompt's hidden state adds [§sec_4_1].

Table 1 evaluates both at the prompt's last position, averaged over the eval split, across three model families and up to seven datasets each; Mistral-7B on TriviaQA was skipped for compute reasons. The probe wins every cell it competes in [§sec_4_1] [tab_1].

| Model | Dataset | Baseline MAE | Probe MAE | Reduction |
|---|---|---|---|---|
| Llama-3.1-8B | Count | 150.17 | 29.73 | 80.2% [tab_1] |
| Llama-3.1-8B | Countdown | 150.18 | 5.27 | 96.5% [tab_1] |
| Llama-3.1-8B | GSM8K | 58.66 | 42.29 | 27.9% [tab_1] |
| Llama-3.1-8B | MATH | 166.32 | 115.29 | 30.7% [tab_1] |
| Llama-3.1-8B | MMLU-Pro | 204.21 | 117.19 | 42.6% [tab_1] |
| Llama-3.1-8B | OpenThoughts-1k | 212.24 | 141.65 | 33.3% [tab_1] |
| Llama-3.1-8B | TriviaQA | 57.86 | 44.20 | 23.6% [tab_1] |
| Olmo-3-7B | Count | 147.67 | 31.22 | 78.9% [tab_1] |
| Olmo-3-7B | Countdown | 150.58 | 8.40 | 94.4% [tab_1] |
| Olmo-3-7B | GSM8K | 116.17 | 80.46 | 30.7% [tab_1] |
| Olmo-3-7B | MATH | 194.05 | 132.13 | 31.9% [tab_1] |
| Olmo-3-7B | MMLU-Pro | 204.82 | 134.86 | 34.2% [tab_1] |
| Olmo-3-7B | OpenThoughts-1k | 272.58 | 199.13 | 27.0% [tab_1] |
| Olmo-3-7B | TriviaQA | 160.56 | 110.84 | 31.0% [tab_1] |
| Mistral-7B | Count | 263.15 | 135.09 | 48.7% [tab_1] |
| Mistral-7B | Countdown | 265.12 | 35.92 | 86.5% [tab_1] |
| Mistral-7B | GSM8K | 84.81 | 74.92 | 11.7% [tab_1] |
| Mistral-7B | MATH | 174.71 | 132.28 | 24.3% [tab_1] |
| Mistral-7B | MMLU-Pro | 196.16 | 131.51 | 33.0% [tab_1] |
| Mistral-7B | OpenThoughts-1k | 195.77 | 165.36 | 15.5% [tab_1] |
| Mistral-7B | TriviaQA | — | — | omitted, compute limits [tab_1] |

## The Math {#the-math}

Table 1's own numbers carry the quantitative content here, worked through three regimes: synthetic near-determinism, a natural-language floor, and the typical natural-language case [tab_1].

**Countdown boundary case:** T is a deterministic function of the prompt — the announced target and available numbers — so a linear probe reading the final hidden state can in principle recover it exactly. Llama's Countdown MAE of 5.27 against a 150.18 baseline, a 96.5% reduction, is empirical confirmation of that ceiling [§sec_4_1] [tab_1].

**Natural-language floor:** No natural-language dataset approaches Countdown's reduction. Llama's weakest case, TriviaQA, drops MAE from 57.86 to 44.20 tokens, a 23.6% reduction. Response length there depends on decoding choices the prompt does not fully fix, so the error floor stays well above zero [§sec_4_1] [tab_1].

**Typical natural-language case:** Most natural-language cells fall between these two extremes, at roughly half to three-quarters of the baseline. Llama's MATH cell moves from 166.32 to 115.29 MAE, a 30.7% reduction — squarely in that middle band [§sec_4_1] [tab_1].

**Cross-model consistency:** The same three-band pattern — near-total Countdown reduction, a nonzero natural-language floor, and 25–45% typical natural-language reduction — recurs for Olmo-3-7B and Mistral-7B, so the effect tracks the completion-length signal itself rather than one model's fit [tab_1].

## Go Deeper {#go-deeper}

No external resources were curated for this concept. Within the paper itself, the Appendix extends Table 1's summary with the full spread of (model, dataset) MAE values, useful if you want every cell rather than the headline pattern described here [§sec_4_1].

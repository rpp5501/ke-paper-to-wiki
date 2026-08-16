# Prompt Templates

## TL;DR {#tldr}

Every dataset feeds the base model through the same pipeline: a fixed, dataset-specific system prompt plus a user message, formatted with the model's own chat template [§sec_8_5].

The user-message body itself comes from one of two sources: a synthetic template for Count and Countdown, or a HuggingFace dataset column for the natural-language sets.

## Intuition {#intuition}

Think of the prompt template as an experimental control. The paper wants to show that a model's own generation process encodes how much output is left — not that clever prompt engineering produces that signal.

So every input is built the same mechanical way: system prompt, then user message, then the model's native chat template. Nothing is rephrased, nothing is added.

## Mechanics {#mechanics}

Each input has two parts: a fixed system prompt and a user message. Both are dataset-specific, and both pass through the model's own chat-template formatting before reaching the model [§sec_8_5].

The paper does not preprocess or rephrase any prompt beyond this formatting step. Whatever wording a dataset supplies is what the model sees, verbatim [§sec_8_5].

The system prompt is fixed per dataset: the paper's table reproduces one system prompt for every dataset used in the paper [§sec_8_5].

The user-message body has two possible origins, depending on the dataset:

| Dataset type | User-message source | Note |
|---|---|---|
| Count, Countdown | Synthetic template | Template text is already given verbatim earlier in the paper [§sec_8_5] |
| Natural-language sets | HuggingFace dataset column | Body text comes directly from the dataset, unmodified [§sec_8_5] |

The exact prompts and templates are preserved in the paper's released repository, not only summarized in the table [§sec_8_5].

## The Math {#the-math}

Consider what breaks if prompt wording varied freely per model instead of being fixed per dataset. A differently-worded prompt could change output length for reasons unrelated to the model's internal length signal — the wording itself would explain the variation, not remaining-length tracking [§sec_8_5].

Fixing the system prompt and applying only the native chat template removes that confound. Any length signal the paper measures then must come from what the model tracks internally, not from prompt engineering [§sec_8_5].

The two user-message sources are a boundary case worth checking. Count and Countdown pull from a synthetic template the authors wrote; the natural-language sets pull from an external HuggingFace column the authors did not write [§sec_8_5].

That difference in origin does not reopen the confound, because the chat-template formatting step is identical either way. What varies across datasets is the reference content itself, which is exactly the variable the experiment needs to vary [§sec_8_5].

Take Count as a concrete case: a synthetic prompt fixes both the task and its expected output length in the template text itself. A HuggingFace row for a natural-language dataset instead brings whatever length its source text happens to have, uncontrolled by the authors [§sec_8_5].

## Go Deeper {#go-deeper}

No external resource links were supplied for this concept. The most useful next step is the paper's own released repository, where the exact system prompts, synthetic templates, and dataset-column mappings are preserved beyond what the summary table shows [§sec_8_5].

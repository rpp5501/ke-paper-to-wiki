# Conclusion
## TL;DR {#tldr}
The residual stream linearly encodes an internal estimate of remaining output length, and three properties argue this is a genuine internal plan rather than a decoding artifact: it exists before generation starts, it transfers across length distributions in one direction only, and it updates when the model retracts and restarts [§sec_7].

## Intuition {#intuition}
Imagine committing to a rough page count before writing a single sentence — that's what the model does with its own response before generating the first token [§sec_7].

The evidence for this being a real plan rather than a side effect of predicting the next token comes from how the estimate behaves when it's tested outside comfortable conditions: on new kinds of text, and mid-generation when the model changes its mind [§sec_7].

## Mechanics {#mechanics}
**Decodable before generation begins:** the probe reads an estimate of remaining length directly from the prompt's last hidden state, before any tokens have been generated. The model has already committed to an approximate response length prior to emitting output [§sec_7].

**Transfer rules out pure memorization — one direction works:** a probe trained on natural-language datasets and tested on datasets with markedly different length distributions still predicts remaining length accurately. If the probe had simply memorized each dataset's marginal length distribution, it would fail on an unfamiliar one [§sec_7].

**The converse direction fails, and that asymmetry is informative:** a probe trained on synthetic data does not transfer to natural language. Training on natural language forces the probe onto a more general length-tracking direction that synthetic data alone doesn't demand, explaining why only one direction transfers [§sec_7].

**Retraction updates the estimate:** on curated examples where the model discards a partial solution and restarts, the probe's predicted remaining length shifts upward at the moment of retraction [§sec_7].

**Why this rules out a position-only predictor:** if the probe merely tracked token position — remaining length as a fixed countdown from a predetermined total — retraction would leave its prediction unchanged, since position alone does not know the plan has changed [§sec_7].

An upward shift right when the model restarts is only possible if the estimate depends on the model's current intent to keep generating, not on position by itself; that dependency is what makes result (iii) qualitative evidence for a plan-like signal [§sec_7].

**Scope of the retraction evidence:** result (iii) is drawn from curated examples, not an aggregate analysis across many retractions; the paper flags an aggregate retraction study as the natural follow-up work [§sec_7].

That follow-up aggregate analysis is also the paper's suggested entry point for the safety and capabilities applications it sketches elsewhere — using the estimate to detect or intervene on generation before it completes [§sec_7].

## The Math {#the-math}
**The counterfactual that separates a plan from a countdown:** consider a position-only predictor — one that infers remaining length purely from token index t and the (unknown but fixed) total length L, i.e. predicts L − t. Under this model, remaining length is a deterministic function of position alone, so it cannot change unless t changes [§sec_7].

Retraction is precisely a case where the model discards work and restarts without position resetting — t keeps advancing, but the actual number of tokens left to produce increases, since the model must now regenerate what it discarded. A position-only predictor's output would be flat or still decreasing across that event, because it only sees t [§sec_7].

The probe instead moves upward exactly at retraction. That single data point is enough to separate the two hypotheses by construction: any predictor whose output is a function of t alone cannot produce an upward jump when t itself is monotonically increasing, so the observed shift requires the estimate to depend on something beyond position — the model's current plan for what remains to be generated [§sec_7].

## Go Deeper {#go-deeper}
- [Future Lens: Anticipating Subsequent Tokens from a Single Hidden State](https://arxiv.org/abs/2311.04897) — the closest verified related work: shows a single hidden state linearly encodes information about several future tokens, the same style of claim made here about remaining length [S1].
- [But what is a GPT? Visual introduction to transformers | Chapter 5, Deep Learning](https://www.youtube.com/watch?v=wjZofJX0v4M) — a visual walkthrough of the residual stream itself, the additive vector every layer reads from and writes to, which is the substrate any remaining-length estimate would live in [S2].

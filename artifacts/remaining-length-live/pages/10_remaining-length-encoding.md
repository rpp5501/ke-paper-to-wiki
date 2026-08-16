# LLMs Linearly Encode Remaining Output Length

## TL;DR {#tldr}
A linear probe on an LLM's residual stream recovers how many tokens are left before the model stops generating [S1]. The estimate is present before the first generated token, transfers across datasets in one direction, and shifts upward when the model catches itself mid-error and restarts [§sec_7].

## Intuition {#intuition}
Mechanistic interpretability work keeps finding that high-level, scalar quantities are linearly decodable from a model's intermediate activations, which is why a linear probe is the default first tool for a question like "does the model track its own remaining length" [S4].

"Remaining output length" is a plausible candidate for such a direction: it is a single number, it changes in a structured way as generation proceeds, and the model needs some internal signal to know when to stop.

The residual stream is the substrate this kind of direction would live in. Architecturally, it is a shared additive channel: every layer reads the running sum of everything written so far and adds its own contribution back in [S2].

A persistent scalar like "tokens left" is exactly the kind of quantity that channel can carry and update layer over layer, rather than something computed fresh and discarded at each step [S2][S3].

## Mechanics {#mechanics}
The paper's conclusion frames the finding as three properties of the recovered estimate, chosen because together they argue for a plan-like representation rather than a byproduct of decoding [§sec_7]:

- **Decodable before generation starts:** the estimate can be read off the prompt's last hidden state alone, before the model emits a single token of its response — it has committed to an approximate length in advance [§sec_7].
- **Transfers asymmetrically across datasets:** a probe direction fit on natural-language data predicts well on synthetic data with a very different length distribution, but a direction fit on synthetic data does not transfer back to natural language [§sec_7].
- **Updates directionally on retraction:** on curated examples where the model abandons a partial solution and restarts, the probe's predicted remaining length shifts upward at that moment [§sec_7].

Each property rules out a simpler account of what the probe is reading. Decodability from the prompt alone rules out a signal that is only computed once tokens exist to count. The retraction result is the sharpest of the three, since it is the only one that a position-based predictor cannot produce even in principle [§sec_7].

| Candidate account | Survives the three properties? |
|---|---|
| Position-only predictor (a function of token index alone) | No — token index only increases, so it cannot explain an upward jump at retraction [§sec_7]. |
| Memorized marginal (the dataset's typical length, not this response's) | Weakened — a direction fit to one dataset's marginal has no reason to predict a differently-shaped dataset, yet natural→synthetic transfer holds [S1]. |
| Plan-like internal estimate (tracks the actual remaining content) | Consistent with all three properties [§sec_7]. |

This is why the paper is careful to call result (iii) qualitative rather than aggregate: it is demonstrated on curated retraction examples, not measured across a dataset, and the paper flags the aggregate version as unfinished work [§sec_7].

## The Math {#the-math}
Take the retraction property and make it precise. Token index t increases by exactly one at every generation step, with no exceptions — that holds by construction, regardless of what the model is saying [§sec_7].

A position-only predictor is any function of t alone that has been fit to predict remaining length. Because more tokens generated means, on average, fewer tokens remain, such a function must be non-increasing in t [§sec_7].

At a retraction, t still increases by one — the retraction token is itself generated — so a position-only predictor's output can only fall or hold steady. The probe's actual output rises at exactly that token, which a non-increasing function of t cannot do. That single observation rules the account out [§sec_7].

The transfer asymmetry isolates a different rival: a probe that has memorized one dataset's typical length rather than tracking the response in front of it. Natural-language response lengths span a wide, multimodal range across tasks; fitting a direction against that range gives the fit little room to lean on any one narrow regularity [S1].

A direction recovered from a narrow synthetic distribution faces no such pressure — it can fit the marginal and still score well on held-out synthetic examples. That direction is the one that fails to transfer back to natural language, which is the asymmetry the paper reports and the memorized-marginal account alone does not explain [§sec_7].

## Go Deeper {#go-deeper}
- [How Much is Left? LLMs Linearly Encode Their Remaining Output Length](https://arxiv.org/abs/2607.05316v1) — the primary source; read this first for the actual probe and causal-intervention results behind every claim on this page.
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — a visual walkthrough of the residual stream as the additive pathway every layer reads from and writes to, the substrate the "remaining length" direction lives in.
- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html) — the canonical diagram-heavy account of why the residual stream behaves as a shared channel that a global linear direction can persist in and accumulate across layers.

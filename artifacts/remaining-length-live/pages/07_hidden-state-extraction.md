# Hidden State Extraction

## TL;DR {#tldr}
- For every token position in a (prompt, completion) sequence, extract the residual-stream vector $h_t^{(\ell)} \in \mathbb{R}^d$ at every layer $\ell \in \{0, \dots, L\}$, via one forward pass with $M$'s parameters frozen [§sec_3_2].
- Probe training loss is masked to completion positions only, with one documented exception for a probe that also needs the prompt's last position [§sec_3_2].

## Intuition {#intuition}
The residual stream is the transformer's single read/write channel: every attention and MLP sublayer reads from it and writes back into it, so a token's hidden state at a given layer is the running sum of everything the model has computed about that position so far [S1].

Extracting $h_t^{(\ell)}$ is not a special computation — it is reading a value the forward pass already produces at every position and layer, before any probe ever touches it [§sec_3_2].

Jay Alammar's illustrated walkthroughs make this per-position, per-layer vector concrete, drawing it as it flows up through the stack one layer at a time [S2].

## Mechanics {#mechanics}
One forward pass over the full (prompt, completion) sequence, with $M$'s parameters frozen, produces $h_t^{(\ell)}$ for every position $t$ and every layer $\ell \in \{0, \dots, L\}$; extraction reads these values off rather than running any extra computation [§sec_3_2].

**Why prompt positions are extracted at all.** Prompt positions receive no probe loss, yet they are kept because later completion tokens attend back to prompt-position keys and values — a prompt token's residual state already encodes how the model represents that context before generation starts [S1][S2].

```algorithm
title: Hidden state extraction procedure
lines:
  - code: "for t in range(len(prompt_ids) + len(completion_ids)):"
    intent: "The forward pass computes a representation at every position in the full (prompt, completion) sequence, not only the completion [§sec_3_2]"
  - code: "    for l in range(L + 1):"
    intent: "Every layer's residual-stream state is available at each position because the residual stream carries forward everything written by earlier layers [S1]"
  - code: "        h[t][l] = cache(M, prompt_ids + completion_ids)[t][l]"
    intent: "A single forward pass with M's parameters frozen yields all of these vectors at once; extraction reads them off rather than recomputing anything [§sec_3_2]"
  - code: "loss_mask = [t >= len(prompt_ids) for t in positions]"
    intent: "Probes are trained on completion positions only, so prompt positions are excluded from the loss by default [§sec_3_2]"
  - code: "loss_mask[len(prompt_ids) - 1] = True  # Completion Length Probe only"
    intent: "The one documented exception adds back the prompt's last position, where the Completion Length Probe must already estimate completion length [§sec_3_2]"
```

**The masking rule.** Probes are trained on completion positions only — prompt positions contribute no loss during training, since the goal is to predict properties of the completion that has not yet been generated [§sec_3_2].

**Its one exception.** The Completion Length Probe departs from this: its loss is masked everywhere except at the prompt's last position, because that is precisely where the model must estimate completion length before any completion token exists [§sec_3_2].

## The Math {#the-math}
**Sizing the extraction.** Take a sequence with prompt length $P$ and completion length $C$, so $T = P + C$ positions total, run through a model with $L+1$ layers and hidden size $d$. The full cache is a rank-3 tensor of shape $(T, L+1, d)$: one $d$-dimensional vector per position per layer [§sec_3_2].

- Total hidden states extracted: $T \times (L+1)$ [§sec_3_2]
- Hidden states carrying the standard probe loss: $C \times (L+1)$, since training is restricted to completion positions [§sec_3_2]
- Hidden states added by the one exception: $1$, at prompt position $P-1$, used only by the Completion Length Probe [§sec_3_2]

**Why the boundary position matters.** Position $P-1$ is the last prompt token — the one point where the model has seen the entire context but has not yet emitted a single completion token, making it the only place a length estimate is not confounded by partial completion evidence [§sec_3_2][S1].

## Go Deeper {#go-deeper}
- [The Illustrated GPT-2](https://jalammar.github.io/illustrated-gpt2/) — diagrams the per-position, per-layer hidden-state vector flowing through the stack, making token-by-token extraction concrete before you touch code.
- [A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html) — establishes the residual stream as the shared read/write bus every hidden state is built from, explaining why prompt-position states carry meaningful information.
- [TransformerLens](https://github.com/TransformerLensOrg/TransformerLens) — the standard library for extracting residual-stream activations at every position in one call, exactly the extraction this concept describes.

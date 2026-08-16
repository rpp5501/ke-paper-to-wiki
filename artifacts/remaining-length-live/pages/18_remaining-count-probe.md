I'll write the concept page for "Remaining Count Probe" following the write-paper-tutor contract, using only the supplied section and equation evidence.

```markdown
# Remaining Count Probe

## TL;DR {#tldr}
The remaining count probe is a single linear layer that reads the number of tokens left in a generation, $r_t = T - t$, straight off the residual-stream activation $h_t^{(\ell)}$ at every completion position. Because it has no nonlinearity, strong accuracy is evidence that "how much is left" is already linearly encoded in the hidden state, not computed by the probe.

## Intuition {#intuition}
Treat the probe as a stethoscope, not a calculator: it listens to one activation vector and reports a number, with no hidden layer to do arithmetic of its own. If it still tracks the countdown accurately, the arithmetic already happened inside the model before the probe ever saw it.

The paper checks that claim against two deliberately weaker readers of the same signal. One just repeats the median remaining length from training, ignoring the activation entirely. The other looks at the hidden state exactly once, at the end of the prompt, guesses the total length $T$, and then counts down mechanically — never consulting the residual stream again during generation. The linear probe earns its interpretive weight only by beating both.

## Mechanics {#mechanics}
The probe $f_\theta: \mathbb{R}^d \to \mathbb{R}$ is restricted to a single linear layer on purpose: keeping its capacity minimal means any predictive success has to come from information already present in $h_t^{(\ell)}$, rather than from computation the probe performs on top of it [§sec_3_3].

At every completion position it regresses the same target, $r_t = T - t$, against the loss $\mathcal{L}_{\text{count}} = (\hat{r}_t - r_t)^2$, so the probe is trained and scored position by position rather than once per sequence [§sec_3_3].

Because $\hat{r}_t$ is a function of $h_t^{(\ell)}$ rather than of $t$ directly, nothing forces the probe's predictions to decrease monotonically as generation proceeds — a freedom the paper exploits elsewhere in its analysis [§sec_3_3].

All three predictors in the family — the full probe, the constant baseline, and the prompt-only baseline — share a single LM forward pass per minibatch and a single dataloader, so any gap between them is attributable to the target each one is trained on, not to sampling variance [§sec_3_3].

| Predictor | Reads | Target | Computed at | |
|---|---|---|---|---|
| Remaining count probe | $h_t^{(\ell)}$, every position | $r_t = T - t$ | every completion position | [§sec_3_3] |
| Constant baseline | nothing (train-split statistic) | median $\tilde r$ of $r_t$, optimal under $L^1$ | every position | [§sec_3_3] |
| Prompt-only probe | last hidden state, prompt end only | $T$ (via $\hat T_0$), then countdown | prompt end, reused by formula | [§sec_3_3] |

## The Math {#the-math}
The target itself is an identity, $r_t = T - t$: whatever total length $T$ the sequence turns out to have, the number of tokens still owed at position $t$ is just the gap between them [§sec_3_3]. For a four-token completion occupying positions $T-3, T-2, T-1, T$, this gives targets $3, 2, 1, 0$ — the probe must report exactly three tokens remaining right after the first output token, then two, then one, then zero at the last [§sec_3_3].

The prompt-only baseline is scored differently, at a single position rather than across the whole completion:

$$\mathcal{L}_{\text{prompt-only}} = \bigl(\hat{T} - T\bigr)^2 \quad \text{evaluated only at } t = \text{prompt\_length} - 1,$$
[eq_2]

and its downstream predictions are then generated deterministically, without touching $h_t$ again:

```annotated-eq
latex: "\\hat{r}_t = \\max(\\hat{T}_0 - t - 1,\\, 0)"
terms:
  - tex: "\\hat{T}_0"
    role: 1
    words: "The prompt-end estimate of total length, computed once from the last hidden state and frozen for the rest of generation [§sec_3_3]"
  - tex: "t"
    role: 2
    words: "The absolute position counter, advancing by one each generated token regardless of content [§sec_3_3]"
  - tex: "\\max(\\cdot,\\, 0)"
    role: 3
    words: "Floors the countdown at zero so the estimate cannot go negative once generation should already have ended [§sec_3_3]"
```

This structure has a sharp failure mode the full probe does not share. Suppose $\hat{T}_0$ overestimates $T$ by $\delta = 2$. Since the countdown only ever consumes $\hat{T}_0$ and $t$, every downstream prediction inherits that same $+2$ offset until the floor at zero absorbs it — the countdown has no way to learn from $h_t$ that its one-time guess was wrong. The remaining count probe recomputes $\hat{r}_t$ fresh from $h_t^{(\ell)}$ at each position, so nothing forces its error to stay constant across positions the way the countdown's does [§sec_3_3].

## Go Deeper {#go-deeper}
No research-note resources are attached to this concept.

Within the paper itself, two pointers follow directly from this definition:
- The Results concept reports how well this probe, against the constant and prompt-only baselines, actually performs — read it once the three-way comparison above is clear.
- Cross-Dataset Generalization builds on this same probe definition, asking whether a linear map fit on one dataset's activations still recovers $r_t$ on another.
- The paper also reports a complementary family of $K$-way classification probes as an ablation in its appendix, for readers who want the discretized counterpart of this regression setup [§sec_3_3].
```

That completes the page. One thing to flag: the evidence mentions a Figure illustrating the four-token completion example, but no `[fig_N]` id was supplied for it, so per the contract I described the example directly in prose/math rather than citing a figure block — let me know if you have the figure id and I'll add a `figure` block.

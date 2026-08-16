# Probe Family
## TL;DR {#tldr}

Three regression probes compete to predict how many tokens remain in a completion, all sharing the same minimal-capacity linear form. The remaining-count probe reads the answer fresh at every position; the median baseline never looks at the hidden state; the prompt-only probe reads $T$ once and counts down deterministically. A classification variant is reported separately as an appendix ablation.

## Intuition {#intuition}

**A probe here is a single linear layer, with no nonlinearity.** It is the simplest possible map from a hidden vector to a predicted number.

That minimalism is the point: a probe with more capacity, like a multi-layer network, could learn to solve the task itself, using its own hidden layers as extra computation.

If a linear map can still pull out the remaining-length signal, that signal must already live in the residual stream in an easily accessible form — not one the probe had to construct.

The three predictors in this family differ only in what they are allowed to see, not in their shape: all are single linear layers, trained together in the same forward pass on the same dataloader.

The remaining-count probe looks at the hidden state at every position. The median baseline looks at nothing. The prompt-only probe looks once, at the prompt's last hidden state, then counts down without touching the hidden state again.

## Mechanics {#mechanics}

**The remaining-count probe regresses on the hidden state at every position.** It maps $h_t^{(\ell)}$ to a predicted count $\hat{r}_t$, trained with squared-error loss against the true remaining length $r_t = T - t$ [§sec_3_3].

**Because it conditions on $h_t^{(\ell)}$ rather than on $t$ itself, this probe is not forced to be monotonic in position.** The paper flags this as a freedom it later exploits [§sec_3_3].

**The median baseline never touches the hidden state.** It always outputs $\widetilde{r}$, the median of $r_t$ over the training split — the optimal constant predictor under $L^1$ loss, and the paper's natural reference point for mean absolute error [§sec_3_3].

**The prompt-only probe is trained on a single position: the prompt's last hidden state, with target $T$.** Its loss is masked everywhere else, so it never sees a completion-position hidden state during training [§sec_3_3] [eq_2].

**At evaluation, the prompt-only probe's one prediction, $\hat{T}_0$, is reused at every completion step through a deterministic countdown.** This gives it the same position-dependent shape as a naive length-minus-position baseline, but substitutes the model's own estimate of $T$ for the true length [§sec_3_3].

**The prompt-only probe's headline number is the prompt-end absolute error, $\text{prompt\_AE} = |\hat{T}_0 - T|$, measured before any countdown steps are taken** [§sec_3_3].

**All three regression probes share a single LM forward pass per minibatch and a single dataloader.** That shared pipeline means any gap between them in evaluation is attributable to what each target asks the probe to predict, not to sampling variance [§sec_3_3].

**A separate classification variant of this family, mapping hidden states to discrete length bins instead of continuous counts, is reported only as an appendix ablation** [§sec_3_3].

## The Math {#the-math}

**The prompt-only probe is trained with squared error at exactly one position: the last prompt token, $t = \text{prompt\_length} - 1$** [§sec_3_3].

$$
\mathcal{L}_{\text{prompt-only}} = \bigl(\hat{T} - T\bigr)^2 \quad \text{evaluated only at } t = \text{prompt\_length} - 1,
$$
[eq_2]

```annotated-eq
latex: "\\mathcal{L}_{\\text{prompt-only}} = \\bigl(\\hat{T} - T\\bigr)^2 \\quad \\text{evaluated only at } t = \\text{prompt\\_length} - 1"
terms:
  - tex: "\\hat{T}"
    role: 1
    words: "The probe's one-shot prediction of total completion length, read from the prompt's last hidden state [§sec_3_3]"
  - tex: "T"
    role: 2
    words: "The true completion length, the regression target [§sec_3_3]"
  - tex: "t = \\text{prompt\\_length} - 1"
    role: 3
    words: "The single position where this loss is evaluated — the last prompt token, never a completion position [§sec_3_3]"
```

**Restricting training to one position forces the probe to compress its whole estimate of $T$ into that single hidden state — it gets no other chance to learn the target** [§sec_3_3].

**Worked example, matching the paper's four-token illustration: suppose the true completion length is $T = 4$ and the prompt-only probe's single estimate is $\hat{T}_0 = 5$, one token too high** [§sec_3_3].

**The countdown then produces $\hat{r}_t = \max(\hat{T}_0 - t - 1, 0)$ at each completion step $t = 0,1,2,3$: $4, 3, 2, 1$ — off by exactly one at every position, since the initial error carries forward uncorrected** [§sec_3_3].

**Contrast this with the remaining-count probe, which re-reads $h_t^{(\ell)}$ at every step: a one-token initial error there need not propagate, because each prediction is a fresh readout rather than an extrapolation from position 0** [§sec_3_3].

**The median is optimal under $L^1$ loss because it minimizes the sum of absolute deviations — any predictor that shifts away from the median increases the total absolute error, a standard property of medians** [§sec_3_3].

## Go Deeper {#go-deeper}

- [Designing and Interpreting Probes with Control Tasks](https://arxiv.org/abs/1909.03368) — explains, via the selectivity metric, why probe capacity must be kept minimal so a probe's success reflects the representation rather than the probe's own learning.
- [Understanding intermediate layers using linear classifier probes](https://arxiv.org/abs/1610.01644) — the original paper defining probes as linear layers, and the case for minimal capacity as a way to read out information already present.
- [A Structural Probe for Finding Syntax in Word Representations](https://nlp.stanford.edu/~johnhew/structural-probe.html) — a worked linear regression probe, with the iconic diagram of a parse tree recovered purely from embedding-space distances.
- [Probing Classifiers: Promises, Shortcomings, and Advances](https://arxiv.org/abs/2102.12452) — a survey placing the linear-vs-nonlinear and classification-vs-regression choices within the broader probing design space.

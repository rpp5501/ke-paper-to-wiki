# Problem Formulation

## TL;DR {#tldr}

- The paper asks whether a frozen LM's hidden state at position $t$ already encodes how many tokens remain until the completion ends, $r_t = T - t$ [eq_1].
- Testing this means training a lightweight probe on frozen hidden states and comparing it against reference predictors that see only $t$, never the hidden state itself [§sec_3_1].

## Intuition {#intuition}

Picture the model mid-sentence, generating token by token. Nothing in its output says "3 tokens left" — it just predicts the next token. The paper's question is whether that information is there anyway, hidden inside the hidden state the model already computes, waiting to be read out [§sec_3_1].

A probe is a small classifier trained on top of that frozen hidden state, the same recipe used across interpretability work to test what a fixed encoder secretly represents [S3]. If the probe predicts remaining length well, that information was already there before the probe existed — the model just wasn't asked to report it.

## Mechanics {#mechanics}

**The generation setup:** $M$ is a frozen autoregressive Transformer LM — its weights are never updated, and it is used only to produce hidden states as it processes the prompt $x$ and completion $y$ [S1]. Generation stops when the model emits an end-of-sequence token at position $T$, or when a maximum-length cutoff is hit [§sec_3_1].

Only naturally terminated sequences — those ending in EOS rather than a cutoff — are used for training and evaluation [§sec_3_1]. A cutoff-truncated sequence has no true $T$: the model was stopped, not finished, so "remaining length" would be undefined for it.

**The target:** for each completion position $t \in \{1, \ldots, T\}$, the label is the remaining token count $r_t = T - t$ [eq_1]. It's a property of the completion's structure, not its content — the label never depends on which tokens were actually generated, only on how many are left [§sec_3_1].

**The probe family:** the empirical question is whether the hidden state $h_t^{(\ell)}$ at layer $\ell$ and position $t$ contains enough information to predict $r_t$ [§sec_3_1]. A probe is a lightweight classifier trained on top of these frozen hidden states [S3].

This mirrors the general probing-classifier paradigm, where a fixed encoder's representations are diagnosed by a shallow supervised model trained on top of them while the encoder's own parameters stay untouched [S3]. The probe is compared against two reference predictors that use no information from the residual stream, only the position $t$ itself [§sec_3_1].

The premise that a single hidden state already encodes information about tokens beyond the immediate next one is the same premise behind reading out predictions at intermediate layers, as in the logit-lens technique, which applies the model's own unembedding matrix to hidden states from any layer to see what the model already "knows" early [S2].

## The Math {#the-math}

$$
r_t = T - t \quad \text{(remaining token count)}
$$
[eq_1]

```annotated-eq
latex: "r_t = T - t"
terms:
  - tex: "r_t"
    role: 1
    words: "The probe's target at position t — a count, not a token or a distribution [eq_1]"
  - tex: "T"
    role: 2
    words: "The completion's total length, fixed only once an EOS token is actually emitted [§sec_3_1]"
  - tex: "t"
    role: 3
    words: "The current completion position — known to the model without any probe, since it is just a counter [§sec_3_1]"
```

The target is exactly the countdown to the end of the sequence [eq_1]. Two boundary values pin it down. At the very first completion token, $t=1$, so $r_t = T-1$: the full length still to come. At the last completion token, $t=T$, so $r_t=0$: nothing remains, and the next token is EOS.

This means $r_t$ is a deterministic function of $t$ and $T$ alone — it carries no information about token identity or content, only about position within a completion whose final length is already fixed once generation stops [eq_1]. A probe that recovers $r_t$ from $h_t^{(\ell)}$ is therefore recovering length information the model computed for itself, not information supplied externally.

## Go Deeper {#go-deeper}

- [The Illustrated GPT-2 (Visualizing Transformer Language Models)](https://jalammar.github.io/illustrated-gpt2/) — start here for what a "hidden state at a token position" actually is inside a frozen autoregressive $M$, with diagrams of the forward pass the probe taps into.
- [interpreting GPT: the logit lens](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens) — the canonical demonstration that a frozen model's intermediate hidden states already carry decodable information beyond the immediate next token, the same intuition behind training a probe on those states.
- [Probing Classifiers: Promises, Shortcomings, and Advances (Belinkov, 2022)](https://aclanthology.org/2022.cl-1.7/) — the formal definition of the probing-classifier paradigm (frozen encoder + auxiliary classifier trained on its representations) that this problem formulation instantiates.

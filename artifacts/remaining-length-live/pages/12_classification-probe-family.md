# Classification Probe Family
## TL;DR {#tldr}

A second probe family turns "how many tokens are left" into a $K$-way classification problem — coarse (K=2, first vs. second half) up to fine-grained (K=9, which ninth of the output). Cohen's $\kappa$, which corrects for the shrinking chance baseline as $K$ grows, shows the residual stream still carries a meaningful progress signal even at K=9, though it degrades and does so unevenly across tasks.

## Intuition {#intuition}

The regression probes ask "how many tokens are left?" as a number. This family asks a coarser question instead: "which slice of the answer am I in right now?" Slicing more finely (higher K) is a harder question, so accuracy should fall — the interesting result is how gracefully it falls, and where it falls off a cliff.

## Mechanics {#mechanics}

**Setup.** Alongside the regression probes, this family trains $K$-way classifiers ($K \in \{2,3,5,7,9\}$) on the same hidden state $h_t^{(\ell)}$, with class anchors $a_i = i/(K-1)$ spaced evenly over normalized progress $u_t = t/(T-1)$ [§sec_8_8].

At $K=2$ the classifier predicts first vs. second half of the output; at $K=9$ it predicts which ninth, giving a much finer-grained readout of completion progress [§sec_8_8].

Cohen's $\kappa$ corrects for chance agreement, which shrinks as $K$ grows, so it is the metric that lets $\kappa$ values be compared fairly across different class counts [§sec_8_8].

Table 11 reports dataset-wide $\kappa$ for every (model, dataset, $K$) cell [tab_11]:

| Model | Dataset | K=2 | K=3 | K=5 | K=7 | K=9 |
|---|---|---|---|---|---|---|
| Llama-3.1-8B | Count | 0.966 | 0.942 | 0.912 | 0.819 | 0.774 [tab_11] |
| Llama-3.1-8B | Countdown | 0.983 | 0.990 | 0.935 | 0.911 | 0.775 [tab_11] |
| Llama-3.1-8B | GSM8K | 0.838 | 0.804 | 0.693 | 0.553 | 0.463 [tab_11] |
| Llama-3.1-8B | MATH | 0.744 | 0.707 | 0.559 | 0.427 | 0.332 [tab_11] |
| Llama-3.1-8B | MMLU-Pro | 0.744 | 0.677 | 0.516 | 0.385 | 0.300 [tab_11] |
| Llama-3.1-8B | OpenThoughts-1k | 0.766 | 0.697 | 0.545 | 0.420 | 0.332 [tab_11] |
| Llama-3.1-8B | TriviaQA | 0.617 | 0.549 | 0.380 | 0.280 | 0.222 [tab_11] |
| Olmo-3-7B | Count | 0.949 | 0.919 | 0.878 | 0.809 | 0.708 [tab_11] |
| Olmo-3-7B | Countdown | 0.976 | 0.985 | 0.926 | 0.900 | 0.903 [tab_11] |
| Olmo-3-7B | GSM8K | 0.823 | 0.769 | 0.646 | 0.519 | 0.422 [tab_11] |
| Olmo-3-7B | MATH | 0.777 | 0.714 | 0.574 | 0.447 | 0.358 [tab_11] |
| Olmo-3-7B | MMLU-Pro | 0.770 | 0.709 | 0.554 | 0.412 | 0.330 [tab_11] |
| Olmo-3-7B | OpenThoughts-1k | 0.707 | 0.547 | 0.380 | 0.272 | 0.208 [tab_11] |
| Olmo-3-7B | TriviaQA | 0.705 | 0.636 | 0.439 | 0.324 | 0.250 [tab_11] |
| Mistral-7B | Count | 0.951 | 0.919 | 0.863 | 0.786 | 0.672 [tab_11] |
| Mistral-7B | Countdown | 0.990 | 0.976 | 0.946 | 0.927 | 0.863 [tab_11] |
| Mistral-7B | GSM8K | 0.793 | 0.762 | 0.625 | 0.506 | 0.414 [tab_11] |
| Mistral-7B | MATH | 0.723 | 0.697 | 0.548 | 0.407 | 0.315 [tab_11] |
| Mistral-7B | MMLU-Pro | 0.754 | 0.704 | 0.540 | 0.416 | 0.332 [tab_11] |
| Mistral-7B | OpenThoughts-1k | 0.732 | 0.679 | 0.524 | 0.379 | 0.315 [tab_11] |

- **Synthetic tasks degrade least.** On Llama-3.1-8B, Countdown keeps $\kappa=0.775$ at $K=9$, barely below its $K=2$ value of $0.983$, because completion length is fully determined by the prompt [tab_11].
- **Natural-language tasks degrade sharply.** TriviaQA on the same model falls from $\kappa=0.617$ at $K=2$ to $0.222$ at $K=9$, consistent with its short and variable answer lengths [tab_11].
- **The decline is not perfectly monotonic.** Olmo-3-7B's Countdown $\kappa$ rises slightly from $0.900$ at $K=7$ to $0.903$ at $K=9$, the one reversal in an otherwise smooth degradation [tab_11].

## The Math {#the-math}

For $K=5$, the class anchors are $a_i = i/(K-1)$ for $i=0,\dots,4$, giving evenly spaced targets $0, 0.25, 0.5, 0.75, 1$ over normalized progress $u_t$; a token is assigned to whichever interval its true progress falls nearest [§sec_8_8].

Retention from $K=2$ to $K=9$ makes the "smooth degradation" claim concrete: Countdown on Llama-3.1-8B keeps $0.775/0.983 \approx 79\%$ of its coarse-grained $\kappa$, while TriviaQA keeps only $0.222/0.617 \approx 36\%$ — more than double the relative loss [tab_11].

At $K=9$, a classifier guessing uniformly at random scores about $11\%$ raw accuracy yet $\kappa \approx 0$, the same chance baseline as a $K=2$ coin flip at $50\%$ accuracy; this is what makes a $\kappa$ of $0.775$ meaningfully non-trivial rather than an artifact of more classes being harder to guess [§sec_8_8].

## Go Deeper {#go-deeper}

No external resources were supplied for this concept. Table 11 [tab_11] is the primary evidence; for the complementary continuous-output view of the same hidden state, see the regression probes in the parent Probe Family concept.

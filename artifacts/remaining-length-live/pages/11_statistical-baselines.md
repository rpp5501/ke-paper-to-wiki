# Statistical Baselines

## TL;DR {#tldr}
The paper's non-learned reference is a constant predictor: always guess the median of $r_t$ over the training marginal, ignoring the input entirely [§sec_3_4].

Because every reported score is MAE, that constant is optimal only if it is the median, not the mean — so a probe demonstrates learned information about $r_t$ only when its error falls below this median floor [§sec_3_4].

## Intuition {#intuition}
Think of remaining-length prediction as a bet: commit to one number before seeing the prompt, then pay the absolute value of the error.

Squared-error loss rewards betting the mean, since outliers pull the average toward them; absolute-error loss rewards betting the median instead, since it only counts how many examples land above versus below the guess, not how far [S1].

That is why this concept sits as a contrast to both the Probe Family and the Results tiers: it fixes the score a method with zero access to hidden state would earn, so any gap above it is the signal the probe is actually extracting rather than dataset skew [§sec_3_4].

## Mechanics {#mechanics}
**The baseline predictor:** for the true remaining length $r_t$ at each token position, the optimal constant under L1 loss is the median $m$ of $r_t$'s distribution, since $\arg\min_c \mathbb{E}|X-c| = m$ mirrors the familiar mean-minimizes-squared-loss fact but for absolute error [§sec_3_4].

The paper instantiates this as $\hat r_t = \widetilde r$, a single scalar fit once on the train split's marginal distribution of $r_t$ and then applied unchanged to every token and every example, regardless of prompt content [§sec_3_4].

This constant's MAE on the train marginal has a name: it is exactly the Mean Absolute Deviation about the median, the L1 analogue of variance, so the baseline score doubles as a measure of how spread out $r_t$ is in the training data [§sec_3_4].

That equivalence sets the bar precisely: a probe beats the baseline only by extracting information about $r_t$ beyond what any position-independent, input-independent predictor could recover from the label marginal alone [§sec_3_4].

## The Math {#the-math}

```derivation
shape: Why the median, not the mean, minimizes expected absolute error.
steps:
  - latex: "f(c) = \\mathbb{E}|X - c|"
    why: "The L1 risk of a constant predictor c, the quantity the baseline predictor minimizes [§sec_3_4]"
  - latex: "\\partial f(c) = P(X < c) - P(X > c)"
    why: "The subgradient of the absolute-value loss counts how much probability mass sits below c minus how much sits above it [S1]"
  - latex: "P(X < c) = P(X > c) \\implies c = m"
    why: "Setting the subgradient to zero balances the two sides, which is exactly the defining property of the median [S1]"
```

Suppose the train marginal of $r_t$ takes values $\{5, 8, 8, 20, 100\}$: the mean is $28.2$, pulled far right by the outlier at $100$, while the median is $8$ [S1].

Predicting the mean gives an MAE of $\frac{1}{5}(23.2+20.2+20.2+8.2+71.8) = 28.72$; predicting the median gives $\frac{1}{5}(3+0+0+12+92) = 21.4$, confirming the median is the cheaper constant guess under L1 even though it ignores the outlier's magnitude entirely [S1].

This train-marginal MAE at the median is the baseline's Mean Absolute Deviation, so a probe on this same data must clear that number before it can claim any position-specific signal [§sec_3_4].

## Go Deeper {#go-deeper}
- [Median — Optimality property](https://en.wikipedia.org/wiki/Median#Optimality_property) — the direct proof that the median minimizes expected absolute deviation, plus the classic mean/median/mode figure under right skew that gives the visual intuition for why L1 favors the median [S1].
- [A median loss control chart for monitoring quality loss under skewed distributions (2017)](https://doi.org/10.1080/00949655.2017.1362697) — an applied case of the same optimality property, where median-based control limits are chosen over mean-based ones specifically because the median stays the robust L1-optimal center under skewed process data [S2].

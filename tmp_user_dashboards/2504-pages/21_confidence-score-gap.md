# Confidence score gap: the black-box signal that leaks correlation

## TL;DR {#tldr}

The confidence score gap is the difference in a model's confidence when you ask it the same question with different guesses for a hidden attribute, and that gap reveals how strongly the attribute is tied to the answer.

This is the paper's key insight bridging "correlation causes vulnerability" and "an attacker can measure vulnerability without seeing the training data." A model's confidence, when queried with different candidate sensitive-attribute values for the same record, doesn't drift randomly — it shifts by an amount that depends on how imbalanced the sensitive attribute was relative to the output label during training. That shift is directly observable by anyone who can query the model, which is exactly what a realistic black-box adversary can do.

## Intuition {#intuition}

Think about what a model actually learns when marital status is unusually common among high earners in its training data. It doesn't learn "marital status causes income" — it learns a statistical shortcut: when other things line up with the high-income pattern, and marital status is set to "married," predict high income with a bit more confidence, because that's what the training data showed most often.

Now flip that around. If you take a real record, tell the model the person is married, and ask for a prediction, you get one confidence score. Tell it the same record is single, holding everything else fixed, and you get another. The gap between those two confidence scores is a fingerprint of how lopsided married-vs-single was among high earners in training. If married records were only slightly more common among high earners, the model barely notices the difference and the gap is small. If married records were overwhelmingly more common, the model leans hard toward higher confidence for "married," and the gap is large.

This means the confidence score gap is doing something remarkable: it lets an outsider, who has never seen the training data and doesn't know a single true sensitive value, infer how strongly that sensitive value was correlated with the output — for a specific subgroup of records, not just the dataset as a whole. Compute this gap across many groups and you can compare which groups had a stronger sensitive-output relationship during training, purely from how the model reacts to hypothetical queries.

There is one wrinkle worth knowing before trusting a naive version of this idea: a huge fraction of confidence scores across almost every group sit bunched up near the top of the scale (0.95 to 1.0), regardless of correlation. A crude "subtract the confidence distributions" approach gets swamped by that shared high-density region and loses the signal that actually distinguishes high-correlation groups from low-correlation ones. This is precisely the problem that motivates measuring the *angle* between fitted regression lines instead of a raw distributional difference — the tails of the distribution, which the regression line is sensitive to, carry the real information [§sec_4_2].

## Mechanics {#mechanics}

**The setup, made concrete.** Consider a binary sensitive attribute ("yes"/"no") and a binary output ("True"/"False"). If the dataset has strong correlation, the "True" class contains far more "yes" records than "no" records. Training on that imbalance biases the model toward higher confidence for the "True" class when queried with "yes" than with "no," for the same underlying record. A highly imbalanced group produces a large expected confidence gap; a nearly balanced group produces a small one [§sec_4_2].

**The visual evidence.** Plotting confidence scores for records where every sensitive-value query returned the correct label, using hexagon-binned bivariate histograms with univariate margins, produces comet-shaped clouds: a dense head near the top-right (high confidence for both queried values) trailing off into a tail. High Income records' tails slant horizontally, Low Income records' tails slant vertically, and — critically — the *angle* of that slant shifts systematically as group correlation moves from −0.6 (Male group) to −0.5 (White group) to −0.4 (Female group) in the paper's Census19 example [§sec_4_2].

**From gap to measurable proxy.** A raw comparison of confidence-score distributions between groups is unreliable because of the shared high-density cluster near 1.0 mentioned above. The paper's fix is to fit a regression line through each comet-shaped cloud and compare the *angle* between lines for different output labels, rather than comparing the distributions directly — this becomes the angular difference metric [§sec_4_2].

**Generalizing beyond the binary case.** For sensitive attributes with more than two values, the paper fits regression lines in an \(|\mathcal{S}|\)-dimensional space, one axis per possible sensitive value. For multi-class outputs, it fits one line per class label and averages the angular difference over all pairs. For non-discrete sensitive attributes, it follows Mehnaz et al.'s approach of binning the value range and using bin means as substitute discrete values [§sec_4_2].

**Why this survives a data-blind adversary.** Nothing in this measurement requires knowing any record's true sensitive value, and nothing requires an auxiliary dataset — only the ability to query the model with hypothetical sensitive-attribute values and read off confidence scores, which is exactly the black-box capability the paper's threat model assumes [§sec_3].

## The Math {#the-math}

The paper does not give the confidence score gap a standalone closed-form definition — it is introduced descriptively as "the difference in confidence scores generated by querying the same record with different sensitive attribute values" [§sec_4_2], and its formal treatment is folded directly into the angular difference construction rather than kept as a separate scalar. Given a record \(x\) with non-sensitive attributes \(n(x)\), and two sensitive-value variants \(x_i, x_j\) with \(s(x_i) = s_i \neq s_j = s(x_j)\) but identical non-sensitive attributes, the gap for that single pair of queries is simply

$$
g_{ij}(x) \;=\; conf(\mathcal{M}(x_i)) - conf(\mathcal{M}(x_j))
$$

The paper's argument is that the *expected magnitude* of \(g_{ij}\) over a group of records, conditioned on output label, depends on the group's sensitive-output correlation — high correlation produces a large expected gap, low correlation a small one [§sec_4_2]. Rather than aggregating gaps directly (which the high-density region near confidence 1.0 makes unreliable), the paper aggregates the full confidence vectors across the sensitive-value dimensions per record, fits regression lines per output label through that collection, and measures the angle between those lines — this is angular difference, and it is the operational replacement for a direct confidence-score-gap statistic [§sec_5_1].

## Go Deeper {#go-deeper}

- **[§sec_4_2] Comparing Correlation between Groups** — the full argument and the comet-shaped histogram evidence this page is built on.
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — establishes why correlation matters in the first place, which is the premise this page's proxy is measuring.
- **[§sec_5_1] Computing Angular Difference** — where the intuition here becomes the formal, computable angular-difference metric.
- **[§sec_3] Attack Threat Model** — confirms the black-box query capability this signal relies on is within the adversary's assumed reach.
- Related concepts: `angular-difference` for the formal metric this gap motivates, `confidence-score-distribution-histograms` for the visual evidence, and `correlation-drives-vulnerability` for the underlying cause this signal is a proxy for.

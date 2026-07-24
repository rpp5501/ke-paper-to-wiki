# Comet-shaped confidence distributions and their tilting regression lines

## TL;DR {#tldr}

This page describes a figure the paper uses to show that a model's confidence scores, plotted as a shape, visibly tilt by an amount that tracks a group's hidden correlation — no image is rendered here, only the paper's own description.

Figure 3 in the paper plots confidence scores gathered by querying the same record repeatedly, once for each possible value of the sensitive attribute, for groups with three different correlation levels in the Census19 dataset. This page describes what the paper says that plot shows — a comet-shaped cluster of points with a dense head and a tail whose angle shifts systematically with the group's correlation — because the image itself cannot be rendered in this environment. Everything below is drawn from the paper's prose, not from independent visual inspection.

## Intuition {#intuition}

Imagine querying a trained model twice for the same person, once pretending they're married and once pretending they're single, and writing down how confident the model was each time. Do this for many people in a group, and plot each person's "confidence when married" against their "confidence when single" as a single point on a 2D grid. If the group has a strong correlation between marital status and income, the model will have learned to lean hard on marital status when predicting income — so most points cluster tightly near "very confident under the true value, much less confident under the fake one." If the correlation is weak, the model barely relies on marital status at all, so confidence stays close to symmetric between the two queries.

The paper reports that when you actually make this plot, most points bunch up near the corner where both confidences are high (records the model is generally sure about), and a smaller tail of points stretches away from that corner in a direction that depends on which sensitive value the model favored. The overall shape resembles a comet: a dense head, a thinning tail. What matters is not the head — it's crowded and uninformative — but the *direction* the tail points in, because that direction reveals the model's bias toward one sensitive value over another for that group.

The paper fits a regression line through each class label's cloud of points (one line for "High Income" records, one for "Low Income" records) and reports that these two lines are tilted at different angles, and that the gap between those two angles — the angular difference — shrinks visibly as you move from higher-correlation groups to lower-correlation groups. That's the whole payoff of the figure: a purely visual, purely black-box signal that lines up with something the adversary cannot see directly (the group's true correlation).

## Mechanics {#mechanics}

**What the plot actually shows, per the paper's description.** Figure 3 presents bivariate and univariate histograms — hexagon-binned 2D histograms with marginal univariate histograms on the axes — of confidence scores gathered by querying the same record under different sensitive attribute values. Three groups from Census19 are shown, at correlation levels -0.6 (Male group), -0.5 (a "White" group, defined by the RACE attribute), and -0.4 (Female group). Sensitive attribute is marital status (Married/Single); output classes are High Income and Low Income, plotted in different colors [§sec_4_2].

**The comet shape and what the tail direction encodes.** Each class label's distribution forms what the paper calls a comet-like shape: a concentrated head in the top-right (both confidences high — the model agrees on the record's class regardless of which sensitive value it's told) and a tail extending away from that corner. For High Income records, the paper reports the tail slants horizontally, meaning the model is more confident when the sensitive attribute is set to "Married" than "Single" for these records — the model's learned bias toward the majority sensitive value within that class. Low Income records show the mirror pattern: a vertically slanted tail [§sec_4_2].

**Why regression lines rather than raw distribution differences.** The paper explicitly tried the more obvious approach first — directly comparing the confidence-score distributions for different class labels — and reports that this fails, because the high density of points shared in the 0.95–1.0 confidence range across both distributions distorts the comparison. Fitting a regression line to each class's tail points sidesteps this: the line reflects the tail's trajectory, which is the part of the distribution that actually differentiates high- from low-correlation groups, rather than the crowded, uninformative head [§sec_4_2].

**How the angle shift tracks correlation.** Across the three groups shown (correlations -0.6, -0.5, -0.4), the paper reports the regression lines' angle shifting gradually toward the center — meaning the angular gap between the High Income line and the Low Income line narrows — as correlation moves from higher to lower magnitude. This gradual, visible shift across just three groups is the qualitative demonstration that motivates using angular difference as a quantitative proxy for correlation across all groups, not just the three shown here [§sec_4_2].

**Extension beyond the binary case.** For sensitive attributes with more than two possible values, the paper describes fitting regression lines in an n-dimensional space, where n is the number of sensitive attribute values. For outputs with more than two classes, a regression line is fit per class label, and the angular difference is averaged across all pairs of lines [§sec_4_2].

## The Math {#the-math}

This page has no equation of its own — it is the visual, descriptive precursor to the angular difference computation formalized elsewhere. The confidence matrix that the plotted points are drawn from is defined as

$$
C = \left[\, \Pr(\mathcal{M}(x')) : x' \in T(x) \,\right]^T \; \forall\, x \in D
$$

where \(T(x)\) is the set of records generated by varying record \(x\)'s sensitive attribute value across all values in \(S\), and \(\mathcal{M}\) is the target model [§sec_5_1]. The regression lines this page describes are fit to the per-class submatrices of \(C\), and the angular difference — the quantity this figure exists to motivate — is the mean pairwise angle between those lines. Its full definition and computation algorithm live on the `angular-difference` page, not here; this page's job is only to describe what the figure looks like and why it prompted that definition.

## Go Deeper {#go-deeper}

- **[§sec_4_2] Comparing Correlation between Groups** — the source section for this entire page; read the full prose description here, since no rendering of the actual figure is available.
- **[§sec_5_1] Computing Angular Difference** — where the confidence matrix shown conceptually in this figure gets a formal algorithmic definition.
- **[§sec_13_3] Angular Difference Visualization Across States** — a second, related figure (Figure 9) showing the same confidence-matrix concept for three specific Census19 states at correlations 0, -0.25, and -0.5.
- **[§sec_13_2] Correlation vs. Angular Difference** — a follow-up figure (Figure 8) plotting the relationship this figure's regression-line tilts are meant to foreshadow, this time across all 51 states rather than 3.
- Related concepts: `angular-difference` for the metric this figure motivates, `confidence-score-gap` for the underlying quantity being visualized, `disparity-inference-attack` for the attack that turns this into a working ranking.

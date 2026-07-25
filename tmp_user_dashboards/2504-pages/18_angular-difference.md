# Angular difference: a black-box proxy for group-level correlation

## TL;DR {#tldr}

Angular difference turns the tilt of a model's confidence patterns into a number that stands in for the correlation an attacker can never directly measure.

Everything the paper's disparity attacks do downstream — ranking groups, choosing which subset to target — needs a way to compare "how correlated is the sensitive attribute with the output" between groups, without ever seeing the sensitive attribute values or the training data. Angular difference is that measurement. It's computed entirely from confidence scores the model already exposes to a black-box caller: query a group's records under every possible sensitive value, fit a regression line through the confidence scores for each output class, and measure how far apart those lines point. A bigger angle means a stronger group-level correlation, and a stronger group-level correlation means a more vulnerable group.

## Intuition {#intuition}

Picture querying the same record twice — once telling the model the sensitive attribute is "yes," once telling it "no" — and plotting the two confidence scores you get back against each other, for every record with a given true output label. If the sensitive attribute barely matters to that output label in the training data, the two confidence scores you get should be roughly similar no matter which value you claimed, and the cloud of points you get across many records looks scattered in a fairly neutral direction. If the sensitive attribute is strongly tied to that output label, one of the two confidence scores will systematically run higher than the other, and the cloud of points leans hard in one direction.

Now do this separately for records with each output label, and draw a best-fit line through each cloud. If the sensitive attribute barely matters, the two lines — one per output label — point in nearly the same direction. If the sensitive attribute matters a lot, the two lines diverge, because a high correlation makes the model behave in *opposite* ways for the two output labels: it favors one sensitive value for one label and the other sensitive value for the other label. The angle between those two lines is the angular difference, and the paper argues it grows and shrinks in step with the group's true correlation, entirely observable from outside [§sec_4_2].

The reason this measurement beats the more obvious idea — directly comparing the confidence-score distributions between groups — is that a huge share of confidence scores across every group cluster near the top of the range (0.95 to 1), which drowns out the differences a naive comparison would be trying to detect. The tails of the distributions carry the real signal, and a regression line through the whole cloud is dominated by where the tail points, which is precisely the information a raw distributional comparison throws away [§sec_4_2].

## Mechanics {#mechanics}

**Where the numbers come from.** Angular difference is computed from the confidence matrix: for a training subset \(\mathbb{D}\) and model \(\mathcal{M}\), each record is queried once per possible sensitive value, producing a matrix of confidence scores indexed by record and sensitive value [§sec_5_1]. Only records where every one of those queries produced a correct prediction are used — the paper's hypothesis is that for these records, the variation in confidence scores across sensitive values is the cleanest signal of correlation, uncontaminated by the model simply being wrong [§sec_5_1].

**Fitting the lines.** For each output label \(y\), the rows of the confidence matrix belonging to records with that label are collected and a regression line is fit through them, in a space with one dimension per possible sensitive value [§sec_5_1]. For a binary sensitive attribute this is a 2-D scatter and an ordinary regression line; for a multi-valued sensitive attribute with \(|\mathcal{S}|\) possible values, the fit happens in \(|\mathcal{S}|\)-dimensional space [§sec_5_1].

**Taking the angle.** With one regression line per output label, angular difference is the average pairwise angle between all these lines. For a binary-output problem this is just the angle between two lines; for multi-class outputs, it's the average over every pair of the per-class lines [§sec_5_1].

**Why it works as a black-box proxy.** The whole computation needs only queries to the model and knowledge of every possible sensitive value — the same capabilities the paper's threat model already assumes the adversary has, with no auxiliary dataset and no ground-truth sensitive values required anywhere in the pipeline [§sec_3]. The empirical link back to correlation is direct: on the 51-group Census19 sweep, correlation ranging from 0 to −0.5 produces an angular difference that tracks it visibly linearly, which the paper offers as justification for using a linear regression fit in the first place rather than something more elaborate [§sec_13_2].

**Where it plugs in.** Angular difference is the sort key for the disparity inference attack's group ranking [§sec_5_2], and it's the quantity the targeted attacks search over to find the grouping attribute and subset with the widest spread of vulnerability [§sec_5_3_1] [§sec_5_3_2].

## The Math {#the-math}

Given a training subset \(\mathbb{D}\) with \(n\) records, model \(\mathcal{M}\), confidence matrix \(C \in \mathbb{R}^{n \times |\mathcal{S}|}\) generated by querying \(\mathcal{M}\) with every sensitive-value variant of \(\mathcal{N}(\mathbb{D})\), and \(\mathcal{Y}\) the set of output labels, angular difference is defined as the average pairwise angle between regression lines fit per output label:

$$
\begin{aligned}
\Delta_{\angle}(\mathbb{D}) \;=\; \underset{y_1 \neq y_2 \,\in\, \mathcal{Y}}{\text{avg}} \;\; \angle\big(L_{y_1},\, L_{y_2}\big)
\end{aligned}
$$

where \(L_y\) denotes the regression line fitted through the \(|\mathcal{S}|\)-dimensional points of \(C_y\), the submatrix of \(C\) containing rows for records with output label \(y\) [§sec_5_1].

For non-discrete sensitive attributes, the paper bins the value range and substitutes the set of bin means for the discrete sensitive-attribute values, following Mehnaz et al.'s approach, before fitting the same regression lines [§sec_4_2]. This keeps the same angular-difference machinery applicable without requiring the sensitive attribute to be categorical to begin with.

No numeric closed form for \(\angle(L_{y_1}, L_{y_2})\) beyond "the angle between the fitted lines" is given in the paper's main text; the fitting itself is the standard least-squares regression through the points of \(C_y\), and the angle is computed from the resulting line directions [§sec_5_1].

## Go Deeper {#go-deeper}

- **[§sec_5_1] Computing Angular Difference** — the formal definition and the algorithm for building the confidence matrix that feeds it.
- **[§sec_4_2] Comparing Correlation between Groups** — the qualitative argument, with the comet-shaped confidence-score histograms, for why the regression-line angle is a better signal than a raw distributional comparison.
- **[§sec_13_2] Correlation vs. Angular Difference** — the empirical check that angular difference tracks true correlation nearly linearly across the 51 Census19 groups.
- **[§sec_13_3] Angular Difference Visualization Across States** — concrete confidence-matrix plots for three states at low, medium, and high correlation, showing the regression lines directly.
- Related concepts: `confidence-score-gap` for the underlying phenomenon angular difference is measuring, `confidence-matrix` for the object it's computed from, and `disparity-inference-attack` for the first attack built directly on top of it.

# Sampling training sets to a prescribed sensitive-output correlation

## TL;DR {#tldr}

This is the knob the paper turns to build training sets with an exact, chosen correlation between the secret attribute and the output.

Once correlation is identified as the thing that drives vulnerability, the obvious next step is to run controlled experiments over a range of correlation values — but real datasets come with whatever correlation they happen to have. The paper solves this with a sampling technique that picks records from a large pool so that the resulting training set (or a specific group within it) hits a target correlation \(c\) almost exactly, while keeping the number of positive and negative output samples balanced. This is the machine behind nearly every experiment in the paper: the correlation-vs-accuracy plots, the per-group correlation sweeps, and the ranking evaluations all depend on being able to dial correlation up or down on demand.

## Intuition {#intuition}

You cannot study "does correlation cause vulnerability" by finding datasets that happen to have different correlations lying around — there are too many other differences between real datasets to isolate the one variable you care about. What you want is a dial: turn it to −0.9 and get a training set with that correlation, turn it to 0.2 and get another, with everything else about the dataset held as similar as possible.

The paper builds that dial. Given a big pool of records (Census19 and Texas-100X each have on the order of a million), it picks a subset whose sensitive attribute and output land in the right proportions to produce a chosen correlation. Because both quantities here are binary in the simple case — sensitive value is "yes" or "no," output is "True" or "False" — hitting a target correlation reduces to choosing how many records fall into each of the four combinations: yes-and-True, yes-and-False, no-and-True, no-and-False. Get those four counts right and the correlation comes out where you wanted it.

The technique also keeps positive and negative outputs balanced, so that a change in correlation isn't secretly also a change in how skewed the output labels are — otherwise you couldn't tell whether an accuracy change came from correlation or from class imbalance. And because it can be applied to any subset of the data, not just the whole training set, the same tool lets the paper assign *different* correlations to different demographic groups within one dataset, which is exactly what the group-level disparity experiments need [§sec_4_1].

## Mechanics {#mechanics}

**What's being controlled.** Let \(n\) be the number of desired samples (for the full training set or for one group), \(m\) the ratio between negative-sensitive-value and positive-sensitive-value samples, and \(c\) the desired Pearson correlation between the sensitive attribute and the output. The sampler computes four counts — positive-sensitive/positive-output, positive-sensitive/negative-output, negative-sensitive/positive-output, negative-sensitive/negative-output — and draws that many records of each kind from the pool [§sec_6_1].

**Why balance is enforced alongside correlation.** The sampling method is explicitly built to hit the target correlation "while maintaining a balanced number of positive and negative output samples" [§sec_6_1]. For Census19 and Texas-100X, \(m\) is fixed at 1 to match the original dataset's sensitive-attribute distribution, so only the correlation is being swept in most experiments [§sec_6_1].

**Where it's used.** This sampler produces the 19 training sets with varying correlation used to show CSMIA and LOMIA accuracy tracking correlation magnitude [§sec_4_1]; the per-group correlation assignments across Male and Female records used to demonstrate disparity at the group level [§sec_4_1]; the 51-group and 10-group correlation sweeps (Census19 by state, Texas-100X by principal diagnosis code) used to evaluate the disparity inference attack's ranking quality [§sec_6_3]; and the BCorr defense's subsampling step, which reuses the same correlation-targeting logic to pull every group's correlation down to the least-correlated group's level [§sec_7_2].

**The one dataset it's deliberately not used on.** The Adult dataset is run *without* controlled sampling, specifically to check that the paper's findings hold up under a real, uncontrolled correlation rather than only in engineered scenarios [§sec_6_1]. That is the honesty check against over-fitting conclusions to an artificial setup.

## The Math {#the-math}

Pearson's correlation between the sensitive attribute \(s\) and the output \(y\) over \(n\) records is

$$
c \;=\; \frac{n\sum sy - \left(\sum s\right)\left(\sum y\right)}{\sqrt{\left(n\sum s^2 - \left(\sum s\right)^2\right)\left(n\sum y^2 - \left(\sum y\right)^2\right)}}
$$

[eq_4]. For binary \(s, y \in \{0,1\}\), writing \(n_+^+\) for the count of records with positive sensitive value and positive output (and similarly \(n_+^-\), \(n_-^+\), \(n_-^-\)), this reduces to the familiar phi-coefficient form

$$
c \;=\; \frac{n_+^+ \times n_-^- - n_+^- \times n_-^+}{\sqrt{(n_+^+ + n_+^-)(n_+^+ + n_-^+)(n_-^+ + n_-^-)(n_+^- + n_-^-)}}
$$

[eq_5]. The sampler fixes the marginal totals — equal positive and negative outputs, and a sensitive-value split governed by the ratio \(m\) — as

$$
\begin{aligned}
n_+^+ + n_-^+ &= n_+^- + n_-^- = \frac{n}{2} \\
n_+^+ + n_+^- &= \frac{n}{m+1}, \quad n_-^+ + n_-^- = \frac{mn}{m+1}
\end{aligned}
$$

[eq_6]. Substituting these constraints back into the correlation formula and solving isolates the cross term:

$$
n_+^+ \times n_-^- - n_+^- \times n_-^+ \;=\; c\sqrt{m} \times \frac{n}{m+1} \times \frac{n}{2}
$$

[eq_7], and combined with the marginal totals this pins down the difference between the two negative-sensitive-value counts:

$$
n_-^- - n_-^+ \;=\; c\sqrt{m} \times \frac{n}{m+1}
$$

[eq_8]. From here the four counts \(n_+^+, n_+^-, n_-^+, n_-^-\) are each solvable in closed form and then rounded to integers, which is why the sampled correlation is only approximately \(c\) rather than exact — the paper notes the resulting difference is negligible for its purposes [§sec_11_1].

## Go Deeper {#go-deeper}

- **[§sec_11_1] Correctness Proof of Sampling Technique** — the full derivation behind eq_4 through eq_8; read this if you want to verify the sampler actually hits the correlation it claims to.
- **[§sec_6_1] Experimental Setup** — where the sampler is introduced in context, alongside dataset sizes and the decision to leave Adult unsampled.
- **[§sec_4_1] Key Factor Contributing to Vulnerability** — the first place this sampler is put to use, generating the correlation sweep that establishes correlation as the driver of vulnerability.
- **[§sec_7_2] Balanced Correlation Defense (BCorr)** — reuses the same correlation-targeting logic in reverse, to pull every group down to a common, low correlation as a defense.
- Related concepts: `correlation-drives-vulnerability` for why this sampler exists at all, `tabular-benchmark-datasets` for the pools it draws from, and `bcorr-defense` for the sampler's role as a mitigation tool rather than just an experimental one.

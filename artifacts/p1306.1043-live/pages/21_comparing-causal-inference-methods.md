# Comparing Causal Inference Methods
## TL;DR {#tldr}
This experiment asks a sharper question than the earlier SID-versus-SHD comparison: when you evaluate real causal discovery algorithms rather than random perturbations of the true graph, does SID change which method looks best? The answer is yes — an algorithm that wins on SHD can be the worst performer on SID, because the two metrics reward different things. SID rewards getting the causal effects right; SHD rewards getting the edges right.

## Intuition {#intuition}
Four estimators are pitted against a random baseline: PC, conservative PC (CPC), and greedy equivalent search (GES) all return a Markov equivalence class rather than a single DAG, while a fourth method exploits the extra assumption of equal error variances to identify the DAG outright. Because PC-type methods only commit to a skeleton and a partial orientation, their SID score isn't one number but a range — how good or bad the estimate looks depends on which member of the equivalence class you pick. The experiment shows that this range can swing from "close to the truth" down to "no better than guessing," and that ranking algorithms by SHD versus by SID can point in opposite directions.

## Mechanics {#mechanics}
The setup mirrors the earlier simulation: sparse random ground-truth DAGs, data drawn from a linear Gaussian SEM with equal error variances and uniformly chosen coefficients, repeated 100 times per setting. The difference is that instead of hand-perturbing the true DAG, the estimates now come from actual inference algorithms run on the sampled data, and both average SID and average SHD to the true DAG are recorded for comparison [§sec_3_2].

The five estimators differ in what they output and what they assume, which is why they need different treatment before SID can even be computed [§sec_3_2]:

| Method | Output | Assumption exploited | SID reported |
|---|---|---|---|
| ARGES-type method | single DAG | equal error variances → identifiability from the distribution alone | one value [§sec_3_2] |
| PC | CPDAG (equivalence class) | conditional-independence structure only | lower and upper bound [§sec_3_2] |
| CPC | CPDAG, conservative orientation rule | conditional-independence structure only | lower and upper bound [§sec_3_2] |
| GES | CPDAG | score-based search over equivalence classes | lower and upper bound [§sec_3_2] |
| RAND | DAG, ignores the data | none — density parameter drawn as in the earlier simulation | one value [§sec_3_2] |

Because PC, CPC, and GES only commit to a Markov equivalence class, each is scored with the extension from the earlier section that reports the smallest and largest SID achievable by any DAG consistent with the estimated CPDAG — the lower and upper bound rows in the table [§sec_3_2]. The paper's headline finding is that the two metrics disagree on rankings: for some combinations of sample size and sparsity, PC is best under SHD but worst under SID, since SHD and SID are counting fundamentally different kinds of error [§sec_3_2].

## The Math {#the-math}
No new estimator or bound is introduced here — the section instead uses the already-defined lower/upper-bound extension and average SID/SHD to expose a gap between the metrics that a single-number comparison would hide [§sec_3_2]. The key observation is about *where* SHD and SID put their weight, and a small worked case makes it concrete [§sec_3_2].

Take a chain of three variables where the true DAG has one edge reversed by the estimator, so SHD registers exactly one error regardless of which edge it is [§sec_3_2]. SID does not treat all single-edge errors alike: reversing an edge near the root of the chain corrupts the parent set used to compute every downstream intervention distribution, inflating SID by counting every pair whose do-effect is now miscalculated, while reversing a leaf edge affects only that one pair [§sec_3_2]. This is exactly the asymmetry the section reports empirically — the PC algorithm gets skeletons largely right (good SHD) but its orientation errors, when they occur, tend to be exactly the propagating kind that SID penalizes heavily, which is why it can lag behind random guessing on SID while still beating it on SHD [§sec_3_2].

The bound gap also carries information. When the upper bound for PC is no better than the RAND estimator at small sample size while the lower bound is close to the truth, the two numbers together say the correct skeleton has been found but its orientation is essentially unresolved — an average SID alone would blur this into a single mediocre-looking value [§sec_3_2]. The method restricted to equal-error-variance identifiability avoids this ambiguity entirely by outputting one DAG rather than a class, converting the extra distributional assumption directly into a narrower, single-valued SID rather than a bound [§sec_3_2].

## Go Deeper {#go-deeper}
- Builds on **SID versus SHD Simulation** — this section reuses that experiment's DAG-sampling and data-generating setup, and its lower/upper-bound extension for CPDAG-valued estimates, so read it first to know what the bounds mean.
- No research note is attached to this concept; the table and its exact percentages referenced in the text (e.g., how often RAND beats PC's upper bound) live in the paper's Table for Section 3.2 and are worth checking directly for the precise figures.

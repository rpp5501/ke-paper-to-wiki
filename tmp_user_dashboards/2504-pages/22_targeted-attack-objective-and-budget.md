# Targeted attack objective and the attack budget kappa

## TL;DR {#tldr}

The targeted attack's goal is to find the smallest slice of data — sized by a budget kappa — that still beats every larger slice on attack accuracy.

The targeted attribute inference attack reframes attribute inference as a search problem: find a subset of the target dataset that (1) is close to a chosen size, controlled by a budget \(\kappa \in (0, 0.5]\), and (2) achieves a higher attack success rate than every other subset at least as large as it. Because evaluating this directly over every possible subset is computationally intractable, and because the adversary cannot measure attack success rate without the sensitive values it's trying to steal, the search is restricted to subsets defined by non-sensitive attribute values and guided by angular difference as a stand-in for attack success.

## Intuition {#intuition}

An untargeted attribute inference attack throws every record at the model and reports one accuracy number for the whole dataset. That number is a blend — good performance on vulnerable groups gets averaged down by poor performance on safe groups. If an attacker could instead choose to attack *only* the vulnerable groups, their reported accuracy on that smaller slice would be much higher, at the cost of not learning anything about the rest of the dataset.

The attack budget \(\kappa\) formalizes the trade-off in that choice: it's the fraction of the dataset the attacker is willing to commit to attacking, out of the full range from "attack almost nobody" to "attack half the dataset." A small \(\kappa\) means the attacker is very selective — attacking only the most obviously vulnerable sliver of records — and should therefore see very high accuracy on that sliver. A large \(\kappa\) (up to 0.5, since beyond half the dataset the notion of "the vulnerable half" stops being meaningful) means the attacker is casting a wider net and should see lower, more average-like accuracy, converging toward the untargeted number as \(\kappa \to 1\).

The definition doesn't just say "pick a subset of roughly the right size" — it also demands that the chosen subset actually be *the best available* subset of that size or larger. This is the condition that gives the whole exercise teeth: if you were merely allowed to cherry-pick any subset near the target size, you could construct something misleadingly good by chance. Requiring the target subset to beat every larger subset means the gain has to be real disparity, not noise or luck. That's also what makes the underlying search hard — comparing a candidate subset against literally every possible subset of equal or greater size is not something anyone can do exhaustively, so the paper restricts the search to subsets defined by actual attribute values (State, Occupation, and so on) and picks the best ones by exactly the angular-difference proxy developed on the `disparity-inference-attack` page.

## Mechanics {#mechanics}

**Setup.** Let \(\mathcal{M}\) be the target model trained on dataset \(\mathbb{D}\), with \(ASR(\mathcal{M}, \mathcal{N}(\mathbb{D}), \mathcal{A})\) the attack success rate of algorithm \(\mathcal{A}\) using the non-sensitive portion \(\mathcal{N}(\mathbb{D})\) of any dataset. The adversary's objective is to find a target subset \(\mathbb{D}_{target} \subset \mathbb{D}\) satisfying two conditions simultaneously [§sec_5_3].

**Why the search is restricted rather than exhaustive.** Evaluating condition 2 (below) against every possible subset \(D'\) of \(\mathbb{D}\) is computationally intractable — the space of subsets is exponential. The paper's fix is to only consider subsets defined by restricting one or more non-sensitive attributes to a subset of their possible values (e.g., "State = Texas" or "State ∈ {Texas, Ohio} and Occupation = Nurse"), which is a much smaller, structured search space [§sec_5_3].

**Why angular difference substitutes for ASR here too.** The adversary still cannot compute \(ASR\) on any candidate subset directly, for the same reason as in the disparity inference attack: doing so would require the true sensitive values. So the search goal shifts from "maximize \(ASR\)" to "maximize angular difference," reusing the exact proxy metric from the `angular-difference` and `disparity-inference-attack` concepts [§sec_5_3].

**Single attribute-based targeted attack.** Sample a query subset \(D_q\) of size \(q \times |\mathbb{D}|\) to limit model queries. For each non-sensitive attribute \(a\), split \(D_q\) into subsets by the values of \(a\), compute the angular difference of each subset, and record the range (max minus min) of those angular differences. Pick the attribute \(a\) with the widest range — the intuition being that the attribute whose subsets vary most in angular difference is the one most likely to contain a genuinely vulnerable slice. Rank that attribute's groups by angular difference and aggregate the most vulnerable ones, in decreasing order, until the accumulated size satisfies the budget condition [§sec_5_3_1].

**Nested attribute-based targeted attack.** Instead of committing to a single attribute, this variant intersects the "above-average-risk" segments (roughly the top half of records by angular difference) of several attributes. The number of attributes nested, \(d\), is set to \(\lceil \log_2(\kappa) \rceil\) — smaller \(\kappa\) (a tighter budget) permits deeper nesting, since intersecting more attributes' risky segments naturally shrinks the resulting subset. This lets the attack carve out narrower, more precisely targeted slices than a single attribute alone could reach [§sec_5_3_2].

**Empirical payoff.** On Census19, single attribute-based targeted CSMIA rises from 62.56% (untargeted, \(\kappa=1\)) to 73.27% at \(\kappa=0.05\); LOMIA rises from 61.24% to 73.78% — gains the paper reports as 17.12% and 20.48% respectively. On Texas-100X and Adult the same pattern holds, and the nested variant pushes further: on Texas-100X, nested attacks reach 100% accuracy at a nesting depth of 5; on Adult, 86.77% [§sec_6_4]. The paper also confirms this gain isn't an artifact of a particular model: varying MLP depth from 2 to 4 hidden layers produces essentially the same targeted-attack accuracy at a given \(\kappa\) [§sec_6_4].

## The Math {#the-math}

The target subset \(\mathbb{D}_{target}\) must first satisfy a size constraint tied to the budget \(\kappa\) [eq_2]:

$$
\left| \frac{|\mathbb{D}_{target}|}{|\mathbb{D}|} - \kappa \right| < \epsilon
$$

Here \(\kappa \in (0, 0.5]\) is the attack budget — the target fraction of the dataset the adversary commits to attacking — and \(\epsilon\) is set to a very small value, present only to allow the discrete subset size to approximate \(\kappa\) exactly rather than hit it precisely. \(\kappa = 1\) is used elsewhere as shorthand for the untargeted baseline, i.e., attacking the whole dataset [§sec_5_3].

Second, among all subsets meeting that size constraint, \(\mathbb{D}_{target}\) must be at least as good as every subset that is at least as large as it [eq_3]:

$$
\begin{aligned}
ASR(\mathcal{M},\; \mathcal{N}(\mathbb{D}_{\text{target}}),\; \mathcal{A}) &\geq ASR(\mathcal{M},\; \mathcal{N}(\mathbb{D}'),\; \mathcal{A}) \\
\forall\; \mathbb{D}' \in \{\mathbb{D}' \subset \mathbb{D} \;&\mid\; |\mathbb{D}'| > |\mathbb{D}_{\text{target}}|\}
\end{aligned}
$$

The role of this second condition is to rule out cherry-picking: it is not enough for \(\mathbb{D}_{target}\) to merely be a subset near the right size with decent accuracy — it must be provably at least as good as everything larger, so the accuracy gain when shrinking to \(\mathbb{D}_{target}\) is attributable to real, exploitable disparity in the data rather than to accidentally selecting a lucky handful of records [eq_3]. The paper notes explicitly that the *degree* of disparate vulnerability in the dataset is what bounds how much a targeted attack can improve over an untargeted one — a dataset with little disparity gives a targeted attacker little room to gain [§sec_5_3].

Because evaluating condition [eq_3] over all subsets \(\mathbb{D}'\) is intractable, the actual search (detailed in Mechanics) restricts \(\mathbb{D}'\) to attribute-value-defined subsets and substitutes angular difference for \(ASR\) as the objective being greedily maximized [§sec_5_3].

## Go Deeper {#go-deeper}

- **[§sec_5_3] Targeted Attribute Inference Attack** — the source section for both equations on this page, and the intractability argument that shapes the entire search strategy.
- **[§sec_5_3_1] Single Attribute-based Targeted Attack** — the concrete six-step procedure for the simpler of the two targeted attacks.
- **[§sec_5_3_2] Nested Attribute-based Targeted Attack** — the depth-\(d\) intersection procedure for the more aggressive targeted attack.
- **[§sec_6_4] Targeted Attribute Inference Attack** — the accuracy-vs-\(\kappa\) results tables (Census19, Texas-100X, Adult) and the MLP-depth robustness check.
- Related concepts: `disparity-inference-attack` for the ranking this attack consumes, `single-attribute-targeted-attack` and `nested-attribute-targeted-attack` for the two concrete strategies built on this objective, `angular-difference` for the proxy metric the search actually optimizes.

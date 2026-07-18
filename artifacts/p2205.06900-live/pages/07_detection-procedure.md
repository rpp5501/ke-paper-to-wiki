# Detection Procedure

## TL;DR {#tldr}
The Detection Procedure is the core two-stage algorithm of MM-BD: for every class in the classifier, it estimates a Maximum Margin (MM) statistic, then treats the largest of these statistics as a potential signal of a backdoor attack (BA), flagging an attack and its target class only if that maximum is a statistical outlier relative to the rest.

## Intuition {#intuition}
The procedure sits at the heart of MM-BD: Maximum-Margin Backdoor Detection, and it directly consumes the Maximum Margin (MM) Statistic as a prerequisite input — one MM value is computed per putative target class. Internally, the Detection Procedure is composed of two sub-parts: an Estimation Step (MM Optimization) that produces the per-class statistics, and a Detection Threshold via Null Distribution stage that decides whether the largest statistic is anomalous enough to declare an attack. The intuition is that a backdoored class will let an adversarial input reach an unusually large margin over all other classes, so scanning every class for this "too easy to push into" behavior and comparing the most extreme case against the typical spread of the rest is enough to catch the attack without needing any labeled poisoned examples. Once a target class is flagged this way, the result feeds forward into Mitigation of Backdoor Attack, and the same detection logic is later generalized by UnivBD (Universal Backdoor Detector).

## Mechanics {#mechanics}
For each putative target class, the procedure estimates an MM statistic by solving an optimization problem over the input domain using gradient ascent with projection onto the valid input space, iterating until convergence — a guarantee that holds because the logit functions are continuous and the domain is compact [§sec_3_2]. To avoid poor local optima, the optimization is repeated from multiple random initializations (e.g., uniformly random pixel values for images), and the best solution found is kept [§sec_3_2]. A key structural property of this estimation step is that it is agnostic to the backdoor pattern (BP) type, unlike reverse-engineering defenses (REDs) that presume a specific embedding function, and it requires no clean legitimate samples from source classes, which lets it detect attacks with an arbitrary number of source classes even when REDs would fail because most non-target classes are not actual source classes [§sec_3_2]. Once every class has an estimated MM statistic, the detection inference step designates the largest one as the candidate signal and fits an unsupervised null distribution from all the remaining, non-maximal statistics, reasoning that under an attack the true target class's statistic will be an outlier against this null [§sec_3_2]. Because MM statistics are strictly positive both theoretically and empirically, the null is modeled with a single-tailed density such as a Gamma distribution, and atypicality of the maximum is quantified via an order-statistic p-value; a detection is declared with confidence level α (e.g., the classical α = 0.05) whenever this p-value falls below α, and the class that produced the maximum statistic is then inferred to be the backdoor's target class [§sec_3_2].

## The Math {#the-math}
The per-class MM statistic is obtained by solving the following maximization over the input domain, where the objective is the target class's logit minus the maximum logit among all other classes [eq_2].

$$
\label{eq:opt_main}
\maximize_{{\bf x}\in{\mathcal X}} \quad g_c({\bf x}) - \max_{k\in{\mathcal Y}\setminus c} g_{k}({\bf x})
$$ [eq_2]

Given the estimated null distribution $H_0$ fitted to the non-maximal statistics and the maximum statistic $r_{\rm max}$, the atypicality of the candidate target class is quantified by the following order-statistic p-value over $K$ classes [eq_3].

$$
{\rm pv}=1-H_0(r_{\rm max})^{K-1},
$$ [eq_3]

## Go Deeper {#go-deeper}
No research note is associated with this concept, so no external resources can be listed here.

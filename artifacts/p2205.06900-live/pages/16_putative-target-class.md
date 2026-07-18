# Putative Target Class
## TL;DR {#tldr}
A putative target class is simply one of the candidate output classes, considered in turn as the *hypothesized* backdoor target during detection. MM-BD does not assume in advance which class an attacker targeted; instead it treats every class as a putative target and lets the Estimation Step decide which one actually looks anomalous.

## Intuition {#intuition}
Think of the detector as interrogating every class as a suspect: for each class c, it asks "if the true backdoor target were c, how easy would it be to force any input into being classified as c?" Classes that are not actually backdoored require large, unnatural perturbations to force this misclassification, while the true target class (if one exists) admits a suspiciously "cheap" shortcut. Cycling through all classes as putative targets is what lets the method work without knowing the attack pattern or which classes the attacker used as sources.

## Mechanics {#mechanics}
For each putative target class, the estimation step solves an optimization problem over the input domain, using gradient ascent with projection onto the valid input space, and this optimization is guaranteed to converge because the logit functions are continuous and the domain is compact [§sec_3_2]. Because convergence is not guaranteed to reach a global optimum, the procedure uses multiple random initializations within the input domain and keeps the best solution found for that class [§sec_3_2]. A key property of treating each class as a putative target this way is that the optimization is entirely independent of the backdoor pattern's type, unlike reverse-engineering defenses (REDs) that presume a specific embedding function [§sec_3_2]. This also means the approach does not require clean samples from every non-target class, so it remains effective even when a backdoor attack uses an arbitrary or limited number of source classes, a scenario where REDs can fail [§sec_3_2].

## The Math {#the-math}
For a putative target class c, the estimation step solves the following maximum-margin optimization over the input domain [eq_2]:
$$
\maximize_{{\bf x}\in{\mathcal X}} \quad g_c({\bf x}) - \max_{k\in{\mathcal Y}\setminus c} g_{k}({\bf x})
$$ [eq_2]
The largest statistic across all putative target classes is then tested for atypicality by computing an order-statistic p-value against a null distribution fit from the other classes' statistics [eq_3]:
$$
{\rm pv}=1-H_0(r_{\rm max})^{K-1},
$$ [eq_3]
where the class achieving this largest, atypical statistic is inferred as the backdoor target class if the p-value falls below the detection threshold [§sec_3_2].

## Go Deeper {#go-deeper}
No research note is available for this concept, so no external resources can be listed here.

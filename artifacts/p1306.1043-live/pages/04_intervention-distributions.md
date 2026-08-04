# Intervention Distributions
## TL;DR {#tldr}
Intervention distributions describe what happens to the distribution of a variable when another variable is forced to a fixed value by external intervention, rather than merely observed. They are the building block that the Structural Intervention Distance (SID) uses to compare how well one causal graph's implied interventions match another's.

## Intuition {#intuition}
Asking "what is the distribution of Y given that we observe X = x" is different from asking "what would the distribution of Y be if we forced X = x by intervention." The first is a conditional distribution; the second, written using the do-operator, strips away the influence of X's normal causes and asks what would happen if X were set from outside the system. Intervention distributions formalize this second, causal question, and comparing intervention distributions implied by two different graphs is the core idea behind evaluating how "causally right" an estimated graph is — the motivation for SID.

## Mechanics {#mechanics}
The intervention distribution for a target Y under an intervention setting X to a fixed value x̂ is defined via the graph's Markov factorization: when the joint density is Markov with respect to the graph, it factorizes accordingly, and the intervention distribution is obtained from this factorization by replacing X's own mechanism with the fixed value [§sec_1_2].

If X is not a parent of Y, the intervention distribution can still be computed by marginalizing over only a subset of the variables in the graph rather than the full joint, and whenever this marginalized computation can be written as a summation over such a subset, that subset is called an adjustment set for the intervention [§sec_1_2].

A given graph can admit multiple valid adjustment sets for the same pair of nodes — some larger, some smaller, and some sets are invalid regardless of size (for instance, sets containing a node that opens a biasing path) — which is why identifying the parents of X, or another valid adjustment set, is central to computing the effect correctly [§sec_1_2].

## The Math {#the-math}
When Y is unaffected by intervening on X — for example when Y is a parent or non-descendant of X — the intervention distribution collapses to the ordinary marginal distribution of Y, since forcing X provides no new information propagating to Y [eq_2].

$$p_{\G}(y \given \doo(X = \hat x)) = p(y) \,.$$ [eq_2]

When X does have parents that mediate its effect, the intervention distribution is instead computed by adjusting for the parents of X: summing the conditional distribution of Y given the intervened value and X's parents, weighted by the distribution of those parents [eq_3].

$$p_{\G}(y \given \doo(X = \hat x)) = \sum_{\pa[]{X}} p(y \given \hat x, \pa[]{X}) \, p(\pa[]{X}) \,.$$ [eq_3]

This parent-adjustment formula shows that the parents of X always form a valid adjustment set for computing the intervention distribution on Y, though the local context notes other, sometimes smaller, valid adjustment sets can also exist for a given graph [§sec_1_2].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here beyond the paper's own treatment in §sec_1_2.

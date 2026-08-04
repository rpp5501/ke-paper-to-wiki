# Comparing Estimated and True Causal Graphs

## TL;DR {#tldr}
When you estimate a causal graph from data, you need a way to grade how good that estimate is against the true underlying structure. This concept is about the general problem of measuring closeness between an estimated DAG and a true DAG — a problem for which the Structural Intervention Distance (SID) was proposed as a better tool than simple edge-counting.

## Intuition {#intuition}
Imagine you've learned a causal graph from observational data, and you want to know how "wrong" it is compared to the real one. The obvious approach is to count how many edges differ — but that treats every mistake as equally bad, even though some wrong edges completely break your ability to reason about interventions while others barely matter. The motivating idea behind this concept is that graph comparison should be judged by what the graphs let you *do* — specifically, whether the estimated graph lets you correctly predict what happens when you intervene on the system — rather than by superficial structural similarity alone.

## Mechanics {#mechanics}
Given a true causal DAG and an estimated DAG, the goal is to assess the quality of the estimate, or more generally to measure closeness between any two DAGs [§sec_1]. The Structural Hamming Distance (SHD) is the established baseline: it simply counts the number of incorrect edges between the two graphs [§sec_1]. The key limitation motivating this concept is that SHD, while an intuitive distance, does not reflect the graphs' capacity for causal inference — two graphs can have a small edge-count difference yet disagree sharply on what interventions predict, or vice versa [§sec_1]. This gap is what motivates counting, instead, the pairs of vertices for which the estimated graph correctly predicts intervention distributions within the class of distributions Markov with respect to the true graph — the construction underlying the prerequisite concept, the Structural Intervention Distance [§sec_1].

## The Math {#the-math}
The local context for this concept is the paper's introduction, which frames the comparison problem and motivates SID conceptually rather than presenting its formal definition or equations — no equations are available at this tier, so the formal machinery belongs to the SID concept itself [§sec_1].

## Go Deeper {#go-deeper}
- Structural Intervention Distance (SID) — the prerequisite concept that formalizes the intervention-based comparison motivated here; read it for the actual definition and properties.

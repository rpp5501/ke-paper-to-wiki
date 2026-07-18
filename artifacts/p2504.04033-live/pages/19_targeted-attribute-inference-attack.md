# Targeted Attribute Inference Attack

## TL;DR {#tldr}
A Targeted Attribute Inference Attack is a refinement of standard attribute inference where the adversary, instead of attacking the whole population uniformly, searches for a small subset of records on which the attack performs disparately better than it does elsewhere — exposing that privacy risk is not evenly distributed across a dataset. It sits within the broader Attack Methodology, depends on the ability to compute angular difference as a proxy for attack strength, and branches into two concrete strategies, Single Attribute-based and Nested Attribute-based targeted attacks, whose results feed directly into evaluating Targeted Attribute Inference Attack Performance.

## Intuition {#intuition}
An untargeted attack reports one average success rate for an entire population, which can hide the fact that some slice of records — say, people sharing a particular combination of non-sensitive attributes — are far easier to de-anonymize than others. The targeted attack formalizes the adversary's incentive to go hunting for that worst-case slice rather than settling for the population average, since finding it demonstrates a much sharper, more concrete privacy failure. The catch is that the adversary has no labeled auxiliary data to directly measure success rate on candidate subsets, so instead of brute-force search, the attack leans on a cheaper geometric signal — angular difference — that correlates with attack success and can be computed from the non-sensitive attributes alone, making the search for a vulnerable subgroup tractable.

## Mechanics {#mechanics}
Given a target model trained on dataset , the adversary measures an attack's success rate using only the non-sensitive portion of whatever data subset it examines, and its goal is to locate a target subset that is small — pinned to a chosen attack budget within a small tolerance — while also outperforming, in attack success rate, every other subset of equal or larger size [§sec_5_3]. This second requirement is what captures "disparate vulnerability": the gap between what the adversary achieves on the targeted subset versus an untargeted attack on the full population quantifies how much extra harm targeting produces [§sec_5_3]. Checking this condition exhaustively over all possible subsets is computationally intractable, so the search space is constrained to subsets defined by restricting one or more non-sensitive attributes to particular value ranges, and even within that constrained space, naively computing angular difference for every candidate subset remains exponentially expensive — motivating the two optimized exploration strategies (single-attribute and nested-attribute) developed to make the search feasible [§sec_5_3].

## The Math {#the-math}
The size constraint requires the target subset's share of the full dataset to sit within of the attack budget [eq_2]:
$$
\begin{aligned}
\left| \frac{|\mathbb{D}_{target}|}{|\mathbb{D}|} - \kappa \right| < \epsilon
\end{aligned}
\label{eq:targeted_attack_size_condition}
$$ [eq_2]

The performance-superiority condition requires that the attack's success rate on the non-sensitive portion of the target subset be at least as high as its success rate on any other subset of equal or greater size, which is what makes the found subset "targeted" rather than an arbitrary sample [eq_3]:
$$
\begin{aligned}
ASR(\mathcal{M},\;\mathcal{N}(\mathbb{D}_{\text{target}}),\;\mathcal{A}) &\geq ASR(\mathcal{M},\;\mathcal{N}(\mathbb{D}'),\;\mathcal{A}) \\
\forall\;\mathbb{D}' \in \{\mathbb{D}' \subset \mathbb{D} &\mid |\mathbb{D}'| > |\mathbb{D}_{\text{target}}|\}
\end{aligned}
\label{eq:targeted_attack_condition}
$$ [eq_3]

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.

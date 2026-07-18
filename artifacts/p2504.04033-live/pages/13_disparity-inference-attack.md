# Disparity Inference Attack
## TL;DR {#tldr}
The Disparity Inference Attack is the core attack methodology studied in this paper: rather than trying to infer a sensitive attribute for every individual, the adversary tries to rank subgroups of a dataset by how vulnerable each one is to attribute inference, without ever learning the true sensitive values. It sits within the broader Attack Methodology of the paper and depends on first being able to compute an angular difference signal for each subgroup, which is later used to evaluate how well the ranking predicts real attack performance.

## Intuition {#intuition}
Instead of asking "can I guess this person's sensitive attribute?", this attack asks a subtler question: "which groups of people are more exposed to attribute-inference attacks than others?" An attacker who can answer that question learns where a model's privacy leakage is concentrated even while remaining blind to the actual sensitive labels — which is exactly what makes the attack realistic, since a real adversary rarely has ground-truth sensitive attributes to check their work against. The attack is a ranking problem: order the subgroups from most to least vulnerable, and try to match that order to the ranking that would appear if the attacker's true success rates were known.

## Mechanics {#mechanics}
The setup is a target model trained on a dataset that is split into non-overlapping subsets, and the attacker only has access to the non-sensitive part of the data for each subset [§sec_5_2]. The attack vulnerability ranking of interest is the ordering of these subsets by the true attack success rate on each one, and the attacker's goal is to recover this ordering, or one very close to it, using only the accessible non-sensitive data [§sec_5_2]. Critically, the attacker does not know the true sensitive attribute values, which is what makes the ranking problem non-trivial rather than something solvable by direct lookup [§sec_5_2]. The procedure itself queries the target model to build a confidence matrix for each subset, then computes an angular difference measure for each subset from that matrix, and finally ranks the subset indices by decreasing angular-difference values to produce the output ranking [§sec_5_2].

## The Math {#the-math}
The target ranking the attacker is trying to approximate is defined over the true attack success rates ASR of the subsets, stated as an ordering condition over indices [eq_1]:

$$\{r_1, r_2, \dots, r_k\} &= [1, k] \\
    ASR(\mathcal{M},\;\mathcal{N}(\mathbb{D}_{r_i}),\;\mathcal{A}) &\geq ASR(\mathcal{M},\;\mathcal{N}(\mathbb{D}_{r_j}), \mathcal{A}) \\
    &\forall\; 1 \leq i < j \leq k$$ [eq_1]

This says that indices are permuted into an order $r_1,\dots,r_k$ such that the attack success rate against the non-sensitive data of subset $r_i$ is at least as high as that of subset $r_j$ for every earlier-later index pair, i.e., the permutation sorts subsets from most to least attackable [eq_1]. The local context does not provide further derivations or additional equations beyond this ranking definition for the Disparity Inference Attack itself [§sec_5_2].

## Go Deeper {#go-deeper}
- **Computing Angular Difference** (prerequisite) — needed first, since the attack's ranking output is produced by sorting subsets on this exact angular-difference score.
- **Disparity Inference Attack Performance** (builds-on) — the natural next read, since it evaluates how closely the recovered ranking matches the true vulnerability ranking defined here.
- **Attack Methodology** (part-of) — the parent section for broader context on where this attack fits among the paper's other attacks.
- No dedicated research note exists for this concept, so no external research resources are listed here.

# Comparing Estimated and True Causal Graphs

## TL;DR {#tldr}

Given a true causal DAG and an estimate of it produced by some structure-learning procedure, how good is the estimate? The obvious answer — count the edges that differ — misses the point of learning a causal graph in the first place: what you actually care about is whether the estimate lets you predict the *effect of interventions* correctly, not whether it matches the true graph edge-for-edge. Comparing two DAGs for causal purposes therefore means asking, for each pair of variables, whether the estimated graph would get the interventional prediction right if you used it and were correct in every other respect. This reframing is what motivates the Structural Intervention Distance (SID), the prerequisite concept this page sits under.

## Intuition {#intuition}

Two estimated graphs can have the same number of wrong edges and yet be wildly different in how useful they are for causal reasoning — a wrong edge near a variable that acts as a confounder can corrupt many downstream intervention predictions, while a wrong edge elsewhere might change nothing about what you'd conclude from an intervention. A metric that only counts edges, like the Structural Hamming Distance, cannot tell these two situations apart. The idea behind comparing graphs by their causal capacity is to instead ask a "would this still work" question for every ordered pair of variables: if you used the estimated graph's parent structure to compute the effect of intervening on one variable and reading off another, would you get the same answer as the true graph gives? Counting how often the answer is yes turns "how wrong is my graph" into "how much of my graph's causal usefulness survived."

## Mechanics {#mechanics}

The comparison is set up over a finite family of random variables indexed by a vertex set, with a joint distribution and (assumed-existing) densities with respect to Lebesgue or counting measure, plus the corresponding conditional densities; graphs are pairs of nodes and edges, and nodes are identified with the variables they represent [§sec_1]. This identification is what lets the same object serve two roles: a vertex in the DAG and a random variable whose distribution can be conditioned on or intervened upon [§sec_1].

The estimate is scored by counting, over pairs of vertices, how many pairs it gets right — where "right" means it correctly predicts the intervention distribution for that pair, evaluated within the class of distributions that are Markov with respect to the true graph [§sec_1]. Fixing the reference class to distributions Markov to the *true* graph (rather than the estimate) is what keeps the comparison well-defined: the ground truth being tested against does not itself depend on which graph you happen to be scoring [§sec_1].

This produces a genuinely new pre-distance between DAGs rather than a variant of SHD, and the paper is explicit that it is not aware of a directly related prior notion — it is meant to supplement SHD with information about causal-inference capacity, not replace it [§sec_1].

## The Math {#the-math}

No display equation is introduced yet at this point in the paper — the formal apparatus below is the notation the rest of the SID definition builds on, not the metric itself [§sec_1].

**Why the formalism separates variables from their densities:** the family of random variables is indexed by the vertex set, its joint distribution is denoted separately from its densities, and conditional densities are denoted separately again [§sec_1]. Keeping these three objects distinct matters because the intervention distributions that SID compares are conditional/interventional densities of exactly this kind — the notation has to support writing "the density of one variable given an intervention on another" before any comparison of graphs can even be stated [§sec_1].

**What breaks without the node–variable identification:** treating vertices and variables as literally the same object (with only "a slight abuse of notation" flagged) is what allows a graph edge to be read simultaneously as a structural claim and as a statement about conditional independence or intervention effects [§sec_1]. If nodes and variables were kept formally distinct, every downstream definition of an intervention distribution "with respect to a graph" would need an explicit translation step between the two; the abuse of notation is a deliberate simplification that removes that overhead [§sec_1].

**Boundary condition worth noting:** existence of the densities is assumed rather than derived, which quietly restricts the results that follow to distributions absolutely continuous with respect to Lebesgue or counting measure — discrete or continuous, but not, e.g., distributions with a singular component [§sec_1].

## Go Deeper {#go-deeper}

- **§sec_2 (Structural Hamming Distance)** — the baseline metric this concept is defined in contrast to; read it first to see exactly what "counting wrong edges" misses [§sec_1].
- **§sec_3 (do-calculus)** — supplies the machinery for the intervention distributions that SID actually compares, referenced here as prerequisite background [§sec_1].
- **§sec_4 (SID definition and properties)** — where the pairwise-correctness counting sketched above is turned into the formal (pre-)distance [§sec_1].
- **Appendix (DAG terminology)** — the graph-theoretic definitions the paper leans on throughout, flagged in the introduction as required background [§sec_1].

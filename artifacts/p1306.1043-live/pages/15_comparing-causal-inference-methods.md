# Comparing Causal Inference Methods

## TL;DR {#tldr}
This concept asks a practical question: when different causal discovery algorithms are run on the same data, which one actually recovers a graph that is *causally* closer to the truth? It builds on the earlier comparison of SID versus SHD in a simulation setting, extending that analysis to a head-to-head evaluation of several real inference methods rather than synthetic graph perturbations.

## Intuition {#intuition}
Different algorithms make different tradeoffs. Some are good at finding which variables are connected but unreliable about the direction of the connection; others use stronger distributional assumptions to pin down direction as well. The point of comparing methods this way is to see whether a metric that rewards "getting the causal effect structure right" (SID) tells a different story than one that just counts edge mismatches (SHD) — and if so, which story should guide a practitioner choosing a method for a downstream causal task.

## Mechanics {#mechanics}
The experiment simulates sparse random ground-truth DAGs and draws data from a linear Gaussian structural equation model with equal error variances, then runs several inference methods on that data: the PC algorithm, conservative PC (CPC), greedy equivalence search (GES), and a greedy DAG search variant (GDS) that exploits the equal-error-variance assumption to identify the DAG directly [§sec_3_2]. Because PC, CPC, and GES output a Markov equivalence class rather than a single DAG, the evaluation reports both a lower and an upper bound on SID — the smallest and largest distance achievable by any DAG in that class — while GDS, which outputs a single DAG, gets one number [§sec_3_2]. A random baseline (RAND), which ignores the data entirely and samples a DAG with a uniformly chosen number of edges, is included to give a sense of the floor performance any real method should beat [§sec_3_2].

## The Math {#the-math}
The local context for this section reports simulation results (average SID and SHD across 100 trials per setting) but does not include the underlying equations; those appear in the earlier sections defining SID and SHD themselves [§sec_3_2]. The key quantitative finding is that the SID upper bound for methods like PC can be no better than the RAND baseline in a substantial fraction of trials for small sample sizes, even though PC reliably beats RAND on SHD in the same regime — indicating PC recovers the skeleton of the DAG more reliably than it recovers edge orientations [§sec_3_2]. Consequently the two metrics can disagree sharply on which method is "best": for some settings PC has the best (lowest) SHD while simultaneously having the worst SID, showing that a method's apparent structural accuracy under Hamming distance does not guarantee accuracy of the causal effects it implies [§sec_3_2].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to list here.

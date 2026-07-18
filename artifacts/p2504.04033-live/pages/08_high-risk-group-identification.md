# Uncovering High-Risk Groups
## TL;DR {#tldr}
Not all subgroups in a population are equally exposed to attribute inference attacks — some demographic or behavioral groups leak sensitive attributes far more easily than others, and this concept is about how to systematically find those high-risk groups rather than just measuring privacy risk in aggregate. It sits inside the paper's broader account of Disparate Privacy Vulnerability, and it builds directly on the paper's Attack Methodology: you first need a working attribute inference attack before you can ask which groups that attack is most dangerous against.

## Intuition {#intuition}
Think of an attribute inference attack as a metal detector sweeping over a population: a single aggregate accuracy number tells you the detector works "well enough" on average, but it hides the fact that it beeps loudly over some patches of ground and stays silent over others. Uncovering High-Risk Groups is the process of walking that detector back over the population, subgroup by subgroup, to find where it beeps loudest — i.e., where the correlation between an easily observed proxy and the sensitive attribute is strong enough that the attacker barely needs to guess. This framing connects to two supporting ideas in the same neighborhood: identifying the Key Factor Contributing to Vulnerability (what makes a group risky in the first place) and Comparing Correlation between Groups (the comparative lens used to rank groups by exposure).

## Mechanics {#mechanics}
The local context available for this concept is limited to the section heading "Uncovering High-Risk Groups" (sec_4) without further extracted body text, so the specific procedural steps — how groups are partitioned, what threshold defines "high-risk," and what data drives the search — cannot be reproduced here beyond what the section title itself conveys [§sec_4].

## The Math {#the-math}
No equations were extracted into the local context for this section, so no formal risk metric or grouping criterion can be reproduced verbatim here [§sec_4].

## Go Deeper {#go-deeper}
No research note is attached to this concept, so there are no external resources to summarize here. Within the paper's own concept graph, the most relevant next stops are: **Key Factor Contributing to Vulnerability**, which likely explains *why* a group ends up high-risk; **Comparing Correlation between Groups**, which likely supplies the comparative method used to rank groups; and **Attack Methodology**, the prerequisite attack this concept applies across groups.

# Hidden Variables (Future Work)

## TL;DR {#tldr}
This concept sketches how the Structural Intervention Distance could be extended to settings where some variables are unobserved. It builds directly on the core SID framework, proposing that the same strategy used for CPDAGs — excluding non-identifiable pairs — could be adapted to graphs with hidden confounders.

## Intuition {#intuition}
The base SID assumes the true causal structure is fully observed, so every intervention distribution is identifiable from the DAG. Once hidden variables enter the picture, that assumption breaks: some causal effects simply can't be pinned down from the observed variables alone. Rather than abandoning the SID in this setting, the idea is to carve out the pairs of variables whose effects are identifiable and score only those, echoing how the CPDAG extension of SID already handles a related kind of ambiguity by excluding non-identifiable pairs.

## Mechanics {#mechanics}
When variables are unobserved, not all intervention distributions are identifiable from the true DAG, so the proposed road map explicitly excludes non-identifiable pairs from the structural intervention distance, mirroring the approach already used for CPDAGs [§sec_2_4_6].

The true structure in this setting can be represented in two alternative ways: as an acyclic directed mixed graph (ADMG), for which existing work characterizes which intervention distributions are identifiable, or as a maximal ancestral graph (MAG), where this characterization becomes more difficult [§sec_2_4_6].

Because methods like FCI output not a single MAG but an equivalence class of MAGs called partial ancestral graphs (PAGs), comparing an estimated PAG to a true MAG would require enumerating all MAGs represented by the PAG and computing lower and upper bounds on the distance, the same strategy used elsewhere for CPDAG comparisons; whether this can be done efficiently is left as an open question [§sec_2_4_6].

A further extension considers causal inference methods that output some other kind of graph over the observed variables together with, for each potential causal effect, either a valid adjustment set or a message that the effect is not identifiable — in that case the SID could compare methods by the proportion of effects that are identified and correctly identified [§sec_2_4_6].

## The Math {#the-math}
The local context for this concept describes a research road map in prose and does not provide any equations to reproduce [§sec_2_4_6].

## Go Deeper {#go-deeper}
- Structural Intervention Distance (SID) — the parent concept this future-work direction extends to handle unobserved variables.

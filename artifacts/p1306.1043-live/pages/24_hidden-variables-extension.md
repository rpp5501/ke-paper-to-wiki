# Hidden Variables (Future Work)

## TL;DR {#tldr}
When some variables are unobserved, the true causal structure can no longer be assumed to be a fully identifiable DAG, so the Structural Intervention Distance (SID) as originally defined cannot be computed outright. This section sketches a roadmap rather than a finished method: treat the ground truth as a richer object (an ADMG or a MAG), exclude pairs whose intervention effect isn't identifiable, and — when the estimate is only known up to an equivalence class (a PAG) — bound the SID the same way CPDAGs are bounded against DAGs. A second, looser option scores a causal-discovery method by how often it correctly reports an effect as identifiable (or not) at all.

## Intuition {#intuition}
SID's whole premise is that the true DAG's parent sets give you the *actual* intervention distributions to check the estimate against. Hidden confounders break that premise: for some pairs, no observed adjustment set recovers p(y | do(x)), no matter how good the estimated graph is. Those pairs aren't "wrong," they're simply unanswerable, and folding them into the same count as genuine errors would unfairly penalize (or credit) an estimate for something the data never determined.

The natural fix, already used elsewhere in the paper for equivalence classes, is to drop what can't be judged and only count what can. The complication with hidden variables is that even "what can be judged" is harder to pin down, because the object standing in for the true graph is itself less informative than a DAG.

## Mechanics {#mechanics}
**Three candidate ground-truth objects, in increasing order of difficulty.** An acyclic directed mixed graph (ADMG) marks confounders explicitly with bidirected edges, and existing work characterizes exactly which intervention distributions are identifiable from such a graph — so non-identifiable pairs can simply be excluded from the SID count, mirroring how CPDAGs exclude pairs with undetermined orientation. A maximal ancestral graph (MAG) is a coarser representation with no direct marker for which variables are confounders, so working out identifiability there is described as harder. A partial ancestral graph (PAG) — what FCI-type algorithms actually output — is coarser still: an equivalence class of MAGs, exactly analogous to how a CPDAG is an equivalence class of DAGs [§sec_2_4_6].

**Comparing an estimated PAG to a true MAG reuses the CPDAG machinery.** Because a PAG doesn't pick out one MAG, the roadmap proposes enumerating every MAG the PAG represents and computing lower and upper bounds on the SID over that set, the same bracketing strategy used for CPDAG-vs-DAG comparisons elsewhere in the paper. Making that enumeration efficient is explicitly left open [§sec_2_4_6].

```algorithm
title: Roadmap — comparing an estimated PAG to the true MAG
lines:
  - code: "for each ordered pair (i, j):"
    intent: "SID is still scored pointwise per intervention target/effect pair, as in the DAG and CPDAG cases [§sec_2_4_6]"
  - code: "    if effect of i on j is non-identifiable under the true structure:"
    intent: "Hidden confounders can make an intervention distribution unrecoverable from the graph alone [§sec_2_4_6]"
  - code: "        exclude (i, j) from the count"
    intent: "Mirrors how CPDAG-SID drops pairs whose orientation is undetermined by the equivalence class [§sec_2_4_6]"
  - code: "    else:"
    intent: "Only identifiable effects can meaningfully be checked against the estimate [§sec_2_4_6]"
  - code: "        enumerate every MAG consistent with the estimated PAG"
    intent: "A PAG stands for a class of MAGs just as a CPDAG stands for a class of DAGs [§sec_2_4_6]"
  - code: "        compute lower and upper bound of the mismatch over that class"
    intent: "Reuses the bracketing already built for CPDAG-vs-DAG, since no single representative MAG can be singled out [§sec_2_4_6]"
```

**A looser, method-agnostic alternative sidesteps graph comparison entirely.** If a causal-discovery method reports, for every pair, either a usable adjustment set or an explicit "not identifiable" flag, SID can instead score it by the proportion of pairs correctly identified as identifiable *and* correctly solved among those — trading precision about graph structure for a metric that works for any method, not just DAG/CPDAG estimators [§sec_2_4_6].

## The Math {#the-math}
No display equation accompanies this section — it is a roadmap, not a derivation — but the *why* behind the stated difficulty is concrete enough to work out.

**Why identifiability is easy to read off an ADMG but not a MAG:** in a plain DAG, pa(X) is a single graph-determined adjustment set, so identifiability is immediate and the SID never has to ask "can this even be checked?" An ADMG keeps that property for the confounded case because bidirected edges mark exactly where the unobserved common causes sit, so the existing identifiability characterization can be applied edge-by-edge. A MAG discards that marker: it encodes ancestral and separation relations that are consistent with some underlying confounded structure, but not the structure itself, so deciding identifiability means reasoning over the whole family of latent-variable graphs a MAG could compress — which is precisely why the text calls this characterization "more difficult" rather than solved [§sec_2_4_6].

**Why the PAG case compounds the enumeration cost already flagged for CPDAGs:** an undirected CPDAG edge has exactly two resolutions (X→Y or Y→X), so each undetermined edge doubles the DAG count in the equivalence class. A PAG edge carries an endpoint mark at *each* end (arrowhead, tail, or still-circle), and those two marks can resolve independently, so an undetermined PAG edge admits at least as many resolutions as a CPDAG edge and typically more. The enumeration of the equivalence class therefore grows at least as fast, which is the concrete reason the lower/upper-bound approach is proposed rather than an exact count, and why making it efficient is left as an open question [§sec_2_4_6].

## Go Deeper {#go-deeper}
- **Structural Intervention Distance (SID)** — this section is explicitly framed as extending SID's machinery (exclusion of non-identifiable pairs, lower/upper bounding over an equivalence class) to settings with hidden variables; read it first to see the CPDAG version of the same bounding trick this roadmap reuses.

# Hidden Variables (Future Work)

## TL;DR {#tldr}
SID as originally defined assumes every variable is observed, so every intervention distribution needed for the comparison can actually be computed from the true DAG. This concept sketches a road map for what happens when that assumption breaks: some intervention effects are no longer identifiable at all, and the framework has to be extended to graph classes that explicitly represent hidden confounding. The extension is not a finished method — it is a set of directions building on the core SID definition.

## Intuition {#intuition}
Think of the original SID as grading a map against the true terrain, where every landmark on the terrain is visible. Hidden variables punch blank patches into that terrain: some causal effects simply cannot be read off from the data no matter how good the graph estimate is. The natural response, already used once before when comparing to a CPDAG, is not to guess at the blank patches but to route around them — score only the effects that are knowable, and widen the comparison itself to admit graph types built to represent unobserved confounding.

## Mechanics {#mechanics}
The first move mirrors what was already done for CPDAGs: rather than trying to score every pair of variables, **non-identifiable pairs are excluded from the structural intervention distance outright**, so the metric only ever grades effects that could in principle be recovered from the data. This keeps the comparison honest instead of forcing a value onto an effect nothing could estimate [§sec_2_4_6].

With unobserved variables in play, the "true" structure itself needs a richer representation than a DAG. The road map considers two candidates side by side:

| Ground-truth representation | What it adds over a DAG | Identifiability characterization | Role in the SID road map |
|---|---|---|---|
| Acyclic directed mixed graph (ADMG) | bidirected edges for latent confounding | already addressed by prior work | preferred ground truth — lets non-identifiable pairs be excluded directly [§sec_2_4_6] |
| Maximal ancestral graph (MAG) | ancestral/non-ancestral relations abstracting hidden variables | markedly harder, open | alternative ground truth — usable but costlier to work with [§sec_2_4_6] |

Methods like FCI don't output a single MAG; they output a **partial ancestral graph (PAG)**, an equivalence class of MAGs, which is the estimation-side analogue of a CPDAG standing in for a class of DAGs [§sec_2_4_6]. Comparing an estimated PAG against a true MAG therefore has to reuse the same enumeration trick used for CPDAGs: walk every MAG the PAG represents, score each one, and report the resulting interval.

```algorithm
title: Road map — scoring an estimated PAG against a true MAG
lines:
  - code: "for each MAG M consistent with the estimated PAG:"
    intent: "A PAG leaves some edge marks undetermined, so it stands for a whole equivalence class of MAGs, exactly as a CPDAG stands for a class of DAGs [§sec_2_4_6]"
  - code: "    compute SID(M, true_MAG)"
    intent: "Each resolved MAG can be scored against the true MAG directly, since identifiability is well-defined once the marks are fixed [§sec_2_4_6]"
  - code: "report [min over M, max over M]"
    intent: "The true resolution is unknown, so the comparison degrades gracefully to a lower/upper bound rather than a single guessed number, the same move used for CPDAGs [§sec_2_4_6]"
```

A separate, more permissive extension drops the DAG-like structure altogether: if a causal inference method outputs *any* graph over the observed variables together with, for each potential effect, either an adjustment set or an explicit "not identifiable" flag, SID can still compare methods — by the proportion of effects each one identifies and identifies **correctly** [§sec_2_4_6].

## The Math {#the-math}
No display equation accompanies this extension in the source text, but the two mechanisms above still have concrete content worth making explicit. Take the enumeration-and-bound procedure first: its cost is driven entirely by how many MAGs a single PAG can represent. Every edge mark a PAG leaves unresolved is a fork in what the true MAG might be, so the count of representable MAGs grows combinatorially in the number of unresolved marks — structurally the same blow-up that makes CPDAG-to-DAG enumeration expensive, just transplanted to ancestral graphs. The text is explicit that no efficient algorithm is known yet; it flags this as open, not solved [§sec_2_4_6].

The adjustment-set-oracle variant is easier to pin down with a worked count. Suppose a method is run on $p = 4$ observed variables, giving $p(p-1) = 12$ ordered pairs, each pair being one potential causal effect $i \to j$. Say the method returns an adjustment set (rather than "not identifiable") for 9 of those 12 pairs, and of those 9, 7 match what the true, possibly-hidden-variable structure actually licenses. The comparison metric is then the proportion $7/12$ — a single number that simultaneously penalizes both under-identification (the 3 pairs left unaddressed) and mis-identification (the 2 wrong adjustment sets among the 9 attempted) [§sec_2_4_6].

The reason both routes exclude rather than impute unidentifiable effects is the same reason the CPDAG case excludes ambiguous pairs: assigning a numeric penalty to an effect that no amount of data could pin down would make the metric measure the graph class's inherent non-identifiability rather than the estimator's quality. Exclusion keeps SID measuring the thing it was built to measure [§sec_2_4_6].

## Go Deeper {#go-deeper}
No dedicated research note is attached to this concept; the paragraph itself names three threads worth following from here, each a direct extension of [[Structural Intervention Distance (SID)]]:
- **ADMG identifiability characterization** — cited work already characterizes which intervention distributions are identifiable from an ADMG; this is the load-bearing piece that lets non-identifiable pairs be excluded cleanly [§sec_2_4_6].
- **MAG/PAG enumeration bounds** — the harder, open half of the road map: extending the CPDAG-style lower/upper-bound enumeration to MAGs and PAGs, with efficiency left as future work [§sec_2_4_6].
- **FCI and successors** — the estimation methods that actually produce PAGs in practice, making them the natural test bed once the PAG-to-MAG comparison exists [§sec_2_4_6].
